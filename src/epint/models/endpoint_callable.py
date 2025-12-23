# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Dict, Any

import epint
from ..modules.authentication.auth_manager import Authentication
from ..modules.http_client import HTTPClient
from ..modules.error_handler import ErrorHandler
from ..modules.search.find_closest import dict_key_search
from ..modules.repr_formatter.endpoint_repr import format_endpoint_repr
from .request_model import RequestModel
from .response_model import ResponseModel


class Endpoint:
    """Endpoint model'ini wrap eden callable sınıf"""

    def __init__(self, category: str, name: str, data: Dict[str, Any]):
        self._category = category
        self._name = name
        self._data = data
        self.client = HTTPClient()

    def __repr__(self) -> str:
        """Endpoint bilgilerini detaylı olarak göster"""
        return format_endpoint_repr(self._category, self._name, self._data)

    def __call__(self, **kwargs: Any) -> Dict[str, Any]:
        """Endpoint çağrıldığında çalışır"""

        all_data = dict_key_search(['allData', 'all_data', 'alldata', 'all-data', 'AllData', 'ALL_DATA'], kwargs)

        debug = dict_key_search(['debug', 'Debug', 'DEBUG'], kwargs)

        target_service = "transparency" if "seffaflik" in self._category else "epys"
        runtime_mode = epint._mode
        auth = Authentication(epint._username, epint._password, target_service, runtime_mode)

        # HTTPClient'a auth parametresini geç
        if not hasattr(self.client, 'auth') or self.client.auth != auth:
            self.client.auth = auth

        # RequestModel oluştur
        request_model = RequestModel(self._data, kwargs)

        if "gop" != self._category:
            request_model.headers["TGT"] = auth.get_tgt()[0]
        if not ("gop" in self._category or "seffaflik" in self._category):
            request_model.headers["ST"] = auth.get_st(request_model.st_service_url)[0]
        if "gop" in self._category:
            request_model.headers["gop-service-ticket"] = auth.get_st(request_model.st_service_url)[0]


        url = self.client.buildurl(self._data.get("host"), self._data.get("basePath"), self._data.get("path"))
        method = self._data.get("method")

        # Prepare parameters for the HTTP request, including body if exists
        request_args = {
            "headers": request_model.headers
        }
        if request_model.params:
            request_args["params"] = request_model.params
        if request_model.json is not None:
            request_args["json"] = request_model.json
        if request_model.data is not None:
            request_args["data"] = request_model.data

        # ErrorHandler oluştur
        error_handler = ErrorHandler(auth)
        try:
            response = self.client.__getattribute__(method.lower())(
                url,
                **request_args
            )
            # ResponseModel oluştur
            response_model = ResponseModel(self._data, response)
            result_data = response_model.data

            return result_data
        except Exception as e:
            # Hataları ErrorHandler ile yönet
            error_handler.handle_exception(e)

            raise


__all__ = ['Endpoint']

