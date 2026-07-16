# -*- coding: utf-8 -*-
import pytest

import epint
from epint.models.endpoint_registry import EndpointModel
from epint.modules.category_proxy import CategoryProxy


def test_exact_category_name_resolves():
    proxy = epint.customer
    assert isinstance(proxy, CategoryProxy)
    assert proxy._category == "customer"


def test_alias_resolves_to_target_category():
    assert epint.transparency._category == "seffaflik-electricity"
    assert epint.invoice._category == "reconciliation-invoice"
    assert epint.bpm._category == "reconciliation-bpm"


def test_seffaflik_typo_fuzzy_resolves_to_electricity():
    assert epint.seffalik._category == "seffaflik-electricity"


def test_unknown_category_raises_attribute_error():
    with pytest.raises(AttributeError):
        epint.totally_unknown_category_xyz


def test_category_objects_are_cached():
    first = epint.customer
    second = epint.customer
    assert first is second


def test_category_proxy_without_auth_raises_runtime_error():
    EndpointModel.register_endpoint(
        "fakecat", "sample_method", {"category": "fakecat", "parameters": []}
    )
    proxy = CategoryProxy("fakecat")
    with pytest.raises(RuntimeError):
        proxy.sample_method


def test_category_proxy_exact_and_fuzzy_method_resolution():
    EndpointModel.register_endpoint(
        "fakecat", "sample_method", {"category": "fakecat", "parameters": []}
    )
    epint.set_auth("user", "pass")
    proxy = CategoryProxy("fakecat")

    endpoint = proxy.sample_method
    assert endpoint._name == "sample_method"

    camel_cased = proxy.sampleMethod
    assert camel_cased._name == "sample_method"

    typo = proxy.smaple_method
    assert typo._name == "sample_method"


def test_category_proxy_unknown_method_raises_attribute_error():
    EndpointModel.register_endpoint(
        "fakecat", "sample_method", {"category": "fakecat", "parameters": []}
    )
    epint.set_auth("user", "pass")
    proxy = CategoryProxy("fakecat")

    with pytest.raises(AttributeError):
        proxy.completely_unrelated_endpoint_name
