# -*- coding: utf-8 -*-
import epint
from epint.models.request_model import RequestModel


def _endpoint(category, parameters, consumes=None, produces=None):
    return {
        "category": category,
        "parameters": parameters,
        "consumes": consumes if consumes is not None else ["application/json"],
        "produces": produces if produces is not None else ["application/json"],
    }


def test_page_default_is_applied_when_missing():
    endpoint = _endpoint(
        "customer", [{"name": "page", "in": "query", "type": "object"}]
    )
    rm = RequestModel(endpoint, {})
    assert rm.params["page"] == {"number": 1, "size": 1000, "limit": 1000}


def test_page_default_partial_override_keeps_user_values():
    endpoint = _endpoint(
        "customer", [{"name": "page", "in": "query", "type": "object"}]
    )
    rm = RequestModel(endpoint, {"page": {"number": 2}})
    assert rm.params["page"] == {"number": 2, "size": 1000, "limit": 1000}


def test_region_default_is_tr1():
    endpoint = _endpoint(
        "demand", [{"name": "region", "in": "query", "type": "string"}]
    )
    rm = RequestModel(endpoint, {})
    assert rm.params["region"] == "TR1"


def test_region_user_value_overrides_default():
    endpoint = _endpoint(
        "demand", [{"name": "region", "in": "query", "type": "string"}]
    )
    rm = RequestModel(endpoint, {"region": "TR2"})
    assert rm.params["region"] == "TR2"


def test_query_param_fuzzy_matched_and_removed_from_kwargs():
    endpoint = _endpoint(
        "customer",
        [{"name": "readingOrganizationId", "in": "query", "type": "integer"}],
    )
    rm = RequestModel(endpoint, {"readingorganizationid": "42"})
    assert (
        rm.params["readingOrganizationId"] == 42
    )  # integer format dönüşümü de uygulanmış olmalı


def test_date_time_conversion_default_category():
    endpoint = _endpoint(
        "customer",
        [{"name": "startDate", "in": "query", "type": "string", "format": "date-time"}],
    )
    rm = RequestModel(endpoint, {"startDate": "2026-07-20"})
    assert rm.params["startDate"] == "2026-07-20T00:00:00+03:00"


def test_date_time_conversion_gop_category():
    endpoint = _endpoint(
        "gop",
        [
            {
                "name": "deliveryDay",
                "in": "body",
                "schema": {
                    "type": "object",
                    "properties": {
                        "deliveryDay": {"type": "string", "format": "date-time"}
                    },
                },
            }
        ],
    )
    rm = RequestModel(endpoint, {"deliveryDay": "2026-07-20"})
    assert rm.json["deliveryDay"] == "2026-07-20T00:00:00.000+0300"


def test_date_time_conversion_gunici_category():
    endpoint = _endpoint(
        "gunici",
        [{"name": "startDate", "in": "query", "type": "string", "format": "date-time"}],
    )
    rm = RequestModel(endpoint, {"startDate": "2026-07-20"})
    assert rm.params["startDate"] == "2026-07-20T00:00:00"


def test_gop_service_wrapper_wraps_body_and_adds_header():
    schema = {
        "type": "object",
        "properties": {
            "header": {"type": "array", "items": {"type": "object"}},
            "body": {
                "type": "object",
                "properties": {
                    "organizationCode": {"type": "integer"},
                },
            },
        },
    }
    endpoint = _endpoint("gop", [{"name": "request", "in": "body", "schema": schema}])
    rm = RequestModel(endpoint, {"organizationCode": 12345})

    assert "header" in rm.json
    assert "body" in rm.json
    assert rm.json["body"]["organizationCode"] == 12345
    header_keys = {h["key"] for h in rm.json["header"]}
    assert header_keys == {"transactionId", "application"}
    application_value = next(
        h["value"] for h in rm.json["header"] if h["key"] == "application"
    )
    assert application_value == epint.__fullname__


def test_nested_array_field_mapping_flat_kwarg_to_array():
    schema = {
        "type": "object",
        "properties": {
            "contracts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"deliveryDay": {"type": "string"}},
                },
            }
        },
    }
    endpoint = _endpoint(
        "customer", [{"name": "request", "in": "body", "schema": schema}]
    )
    rm = RequestModel(endpoint, {"deliveryDay": "2026-07-20"})
    assert rm.json["contracts"] == [{"deliveryDay": "2026-07-20"}]


def test_no_body_schema_passes_remaining_kwargs_as_json():
    endpoint = _endpoint("customer", [])
    rm = RequestModel(endpoint, {"foo": "bar"})
    assert rm.json == {"foo": "bar"}


def test_content_type_header_set_from_consumes():
    endpoint = _endpoint("customer", [], consumes=["application/json"])
    rm = RequestModel(endpoint, {})
    assert rm.headers["Content-Type"] == "application/json"


def test_host_selection_seffaflik():
    endpoint = _endpoint("seffaflik-electricity", [])
    epint.set_mode("prod")
    rm = RequestModel(endpoint, {})
    assert rm._endpoint_data["host"] == "https://seffaflik.epias.com.tr"


def test_host_selection_gop_test_mode():
    endpoint = _endpoint("gop", [])
    epint.set_mode("test")
    rm = RequestModel(endpoint, {})
    assert rm._endpoint_data["host"] == "https://testgop.epias.com.tr"
