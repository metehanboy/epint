# -*- coding: utf-8 -*-

import os
import logging
import tempfile
from logging.handlers import RotatingFileHandler
from typing import Optional
import time
import functools


class PerformanceLogger:
    """Performans ve işlem logları için logger sınıfı"""

    def __init__(
        self,
        name: str = "epint",
        log_dir: Optional[str] = None,
        debug_mode: Optional[bool] = None,
    ):
        self.name = name
        self.log_dir = log_dir or self._get_default_log_dir()
        # Debug modunu environment variable'dan kontrol et
        self.debug_mode = (
            debug_mode
            if debug_mode is not None
            else os.getenv("EPINT_DEBUG", "false").lower() == "true"
        )
        self._ensure_log_dir()
        self._setup_loggers()

    def _get_default_log_dir(self) -> str:
        """Varsayılan log dizinini oluştur (auth manager ile aynı dizin)"""
        temp_dir = tempfile.gettempdir()
        epint_dir = os.path.join(temp_dir, "epint")
        log_dir = os.path.join(epint_dir, "logs")
        return log_dir

    def _ensure_log_dir(self):
        """Log dizinini oluştur"""
        os.makedirs(self.log_dir, exist_ok=True)

    def _setup_loggers(self):
        """Logger'ları kur"""
        # Ana logger
        self.main_logger = self._create_logger(
            name=f"{self.name}_main", filename="epint_main.log", level=logging.INFO
        )

        # Performans logger
        self.performance_logger = self._create_logger(
            name=f"{self.name}_performance",
            filename="epint_performance.log",
            level=logging.INFO,
        )

        # Hata logger
        self.error_logger = self._create_logger(
            name=f"{self.name}_error", filename="epint_error.log", level=logging.ERROR
        )

        # Debug logger
        self.debug_logger = self._create_logger(
            name=f"{self.name}_debug", filename="epint_debug.log", level=logging.DEBUG
        )

    def _create_logger(self, name: str, filename: str, level: int) -> logging.Logger:
        """Logger oluştur"""
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Eğer handler zaten varsa, temizle ve yeniden ekle
        if logger.handlers:
            logger.handlers.clear()

        # Log dosya yolu
        log_file = os.path.join(self.log_dir, filename)

        # Rotating file handler (10MB, 5 dosya)
        handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
        )

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)

        # Console handler (debug modunda veya DEBUG level'da tüm loglar, normal modda sadece hata)
        if self.debug_mode or level == logging.ERROR or level == logging.DEBUG:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger

    def log_performance(self, operation: str, duration: float, **kwargs):
        """Performans logu"""
        message = f"PERF: {operation} - {duration:.4f}s"
        if kwargs:
            details = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            message += f" | {details}"

        self.performance_logger.info(message)

    def log_operation(self, operation: str, **kwargs):
        """Genel işlem logu"""
        message = f"OP: {operation}"
        if kwargs:
            details = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            message += f" | {details}"

        self.main_logger.info(message)

    def log_error(self, error: str, **kwargs):
        """Hata logu"""
        message = f"ERROR: {error}"
        if kwargs:
            details = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            message += f" | {details}"

        self.error_logger.error(message)

    def log_debug(self, message: str, **kwargs):
        """Debug logu"""
        if kwargs:
            details = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            message += f" | {details}"

        self.debug_logger.debug(message)


# Global logger instance
_logger_instance: Optional[PerformanceLogger] = None


def get_logger(debug_mode: Optional[bool] = None) -> PerformanceLogger:
    """Global logger instance'ını al"""
    global _logger_instance
    if _logger_instance is None or debug_mode is not None:
        _logger_instance = PerformanceLogger(debug_mode=debug_mode)
    return _logger_instance


def reset_logger():
    """Logger instance'ını sıfırla (test için)"""
    global _logger_instance
    _logger_instance = None


def performance_timer(operation_name: Optional[str] = None):
    """Performans ölçümü decorator'ı"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            operation = operation_name or f"{func.__module__}.{func.__name__}"

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                logger = get_logger()
                logger.log_performance(
                    operation=operation,
                    duration=duration,
                    success=True,
                    args_count=len(args),
                    kwargs_count=len(kwargs),
                )

                return result

            except Exception as e:
                duration = time.time() - start_time

                logger = get_logger()
                logger.log_performance(
                    operation=operation,
                    duration=duration,
                    success=False,
                    error=str(e),
                    args_count=len(args),
                    kwargs_count=len(kwargs),
                )

                logger.log_error(f"Error in {operation}", error_msg=str(e))
                raise

        return wrapper

    return decorator


def log_operation(operation: str, **kwargs):
    """Hızlı işlem logu"""
    get_logger().log_operation(operation, **kwargs)


def log_performance(operation: str, duration: float, **kwargs):
    """Hızlı performans logu"""
    get_logger().log_performance(operation, duration, **kwargs)


def log_error(error: str, **kwargs):
    """Hızlı hata logu"""
    get_logger().log_error(error, **kwargs)


def log_debug(message: str, **kwargs):
    """Hızlı debug logu"""
    get_logger().log_debug(message, **kwargs)
