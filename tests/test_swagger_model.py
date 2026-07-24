# -*- coding: utf-8 -*-
import json
import warnings

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


def test_endpoints_without_operation_id_are_derived_from_path(swagger_path):
    # Regresyon testi: operationId eksikse endpoint artık sessizce
    # atlanmıyor, path'ten isim türetilip erişilebilir kalıyor.
    model = SwaggerModel(swagger_path)
    assert model.get_endpoint("no_operation_id") is not None
    assert len(model.get_all_endpoints()) == 2


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


@pytest.fixture
def colliding_swagger_path(tmp_path):
    spec = {
        "host": "example.epias.com.tr",
        "basePath": "/example-servis/rest",
        "paths": {
            "/parameter/approved/list": {
                "post": {"operationId": "list-parameter", "parameters": [], "responses": {}},
            },
            "/parameter/list": {
                "post": {"operationId": "list-parameter", "parameters": [], "responses": {}},
            },
            "/contract/bad/list": {
                "post": {"operationId": "#{BAD_CONTRACT_LIST_NICKNAME}", "parameters": [], "responses": {}},
            },
            "/rest/v1/announcement/exist/list": {
                "post": {
                    "operationId": "AnnouncementAdminController_listAnnouncement_POST",
                    "parameters": [],
                    "responses": {},
                },
            },
        },
    }
    path = tmp_path / "swagger.json"
    path.write_text(json.dumps(spec), encoding="utf-8")
    return str(path)


def test_duplicate_operation_id_resolved_via_path_no_data_loss(colliding_swagger_path):
    # Regresyon testi: iki path aynı operationId'yi paylaşınca ikincisi artık
    # sessizce ilkinin üzerine yazmıyor, her ikisi de path'ten türetilen ayrı
    # isimlerle erişilebilir kalıyor.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        model = SwaggerModel(colliding_swagger_path)

    endpoints = model.get_all_endpoints()
    paths = {data["path"] for data in endpoints.values()}
    assert "/parameter/approved/list" in paths
    assert "/parameter/list" in paths
    assert "list_parameter" not in endpoints  # çakışan isim artık kullanılmıyor
    assert any("list_parameter" in str(w.message) for w in caught)


def test_unresolved_template_operation_id_derived_from_path(colliding_swagger_path):
    # "#{...}" gibi hiç çözülmemiş i18n/nickname şablonu operationId olarak
    # kullanılamaz; path'ten türetilen temiz bir isme düşmeli.
    model = SwaggerModel(colliding_swagger_path)
    assert model.get_endpoint("contract_bad_list") is not None


def test_controller_verb_operation_id_derived_from_path(colliding_swagger_path):
    # Springfox'un "XController_method_VERB" varsayılan nickname'i yerine
    # path'ten türetilen kısa isim kullanılmalı.
    model = SwaggerModel(colliding_swagger_path)
    assert model.get_endpoint("announcement_exist_list") is not None
    assert model.get_endpoint("announcement_admin_controller_list_announcement_post") is None
