# -*- coding: utf-8 -*-
import tempfile

import pytest


@pytest.fixture(autouse=True)
def isolate_temp_dir(tmp_path, monkeypatch):
    """Ticket cache dosyalarını gerçek sistem temp dizini yerine test-özel bir dizine yönlendir."""
    monkeypatch.setattr(tempfile, "gettempdir", lambda: str(tmp_path))
    yield


@pytest.fixture(autouse=True)
def reset_endpoint_registry():
    """EndpointModel class-level cache'lerini testler arasında sıfırla."""
    from epint.models.endpoint_registry import EndpointModel

    EndpointModel._endpoints.clear()
    EndpointModel._categories.clear()
    EndpointModel._swagger_models.clear()
    yield
    EndpointModel._endpoints.clear()
    EndpointModel._categories.clear()
    EndpointModel._swagger_models.clear()


@pytest.fixture(autouse=True)
def reset_epint_globals():
    """epint modülünün global auth/mode/kategori-cache state'ini testler arasında sıfırla."""
    import epint

    epint._username = None
    epint._password = None
    epint._mode = "prod"
    epint._category_objects.clear()
    yield
    epint._username = None
    epint._password = None
    epint._mode = "prod"
    epint._category_objects.clear()


class FakeResponse:
    """requests.Response'un ResponseModel/HTTPClient tarafından kullanılan yüzeyini taklit eder."""

    def __init__(
        self, status_code=200, json_data=None, text="", content=b"", headers=None
    ):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text
        self.content = content
        self.headers = headers or {}

    def json(self):
        if self._json_data is None:
            raise ValueError("no json body")
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


@pytest.fixture
def fake_response():
    return FakeResponse
