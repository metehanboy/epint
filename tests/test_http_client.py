# -*- coding: utf-8 -*-
import threading
import time
from unittest.mock import MagicMock

from epint.modules import http_client as http_client_module
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


def _reset_rate_limit_state():
    with http_client_module._rate_limit_lock:
        http_client_module._rate_limit_state["until"] = 0.0
        http_client_module._rate_limit_state["consecutive_429"] = 0


def test_429_backs_off_with_floor_wait_and_recovers_on_success(monkeypatch):
    # Regresyon testi: gateway 429'da 'RateLimit-Reset': '0' döndürebiliyor
    # (canlı örnek: 80 req/60sn limitine takılınca). Bu değere körü körüne
    # güvenip 0s bekleyip hemen tekrar denemek gateway'i daha da yoruyordu
    # (limit dakikalar içinde 50 -> 25 -> 12 -> 6'ya düşüyordu). Artık taban/
    # tavan sınırlı üstel backoff uygulanıyor ve başarı sonrası sayaç sıfırlanıyor.
    _reset_rate_limit_state()
    monkeypatch.setattr(http_client_module, "_RATE_LIMIT_MIN_WAIT", 0.05)
    monkeypatch.setattr(http_client_module, "_RATE_LIMIT_MAX_WAIT", 0.2)

    client = HTTPClient()
    too_many = MagicMock(status_code=429, headers={"RateLimit-Remaining": "0", "RateLimit-Reset": "0"})
    ok = MagicMock(status_code=200, headers={})
    ok.raise_for_status = lambda: None
    responses = [too_many, ok]
    monkeypatch.setattr(client, "_get_session", lambda: MagicMock(request=lambda **kw: responses.pop(0)))

    result = client.get("https://seffaflik.epias.com.tr/x")

    assert result is ok
    assert http_client_module._rate_limit_state["consecutive_429"] == 0


def test_second_client_waits_for_gate_opened_by_first_clients_429(monkeypatch):
    # Regresyon testi: rate-limit kapısı process çapında paylaşılıyor - bir
    # istek 429 alıp kapıyı ileri itince, kendisi hiç 429 almamış BAŞKA bir
    # istek/thread de kapı açılana kadar bekler. Eskiden her thread bağımsız
    # karar verdiği için eş-zamanlı N istek aynı anda 429 alıp hepsi hemen
    # (0s) tekrar deniyor, throttling'i derinleştiriyordu.
    _reset_rate_limit_state()
    monkeypatch.setattr(http_client_module, "_RATE_LIMIT_MIN_WAIT", 0.2)
    monkeypatch.setattr(http_client_module, "_RATE_LIMIT_MAX_WAIT", 0.2)

    client_a = HTTPClient()
    client_b = HTTPClient()

    too_many = MagicMock(status_code=429, headers={"RateLimit-Remaining": "0", "RateLimit-Reset": "0"})
    # A'nın 429 aldığını ve paylaşılan kapıyı ileri ittiğini simüle et.
    wait_time = client_a._register_rate_limit_hit(too_many)
    gate_opens_at = time.monotonic() + wait_time

    ok_b = MagicMock(status_code=200, headers={})
    ok_b.raise_for_status = lambda: None
    b_request_times = []

    def fake_request_b(**kw):
        b_request_times.append(time.monotonic())
        return ok_b

    monkeypatch.setattr(client_b, "_get_session", lambda: MagicMock(request=fake_request_b))

    # B, A ile aynı süreçte farklı bir HTTPClient/thread'i temsil ediyor -
    # kendisi hiç 429 almadı ama modül seviyesindeki paylaşılan kapıya tabi.
    thread_b = threading.Thread(target=client_b.get, args=("https://seffaflik.epias.com.tr/b",))
    thread_b.start()
    thread_b.join(timeout=2)

    assert b_request_times, "B isteği hiç gönderilmemiş"
    assert b_request_times[0] >= gate_opens_at - 0.01, "B, A'nın 429 sonrası açtığı paylaşılan kapıyı beklemeli"
