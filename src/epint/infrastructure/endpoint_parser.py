# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Dict, Any
from .endpoint_models import EndpointParameter, EndpointInfo


class EndpointParser:

    @staticmethod
    def parse_endpoint_parameter(param_data: Dict[str, Any]) -> EndpointParameter:
        properties = param_data.get("properties")
        if properties and isinstance(properties, dict):
            properties_list = []
            for prop_name, prop_data in properties.items():
                if isinstance(prop_data, dict):
                    properties_list.append(
                        EndpointParameter(
                            name=prop_name,
                            var_type=prop_data.get("type", "str"),
                            description=prop_data.get("description", ""),
                            required=prop_data.get("required", False),
                            example=prop_data.get("example"),
                            properties=None,
                            items=prop_data.get("items"),
                        )
                    )
            properties = properties_list

        return EndpointParameter(
            name=param_data.get("name", ""),
            var_type=param_data.get("var_type", "str"),
            description=param_data.get("description", ""),
            required=param_data.get("required", False),
            example=param_data.get("example"),
            properties=properties,
            items=param_data.get("items"),
        )

    @staticmethod
    def parse_endpoint_info(
        name: str, endpoint_data: Dict[str, Any], category: str = ""
    ) -> EndpointInfo:
        var_type_list = [
            EndpointParser.parse_endpoint_parameter(var_data)
            for var_data in endpoint_data.get("var_type", [])
        ]

        return EndpointInfo(
            name=name,
            endpoint=endpoint_data.get("endpoint", ""),
            method=endpoint_data.get("method", "GET"),
            auth=endpoint_data.get("auth", False),
            short_name=endpoint_data.get("short_name", ""),
            short_name_tr=endpoint_data.get("short_name_tr", ""),
            params=endpoint_data.get("params", []),
            required=endpoint_data.get("required"),
            response=endpoint_data.get("response", []),
            var_type=var_type_list,
            summary=endpoint_data.get("summary", ""),
            description=endpoint_data.get("description", ""),
            category=category,
            response_structure=endpoint_data.get("response_structure"),
        )
