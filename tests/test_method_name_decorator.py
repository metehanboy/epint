# -*- coding: utf-8 -*-
import pytest

from epint.modules.search.method_name_decorator import to_python_method_name


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("getUserData", "get_user_data"),
        ("brg-query", "brg_query"),
        ("BRG Query", "brg_query"),
        ("get_user_data", "get_user_data"),
        ("/collateral/organization/", "collateral_organization"),
        ("123method", "_123method"),
        ("class", "class_endpoint"),
        ("", ""),
    ],
)
def test_documented_examples(raw, expected):
    assert to_python_method_name(raw) == expected


def test_turkish_characters_are_ascii_folded():
    # NFKD + ascii-fold: cedilla/breve/dot-above kaldırılır, temel Latin harf kalır.
    assert to_python_method_name("Şirket") == "sirket"


def test_camel_case_with_consecutive_capitals():
    # tradeIncrease path'i trade_increase_* method isimlerine ayrılır (bkz. GOP skill dosyası)
    assert to_python_method_name("tradeIncrease") == "trade_increase"


def test_other_python_keyword_gets_suffixed():
    assert to_python_method_name("import") == "import_endpoint"
    assert to_python_method_name("not") == "not_endpoint"


def test_idempotent_on_already_normalized_name():
    normalized = to_python_method_name("offer_create_hourly")
    assert to_python_method_name(normalized) == normalized
