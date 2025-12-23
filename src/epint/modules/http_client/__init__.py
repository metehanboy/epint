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

from typing import Dict, Optional, Tuple, Union, Any
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests import Session, Response
from requests.exceptions import RequestException, RetryError, Timeout
from ..version import __fullname__
import time


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

    def _make_request(
        self,
        method: str,
        url: str,
        **kwargs: Any
    ) -> Response:
        """
        HTTP request yap

        Args:
            method: HTTP metodu (GET, POST, vb.)
            url: Request URL'i
            **kwargs: requests.Session.request() için ek parametreler

        Returns:
            Response objesi

        Raises:
            RequestException: Request başarısız olduğunda
            Timeout: Timeout olduğunda
            RetryError: Retry limiti aşıldığında
        """
        session = self._get_session()

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

        while retry_count <= max_retries:
            try:
                response = session.request(method=method.upper(), url=url, **kwargs)

                # 429 hatası kontrolü
                if response.status_code == 429:
                    wait_time = self._check_rate_limit(response)
                    if wait_time is None:
                        # 429 durumunda reset süresini header'dan al
                        reset = response.headers.get('RateLimit-Reset')
                        if reset is not None:
                            try:
                                wait_time = float(reset)
                            except (ValueError, TypeError):
                                wait_time = 60.0
                        else:
                            wait_time = 60.0

                    if retry_count < max_retries:
                        time.sleep(wait_time)
                        retry_count += 1
                        continue
                    else:
                        # Max retry aşıldı, exception fırlat
                        response.raise_for_status()

                response.raise_for_status()
                return response

            except (RequestException, RetryError, Timeout) as e:
                # Response varsa rate limit kontrolü yap
                if response is not None:
                    # 429 durumunda retry yap
                    if response.status_code == 429:
                        wait_time = self._check_rate_limit(response)
                        if wait_time is None:
                            reset = response.headers.get('RateLimit-Reset')
                            if reset is not None:
                                try:
                                    wait_time = float(reset)
                                except (ValueError, TypeError):
                                    wait_time = 60.0
                            else:
                                wait_time = 60.0

                        if retry_count < max_retries:
                            time.sleep(wait_time)
                            retry_count += 1
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

