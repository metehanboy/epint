# -*- coding: utf-8 -*-
import io

from epint.models.response_model import ResponseModel


def _endpoint(schema=None):
    return {
        "category": "customer",
        "responses": {"200": {"schema": schema}} if schema else {},
    }


def test_binary_content_returns_bytesio(fake_response):
    response = fake_response(
        status_code=200,
        content=b"PDFDATA",
        headers={"Content-Type": "application/pdf"},
    )
    rm = ResponseModel(_endpoint(), response)
    assert isinstance(rm.data, io.BytesIO)
    assert rm.data.read() == b"PDFDATA"


def test_json_without_schema_returned_as_is(fake_response):
    response = fake_response(status_code=200, json_data={"foo": "bar"}, headers={})
    rm = ResponseModel(_endpoint(schema=None), response)
    assert rm.data == {"foo": "bar"}


def test_non_json_body_falls_back_to_text(fake_response):
    response = fake_response(
        status_code=200, json_data=None, text="plain text", headers={}
    )
    rm = ResponseModel(_endpoint(), response)
    assert rm.raw_data == "plain text"
    assert rm.data == "plain text"


def test_rest_response_wrapper_is_unwrapped(fake_response):
    schema = {
        "properties": {
            "status": {"type": "string"},
            "correlationId": {"type": "string"},
            "body": {
                "properties": {
                    "amount": {"type": "number"},
                }
            },
        }
    }
    response = fake_response(
        status_code=200,
        json_data={"status": "OK", "correlationId": "abc", "body": {"amount": "12.5"}},
        headers={},
    )
    rm = ResponseModel(_endpoint(schema), response)
    assert rm.data == {"amount": 12.5}


def test_gop_service_wrapper_is_unwrapped(fake_response):
    schema = {
        "properties": {
            "header": {"type": "array"},
            "body": {
                "properties": {
                    "organizationCode": {"type": "integer"},
                }
            },
        }
    }
    response = fake_response(
        status_code=200,
        json_data={"header": [], "body": {"organizationCode": "12345"}},
        headers={},
    )
    rm = ResponseModel(_endpoint(schema), response)
    assert rm.data == {"organizationCode": 12345}


def test_status_code_fallback_to_200_schema(fake_response):
    schema = {"properties": {"amount": {"type": "number"}}}
    response = fake_response(status_code=201, json_data={"amount": "5"}, headers={})
    rm = ResponseModel(_endpoint(schema), response)
    # endpoint_data'da yalnızca '200' response tanımlı; farklı status code'da bile
    # 200 şemasına fallback yapılır (bkz. ResponseModel._parse_response).
    assert rm.data == {"amount": 5.0}
