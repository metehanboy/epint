# -*- coding: utf-8 -*-
import json

import pytest

from epint.models.swagger import SwaggerModel


@pytest.fixture
def swagger_path(tmp_path):
    spec = {
        "host": "example.epias.com.tr",
        "basePath": "/example-servis/rest",
        "definitions": {
            "QueryRequest": {
                "type": "object",
                "properties": {
                    "startDate": {"type": "string", "format": "date-time"},
                    "amount": {"type": "number", "format": "double"},
                    "self_ref": {"$ref": "#/definitions/QueryRequest"},
                },
            },
            "QueryResponse": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "correlationId": {"type": "string"},
                    "body": {"$ref": "#/definitions/QueryRequest"},
                },
            },
        },
        "paths": {
            "/available-lookups": {
                "get": {
                    "operationId": "available-lookups",
                    "consumes": [],
                    "produces": ["application/json"],
                    "parameters": [
                        {
                            "name": "filter",
                            "in": "body",
                            "schema": {"$ref": "#/definitions/QueryRequest"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "ok",
                            "schema": {"$ref": "#/definitions/QueryResponse"},
                        }
                    },
                }
            },
            "/no-operation-id": {
                "post": {"parameters": [], "responses": {}},
            },
        },
    }
    path = tmp_path / "swagger.json"
    path.write_text(json.dumps(spec), encoding="utf-8")
    return str(path)


def test_operation_id_hyphens_become_underscores(swagger_path):
    model = SwaggerModel(swagger_path)
    assert "available_lookups" in model.get_all_endpoints()


def test_endpoints_without_operation_id_are_skipped(swagger_path):
    model = SwaggerModel(swagger_path)
    assert model.get_endpoint("no_operation_id") is None
    assert len(model.get_all_endpoints()) == 1


def test_body_schema_ref_is_resolved(swagger_path):
    model = SwaggerModel(swagger_path)
    endpoint = model.get_endpoint("available_lookups")
    body_param = endpoint["parameters"][0]
    assert body_param["in"] == "body"
    assert "properties" in body_param["schema"]
    assert "startDate" in body_param["schema"]["properties"]


def test_response_schema_ref_is_resolved(swagger_path):
    model = SwaggerModel(swagger_path)
    endpoint = model.get_endpoint("available_lookups")
    response_schema = endpoint["responses"]["200"]["schema"]
    assert "status" in response_schema["properties"]
    assert "correlationId" in response_schema["properties"]
    assert "properties" in response_schema["properties"]["body"]


def test_circular_ref_does_not_infinite_loop(swagger_path):
    model = SwaggerModel(swagger_path)
    endpoint = model.get_endpoint("available_lookups")
    resolved_schema = endpoint["parameters"][0]["schema"]
    # Circular self_ref, visited-set koruması sayesinde sonsuz döngüye girmez;
    # key korunur ama değeri None'a çözülür (bkz. SwaggerModel._resolve_all_refs).
    assert resolved_schema["properties"]["self_ref"] is None
