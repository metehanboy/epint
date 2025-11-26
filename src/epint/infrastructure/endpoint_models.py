# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class EndpointParameter:

    name: str
    var_type: str
    description: str
    required: bool
    example: Optional[str] = None
    properties: Optional[List["EndpointParameter"]] = None
    items: Optional[str] = None


@dataclass
class EndpointInfo:

    name: str
    endpoint: str
    method: str
    auth: bool
    short_name: str
    short_name_tr: str
    params: List[str]
    required: Optional[List[str]]
    response: List[str]
    var_type: List[EndpointParameter]
    summary: str
    description: str
    category: str = ""
    response_structure: Optional[Dict[str, Any]] = None

    def _format_header(self) -> list:
        from .service_config import get_service_config

        lines = []
        lines.append(f"🔗 {self.short_name_tr} ({self.name})")
        lines.append("=" * 60)
        if self.category:
            lines.append(f"📁 Kategori: {self.category}")
            config = get_service_config(self.category, "prod")  # Default prod mode
            if config:
                lines.append(f"🌐 Sunucu: {config.get_server('prod')}")
                lines.append(f"📂 Kök Dizin: {config.root_path}")
                lines.append(f"🎫 Service Ticket: {config.get_service_ticket('prod')}")
                lines.append(f"🔐 Auth Mode: {config.auth_mode}")
        lines.append(f"📍 Endpoint: {self.method} {self.endpoint}")
        lines.append(f"🔐 Auth: {'Evet' if self.auth else 'Hayır'}")
        return lines

    def _format_description(self) -> list:
        lines = []
        import textwrap

        if self.description:
            wrapped_desc = textwrap.fill(self.description, width=80)
            wrapped_lines = wrapped_desc.split("\n")
            if wrapped_lines:
                lines.append(f"📝 Açıklama: {wrapped_lines[0]}")
                for line in wrapped_lines[1:]:
                    lines.append(f"\t{line}")
            else:
                lines.append("📝 Açıklama: -")
        else:
            lines.append("📝 Açıklama: -")
        return lines

    def _format_parameters(self) -> list:
        from .service_config import get_auth_mode
        
        lines = []
        if self.var_type:
            # GOP için özel gösterim: header parametresini sayma
            param_count = len(self.var_type)
            auth_mode = get_auth_mode(self.category, "prod")
            if auth_mode == "gop":
                # gop-service-ticket ve body içindeki header'ı sayma
                param_count = sum(1 for p in self.var_type if p.name != "gop-service-ticket")
            
            lines.append(f"\n📋 Parametreler ({param_count} adet):")
            lines.append("-" * 40)
            for param in self.var_type:
                # GOP için gop-service-ticket'ı gösterme (zaten header'a ekleniyor)
                if auth_mode == "gop" and param.name == "gop-service-ticket":
                    continue
                
                required_mark = "🔴" if param.required else "🟡"
                example_text = f" (Örnek: {param.example})" if param.example else ""
                lines.append(
                    f"  {required_mark} {param.name} ({param.var_type}): {param.description}{example_text}"
                )

                if param.properties:
                    # GOP için body içindeki header'ı gösterme (otomatik dolduruluyor)
                    if auth_mode == "gop" and param.name == "body":
                        # Sadece body içindeki parametreleri göster (header'ı atla)
                        body_props = [p for p in param.properties if p.name != "header"]
                        if body_props:
                            lines.append(f"    📝 Body İçeriği:")
                            for prop in body_props:
                                prop_required_mark = "🔴" if prop.required else "🟡"
                                prop_example_text = (
                                    f" (Örnek: {prop.example})" if prop.example else ""
                                )
                                lines.append(
                                    f"      {prop_required_mark} {prop.name} ({prop.var_type}): {prop.description}{prop_example_text}"
                                )
                    else:
                        param_type_name = (
                            "Body"
                            if param.name == "body"
                            else "Header" if param.name == "header" else param.name.title()
                        )
                        lines.append(f"    📝 {param_type_name} İçeriği:")
                        for prop in param.properties:
                            prop_required_mark = "🔴" if prop.required else "🟡"
                            prop_example_text = (
                                f" (Örnek: {prop.example})" if prop.example else ""
                            )
                            lines.append(
                                f"      {prop_required_mark} {prop.name} ({prop.var_type}): {prop.description}{prop_example_text}"
                            )
        return lines

    def _format_required_params(self) -> list:
        from .service_config import get_auth_mode
        
        lines = []
        if self.required:
            # GOP için gop-service-ticket'ı çıkar (zaten header'a ekleniyor)
            auth_mode = get_auth_mode(self.category, "prod")
            required_list = [r for r in self.required if not (auth_mode == "gop" and r == "gop-service-ticket")]
            if required_list:
                lines.append(f"\n⚠️  Zorunlu Parametreler: {', '.join(required_list)}")
        return lines

    def _format_response_structure(self) -> list:
        lines = []
        if self.response_structure:
            lines.append("\n📤 Response Yapısı:")
            lines.append("-" * 40)
            for key, value_type in self.response_structure.items():
                lines.append(f"  • {key}: {value_type}")
        return lines

    def __str__(self) -> str:
        lines = []
        lines.extend(self._format_header())
        lines.extend(self._format_description())
        lines.extend(self._format_parameters())
        lines.extend(self._format_required_params())
        lines.extend(self._format_response_structure())
        return "\n".join(lines)

    def __repr__(self):
        return self.__str__()


@dataclass
class ValidationResult:

    is_valid: bool
    errors: List[str]
    warnings: List[str]
    validated_params: Dict[str, Any]
    endpoint_info: EndpointInfo
