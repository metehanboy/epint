# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import logging
import random
import threading
from typing import Dict, Optional, Tuple, Union, Any
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests import Session, Response
from requests.exceptions import RequestException, RetryError, Timeout, HTTPError
from ..version import __fullname__
import time

logger = logging.getLogger("epint")

# 429 gateway throttling paylaşılan (process çapında) durumu.
#
# EPİAŞ gateway'i rate limiti kaynak IP başına uyguluyor (bkz. header
# `X-RateLimit-Identity`) - yani limit tek bir HTTPClient/thread'e değil,
# process'in yaptığı TÜM isteklere birden uygulanıyor. Eskiden her thread
# kendi retry döngüsünde bağımsız karar veriyordu: `RateLimit-Reset` header'ı
# genellikle '0' geliyor (gateway saniye altı reset veriyor gibi görünüyor)
# ve bu değer olduğu gibi bekleme süresi sayılınca, aynı anda 429 alan N
# thread hemen (0s bekleyip) tekrar deniyor, gateway'i daha da yoruyor ve
# limit sürekli düşüyordu (bkz. canlı log: limit 50 -> 25 -> 12 -> 6
# istek/60sn birkaç saniye içinde). Fix: tüm thread'ler TEK bir paylaşılan
# "şu ana kadar bekle" kapısını (`_rate_limit_state["until"]`) kontrol eder;
# bir thread 429 alınca kapıyı ileri iter, kapının arkasındaki diğer TÜM
# thread'ler de (kendileri 429 almamış olsa bile) aynı pencereyi bekler.
_rate_limit_lock = threading.Lock()
_rate_limit_state: Dict[str, float] = {"until": 0.0, "consecutive_429": 0.0}

_RATE_LIMIT_MIN_WAIT = 1.0
_RATE_LIMIT_MAX_WAIT = 60.0


class HTTPClient:
    """
    Retry mekanizması olan gelişmiş HTTP client.
    Context manager olarak kullanılabilir.
    """

    def __init__(
        self,
        retries: int = 3,
        backoff_factor: float = 1.0,
        status_forcelist: Tuple[int, ...] = (500, 502, 503, 504),
        allowed_methods: Optional[Tuple[str, ...]] = None,
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
        headers: Optional[Dict[str, str]] = None,
        verify: bool = True,
        allow_redirects: bool = True,
        auth: Optional[Any] = None,
        max_rate_limit_retries: int = 8,
    ):
        """
        HTTP Client oluştur

        Args:
            retries: Toplam retry sayısı
            backoff_factor: Retry arasındaki bekleme çarpanı
            status_forcelist: Retry yapılacak HTTP status kodları
            allowed_methods: Retry yapılacak HTTP metodları (None ise tüm metodlar)
            timeout: Request timeout süresi (saniye) veya (connect_timeout, read_timeout) tuple
            headers: Varsayılan header'lar
            verify: SSL sertifika doğrulaması
            allow_redirects: Redirect'lere izin ver (default: True)
        """
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.status_forcelist = status_forcelist
        self.allowed_methods = allowed_methods or ("GET", "POST", "PUT", "DELETE", "PATCH")
        self.timeout = timeout
        self.headers = headers or {}
        self.verify = verify
        self.allow_redirects = allow_redirects
        self.auth = auth
        self.max_rate_limit_retries = max_rate_limit_retries

        self._session: Optional[Session] = None

    def _create_session(self) -> Session:
        """Retry mekanizması ile session oluştur"""
        session = Session()

        # Retry stratejisi
        retry_strategy = Retry(
            total=self.retries,
            read=self.retries,
            connect=self.retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=list(self.status_forcelist),
            allowed_methods=list(self.allowed_methods),
            raise_on_status=False,
        )

        # HTTP adapter'ları mount et
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20,
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Varsayılan header'ları ayarla
        if self.headers:
            session.headers.update(self.headers)

        session.headers.update({"User-Agent":__fullname__, "Accept-Language":"tr-TR"})

        return session

    def __enter__(self) -> HTTPClient:
        """Context manager giriş"""
        self._session = self._create_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager çıkış"""
        if self._session:
            self._session.close()
            self._session = None

    def _get_session(self) -> Session:
        """Session'ı al veya oluştur"""
        if self._session is None:
            self._session = self._create_session()
        return self._session

    def _check_rate_limit(self, response: Response) -> Optional[float]:
        """
        Rate limit header'larını kontrol et ve gerekirse bekleme süresi döndür

        Args:
            response: HTTP response objesi

        Returns:
            Bekleme süresi (saniye) veya None
        """
        headers = response.headers

        # Rate limit header'larını al
        remaining = headers.get('RateLimit-Remaining')
        limit = headers.get('RateLimit-Limit')
        reset = headers.get('RateLimit-Reset')

        if remaining is not None:
            try:
                remaining_int = int(remaining)
                # Eğer kalan istek sayısı 0 veya çok düşükse (örn. 5'ten az)
                if remaining_int <= 5:
                    # Reset süresini kontrol et
                    if reset is not None:
                        try:
                            reset_float = float(reset)
                            return reset_float
                        except (ValueError, TypeError):
                            pass
                    # Reset bilgisi yoksa varsayılan bekleme süresi
                    return 60.0
            except (ValueError, TypeError):
                pass

        return None

    def _wait_for_rate_limit_gate(self) -> None:
        """
        Paylaşılan rate-limit kapısı kapalıysa (başka bir istek/thread 429
        aldığı için), kapı açılana kadar bekle. Böylece aynı gateway'e
        eş-zamanlı istek atan diğer thread'ler de kör kör isteklerini
        gönderip 429'u derinleştirmek yerine ortak pencereyi bekler.
        """
        while True:
            with _rate_limit_lock:
                remaining = _rate_limit_state["until"] - time.monotonic()
            if remaining <= 0:
                return
            time.sleep(min(remaining, 5.0))

    def _register_rate_limit_hit(self, response: Response) -> float:
        """
        429 alındığında bekleme süresini hesapla ve paylaşılan kapıyı ileri
        it (tüm thread'ler bu pencereyi bekler). Ardışık 429 sayısına göre
        üstel geri çekilme uygular - gateway'in `RateLimit-Reset` header'ı
        genellikle '0' döndüğü için (bkz. modül üstü not) header değerine
        körü körüne güvenilmiyor, taban/tavan sınırlı üstel backoff ile
        birleştiriliyor.
        """
        header_wait = self._check_rate_limit(response)
        if header_wait is None:
            reset = response.headers.get('RateLimit-Reset')
            if reset is not None:
                try:
                    header_wait = float(reset)
                except (ValueError, TypeError):
                    header_wait = None

        with _rate_limit_lock:
            _rate_limit_state["consecutive_429"] += 1
            consecutive = _rate_limit_state["consecutive_429"]
            backoff = min(_RATE_LIMIT_MIN_WAIT * (2 ** (consecutive - 1)), _RATE_LIMIT_MAX_WAIT)
            wait = max(header_wait or 0.0, backoff)
            wait += random.uniform(0, wait * 0.1)
            _rate_limit_state["until"] = max(_rate_limit_state["until"], time.monotonic() + wait)

        return wait

    def _register_rate_limit_recovery(self) -> None:
        """Başarılı yanıt sonrası ardışık 429 sayacını sıfırla (backoff geriler)."""
        with _rate_limit_lock:
            _rate_limit_state["consecutive_429"] = 0

    def _is_tgt_invalid(self, response: Response) -> bool:
        """
        404 (CAS: "TGT ... could not be found/is considered invalid") veya 401
        (Şeffaflık/EPYS servisleri: errorCode AUTH009 "Güvenlik bilgisi(TGT)
        hatalı!") hatasında TGT geçersizliğini kontrol et.

        Args:
            response: HTTP response objesi

        Returns:
            TGT geçersizse True, değilse False
        """
        if response.status_code not in (401, 404):
            return False

        try:
            # Response body'yi text olarak al
            response_text = response.text if hasattr(response, 'text') else str(response.content or '')
            response_text_lower = response_text.lower()

            if response.status_code == 401:
                # Servis 401 döndüğünde body'de errorCode: AUTH009 var mı kontrol et
                # (bkz. şeffaflık örneği: {"errorCode": "AUTH009", "errorMessage":
                # "Güvenlik bilgisi(TGT) hatalı!"}) - bu, kullanılan TGT'nin servis
                # tarafında (halihazırda) geçersiz sayıldığı anlamına gelir.
                return 'auth009' in response_text_lower

            # TGT geçersizliğini belirten anahtar kelimeler
            tgt_invalid_keywords = [
                'could not be found',
                'is considered invalid',
                'invalid',
                'not found',
                'geçersiz',
                'bulunamadı'
            ]

            # TGT ile ilgili bir mesaj var mı kontrol et
            has_tgt_reference = 'tgt-' in response_text_lower or 'ticket' in response_text_lower

            # TGT geçersizliği belirtiliyor mu kontrol et
            is_tgt_invalid = any(keyword in response_text_lower for keyword in tgt_invalid_keywords)

            # Eğer TGT referansı var ve geçersizlik belirtiliyorsa True döndür
            return has_tgt_reference and is_tgt_invalid
        except:
            return False

    def _make_request(
        self,
        method: str,
        url: str,
        auth: Optional[Any] = None,
        **kwargs: Any
    ) -> Response:
        """
        HTTP request yap

        Args:
            method: HTTP metodu (GET, POST, vb.)
            url: Request URL'i
            auth: Bu istek için kullanılacak Authentication (verilmezse `self.auth`).
                Paylaşılan/kalıcı bir client'ta (bkz. `get_shared_client`) çağrılar
                arasında farklı auth gerekebileceğinden instance state yerine
                per-call parametre olarak geçirilir.
            **kwargs: requests.Session.request() için ek parametreler

        Returns:
            Response objesi

        Raises:
            RequestException: Request başarısız olduğunda
            Timeout: Timeout olduğunda
            RetryError: Retry limiti aşıldığında
        """
        session = self._get_session()
        effective_auth = auth if auth is not None else self.auth

        # Timeout ayarla
        if self.timeout is not None and 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout

        # SSL doğrulaması
        if 'verify' not in kwargs:
            kwargs['verify'] = self.verify

        # Redirect ayarı
        if 'allow_redirects' not in kwargs:
            kwargs['allow_redirects'] = self.allow_redirects

        response: Optional[Response] = None
        max_retries = 3
        retry_count = 0
        tgt_retry_count = 0
        max_tgt_retries = 3
        rate_limit_retry_count = 0

        while retry_count <= max_retries:
            try:
                # Başka bir thread'in tetiklediği 429 backoff'u varsa, kör kör
                # isteği göndermeden önce paylaşılan pencere kapanana kadar bekle.
                self._wait_for_rate_limit_gate()
                response = session.request(method=method.upper(), url=url, **kwargs)

                # 404 (CAS) veya 401 AUTH009 (şeffaflık/EPYS) - TGT geçersizliği kontrolü
                if response.status_code in (401, 404) and self._is_tgt_invalid(response):
                    if effective_auth and tgt_retry_count < max_tgt_retries:
                        # TGT geçersiz, ticket'ları temizle
                        logger.warning("TGT geçersiz, ticket cache temizleniyor ve yenileniyor (url=%s)", url)
                        effective_auth.clear_tickets()

                        try:
                            # Yeni TGT al
                            new_tgt_code, _ = effective_auth.get_tgt()

                            # URL'de TGT kodu varsa yeni TGT ile güncelle (CAS ST üretimi)
                            if '/cas/v1/tickets/' in url or '/v1/tickets/' in url:
                                import re
                                # TGT- ile başlayan kodu bul ve değiştir
                                url = re.sub(r'TGT-[^/]+', new_tgt_code, url)

                            # Header'da TGT varsa yeni TGT ile güncelle (şeffaflık
                            # injection-quantity gibi servisler TGT'yi 'TGT' header'ında
                            # gönderir, URL'de değil - bkz. AUTH009 örneği)
                            request_headers = kwargs.get('headers')
                            if request_headers and 'TGT' in request_headers:
                                request_headers['TGT'] = new_tgt_code
                        except Exception:
                            pass

                        tgt_retry_count += 1
                        retry_count += 1
                        continue
                    else:
                        # Max TGT retry aşıldı, exception fırlat
                        response.raise_for_status()

                # 429 hatası kontrolü - paylaşılan kapıyı ileri iter (§ modül üstü not),
                # bu sırada diğer thread'ler de gate'e takılıp bekler.
                if response.status_code == 429:
                    wait_time = self._register_rate_limit_hit(response)

                    if rate_limit_retry_count < self.max_rate_limit_retries:
                        logger.info(
                            "429 rate limit, %.1fs bekleyip tekrar denenecek (deneme %d/%d, url=%s)",
                            wait_time, rate_limit_retry_count + 1, self.max_rate_limit_retries, url,
                        )
                        time.sleep(wait_time)
                        rate_limit_retry_count += 1
                        continue
                    else:
                        # Max rate-limit retry aşıldı, exception fırlat
                        response.raise_for_status()

                self._register_rate_limit_recovery()
                response.raise_for_status()
                return response

            except (RequestException, RetryError, Timeout) as e:
                # Response varsa rate limit kontrolü yap
                if response is not None:
                    # 429 durumunda retry yap
                    if response.status_code == 429:
                        wait_time = self._register_rate_limit_hit(response)

                        if rate_limit_retry_count < self.max_rate_limit_retries:
                            time.sleep(wait_time)
                            rate_limit_retry_count += 1
                            continue

                # Response varsa detaylı hata mesajı oluştur
                error_msg = str(e)

                # Request bilgilerini ekle
                error_msg += f"\nRequest Method: {method.upper()}"
                error_msg += f"\nRequest URL: {url}"
                # print(f"Request Method: {method.upper()}")
                # print(f"Request URL: {url}")

                # Request headers
                request_headers = kwargs.get('headers', {})
                if request_headers:
                    error_msg += f"\nRequest Headers: {dict(request_headers)}"
                    # print(f"Request Headers: {dict(request_headers)}")

                # Request body
                request_data = kwargs.get('data')
                request_json = kwargs.get('json')
                if request_json is not None:
                    try:
                        import json
                        body_str = json.dumps(request_json, ensure_ascii=False, indent=2)
                        error_msg += f"\nRequest Body (JSON): {body_str[:2000]}"
                        # print(f"Request Body (JSON): {body_str}")
                    except Exception:
                        body_str = str(request_json)
                        error_msg += f"\nRequest Body (JSON): {body_str[:1000]}"
                        # print(f"Request Body (JSON): {body_str}")
                elif request_data is not None:
                    if isinstance(request_data, (str, bytes)):
                        body_str = request_data if isinstance(request_data, str) else request_data.decode('utf-8', errors='ignore')
                        error_msg += f"\nRequest Body: {body_str[:2000]}"
                        # print(f"Request Body: {body_str}")
                    else:
                        body_str = str(request_data)
                        error_msg += f"\nRequest Body: {body_str[:1000]}"
                        # print(f"Request Body: {body_str}")

                if response is not None:
                    try:
                        response_text = response.text[:1000]  # İlk 1000 karakter
                        error_msg += f"\nResponse Status: {response.status_code}"
                        error_msg += f"\nResponse Headers: {dict(response.headers)}"
                        # print(f"Response Status: {response.status_code}")
                        # print(f"Response Headers: {dict(response.headers)}")
                        if response_text:
                            error_msg += f"\nResponse Body: {response_text}"
                            # print(f"Response Body: {response_text}")
                    except Exception:
                        # Response okunamazsa sadece status code'u ekle
                        error_msg += f"\nResponse Status: {response.status_code}"
                        # print(f"Response Status: {response.status_code}")

                # Yeni exception oluştur (orijinal exception'ı preserve et)
                new_exception = type(e)(error_msg)
                new_exception.__cause__ = e
                # Response'u exception'a ekle
                if response is not None:
                    new_exception.response = response
                logger.error("HTTP isteği başarısız: %s %s -> %s", method.upper(), url, e)
                raise new_exception from e

        # Buraya gelmemeli ama güvenlik için
        if response is not None:
            response.raise_for_status()
        raise RequestException("Max retry limit reached for rate limit")

    def get(self, url: str, **kwargs: Any) -> Response:
        """GET request"""
        return self._make_request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> Response:
        """POST request"""
        return self._make_request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> Response:
        """PUT request"""
        return self._make_request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> Response:
        """DELETE request"""
        return self._make_request("DELETE", url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> Response:
        """PATCH request"""
        return self._make_request("PATCH", url, **kwargs)

    def head(self, url: str, **kwargs: Any) -> Response:
        """HEAD request"""
        return self._make_request("HEAD", url, **kwargs)

    def options(self, url: str, **kwargs: Any) -> Response:
        """OPTIONS request"""
        return self._make_request("OPTIONS", url, **kwargs)

    def buildurl(self, *parts: str) -> str:

        cleaned = [str(part).strip("/") for part in parts if part]
        if not cleaned:
            return ""
        # Eğer ilk parça bir protokol içeriyorsa, protokolü koruyalım (örn: "https://")
        if "://" in cleaned[0]:
            protocol, rest = cleaned[0].split("://", 1)
            url = protocol + "://" + "/".join([rest] + cleaned[1:])
        else:
            url = "/".join(cleaned)
        return url

    def close(self) -> None:
        """Session'ı kapat"""
        if self._session:
            self._session.close()
            self._session = None


_shared_client: Optional["HTTPClient"] = None
_shared_client_lock = threading.Lock()


def get_shared_client() -> "HTTPClient":
    """
    Process ömrü boyunca paylaşılan, tek bir HTTPClient/Session döndürür.

    Her `Endpoint` çağrısında yeni bir `HTTPClient()` (dolayısıyla yeni bir
    `requests.Session` + connection pool) açılıp kapatmak yerine, tekrarlanan
    çağrılar arasında TCP/TLS bağlantısı yeniden kullanılsın diye bu paylaşılan
    client tercih edilir. Auth, bu client üzerinde instance state olarak DEĞİL,
    her çağrıda `auth=` parametresiyle geçirilir (bkz. `_make_request`) — aksi
    halde eşzamanlı farklı kategorideki çağrılar birbirinin auth'unu ezerdi.
    """
    global _shared_client
    if _shared_client is None:
        with _shared_client_lock:
            if _shared_client is None:
                client = HTTPClient()
                client._session = client._create_session()
                _shared_client = client
    return _shared_client

