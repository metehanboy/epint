# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Dict, Optional, Tuple, Union, Any
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests import Session, Response
from requests.exceptions import RequestException, RetryError, Timeout


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
        max_redirects: int = 5,
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
            max_redirects: Maksimum redirect sayısı
        """
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.status_forcelist = status_forcelist
        self.allowed_methods = allowed_methods or ("GET", "POST", "PUT", "DELETE", "PATCH")
        self.timeout = timeout
        self.headers = headers or {}
        self.verify = verify
        self.max_redirects = max_redirects
        
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
            max_redirects=self.max_redirects,
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Varsayılan header'ları ayarla
        if self.headers:
            session.headers.update(self.headers)
        
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
        
        try:
            response = session.request(method=method.upper(), url=url, **kwargs)
            response.raise_for_status()
            return response
        except (RequestException, RetryError, Timeout) as e:
            raise
    
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
    
    def close(self) -> None:
        """Session'ı kapat"""
        if self._session:
            self._session.close()
            self._session = None

