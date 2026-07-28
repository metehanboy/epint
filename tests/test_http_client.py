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


def test_401_auth009_clears_tickets_and_refreshes_tgt_header(monkeypatch):
    # Regresyon testi: şeffaflık servisleri TGT geçersizliğini 404 değil,
    # 401 + {"errorCode": "AUTH009"} ile bildiriyor (bkz. _is_tgt_invalid).
    # Bu durumda eskiden hiç fark edilmeyip aynı bayat TGT ile tekrar
    # denenip nihayetinde exception fırlatılıyordu; artık ticket cache
    # temizlenip yeni TGT alınmalı ve 'TGT' header'ı güncellenmeli.
    client = HTTPClient()

    unauthorized = MagicMock(status_code=401, headers={})
    unauthorized.text = '{"errorCode": "AUTH009", "errorMessage": "Güvenlik bilgisi(TGT) hatalı!"}'
    ok = MagicMock(status_code=200, headers={})
    ok.raise_for_status = lambda: None
    responses = [unauthorized, ok]

    session = MagicMock(request=lambda **kw: responses.pop(0))
    monkeypatch.setattr(client, "_get_session", lambda: session)

    auth = MagicMock()
    auth.get_tgt.return_value = ("TGT-NEW", "2099-01-01 00:00:00")
    headers = {"TGT": "TGT-STALE"}

    result = client.post("https://seffaflik.epias.com.tr/x", auth=auth, headers=headers)

    assert result is ok
    auth.clear_tickets.assert_called_once()
    auth.get_tgt.assert_called_once()
    assert headers["TGT"] == "TGT-NEW"


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
