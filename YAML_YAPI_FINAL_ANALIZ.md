# EPİNT YAML Yapısı - Final Analiz ve Öneriler

## 📊 TÜM YAML DOSYALARI ANALİZİ

### İstatistikler

- **Toplam YAML Dosyası:** 158
- **Toplam Endpoint:** 996
- **var_type Boş:** 564 (%56.6%)
- **var_type Dolu:** 432 (%43.4%)
- **Properties ile:** 108 endpoint
- **Items ile:** 206 endpoint

### Parametre Dağılımı

| Parametre Sayısı | Endpoint Sayısı |
|------------------|-----------------|
| 0 params         | 60              |
| 1-5 params       | 745             |
| 6-15 params      | 180             |
| 16+ params       | 11              |

### Tip Dağılımı

| Tip        | Kullanım Sayısı |
|------------|-----------------|
| str        | 818             |
| int        | 766             |
| datetime   | 403             |
| list       | 202             |
| object     | 108             |
| bool       | 87              |
| float      | 50              |

---

## 🔍 MEVCUT YAPILAR

### 1. Boş var_type (564 endpoint - %56.6%)

```yaml
endpoints:
  daily-prices:
    endpoint: /v1/data/daily-prices
    method: POST
    auth: true
    params:
    - date
    - page
    required:
    - date
    var_type: []  # ❌ BOŞ
    response_structure: {...}
```

**Sorunlar:**
- ❌ Tip doğrulaması yapılamıyor
- ❌ Type conversion çalışmıyor
- ❌ Nested parametreler desteklenmiyor
- ❌ Description ve example yok

### 2. Basit var_type (324 endpoint)

```yaml
var_type:
- name: startDate
  var_type: datetime
  description: Başlangıç tarihi
  required: true
  example: "2021-01-01T00:00:00+03:00"
- name: endDate
  var_type: datetime
  description: Bitiş tarihi
  required: true
  example: "2021-01-01T00:00:00+03:00"
```

**✅ İyi:**
- Tip bilgisi var
- Description var
- Example var
- Required bilgisi var

### 3. Properties ile var_type (108 endpoint)

**Format 1: Dict Format (Mevcut - Infrastructure Uyumlu)**

```yaml
var_type:
- name: page
  var_type: object
  description: Sayfa
  required: false
  properties:          # ✅ DICT FORMAT
    number:
      type: int
      description: İlgili sayfanın numarası
      example: 1
    size:
      type: int
      description: Her bir sayfada bulunacak eleman sayısı
      example: 20
    sort:
      type: object
      description: Sıralama ayarlaması
```

**✅ Infrastructure Uyumlu:**
- `EndpointParser.parse_endpoint_parameter()` dict bekliyor
- `properties` dict formatında
- Nested parametreler destekleniyor

**Format 2: List Format (Pre-reconciliation - Farklı)**

```yaml
var_type:
- name: page
  var_type: object
  description: Sayfa
  required: false
  properties:          # ⚠️ LIST FORMAT (Farklı)
  - name: number
    var_type: int
    description: Sayfa numarası
    required: false
    example: "1"
  - name: size
    var_type: int
    description: Sayfa boyutu
    required: false
    example: "20"
```

**⚠️ Sorun:**
- Infrastructure dict bekliyor, list formatı parse edilemiyor
- `EndpointParser` list formatını desteklemiyor

### 4. Items ile var_type (206 endpoint)

```yaml
var_type:
- name: meterIds
  var_type: list
  description: Sayaç Id'leri
  required: false
  items: int           # ✅ Item tipi
```

**✅ İyi:**
- Array parametreler için item tipi belirtilmiş
- Infrastructure uyumlu

### 5. Enum ile var_type

```yaml
var_type:
- name: exportType
  var_type: str
  description: Dışa Aktarım Tipi
  required: false
  example: XLSX, CSV or PDF
  enum:               # ✅ Enum değerleri
  - XLSX
  - CSV
  - PDF
```

**✅ İyi:**
- Enum değerleri belirtilmiş
- Validation için kullanılabilir

---

## ✅ EN UYGUN YAML YAPISI

### Temel Kurallar

1. **var_type MUTLAKA DOLU OLMALI**
   - Her parametre için detaylı bilgi
   - Boş `var_type: []` kullanılmamalı

2. **Properties DICT FORMAT olmalı**
   - Infrastructure dict bekliyor
   - List formatı desteklenmiyor

3. **Tip Mapping**
   - Swagger `type: "string"` → YAML `var_type: "str"`
   - Swagger `type: "object"` → YAML `var_type: "object"` veya `"dict"`
   - Swagger `type: "array"` → YAML `var_type: "list"`

### Önerilen Yapı

#### Basit Parametreler

```yaml
var_type:
- name: startDate
  var_type: datetime
  description: "2023-01-01T00:00:00+03:00 formatında başlangıç tarihi bilgisi."
  required: true
  example: "2021-01-01T00:00:00+03:00"
```

#### Nested Parametreler (Properties - DICT FORMAT)

```yaml
var_type:
- name: page
  var_type: object
  description: Sayfalama bilgisi
  required: false
  properties:                    # ✅ DICT FORMAT
    number:
      type: int
      description: Sayfa numarası
      example: 1
    size:
      type: int
      description: Sayfa boyutu
      example: 20
    sort:
      type: object
      description: Sıralama ayarlaması
      properties:                # ✅ Nested nested (recursive)
        field:
          type: str
          description: Sıralama alanı
        direction:
          type: str
          description: Sıralama yönü
```

**ÖNEMLİ:** Properties **dict formatında** olmalı, list formatında değil!

#### Array Parametreler

```yaml
var_type:
- name: meterIds
  var_type: list
  description: Sayaç Id'leri
  required: false
  items: int                     # ✅ Item tipi
```

#### Enum Parametreler

```yaml
var_type:
- name: exportType
  var_type: str
  description: Dışa Aktarım Tipi
  required: false
  example: XLSX, CSV or PDF
  enum:                          # ✅ Enum değerleri
  - XLSX
  - CSV
  - PDF
```

---

## 🔧 INFRASTRUCTURE BEKLENTİLERİ

### EndpointParser.parse_endpoint_parameter()

```python
# Beklenen yapı:
{
    "name": str,
    "var_type": str,              # "str", "int", "datetime", "object", "list"
    "description": str,
    "required": bool,
    "example": Optional[str],
    "properties": Optional[Dict],  # ✅ DICT FORMAT (list değil!)
    "items": Optional[str],       # Array item tipi
    "enum": Optional[List[str]]   # Enum değerleri (opsiyonel)
}
```

**Properties Format:**
```python
# ✅ DOĞRU (Dict Format)
properties: {
    "number": {
        "type": "int",
        "description": "...",
        "example": 1
    },
    "size": {
        "type": "int",
        "description": "...",
        "example": 20
    }
}

# ❌ YANLIŞ (List Format)
properties: [
    {
        "name": "number",
        "var_type": "int",
        "description": "..."
    }
]
```

---

## 📋 KARŞILAŞTIRMA TABLOSU

| Özellik | Mevcut (Boş) | Mevcut (Dolu) | Önerilen | Infrastructure Uyumu |
|---------|--------------|---------------|----------|---------------------|
| **Tip Bilgisi** | ❌ | ✅ | ✅ | ✅ |
| **Description** | ❌ | ✅ | ✅ | ✅ |
| **Example** | ❌ | ✅ | ✅ | ✅ |
| **Required** | ⚠️ Sadece top-level | ✅ | ✅ | ✅ |
| **Nested (Properties)** | ❌ | ⚠️ Farklı formatlar | ✅ Dict format | ✅ |
| **Array (Items)** | ❌ | ✅ | ✅ | ✅ |
| **Enum** | ❌ | ✅ | ✅ | ✅ |
| **Type Validation** | ❌ | ✅ | ✅ | ✅ |
| **Fuzzy Matching** | ⚠️ Zayıf | ✅ | ✅ | ✅ |

---

## 🎯 UYGULAMA ÖNERİLERİ

### 1. Swagger'dan YAML Oluşturma

```python
def create_var_type_from_swagger(swagger_param, swagger_definitions):
    """Swagger parametresinden var_type oluştur"""
    var_type_entry = {
        "name": swagger_param.get("name", ""),
        "var_type": map_swagger_type(swagger_param.get("type", "str")),
        "description": swagger_param.get("description", ""),
        "required": swagger_param.get("required", False),
    }
    
    # Example varsa ekle
    if "example" in swagger_param:
        var_type_entry["example"] = str(swagger_param["example"])
    
    # Enum varsa ekle
    if "enum" in swagger_param:
        var_type_entry["enum"] = swagger_param["enum"]
    
    # Schema varsa (body parametreleri için)
    if "schema" in swagger_param:
        schema = swagger_param["schema"]
        if "$ref" in schema:
            # DTO referansı - definitions'dan çöz
            dto_name = schema["$ref"].split("/")[-1]
            dto_def = swagger_definitions[dto_name]
            # ✅ DICT FORMAT oluştur
            var_type_entry["properties"] = extract_properties_as_dict(dto_def, swagger_definitions)
    
    return var_type_entry

def extract_properties_as_dict(dto_def, swagger_definitions):
    """DTO'dan properties'i DICT FORMAT olarak çıkar"""
    properties = {}
    
    if "properties" in dto_def:
        for prop_name, prop_def in dto_def["properties"].items():
            prop_entry = {
                "type": map_swagger_type(prop_def.get("type", "str")),
                "description": prop_def.get("description", ""),
            }
            
            # Example varsa ekle
            if "example" in prop_def:
                prop_entry["example"] = prop_def["example"]
            
            # Required kontrolü
            if prop_name in dto_def.get("required", []):
                prop_entry["required"] = True
            
            # Nested object varsa recursive
            if prop_def.get("type") == "object" or "$ref" in prop_def:
                if "$ref" in prop_def:
                    nested_dto = swagger_definitions[prop_def["$ref"].split("/")[-1]]
                    prop_entry["properties"] = extract_properties_as_dict(nested_dto, swagger_definitions)
                elif "properties" in prop_def:
                    prop_entry["properties"] = extract_properties_as_dict(prop_def, swagger_definitions)
            
            # Array varsa
            if prop_def.get("type") == "array":
                prop_entry["type"] = "list"
                if "items" in prop_def:
                    items_def = prop_def["items"]
                    if "$ref" in items_def:
                        prop_entry["items"] = "object"
                        nested_dto = swagger_definitions[items_def["$ref"].split("/")[-1]]
                        prop_entry["properties"] = extract_properties_as_dict(nested_dto, swagger_definitions)
                    else:
                        prop_entry["items"] = map_swagger_type(items_def.get("type", "str"))
            
            properties[prop_name] = prop_entry
    
    return properties
```

### 2. Tip Mapping

```python
def map_swagger_type(swagger_type, format=None):
    """Swagger tipini EPİNT tipine çevir"""
    type_mapping = {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "array": "list",
        "object": "object",  # veya "dict"
    }
    
    mapped = type_mapping.get(swagger_type, "str")
    
    # Format'a göre özel tipler
    if swagger_type == "string":
        if format == "date-time":
            return "datetime"
        elif format == "date":
            return "date"
    
    return mapped
```

### 3. Mevcut YAML'ları Güncelleme

**Öncelik Sırası:**
1. ✅ Boş `var_type: []` olan 564 endpoint'i doldur
2. ✅ List formatındaki properties'leri dict formatına çevir
3. ✅ Tip bilgilerini standardize et
4. ✅ Description ve example ekle

---

## ✅ SONUÇ VE ÖNERİLER

### En Uygun YAML Yapısı

1. **var_type MUTLAKA DOLU**
   - Her parametre için detaylı bilgi
   - Boş `var_type: []` kullanılmamalı

2. **Properties DICT FORMAT**
   - Infrastructure dict bekliyor
   - List formatı desteklenmiyor
   - Nested properties recursive olabilir

3. **Tip Bilgisi Zorunlu**
   - `var_type` field'ı mutlaka olmalı
   - Swagger'dan otomatik map edilmeli

4. **Description ve Example**
   - Kullanıcı deneyimi için önemli
   - Swagger'dan otomatik alınmalı

5. **Required Bilgisi**
   - Top-level için `required` listesi
   - Nested için `properties` içinde `required` field'ı

### Avantajlar

- ✅ **Type Safety:** Tip doğrulaması çalışır
- ✅ **Better Validation:** Nested parametreler doğrulanır
- ✅ **User Experience:** Description ve example ile kolay kullanım
- ✅ **Fuzzy Matching:** Daha iyi parametre eşleştirmesi
- ✅ **Maintainability:** Swagger ile senkronize kalır
- ✅ **Infrastructure Uyumu:** Tüm özellikler çalışır

### Uygulama Planı

1. ✅ Swagger parser'ı güncelle (var_type oluştur, dict format)
2. ✅ Mevcut YAML'ları güncelle (564 endpoint)
3. ✅ List formatını dict formatına çevir
4. ✅ Test et (validation, matching, conversion)
5. ✅ Dokümantasyon güncelle

---

**Tarih:** 2025-11-10  
**Versiyon:** 2.0  
**Durum:** Final Analiz - Tüm YAML'lar İncelendi

