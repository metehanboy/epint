# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ServiceConfig:
    """Service konfigürasyonu - mode'a göre URL'leri dinamik olarak oluşturur"""

    # Base konfigürasyon
    base_server: str  # Örnek: "epys.epias.com.tr"
    root_path: str
    protocol: str = "https"
    auth_mode: str = "epys"

    # Mode kuralları
    test_prefix: str = "-prp"  # Test için eklenen prefix
    test_suffix: str = ""  # Test için eklenen suffix

    def get_server(self, mode: str = "prod") -> str:
        """Mode'a göre server URL'ini döndür"""
        if mode == "test":
            # Test mode için prefix/suffix ekle
            if self.test_prefix:
                # epys.epias.com.tr -> epys-prp.epias.com.tr
                # gop.epias.com.tr -> testgop.epias.com.tr
                if self.test_prefix.startswith("-"):
                    # -prp gibi prefix'ler için
                    parts = self.base_server.split(".")
                    parts[0] = f"{parts[0]}{self.test_prefix}"
                    return ".".join(parts)
                else:
                    # test gibi prefix'ler için
                    parts = self.base_server.split(".")
                    parts[0] = f"{self.test_prefix}{parts[0]}"
                    return ".".join(parts)
            elif self.test_suffix:
                return f"{self.base_server}{self.test_suffix}"
        return self.base_server

    def get_service_ticket(self, mode: str = "prod") -> str:
        """Mode'a göre service ticket URL'ini döndür"""
        server = self.get_server(mode)
        return f"{self.protocol}://{server}"

    def get_full_url(self, endpoint: str, mode: str = "prod") -> str:
        """Mode'a göre tam URL'i döndür"""
        server = self.get_server(mode)
        base_url = f"{self.protocol}://{server}"
        root_path = self.root_path.rstrip("/")
        endpoint_clean = endpoint.lstrip("/")
        return f"{base_url}{root_path}/{endpoint_clean}"


# Service konfigürasyonları
SERVICE_CONFIGS: Dict[str, ServiceConfig] = {
    "balancing-group": ServiceConfig(
        base_server="epys.epias.com.tr",
        root_path="/balancing-group/",
        auth_mode="epys",
    ),
    "customer": ServiceConfig(
        base_server="epys.epias.com.tr",
        root_path="/customer",
        auth_mode="epys",
    ),
    "gop": ServiceConfig(
        base_server="gop.epias.com.tr",
        root_path="/gop-servis/rest",
        auth_mode="gop",
        test_prefix="test",  # gop.epias.com.tr -> testgop.epias.com.tr
    ),
    "grid": ServiceConfig(
        base_server="epys.epias.com.tr",
        root_path="/grid",
        auth_mode="epys",
    ),
    "gunici": ServiceConfig(
        base_server="gunici.epias.com.tr",
        root_path="/gunici-service",
        auth_mode="epys",
    ),
    "gunici-trading": ServiceConfig(
        base_server="gunici.epias.com.tr",
        root_path="/gunici-trading-service",
        auth_mode="epys",
    ),
    "pre-reconciliation": ServiceConfig(
        base_server="epys.epias.com.tr",
        root_path="/pre-reconciliation/",
        auth_mode="epys",
    ),
    "reconciliation-bpm": ServiceConfig(
        base_server="epys.epias.com.tr",
        root_path="/reconciliation-bpm/",
        auth_mode="epys",
    ),
    "reconciliation-imbalance": ServiceConfig(
        base_server="epys.epias.com.tr",
        root_path="/reconciliation-imbalance/",
        auth_mode="epys",
    ),
    "reconciliation-invoice": ServiceConfig(
        base_server="epys.epias.com.tr",
        root_path="/reconciliation-invoice/",
        auth_mode="epys",
    ),
    "reconciliation-market": ServiceConfig(
        base_server="epys.epias.com.tr",
        root_path="/reconciliation-market/",
        auth_mode="epys",
    ),
    "reconciliation-mof": ServiceConfig(
        base_server="epys.epias.com.tr",
        root_path="/reconciliation-mof/servis/",
        auth_mode="epys",
    ),
    "reconciliation-res": ServiceConfig(
        base_server="epys.epias.com.tr",
        root_path="/reconciliation-res/servis/",
        auth_mode="epys",
    ),
    "registration": ServiceConfig(
        base_server="epys.epias.com.tr",
        root_path="/registration",
        auth_mode="epys",
    ),
    # Seffaflik servisleri test/prod ayrımı yapmıyor
    "seffaflik-electricity": ServiceConfig(
        base_server="seffaflik.epias.com.tr",
        root_path="/electricity-service",
        auth_mode="transparency",
        test_prefix="",  # Test mode'da değişmez
    ),
    "seffaflik-natural-gas": ServiceConfig(
        base_server="seffaflik.epias.com.tr",
        root_path="/natural-gas-service",
        auth_mode="transparency",
        test_prefix="",  # Test mode'da değişmez
    ),
    "seffaflik-reporting": ServiceConfig(
        base_server="seffaflik.epias.com.tr",
        root_path="/reporting-service",
        auth_mode="transparency",
        test_prefix="",  # Test mode'da değişmez
    ),
}


def get_service_config(category: str, mode: str = "prod") -> Optional[ServiceConfig]:
    """Mode'a göre service konfigürasyonunu döndür"""
    return SERVICE_CONFIGS.get(category)


def get_auth_mode(category: str, mode: str = "prod") -> str:
    """Mode'a göre auth mode'unu döndür"""
    config = get_service_config(category, mode)
    return config.auth_mode if config else "epys"


def get_service_ticket_url(category: str, mode: str = "prod") -> str:
    """Mode'a göre service ticket URL'ini döndür"""
    config = get_service_config(category, mode)
    return config.get_service_ticket(mode) if config else ""


def get_full_url(category: str, endpoint: str, mode: str = "prod") -> str:
    """Mode'a göre tam URL'i döndür"""
    config = get_service_config(category, mode)
    if not config:
        return endpoint
    return config.get_full_url(endpoint, mode)


# Auth mode'a göre root URL'ler
AUTH_ROOT_URLS = {
    "prod": {
        "transparency": "https://giris.epias.com.tr",
        "epys": "https://cas.epias.com.tr",
        "gop": "https://cas.epias.com.tr",
    },
    "test": {
        "transparency": "https://giris.epias.com.tr",  # Seffaflik test/prod ayrımı yapmıyor
        "epys": "https://testcas.epias.com.tr",
        "gop": "https://testcas.epias.com.tr",
    },
}


def get_auth_root_url(auth_mode: str, mode: str = "prod") -> str:
    """Mode'a göre auth root URL'ini döndür"""
    return AUTH_ROOT_URLS.get(mode, {}).get(auth_mode, "https://cas.epias.com.tr")
