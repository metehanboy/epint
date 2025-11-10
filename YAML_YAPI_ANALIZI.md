# EPİNT YAML Yapısı - Analiz ve Öneriler

## 📋 Mevcut Durum Analizi

### Infrastructure Beklentileri

#### 1. `EndpointParser.parse_endpoint_parameter()`
```python
# Beklenen yapı:
{
    "name": str,              # Parametre adı
    "var_type": str,          # Tip: "str", "int", "datetime", "dict", vb.
    "description": str,       # Açıklama
    "required": bool,         # Zorunlu mu?
    "example": Optional[str], # Örnek değer
    "properties": Optional[List[Dict]],  # Nested parametreler
    "items": Optional[str]    # Array item tipi
}
```

#### 2. `ParameterMatcher`
- `var_type` içindeki `EndpointParameter` objelerini kullanır
- Fuzzy matching için parametre isimlerine ihtiyaç var
- Tip bilgisi ile doğru dönüşüm yapar

#### 3. `ParameterValidator`
- Tip doğrulaması için `var_type` gerekiyor
- Desteklenen tipler: `str`, `int`, `float`, `bool`, `list`, `dict`, `date`, `datetime`

#### 4. `ValidationService`
- Required kontrolü için `var_type` içindeki `required` field'ı kullanır
- `params` listesi sadece isim listesi için kullanılır

### Mevcut YAML Yapısı (Sorunlu)

```yaml
endpoints:
  daily-prices:
    endpoint: /v1/data/daily-prices
    method: POST
    auth: true
    short_name: daily-prices
    short_name_tr: Günlük Fiyatlar Verisi Servisi
    params:
    - date
    - page
    required:
    - date
    response: Response
    var_type: []  # ❌ BOŞ - Bu sorun!
    summary: Günlük Fiyatlar Verisi Servisi
    description: Günlük Fiyatlar Verisi Servisi
    response_structure:
      items: [...]
      page: {...}
```

**Sorunlar:**
1. ❌ `var_type: []` boş → Parametre validasyonu çalışmıyor
2. ❌ Tip bilgisi yok → Type conversion yapılamıyor
3. ❌ Nested parametreler (page.number, page.size) desteklenmiyor
4. ❌ Description ve example yok → Kullanıcı bilgilendirilemiyor

---

## ✅ ÖNERİLEN YAML YAPISI

### Yapı 1: Basit Parametreler (startDate, endDate)

```yaml
endpoints:
  aof-average-daily-data:
    endpoint: /v1/aof-average/data/daily
    method: POST
    auth: true
    short_name: aof-average-daily-data
    short_name_tr: Epiaş Web Sitesi İçin AOF Günlük Aritmetik Ortalama Listeleme Servisi
    params:
    - startDate
    - endDate
    required:
    - startDate
    - endDate
    response: Response
    var_type:
    - name: startDate
      var_type: datetime
      description: "2023-01-01T00:00:00+03:00 formatında başlangıç tarihi bilgisi."
      required: true
      example: "2021-01-01T00:00:00+03:00"
    - name: endDate
      var_type: datetime
      description: "2023-01-01T00:00:00+03:00 formatında bitiş tarihi bilgisi."
      required: true
      example: "2021-01-01T00:00:00+03:00"
    summary: Epiaş Web Sitesi İçin AOF Günlük Aritmetik Ortalama Listeleme Servisi
    description: Epiaş web sitesinde gösterilmek üzere Güniçi AOF fiyatının seçilen tarihlere göre günlük aritmetik ortalamasını dönen servistir.
    response_structure:
      items:
      - date: string
        period: integer
        averageAof: number
        periodType: string
      statistics:
      - date: string
        min: number
        max: number
        average: number
        weightedAverage: number
        summary: number
```

### Yapı 2: Nested Parametreler (page.number, page.size)

```yaml
endpoints:
  daily-prices:
    endpoint: /v1/data/daily-prices
    method: POST
    auth: true
    short_name: daily-prices
    short_name_tr: Günlük Fiyatlar Verisi Servisi
    params:
    - date
    - page
    required:
    - date
    response: Response
    var_type:
    - name: date
      var_type: datetime
      description: "2023-01-01T00:00:00+03:00 formatında tarih bilgisi."
      required: true
      example: "2021-01-01T00:00:00+03:00"
    - name: page
      var_type: dict
      description: Sayfalama bilgisi.
      required: false
      properties:
      - name: number
        var_type: int
        description: Sayfa numarası
        required: false
        example: "1"
      - name: size
        var_type: int
        description: Sayfa boyutu (item count for a single page)
        required: false
        example: "20"
      - name: sort
        var_type: dict
        description: Özel sıralama konfigürasyonu
        required: false
        properties:
        - name: field
          var_type: str
          description: Sıralama alanı
          required: false
        - name: direction
          var_type: str
          description: Sıralama yönü (ASC/DESC)
          required: false
    summary: Günlük Fiyatlar Verisi Servisi
    description: Günlük Fiyatlar Verisi Servisi
    response_structure:
      items:
      - time: string
        ptf: number
        birAyOncekiPtf: number
        smf: number
        birAyOncekiSmf: number
        sistemYon: string
        sistemYonId: integer
      page:
        number: integer
        size: integer
        total: integer
        sort:
          field: string
          direction: string
```

### Yapı 3: Array Parametreler

```yaml
endpoints:
  bulk-update:
    endpoint: /v1/bulk/update
    method: POST
    auth: true
    short_name: bulk-update
    short_name_tr: Toplu Güncelleme
    params:
    - items
    required:
    - items
    response: Response
    var_type:
    - name: items
      var_type: list
      description: Güncellenecek item listesi
      required: true
      items: dict  # Array içindeki item tipi
      properties:  # Array item'larının yapısı
      - name: id
        var_type: int
        description: Item ID
        required: true
      - name: value
        var_type: str
        description: Güncellenecek değer
        required: true
    summary: Toplu Güncelleme
    description: Birden fazla item'ı toplu olarak günceller
    response_structure: {}
```

---

## 🎯 YAML YAPISI KURALLARI

### 1. `var_type` Yapısı

**Zorunlu Alanlar:**
- `name`: str - Parametre adı (camelCase veya snake_case)
- `var_type`: str - Tip bilgisi (str, int, float, bool, datetime, date, dict, list, array)

**Opsiyonel Alanlar:**
- `description`: str - Parametre açıklaması
- `required`: bool - Zorunlu mu? (varsayılan: false)
- `example`: str - Örnek değer
- `properties`: List[Dict] - Nested parametreler (dict tipi için)
- `items`: str - Array item tipi (list/array tipi için)

**Desteklenen Tipler:**
```python
# Basit tipler
"str", "string"      → String
"int", "integer"     → Integer
"float", "number"    → Float/Number
"bool", "boolean"    → Boolean
"datetime"           → DateTime (ISO 8601)
"date"               → Date (YYYY-MM-DD)

# Karmaşık tipler
"dict", "object"     → Dictionary/Object (properties ile nested)
"list", "array"      → Array/List (items ile item tipi)
```

### 2. `params` Listesi

- Sadece **top-level** parametre isimleri
- Nested parametreler (`page.number`) **EKLENMEZ**
- Sıralama önemli değil ama tutarlılık önemli

```yaml
params:
- startDate      # ✅ Doğru
- endDate        # ✅ Doğru
- page           # ✅ Doğru (nested değil, top-level)
# - page.number  # ❌ YANLIŞ - Nested parametreler eklenmez
```

### 3. `required` Listesi

- Sadece **top-level** zorunlu parametreler
- Nested parametreler için `var_type` içindeki `required` kullanılır

```yaml
required:
- startDate      # ✅ Doğru
- endDate        # ✅ Doğru
# - page.number  # ❌ YANLIŞ - Nested için var_type kullan
```

### 4. Nested Parametreler

Nested parametreler için `properties` kullanılır:

```yaml
var_type:
- name: page
  var_type: dict
  properties:      # ✅ Nested parametreler burada
  - name: number
    var_type: int
    required: false
  - name: size
    var_type: int
    required: false
```

### 5. Array Parametreler

Array parametreler için `items` kullanılır:

```yaml
var_type:
- name: items
  var_type: list
  items: dict      # ✅ Array item tipi
  properties:      # ✅ Array item yapısı (opsiyonel)
  - name: id
    var_type: int
```

---

## 📊 KARŞILAŞTIRMA TABLOSU

| Özellik | Mevcut Yapı | Önerilen Yapı | Fayda |
|---------|-------------|---------------|-------|
| **Tip Bilgisi** | ❌ Yok | ✅ Var | Type conversion çalışır |
| **Nested Parametreler** | ❌ Desteklenmiyor | ✅ Destekleniyor | `page.number` çalışır |
| **Description** | ❌ Yok | ✅ Var | Kullanıcı bilgilendirilir |
| **Example** | ❌ Yok | ✅ Var | Kullanım kolaylaşır |
| **Required Kontrolü** | ⚠️ Sadece top-level | ✅ Tüm seviyeler | Daha doğru validasyon |
| **Fuzzy Matching** | ⚠️ Zayıf | ✅ Güçlü | Daha iyi eşleşme |
| **Type Validation** | ❌ Çalışmıyor | ✅ Çalışıyor | Hatalar önlenir |

---

## 🔧 UYGULAMA ÖNERİLERİ

### 1. Swagger'dan YAML Oluşturma

Swagger'dan YAML oluştururken:

```python
def create_var_type_from_swagger(swagger_param):
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
    
    # Schema varsa (body parametreleri için)
    if "schema" in swagger_param:
        schema = swagger_param["schema"]
        if "$ref" in schema:
            # DTO referansı - definitions'dan çöz
            dto_name = schema["$ref"].split("/")[-1]
            dto_def = swagger_definitions[dto_name]
            var_type_entry["properties"] = extract_properties_from_dto(dto_def)
    
    return var_type_entry
```

### 2. Nested Parametreler için Helper

```python
def extract_nested_params(dto_def, swagger_definitions):
    """DTO'dan nested parametreleri çıkar"""
    properties = []
    
    if "properties" in dto_def:
        for prop_name, prop_def in dto_def["properties"].items():
            prop_entry = {
                "name": prop_name,
                "var_type": map_swagger_type(prop_def.get("type", "str")),
                "description": prop_def.get("description", ""),
                "required": prop_name in dto_def.get("required", []),
            }
            
            # Example varsa ekle
            if "example" in prop_def:
                prop_entry["example"] = str(prop_def["example"])
            
            # Nested dict varsa recursive
            if prop_def.get("type") == "object" or "$ref" in prop_def:
                if "$ref" in prop_def:
                    nested_dto = swagger_definitions[prop_def["$ref"].split("/")[-1]]
                    prop_entry["properties"] = extract_nested_params(nested_dto, swagger_definitions)
                elif "properties" in prop_def:
                    prop_entry["properties"] = extract_nested_params(prop_def, swagger_definitions)
            
            # Array varsa
            if prop_def.get("type") == "array":
                prop_entry["var_type"] = "list"
                if "items" in prop_def:
                    items_def = prop_def["items"]
                    if "$ref" in items_def:
                        prop_entry["items"] = "dict"
                        nested_dto = swagger_definitions[items_def["$ref"].split("/")[-1]]
                        prop_entry["properties"] = extract_nested_params(nested_dto, swagger_definitions)
                    else:
                        prop_entry["items"] = map_swagger_type(items_def.get("type", "str"))
            
            properties.append(prop_entry)
    
    return properties
```

### 3. Tip Mapping

```python
def map_swagger_type(swagger_type, format=None):
    """Swagger tipini EPİNT tipine çevir"""
    type_mapping = {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "array": "list",
        "object": "dict",
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

---

## ✅ SONUÇ VE ÖNERİLER

### En Uygun YAML Yapısı

**Önerilen yapı:**
1. ✅ `var_type` dolu olmalı (her parametre için)
2. ✅ Tip bilgisi mutlaka olmalı
3. ✅ Nested parametreler `properties` ile tanımlanmalı
4. ✅ Description ve example eklenmeli
5. ✅ `params` sadece top-level parametreler
6. ✅ `required` sadece top-level zorunlu parametreler

### Avantajlar

1. **Type Safety**: Tip doğrulaması çalışır
2. **Better Validation**: Nested parametreler doğrulanır
3. **User Experience**: Description ve example ile kullanım kolaylaşır
4. **Fuzzy Matching**: Daha iyi parametre eşleştirmesi
5. **Maintainability**: Swagger ile senkronize kalır

### Uygulama Planı

1. ✅ Swagger parser'ı güncelle (var_type oluştur)
2. ✅ Mevcut YAML'ları güncelle (var_type ekle)
3. ✅ Test et (validation, matching, conversion)
4. ✅ Dokümantasyon güncelle

---

**Tarih:** 2025-11-10  
**Versiyon:** 1.0  
**Durum:** Öneri - Uygulanmayı Bekliyor

