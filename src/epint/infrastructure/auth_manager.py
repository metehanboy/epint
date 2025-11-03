# -*- coding: utf-8 -*-

from __future__ import annotations

import os
import tempfile
import datetime
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

from .http_client import HTTPClient
from .datetime_utils import DateTimeUtils
from .logger import get_logger
import time


@dataclass
class TicketInfo:
    code: str
    expire_date: str
    username: str
    root_endpoint: str
    service: Optional[str] = None


class Authentication:

    TGT_EXPIRE_HOURS: int = 8
    TGT_EXPIRE_HOURS_TRANSPARENCY: int = 1
    ST_EXPIRE_SECONDS: int = 30
    DATE_FORMAT: str = DateTimeUtils.DATETIME_FORMAT

    ENDPOINTS: Dict[str, str] = {
        "tgt": "/cas/v1/tickets",
        "st": "/cas/v1/tickets/{tgt_code}",
    }

    ROOT_URLS: Dict[str, str] = {
        "transparency": "https://giris.epias.com.tr",
        "epys": "https://cas.epias.com.tr",
    }

    def __init__(
        self,
        username: str,
        password: str,
        auth_mode: str = "epys",
        environment_mode: str = "prod",
    ):
        self.username = username
        self.password = password
        self.auth_mode = auth_mode
        self.environment_mode = environment_mode
        self.root = self._get_root_url(auth_mode, environment_mode)
        self.logger = get_logger()
        self._setup_directories()

    def _get_root_url(self, auth_mode: str, environment_mode: str) -> str:
        """Mode'a göre root URL'i döndür"""
        from .service_config import get_auth_root_url

        return get_auth_root_url(auth_mode, environment_mode)

    def _setup_directories(self) -> None:
        temp_dir = os.path.join(tempfile.gettempdir(), "epint")
        os.makedirs(temp_dir, exist_ok=True)

        self.tgt_dir = os.path.join(temp_dir, "tgt.dat")
        self.st_dir = os.path.join(temp_dir, "st.dat")

    def _get_base_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache",
            "Host": self.root.split("://")[1],
            "Accept": "text/plain",
        }

    def _store_ticket(
        self, ticket_type: str, code: str, expire_date: str, **kwargs
    ) -> None:
        file_path = self.tgt_dir if ticket_type == "tgt" else self.st_dir
        with open(file_path, "a", encoding="utf-8") as f:
            if ticket_type == "tgt":
                f.write(f"{code}|{expire_date}|{self.username}|{self.root}\n")
            else:
                service = kwargs.get("service", "")
                f.write(f"{code}|{service}|{expire_date}|{self.username}|{self.root}\n")

    def _generate_tgt(self) -> str:
        start_time = time.time()

        try:
            self.logger.log_operation(
                "auth_tgt_generation_start",
                username=self.username,
                mode=self.auth_mode,
                root_url=self.root,
            )

            headers = self._get_base_headers()
            payload = {"username": self.username, "password": self.password}
            # params = {"format": "text"}

            with HTTPClient() as cl:
                rp = cl.post(
                    self.root + self.ENDPOINTS["tgt"],
                    data=payload,
                    headers=headers,
                    # params=params,
                )
                rp.raise_for_status()

            duration = time.time() - start_time
            self.logger.log_performance(
                "auth_tgt_generation",
                duration,
                username=self.username,
                mode=self.auth_mode,
                success=True,
            )

            return rp.text

        except Exception as e:
            duration = time.time() - start_time
            self.logger.log_error(
                "auth_tgt_generation_error",
                username=self.username,
                mode=self.auth_mode,
                error_msg=str(e),
                duration=duration,
            )
            raise

    def _generate_st(self, service: str) -> str:
        start_time = time.time()

        try:
            self.logger.log_operation(
                "auth_st_generation_start",
                username=self.username,
                service=service,
                mode=self.auth_mode,
            )

            tgt_code, _ = self.get_tgt()
            headers = self._get_base_headers()
            payload = {"service": service}

            with HTTPClient() as cl:
                rp = cl.post(
                    self.root + self.ENDPOINTS["st"].format(tgt_code=tgt_code),
                    data=payload,
                    headers=headers,
                )

                if rp.status_code == 404:
                    self.logger.log_operation(
                        "auth_tgt_invalid_retry",
                        username=self.username,
                        service=service,
                        status_code=404,
                    )
                    print("TGT geçersiz, yeni TGT oluşturuluyor...")
                    self.clear_tickets()
                    tgt_code, _ = self.get_tgt()
                    rp = cl.post(
                        self.root + self.ENDPOINTS["st"].format(tgt_code=tgt_code),
                        data=payload,
                        headers=headers,
                    )

                rp.raise_for_status()

            duration = time.time() - start_time
            self.logger.log_performance(
                "auth_st_generation",
                duration,
                username=self.username,
                service=service,
                mode=self.auth_mode,
                success=True,
            )

            return rp.text

        except Exception as e:
            duration = time.time() - start_time
            self.logger.log_error(
                "auth_st_generation_error",
                username=self.username,
                service=service,
                mode=self.auth_mode,
                error_msg=str(e),
                duration=duration,
            )
            raise

    def _validate_ticket(self, ticket_code: str, ticket_type: str) -> bool:
        prefix = "TGT-" if ticket_type == "tgt" else "ST-"
        return ("cas" in ticket_code) and (ticket_code.startswith(prefix))

    def _get_expire_date(self, ticket_type: str) -> str:
        if ticket_type == "tgt":
            hours = (
                self.TGT_EXPIRE_HOURS_TRANSPARENCY
                if self.auth_mode == "transparency"
                else self.TGT_EXPIRE_HOURS
            )
            delta = datetime.timedelta(hours=hours)
        else:
            delta = datetime.timedelta(seconds=self.ST_EXPIRE_SECONDS)

        return DateTimeUtils.to_string(DateTimeUtils.now() + delta)

    def get_tgt(self) -> Tuple[str, str]:
        existing_tgt = self._find_valid_tgt()
        if existing_tgt:
            return existing_tgt

        return self._create_new_tgt()

    def _find_valid_tgt(self) -> Optional[Tuple[str, str]]:
        if not os.path.exists(self.tgt_dir):
            return None

        with open(self.tgt_dir, "r", encoding="utf-8") as f:
            for line in f:
                tgt_data = self._parse_tgt_line(line)
                if tgt_data and self._is_tgt_valid(tgt_data):
                    return tgt_data["tgt_code"], tgt_data["expire_date"]
        return None

    def _parse_tgt_line(self, line: str) -> Optional[dict]:
        parts = line.strip().split("|")
        if len(parts) != 4:
            return None

        tgt_code, expire_date, username, root_endpoint = parts
        if username != self.username or root_endpoint != self.root:
            return None

        return {
            "tgt_code": tgt_code,
            "expire_date": expire_date,
            "username": username,
            "root_endpoint": root_endpoint,
        }

    def _is_tgt_valid(self, tgt_data: dict) -> bool:
        return not DateTimeUtils.is_expired(tgt_data["expire_date"])

    def _create_new_tgt(self) -> Tuple[str, str]:
        self._invalidate_old_tgts()

        tgt_code = self._generate_tgt()
        if not self._validate_ticket(tgt_code, "tgt"):
            raise Exception(f"TGT Oluşturma Hatası: TGT Geçerli Değil: {tgt_code}")

        expire_date = self._get_expire_date("tgt")
        self._store_ticket("tgt", tgt_code, expire_date)
        return tgt_code, expire_date

    def get_st(self, service: str, find_valid: bool = False) -> Tuple[str, str]:
        if find_valid:
            existing_st = self._find_valid_st(service)
            if existing_st:
                return existing_st

        return self._create_new_st(service)

    def _find_valid_st(self, service: str) -> Optional[Tuple[str, str]]:
        if not os.path.exists(self.st_dir):
            return None

        with open(self.st_dir, "r", encoding="utf-8") as f:
            for line in f:
                st_data = self._parse_st_line(line, service)
                if st_data and self._is_st_valid(st_data):
                    return st_data["st_code"], st_data["expire_date"]
        return None

    def _parse_st_line(self, line: str, service: str) -> Optional[dict]:
        parts = line.strip().split("|")
        if len(parts) != 5:
            return None

        st_code, stored_service, expire_date, username, root_endpoint = parts
        if (
            username != self.username
            or root_endpoint != self.root
            or stored_service != service
        ):
            return None

        return {
            "st_code": st_code,
            "expire_date": expire_date,
            "username": username,
            "root_endpoint": root_endpoint,
            "service": stored_service,
        }

    def _is_st_valid(self, st_data: dict) -> bool:
        return not DateTimeUtils.is_expired(st_data["expire_date"])

    def _create_new_st(self, service: str) -> Tuple[str, str]:
        st_code = self._generate_st(service)
        if not self._validate_ticket(st_code, "st"):
            raise Exception(f"ST Oluşturma Hatası: ST Geçerli Değil: {st_code}")

        expire_date = self._get_expire_date("st")
        self._store_ticket("st", st_code, expire_date, service=service)
        return st_code, expire_date

    def clear_tickets(self) -> None:
        if os.path.exists(self.tgt_dir):
            os.remove(self.tgt_dir)
        if os.path.exists(self.st_dir):
            os.remove(self.st_dir)

    def _invalidate_old_tgts(self) -> None:
        if not os.path.exists(self.tgt_dir):
            return

        lines = []
        with open(self.tgt_dir, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) == 4:
                    tgt_code, expire_date, username, root_endpoint = parts
                    if username == self.username and root_endpoint == self.root:
                        old_date = "1970-01-01 00:00:00"
                        lines.append(
                            f"{tgt_code}|{old_date}|{username}|{root_endpoint}\n"
                        )
                    else:
                        lines.append(line)
                else:
                    lines.append(line)

        with open(self.tgt_dir, "w", encoding="utf-8") as f:
            f.writelines(lines)

    def get_auth_header(self, service: str) -> Dict[str, str]:
        st_code, _ = self.get_st(service)
        return {"Authorization": f"Bearer {st_code}"}

    def report_tickets(self) -> str:
        report = []

        report.append("=== TGT Kayıtları ===")
        report.extend(self._get_tgt_report())

        report.append("")

        report.append("=== ST Kayıtları ===")
        report.extend(self._get_st_report())

        return "\n".join(report)

    def _get_tgt_report(self) -> list:
        if not os.path.exists(self.tgt_dir):
            return ["TGT kayıt dosyası bulunamadı."]

        report = []
        with open(self.tgt_dir, "r", encoding="utf-8") as f:
            content = f.read()
        for line in content.strip().splitlines():
            if line.strip():
                report.append(self._format_tgt_line(line))
        return report

    def _get_st_report(self) -> list:
        if not os.path.exists(self.st_dir):
            return ["ST kayıt dosyası bulunamadı."]

        report = []
        with open(self.st_dir, "r", encoding="utf-8") as f:
            content = f.read()
        for line in content.strip().splitlines():
            if line.strip():
                report.append(self._format_st_line(line))
        return report

    def _format_tgt_line(self, line: str) -> str:
        parts = line.strip().split("|")
        if len(parts) == 4:
            tgt, son_kullanim, kullanici, cas_url = parts
            gecerli = DateTimeUtils.get_validity_status(son_kullanim)
            return (
                f"TGT: {tgt}\n"
                f"  Son Kullanım: {son_kullanim} ({gecerli})\n"
                f"  Kullanıcı: {kullanici}\n"
                f"  CAS URL: {cas_url}"
            )
        return line.strip()

    def _format_st_line(self, line: str) -> str:
        parts = line.strip().split("|")
        if len(parts) == 5:
            return self._format_st_line_5_parts(parts)
        elif len(parts) == 4:
            return self._format_st_line_4_parts(parts)
        return line.strip()

    def _format_st_line_5_parts(self, parts: list) -> str:
        st, servis, son_kullanim, kullanici, cas_url = parts
        gecerli = self._check_ticket_validity(son_kullanim)
        return (
            f"ST: {st}\n"
            f"  Servis: {servis}\n"
            f"  Son Kullanım: {son_kullanim} ({gecerli})\n"
            f"  Kullanıcı: {kullanici}\n"
            f"  CAS URL: {cas_url}"
        )

    def _format_st_line_4_parts(self, parts: list) -> str:
        st, servis, son_kullanim, kullanici = parts
        gecerli = self._check_ticket_validity(son_kullanim)
        return (
            f"ST: {st}\n"
            f"  Servis: {servis}\n"
            f"  Son Kullanım: {son_kullanim} ({gecerli})\n"
            f"  Kullanıcı: {kullanici}"
        )

    def _check_ticket_validity(self, expire_date: str) -> str:
        return DateTimeUtils.get_validity_status(expire_date)
