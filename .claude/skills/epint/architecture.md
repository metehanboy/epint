# epint iç mimarisi

Paket davranışını debug ederken veya `ep.<category>` beklenmedik sonuç verince kullan.

```text
python -c "import epint, pathlib; print(pathlib.Path(epint.__file__).parent)"
# → .../site-packages/epint/  (editable install ise kaynakla aynı yer: src/epint/)
```

İnceleme: `src/epint/__init__.py`, `models/`, `modules/`, `endpoints/<category>/swagger.json`.

Çağrı zinciri: `ep.<category>` → `CategoryProxy.__getattr__(<method>)` → `Endpoint.__call__(**kwargs)` → `RequestModel` → `HTTPClient` → `ResponseModel`.

Geliştirme / test kuralları için `usage-conventions.md`; kategori listesi için `overview.md`.

## 1. Kategori çözümleme — `epint/__init__.py`

- `ep.<isim>` → modül `__getattr__`.
- Sıra: tam ad → `CATEGORY_ALIASES` → alias fuzzy (0.6) → `seffaflik*` / `reconciliation-*` prefix toleransı → normalize / fuzzy → yoksa `AttributeError`.
- İlk erişimde `load_category()` → `endpoints/<category>/swagger.json` → `EndpointModel` cache; `CategoryProxy` da cache'lenir.

## 2. Swagger — `models/swagger.py`

- Method adı normalde `operationId`'deki `-` → `_`.
- **"Güvenilmez" operationId tespiti** (`_is_unreliable_operation_id`): boş, çözülmemiş `#{...}`/`${...}` şablonu, Springfox'un varsayılan `XController_method_VERB` nickname'i, ya da operationId'nin doğrudan path olması. Bu durumlarda isim path'ten türetilir (`_name_from_path`, `rest`/`v1`/`v2`/`api` boilerplate segmentleri atılır).
- **Çakışma çözümü**: aynı isme düşen (operationId çakışması dahil) birden fazla endpoint varsa, hepsi path'ten türetilen isimlerle ayrıştırılır; hâlâ çakışıyorsa sayısal suffix. Her çözüm `warnings.warn` ile bildirilir — kategori ilk yüklenirken (`load_category`) tetiklenir.
- `$ref` recursive çözülür (circular korumalı).

## 3. Registry — `models/endpoint_registry.py`

- Global cache; `get_endpoint(category, name)` her seferinde yeni `Endpoint` örneği.

## 4. Method eşleştirme — `CategoryProxy`

- Önce `epint._check_auth()` (auth yoksa `RuntimeError`).
- Normalize / fuzzy method eşleştirme; `to_python_method_name()` Türkçe→ASCII, camelCase→snake_case.

## 5. İstek — `models/request_model.py`

- Kwargs → `query` / `header` / `path` / `body`.
- Fuzzy param eşleştirme; varsayılanlar: `page`≈`{number:1,size:1000}`, `region`/`regionCode`≈`TR1`.
- `date-time` / sayı format dönüşümü (§7).
- GOP service wrapper: `header`+`body`, otomatik `transactionId` / `application`.
- Host: `seffaflik*` → `seffaflik.epias.com.tr`; `gop` → `gop`/`testgop`; `gunici*` → `gunici.epias.com.tr`; diğer → `epys` / `epys-prp`.

## 6. Auth — `Endpoint.__call__` + `modules/authentication/auth_manager.py`

- `seffaflik*` → yalnızca `TGT` (ST yok); `gop` → `gop-service-ticket`; diğer EPYS → `TGT`+`ST`.
- TGT: EPYS 45 dk (kullanımda uzar); şeffaflık 2 saat (uzamaz). Cache: işletim sistemi temp dizini altında kullanıcı-hash'li klasör.
- 401/404 ticket invalid → cache temiz + retry (`debug=True` ise HTTP atılmaz, `RequestModel` döner).

## 7. Tarih formatları

| Kategori | Format |
|---|---|
| `gop` | ISO + ms + `+HHMM` |
| `gunici` | ISO, TZ yok |
| diğer | ISO + `+HH:MM` |

Saat dilimi: `Europe/Istanbul`.

## 8. Yanıt — `models/response_model.py`

- Binary → `io.BytesIO`.
- `RestResponse` / GOP wrapper → `body` soyulur.

## Not

Patch burada yapılır (`src/epint/`). Değişiklikten sonra: `src/epint/modules/version/__init__.py` bump → commit/push → tüketici repolar (portal/airflow) `requirements.txt` güncelleyip pip ile çeker.
