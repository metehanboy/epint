# -*- coding: utf-8 -*-
from unittest.mock import MagicMock

from epint.modules.http_client import HTTPClient, get_shared_client


def test_get_shared_client_returns_same_instance():
    # Regresyon testi: her Endpoint çağrısı ayrı bir HTTPClient/Session
    # açıp kapatmak yerine process ömrü boyunca tek client'ı paylaşmalı
    # (bağlantı yeniden kullanımı / performans).
    first = get_shared_client()
    second = get_shared_client()
    assert first is second


def test_shared_client_session_persists_across_requests(monkeypatch):
    client = get_shared_client()
    fake_response = MagicMock(status_code=200, headers={})
    monkeypatch.setattr(client._get_session(), "request", lambda **kwargs: fake_response)

    client.get("https://example.epias.com.tr/ping")
    session_after_first_call = client._session
    client.get("https://example.epias.com.tr/ping")

    # Kapanıp yeniden açılmıyor; aynı session iki çağrı arasında yaşamaya devam ediyor.
    assert client._session is session_after_first_call
    assert client._session is not None


def test_make_request_uses_per_call_auth_not_instance_state(monkeypatch):
    # Regresyon testi: auth artık client'a instance state olarak yazılmıyor
    # (paylaşılan client'ta bu, eşzamanlı farklı auth'lu çağrılar arasında
    # race'e yol açardı) — her çağrıya `auth=` parametresiyle geçiriliyor.
    client = HTTPClient()
    fake_response = MagicMock(status_code=200, headers={})
    monkeypatch.setattr(client, "_get_session", lambda: MagicMock(request=lambda **kw: fake_response))

    auth_a = MagicMock(name="auth_a")
    client.get("https://example.epias.com.tr/a", auth=auth_a)

    assert client.auth is None  # instance state hiç değişmedi
