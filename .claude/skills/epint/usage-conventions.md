# epint — geliştirme kuralları

Önce `overview.md`. İç mimari: `architecture.md`. Kategori detayı: bu skill hub (`SKILL.md`) → `services/<category>.md`.

## Kurulum / branch

- Git remote `origin` → `metehanboy/epint`, branch `main` (+ `dev` branch mevcut, ayrı özellikler için).
- Bu repoyu tüketen projelerde (portal, airflow, dev workspace'ler) genelde editable install kullanılır: `pip install -e <bu-repo-yolu>`.

## Yeni endpoint kategori eklemek

1. `src/epint/endpoints/<category>/swagger.json` ekle/güncelle (OpenAPI/swagger; `operationId` zorunlu, method adına dönüşür — ama güvenilmezse (`#{...}` şablon, `Controller_x_VERB`, bare-path) `SwaggerModel` path'ten türetir, bkz. `architecture.md` §2).
2. Alias gerekiyorsa `src/epint/__init__.py` içindeki kategori/alias çözümlemesine ekle.
3. `services/<category>.md` skill dosyası oluştur/güncelle — bu portal/airflow/dev-workspace kopyalarıyla ortak kullanılıyor, tutarlı tut.

## Test

- `tests/` — pytest (`conftest.py` fixtures; `test_auth_manager.py`, `test_request_model.py`, `test_response_model.py`, `test_swagger_model.py`, `test_category_resolution.py`, `test_datetime_utils.py`, `test_find_closest.py`, `test_method_name_decorator.py`).
- Çalıştır: `pytest`.
- Davranış değiştiren her patch karşılık gelen `test_*.py`'yi güncellemeli; CI (`ci.yml`) bunu PR'da çalıştırır.

## Versiyon

- `src/epint/modules/version/__init__.py`: `__major__` (stabil release) / `__minor__` (yeni özellik) / `__semantic__` (bug fix) / `__tag__` — elle bump, otomatik değil.
- `publish.yml` PyPI'a release tag'de yayınlar.

## Kod kalıpları

- Auth: `modules/authentication/auth_manager.py` — TGT/ST cache mantığı hassas, dokunmadan önce `architecture.md` §6 oku.
- HTTP: `modules/http_client/` — 5xx/429 retry zaten var, çift retry ekleme.
- Tarih: `modules/datetime/` — kategoriye göre format farklı (`architecture.md` §7); yeni kategori eklerken formatı doğrula, elle string formatlama yerine mevcut converter kullan.
- Yanıt: `models/response_model.py` — binary → `io.BytesIO`, `RestResponse`/GOP wrapper → `body` soyulur.
- Kategori/method çözümleme / fuzzy: `CategoryProxy`, `modules/search/find_closest.py` — yeni normalize kuralı eklerken mevcut fuzzy toleransını (0.6) bozma.
- Swagger isimlendirme: `models/swagger.py` — yeni bir "güvenilmez operationId" deseni eklerken mevcut çakışma-çözüm testlerini (`tests/test_swagger_model.py`) bozma; her yeni cleanup/disambiguation `warnings.warn` ile bildirilmeli.

## Yapma

- Pull/push öncesi `git status` kontrol etmeden `git pull`/`reset` çalıştırma (local commit varsa fast-forward bozulur).
- Path/host hardcode etme; swagger / `service_config` üzerinden çöz.
- Versiyon bump'sız feature commit atma (`publish.yml` release tag bekler).
- `dict_key_search` gibi iç kontrol bayrağı (`debug`, `allData`) çıkarımlarında fuzzy matching açma — gerçek API parametreleriyle çakışıp sessizce veri kaybına yol açabilir (bkz. `endpoint_callable.py`).
