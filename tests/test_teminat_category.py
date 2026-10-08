# -*- coding: utf-8 -*-
import copy
import warnings

import pytest

import epint
from epint.models.endpoint_registry import EndpointModel
from epint.models.request_model import RequestModel
from epint.models.response_model import ResponseModel
from epint.modules.http_client import HTTPClient

# EPYS Teminat Modülü Web Servis Dokümanı v1.0'daki path'ler (host hariç).
EXPECTED_PATHS = {
    "initial_collateral_list": "/gogi-collateral/rest/v1/initial-collateral/list",
    "gogi_collateral_list": "/gogi-collateral/rest/v1/calculation/calculated/details",
    "gogi_collateral_detail_list": "/gogi-collateral/rest/v1/data/details",
    "additional_collateral_list": "/collateral/rest/v1/additional/list",
    "imbalance_collateral_list": "/imbalance-collateral/v1/imbalance-collateral/list",
    "imbalance_collateral_detail_list": "/imbalance-collateral/v1/imbalance-collateral/list/detail",
    "aosmf_detail_list": "/imbalance-collateral/v1/imbalance-collateral/list/aosmf",
    "risk_collateral_list": "/risk-collateral/rest/v1/list/risk-collateral-by-org",
    "risk_collateral_detail_list": "/risk-collateral/rest/v1/list/risk-daily-by-validity-date",
    "daily_generation_detail_list": "/risk-collateral/rest/v1/list/dsg-risk-daily-generation",
    "daily_portfolio_detail_list": "/risk-collateral/v1/portfolio/dsg/list",
    "rbs_collateral_list": "/rbs-collateral/rest/v1/list",
    "rbs_collateral_powerplant_list": "/rbs-collateral/rest/v1/powerplant/list",
    "rbs_collateral_powerplant_detail_list": "/rbs-collateral/rest/v1/powerplant/detail",
    "rbs_collateral_powerplant_hourly_list": "/rbs-collateral/rest/v1/powerplant/hourly",
    "res_collateral_list": "/res-collateral/rest/v1/list",
    "res_collateral_daily_detail_list": "/res-collateral/rest/v1/list/res-daily-detail",
    "res_collateral_withdrawal_detail_list": "/res-collateral/rest/v1/withdrawal-details/list",
    "risk_daily_detail_report": "/risk-collateral/rest/v1/list/risk-daily-detail",
    "seasonal_constant_report": "/risk-collateral/seasonal/v1/list/seasonal",
    "collateral_report": "/collateral/rest/v1/report/list",
}


@pytest.fixture
def teminat_endpoints():
    epint.set_auth("user", "pass")
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # isim çakışması uyarısı olmamalı
        proxy = epint.teminat
    assert proxy._category == "teminat"
    return EndpointModel.get_category_endpoints("teminat")


def _build(endpoint_data, kwargs):
    data = copy.deepcopy(endpoint_data)
    rm = RequestModel(data, kwargs)
    url = HTTPClient().buildurl(data["host"], data["basePath"], data["path"])
    return url, rm


def test_teminat_exposes_all_documented_endpoints(teminat_endpoints):
    assert set(teminat_endpoints) == set(EXPECTED_PATHS)
    assert all(ep["method"] == "POST" for ep in teminat_endpoints.values())


@pytest.mark.parametrize(
    "mode,host", [("prod", "epys.epias.com.tr"), ("test", "epys-prp.epias.com.tr")]
)
def test_teminat_urls_match_documentation(teminat_endpoints, mode, host):
    # Swagger'da basePath yok; path'ler servis önekini içerir. URL'de "//" oluşmamalı.
    epint.set_mode(mode)
    for name, path in EXPECTED_PATHS.items():
        url, rm = _build(teminat_endpoints[name], {})
        assert url == f"https://{host}{path}"
        assert rm.st_service_url == "https://epys.epias.com.tr"


def test_teminat_request_body_conversion(teminat_endpoints):
    _, rm = _build(
        teminat_endpoints["aosmf_detail_list"],
        {"effective_date_start": "2023-08-01", "month_count": "12"},
    )
    assert rm.json == {
        "effectiveDateStart": "2023-08-01T00:00:00+03:00",
        "monthCount": 12,
    }
    assert rm.headers["Content-Type"] == "application/json"


def test_teminat_response_rest_wrapper_is_unwrapped(teminat_endpoints, fake_response):
    response = fake_response(
        status_code=200,
        json_data={
            "status": "OK",
            "correlationId": "abc",
            "body": {"content": {"amount": "123.5"}},
        },
        headers={"Content-Type": "application/json"},
    )
    rm = ResponseModel(teminat_endpoints["initial_collateral_list"], response)
    assert rm.data == {"content": {"amount": 123.5}}
