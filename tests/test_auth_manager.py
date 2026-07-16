# -*- coding: utf-8 -*-
import datetime as dt
import getpass
import os

import pytest

from epint.modules.authentication.auth_manager import Authentication
from epint.modules.datetime import DateTimeUtils


def test_ticket_cache_dir_is_scoped_per_os_user(monkeypatch):
    """Regresyon: farklı OS kullanıcıları artık ayrı cache dizinleri kullanıyor,
    bu yüzden birinin dizini sahiplenmesi diğerini engellemiyor."""
    monkeypatch.setattr(getpass, "getuser", lambda: "alice")
    auth_alice = Authentication("shared_epias_user", "pass")

    monkeypatch.setattr(getpass, "getuser", lambda: "bob")
    auth_bob = Authentication("shared_epias_user", "pass")

    assert os.path.dirname(auth_alice.tgt_dir) != os.path.dirname(auth_bob.tgt_dir)


def test_each_os_user_can_independently_store_tickets(monkeypatch):
    """Aynı (veya farklı) EPİAŞ kullanıcı adıyla iki farklı OS kullanıcısı,
    aynı anda kendi ticket dosyalarını yazabilmeli (eski ortak dizin
    yaklaşımında ikinci OS kullanıcısı PermissionError alabiliyordu)."""
    monkeypatch.setattr(getpass, "getuser", lambda: "alice")
    auth_alice = Authentication("shared_epias_user", "pass")
    monkeypatch.setattr(auth_alice, "_generate_tgt", lambda: "TGT-cas-alice")
    auth_alice.get_tgt()

    monkeypatch.setattr(getpass, "getuser", lambda: "bob")
    auth_bob = Authentication("shared_epias_user", "pass")
    monkeypatch.setattr(auth_bob, "_generate_tgt", lambda: "TGT-cas-bob")
    auth_bob.get_tgt()

    assert os.path.exists(auth_alice.tgt_dir)
    assert os.path.exists(auth_bob.tgt_dir)
    assert auth_alice.tgt_dir != auth_bob.tgt_dir


def test_same_os_user_different_epias_usernames_get_separate_files(monkeypatch):
    monkeypatch.setattr(getpass, "getuser", lambda: "alice")
    auth1 = Authentication("kullanici1", "pass")
    auth2 = Authentication("kullanici2", "pass")

    assert os.path.dirname(auth1.tgt_dir) == os.path.dirname(auth2.tgt_dir)
    assert auth1.tgt_dir != auth2.tgt_dir


def test_get_tgt_returns_cached_ticket_when_valid(monkeypatch):
    auth = Authentication("user1", "pass")
    calls = []
    monkeypatch.setattr(auth, "_generate_tgt", lambda: calls.append(1) or "TGT-cas-abc")

    code1, _ = auth.get_tgt()
    code2, _ = auth.get_tgt()

    assert code1 == code2 == "TGT-cas-abc"
    assert len(calls) == 1  # ikinci çağrıda TGT yeniden üretilmedi, cache'ten okundu


def test_get_tgt_extends_expiry_for_epys_service(monkeypatch):
    auth = Authentication("user1", "pass", target_service="epys")
    monkeypatch.setattr(auth, "_generate_tgt", lambda: "TGT-cas-abc")

    _, first_expiry = auth.get_tgt()
    _, second_expiry = auth.get_tgt()

    # EPYS için her kullanımda süre şu andan itibaren yeniden 45 dk'ya uzar.
    assert DateTimeUtils.from_string(second_expiry) >= DateTimeUtils.from_string(
        first_expiry
    )


def test_get_st_with_find_valid_reuses_cached_ticket(monkeypatch):
    auth = Authentication("user1", "pass")
    st_calls = []
    monkeypatch.setattr(
        auth, "_generate_st", lambda service: st_calls.append(service) or "ST-cas-xyz"
    )

    code1, _ = auth.get_st("https://epys.epias.com.tr", find_valid=True)
    code2, _ = auth.get_st("https://epys.epias.com.tr", find_valid=True)

    assert code1 == code2 == "ST-cas-xyz"
    assert len(st_calls) == 1


def test_get_st_without_find_valid_always_creates_new(monkeypatch):
    auth = Authentication("user1", "pass")
    st_calls = []
    monkeypatch.setattr(
        auth,
        "_generate_st",
        lambda service: st_calls.append(service) or f"ST-cas-{len(st_calls)}",
    )

    auth.get_st("https://epys.epias.com.tr", find_valid=False)
    auth.get_st("https://epys.epias.com.tr", find_valid=False)

    assert len(st_calls) == 2


def test_cleanup_expired_tickets_removes_stale_entries():
    auth = Authentication("user1", "pass")
    expired = DateTimeUtils.to_string(DateTimeUtils.now() - dt.timedelta(hours=1))
    valid = DateTimeUtils.to_string(DateTimeUtils.now() + dt.timedelta(hours=1))

    with open(auth.tgt_dir, "w", encoding="utf-8") as f:
        f.write(f"TGT-cas-old|{expired}|user1|{auth.root}\n")
        f.write(f"TGT-cas-new|{valid}|user1|{auth.root}\n")

    auth._cleanup_expired_tickets(auth.tgt_dir, "tgt")

    with open(auth.tgt_dir, "r", encoding="utf-8") as f:
        lines = f.readlines()

    assert len(lines) == 1
    assert "TGT-cas-new" in lines[0]


def test_clear_tickets_does_not_raise_and_removes_files(monkeypatch):
    """Regresyon: clear_tickets önceden @classmethod olarak tanımlıydı ve
    instance attribute'u olan self.tgt_dir/self.st_dir'a class üzerinden
    erişmeye çalıştığı için her çağrıldığında AttributeError fırlatıyordu."""
    auth = Authentication("user1", "pass")
    monkeypatch.setattr(auth, "_generate_tgt", lambda: "TGT-cas-abc")
    auth.get_tgt()
    assert os.path.exists(auth.tgt_dir)

    auth.clear_tickets()

    assert not os.path.exists(auth.tgt_dir)


def test_create_new_tgt_raises_on_invalid_ticket_format(monkeypatch):
    auth = Authentication("user1", "pass")
    monkeypatch.setattr(auth, "_generate_tgt", lambda: "not-a-valid-ticket")

    with pytest.raises(Exception):
        auth.get_tgt()
