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
- **`Endpoint.__call__` HER çağrıda YENİ bir `Authentication(...)` nesnesi yaratır** (satır
  `auth = Authentication(epint._username, epint._password, target_service, runtime_mode)`) -
  paylaşılan/cache'lenmiş TEK bir instance YOK. Tek-thread kullanımda sorun değil, ama
  **çoklu-thread'den (ör. `ThreadPoolExecutor` ile paralel istek atan çağıran kod) eş-zamanlı
  çağrılarda** `Authentication.__init__` → `_setup_directories()` çalışır - bkz. GOTCHA aşağıda.

### GOTCHA: paralel/çoklu-thread'den çağrıda her thread kendi TGT'sini yaratıyordu (2026-07-28, canlı testte bulundu, DÜZELTİLDİ)

`epint.set_auth()` sonrası aynı process içinden (aynı kimlik bilgileriyle) 20 thread aynı
seffaflik-electricity servisini `ThreadPoolExecutor` ile eş-zamanlı çağırınca, log'da aynı
saniyede ~20 kez `"Yeni TGT oluşturuldu"` görülüyordu - beklenen: sadece İLK thread TGT
yaratmalı (TGT şeffaflık için 2 saat geçerli), diğerleri onu reuse etmeliydi.

**Kök neden**: `Endpoint.__call__` her çağrıda yeni `Authentication(...)` yarattığı için (§6
yukarıda), her thread kendi `_setup_directories()`'ini KİLİTSİZ çalıştırıyordu:
`_has_permission_issues`/`_reset_temp_directory` (paylaşılan `.epint_test` dosyasında,
`shutil.rmtree` ile TÜM temp_dir'i - tgt_dir + `.lock` dosyaları DAHİL - silebiliyordu) ve
`_test_file_permissions` (tgt_dir/st_dir'i KİLİTSİZ okuyup, okuma hatasında `os.remove` ile
siliyordu - başka bir thread'in AYNI ANDA `_store_ticket()` ile yazdığı dosyayla yarışabiliyordu).
`get_tgt()`'in KENDİ kilidi (`_locked`, `fcntl.flock`) doğruydu ama bu kilide gelmeden ÖNCEKİ
adımlar kilidin dayandığı dosya/lock-inode sürekliliğini bozabiliyordu - sonuç: her thread
"benim için geçerli TGT yok" sanıp ayrı ayrı TGT yaratıyordu.

**Fix**: `_setup_directories()`'in yıkıcı permission-check/reset kısmı artık process başına
EN FAZLA BİR KEZ çalışır (double-checked locking: `_setup_lock` + `_verified_temp_dirs` set'i,
modül seviyesinde) - ilk `Authentication()` bu adımı tamamladıktan sonra aynı process içindeki
(thread farketmeksizin) sonraki construction'lar bu kısmı atlar. `_test_file_permissions` artık
tgt_dir/st_dir'i `get_tgt()`/`_store_ticket()` ile AYNI kilit (`_locked(self._tgt_lock_path)` /
`_locked(self._st_lock_path)`) altında okuyor - başka bir thread'in mid-write dosyasıyla artık
yarışmıyor. Regresyon testi: `tests/test_auth_manager.py`
`test_concurrent_authentication_construction_creates_single_tgt` (20 eş-zamanlı AYRI
`Authentication()` construction'ı simüle eder, fix öncesi kod bu testte `FileNotFoundError` ile
patlıyordu, fix sonrası tek bir TGT üretildiğini doğruluyor).

**Kullanım tarafı not**: bu fix `epint` İÇİNDE - tüketici kod (ör. Airflow DAG'ları) tarafında
paralel/`ThreadPoolExecutor` ile çekim yapan mevcut desenler (bkz. airflow reposu
`dags/pmnt/_seffaflik_generation_common.py` `AdaptiveRateLimiter`) bu fix'i içeren epint
sürümüne güncellenince otomatik faydalanır, ekstra kod değişikliği gerekmez.

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
