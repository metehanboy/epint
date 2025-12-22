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

"""Rate limit handler module for managing 429 errors"""

import os
import time
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class RateLimitHandler:
    """429 Rate Limit hatalarını yöneten modül"""

    RATE_LIMIT_DIR = "/tmp/epint"
    RATE_LIMIT_FILE = os.path.join(RATE_LIMIT_DIR, "rate_limit.json")

    def __init__(self):
        """RateLimitHandler oluştur"""
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Rate limit dizinini oluştur (yoksa)"""
        try:
            os.makedirs(self.RATE_LIMIT_DIR, mode=0o755, exist_ok=True)
        except OSError:
            pass

    def handle_429_error(self, response: Any) -> None:
        """
        429 hatası geldiğinde rate limit bilgisini kaydet

        Args:
            response: HTTP response objesi
        """
        try:
            # Response header'larından reset zamanını al
            reset_time = self._extract_reset_time(response)

            if reset_time is None:
                # Header'dan alınamazsa varsayılan olarak 60 saniye ekle
                reset_time = datetime.now() + timedelta(seconds=60)

            # Rate limit bilgisini dosyaya kaydet
            rate_limit_info = {
                "reset_time": reset_time.isoformat(),
                "created_at": datetime.now().isoformat(),
                "status_code": 429,
                "message": "Too many requests. Rate limit exceeded."
            }

            with open(self.RATE_LIMIT_FILE, 'w', encoding='utf-8') as f:
                json.dump(rate_limit_info, f, indent=2)

        except Exception:
            # Hata durumunda sessizce devam et
            pass

    def _extract_reset_time(self, response: Any) -> Optional[datetime]:
        """
        Response header'larından reset zamanını çıkar

        Args:
            response: HTTP response objesi

        Returns:
            Reset zamanı (datetime) veya None
        """
        try:
            headers = getattr(response, 'headers', {})

            # RateLimit-Reset header'ını kontrol et
            reset_header = headers.get('RateLimit-Reset')
            if reset_header:
                try:
                    # Unix timestamp olabilir (saniye cinsinden)
                    reset_timestamp = float(reset_header)
                    if reset_timestamp > 0:
                        # Eğer timestamp çok küçükse (örn. 0 veya çok küçük),
                        # muhtemelen saniye cinsinden değil, şu anki zamana ekle
                        if reset_timestamp < 1000000000:  # 2001'den önceki bir tarih
                            # Saniye cinsinden offset olarak kabul et
                            return datetime.now() + timedelta(seconds=int(reset_timestamp))
                        else:
                            # Unix timestamp olarak kabul et
                            return datetime.fromtimestamp(reset_timestamp)
                except (ValueError, TypeError):
                    pass

            # RateLimit-Limit header'ından window süresini çıkar
            # Format: "60;w=60" (60 request per 60 seconds)
            limit_info = headers.get('RateLimit-Limit', '')
            if limit_info and 'w=' in limit_info:
                try:
                    # "60;w=60" formatından window süresini al
                    window_part = limit_info.split('w=')[1]
                    # Noktalı virgül veya boşluk ile ayrılmış olabilir
                    window = int(window_part.split(';')[0].split()[0])
                    # Window süresi kadar bekle
                    return datetime.now() + timedelta(seconds=window)
                except (ValueError, IndexError):
                    pass

            # Hata mesajından "1 minute" gibi bilgi çıkarmayı dene
            try:
                response_body = response.json()
                fault = response_body.get('fault', {})
                fault_string = fault.get('faultString', '')
                if 'minute' in fault_string.lower():
                    # "Try again in 1 minute" gibi bir mesaj varsa 60 saniye ekle
                    return datetime.now() + timedelta(seconds=60)
            except Exception:
                pass

            # Varsayılan: 60 saniye (hata mesajında "Try again in 1 minute" yazıyor)
            return datetime.now() + timedelta(seconds=60)

        except Exception:
            # Hata durumunda varsayılan olarak 60 saniye ekle
            return datetime.now() + timedelta(seconds=60)

    def check_rate_limit(self) -> Optional[Dict[str, Any]]:
        """
        Rate limit kontrolü yap

        Returns:
            Rate limit bilgisi dict (varsa) veya None
        """
        try:
            if not os.path.exists(self.RATE_LIMIT_FILE):
                return None

            with open(self.RATE_LIMIT_FILE, 'r', encoding='utf-8') as f:
                rate_limit_info = json.load(f)

            reset_time_str = rate_limit_info.get('reset_time')
            if not reset_time_str:
                # Geçersiz dosya, sil
                self.clear_rate_limit()
                return None

            reset_time = datetime.fromisoformat(reset_time_str)
            now = datetime.now()

            # Reset zamanı geçmişse dosyayı sil
            if reset_time <= now:
                self.clear_rate_limit()
                return None

            # Hala bloklama varsa bilgiyi döndür
            return rate_limit_info

        except Exception:
            # Hata durumunda dosyayı temizle
            self.clear_rate_limit()
            return None

    def clear_rate_limit(self) -> None:
        """Rate limit dosyasını sil"""
        try:
            if os.path.exists(self.RATE_LIMIT_FILE):
                os.remove(self.RATE_LIMIT_FILE)
        except Exception:
            pass

    def get_reset_time(self) -> Optional[datetime]:
        """
        Rate limit reset zamanını döndür

        Returns:
            Reset zamanı (datetime) veya None (rate limit yoksa)
        """
        rate_limit_info = self.check_rate_limit()
        if not rate_limit_info:
            return None

        reset_time_str = rate_limit_info.get('reset_time')
        if not reset_time_str:
            return None

        try:
            return datetime.fromisoformat(reset_time_str)
        except Exception:
            return None

    def get_rate_limit_error(self) -> Optional[Exception]:
        """
        Rate limit hatası exception'ı oluştur

        Returns:
            RateLimitError exception (varsa) veya None
        """
        rate_limit_info = self.check_rate_limit()
        if not rate_limit_info:
            return None

        reset_time_str = rate_limit_info.get('reset_time')
        reset_time = datetime.fromisoformat(reset_time_str)
        now = datetime.now()
        wait_seconds = int((reset_time - now).total_seconds())

        error_msg = (
            f"Rate limit exceeded. Too many requests. "
            f"Please try again in {wait_seconds} seconds. "
            f"(Reset time: {reset_time.strftime('%Y-%m-%d %H:%M:%S')})"
        )

        # RateLimitError exception sınıfı
        class RateLimitError(Exception):
            """Rate limit hatası exception"""
            def __init__(self, message, reset_time, wait_seconds):
                super().__init__(message)
                self.reset_time = reset_time
                self.wait_seconds = wait_seconds
                self.status_code = 429

        return RateLimitError(error_msg, reset_time, wait_seconds)


# Global instance
_rate_limit_handler = RateLimitHandler()


def get_rate_limit_handler() -> RateLimitHandler:
    """Global rate limit handler instance'ını döndür"""
    return _rate_limit_handler


__all__ = ['RateLimitHandler', 'get_rate_limit_handler']

