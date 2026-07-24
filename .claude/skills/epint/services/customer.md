<!-- epint kategori referansı: customer — hub: ../SKILL.md -->

> **Portal:** `epint` pip ile kurulur (`requirements.txt` / Dockerfile). Swagger: kurulu pakette `epint/endpoints/<category>/swagger.json` (`python -c "import epint,pathlib; print(pathlib.Path(epint.__file__).parent)"`). Bu repoda `epint/src` veya `refs/` yok. Kurallar: `../overview.md`, `../usage-conventions.md`.

# customer — Abone Servisleri

EPYS Abone (customer) servisleri, bir tüketim noktasına (EIC / consumptionPointId) bağlı abone kayıtlarının (portföy kayıtlarının) yönetimi için kullanılır: yeni abone kaydı oluşturma, güncelleme, pasifleştirme, sorgulama/listeleme ve kayıt tarihçesi görüntüleme. Abone alanlarındaki (durum, kategori, tarife grubu vb.) sayısal referans değerlerini çözmek için kullanılan "çoklu seçim" (lookup) servisleri de bu kategoride yer alır. Servis JSON/XML istek kabul eder, isteğe göre JSON/XML cevap döner. Bu, `gop`/`seffaflik` ailesinden değil, normal bir `epys` servisidir — TGT + ST header'ları epint tarafından otomatik eklenir (bkz. [[01-epint-architecture]] §6).

## Ne zaman kullanılır

- Bir tüketim noktasına bağlı yeni abone kaydı oluşturmak, mevcut kaydı güncellemek veya pasife almak.
- Portföyünüzdeki (veya sorumlu olduğunuz) aboneleri filtreleyip listelemek, kayıt sayısını almak.
- Bir abone kaydının geçmişte yapılmış değişikliklerini (tarihçe) sorgulamak.
- Yeni bir abone kaydı yapmadan önce geçerlilik/çakışma kontrolü yapmak (pre-check, portföyde önceden tanımlı abonelik durumu kontrolü).
- `customerStatus`, `categoryType`, `updateReason`, `tariffGroup`, `tariffTimeType`, `myPortfolioState`, `bilateralAgreementState`, `processType` gibi alanlarda kullanılan sayısal lookup ID'lerinin insan-okunur karşılığını öğrenmek.

## Endpoint'ler

Toplam 11 endpoint (swagger.json'daki tüm `operationId`'ler):

| method_adı (`ep.customer.<...>`) | HTTP | path | Açıklama |
|---|---|---|---|
| `available_lookups` | GET | `/v1/lookup` | Kullanılabilir lookup anahtarlarını listeler. **Yetki gerektirmez.** |
| `lookup_query` | POST | `/v1/lookup/query` | Belirli bir `lookupType` için id/value/localization listesini getirir. **Yetki gerektirmez.** |
| `customer_register` | POST | `v1/customer/register` | Yeni abone kaydı oluşturur. |
| `customer_update` | POST | `v1/customer/update` | Mevcut abone kaydını günceller. |
| `customer_passivate` | POST | `v1/customer/passivate-customer` | Aktif bir aboneyi pasife alır. |
| `customer_pre_check` | POST | `v1/customer/pre-check` | Kayıt öncesi geçerlilik/portföy çakışma kontrolü yapar (önyüz ön-validasyonu). |
| `get_state_customer_predefined_in_portfolio` | POST | `v1/customer/get-state-customer-predefined-in-portfolio` | Bu kayıttan etkilenip güncellenecek başka bir abonelik olup olmadığını kontrol eder. |
| `customer_query_history` | POST | `v1/customer/history` | Abone üzerindeki değişikliklerin tarihçesini sorgular. |
| `customer_query` | POST | `v1/customer/query` | Aboneleri toplam kayıt sayısıyla birlikte, sayfalı sorgular. |
| `customer_query_without_count` | POST | `v1/customer/query-without-count` | Aboneleri toplam kayıt sayısı olmadan, sayfalı sorgular (büyük veri setinde `customer_query`'e göre daha hafif). |
| `customer_query_count` | POST | `v1/customer/query-count` | Sorgu kriterlerine uyan kayıt sayısını döner, sayfalama parametresi almaz. |

## Önemli parametreler ve gotchalar

- **Zorunlu alanlar** (swagger `required`):
  - `customer_register`: `categoryType`, `customerNo`, `startDate`, `title`.
  - `customer_update`: `customerId`.
  - `customer_passivate`: `customerId`, `statusId`.
  - `customer_query_history`: `customerId`.
  - `customer_pre_check`: `startDate`.
  - `get_state_customer_predefined_in_portfolio`: `categoryType`, `customerNo`.
  - `lookup_query`: `lookupType`.
  - `customer_query`, `customer_query_without_count`, `customer_query_count`: hiçbir alan zorunlu değil, tümü opsiyonel filtre.

- **Lookup ID'leri ezberleme/hardcode etme.** `categoryType`, `customerStatus`/`statusId`, `updateReason`, `tariffGroup`, `tariffTimeType`, `myPortfolioState`, ve query'lerdeki `status`/`category` dizileri gerçek enum değil, lookup tablosundaki sayısal ID'lerdir. Doğru akış: önce `ep.customer.available_lookups()` ile mevcut anahtarları al (bilinen anahtarlar: `categoryType`, `bilateralAgreementState`, `updateReason`, `customerStatus`, `myPortfolioState`, `processType`), sonra `ep.customer.lookup_query(lookupType=<anahtar>)` ile id → value eşlemesini çek. Kılavuzdaki örneklerden bilinen bazı değerler: `categoryType` id=1 → `"REAL_PERSON"`; `customerStatus` id=1 → `"ACTIVE"`; `updateReason` id=1 → `"NEW"` — ama bunlar ortama göre değişebilir, canlı sorguyu tercih et.

- **`consumptionPointEicCode` / `consumptionPointId` birbirini dışlar.** `customer_register`, `customer_query`, `customer_query_without_count`, `customer_query_count` şemalarının hepsinde: biri gönderilirse diğeri **gönderilmemelidir** (swagger alan açıklaması).

- **Sorgu tarihleri kayıt tarihine referans eder.** `customer_query`/`customer_query_without_count`/`customer_query_count`'taki `startDate`/`endDate`, abonenin portföy başlangıç/bitiş tarihi değil, **abone kaydının oluşturulma tarihi**ne (yanıttaki `createDate`) göre filtreler — kılavuzda açıkça belirtiliyor. Ayrı bir `period` alanı da vardır (farklı bir dönem filtresi, birbirine karıştırma).

- **Sayfalama/sıralama** (`customer_query`, `customer_query_without_count`, `customer_query_history`): `page.number` / `page.size` / `page.sort.field` / `page.sort.direction` (`"ASC"`/`"DESC"`, enum). Yanıttaki `sortableFields` (örn. `["startDate"]`) hangi alanlarla sıralama yapılabileceğini gösterir — listede olmayan bir `field` ile sıralama isteme. Vermezsen mimari kuralındaki genel `DEFAULT_PARAMS` devreye girer (`page.number=1`, `page.size=1000`) — büyük portföylerde tek çağrıda tüm sonuçları almadığını unutma.
  - `customer_query_count` **hiç sayfalama parametresi almaz**, sadece `count` alanı içeren bir sonuç döner.
  - `customer_query` zaten `page.total` içinde toplam sayıyı döndürür; ayrı `customer_query_count` çağrısına genelde sadece sayım tek başına gerekliyse (öğe listesi gerekmiyorsa) ihtiyaç var.

- **Yetkilendirme servise göre değişir.** Her yazma/okuma servisinin kendine özgü EPYS yetkisi vardır (örnekler: `ST - Abone İşlemleri - Abone Kaydı Yap`, `ST - Abone İşlemleri - Abone Kaydı Güncelle`, `ST - Abone İşlemleri - Abone Listele`, `ST - Abone İşlemleri - Abone Portföy Kontrolü Yap`). `available_lookups` ve `lookup_query` **hiçbir yetki gerektirmez**; diğer tüm `customer_*` endpoint'leri kullanıcının ilgili yetkiye sahip olmasını gerektirir. Kalıcı 401/403 alıyorsan mimari kuralındaki genel not burada da geçerli: sorun genelde ticket değil, bu spesifik yetkinin eksik olmasıdır.

- **Kılavuz örneğiyle swagger arasında tutarsızlık var** — `customer_register` için kılavuzdaki örnek istek `agreementChecked: 1` kullanıyor, ama swagger'daki gerçek alan adı `isAgreementChecked` (`boolean`). Aynı örnekte swagger şemasında hiç tanımlı olmayan `byPassUpdatingOfAllCurrentCustomersInPortfolio` alanı da geçiyor. Doğru/güncel alan adı için swagger'ı esas al (`print(ep.customer.customer_register)`), fuzzy param matching'e güvenme.

- `authorizedPerson1Name`/`authorizedPerson1No` (ve 2. kişi eşdeğerleri) swagger'da zorunlu değil ama açıklamada "abone tipine göre zorunluluk arz edebilir" deniyor — `categoryType`'a göre (örn. gerçek kişi/tüzel kişi) sunucu tarafında zorunlu olabilir; 400 hatası alırsan önce bu alanları doldurmayı dene.

- **Yanıt sarmalayıcısı zaten soyulmuş gelir.** Swagger'daki ham şema `RestResponse*` (`status`/`correlationId`/`errors`/`body.content`) şeklindedir, ama epint bunu otomatik çıkarır (mimari kuralı §8) — `ep.customer.<method>(...)` çağrısının dönüş değeri doğrudan `body.content` ile eşdeğerdir; `result["body"]["content"]` diye erişmeye çalışma.
- `customer_passivate`/`customer_update` gibi işlemler `{"completed": true/false}` (`BooleanDTO`) döner — sonucu `result["completed"]` (veya nesne ise `result.completed`) ile kontrol et.

## Örnek kullanım

```python
import epint as ep

ep.set_auth("kullanici", "sifre")
ep.set_mode("prod")

# 1) Lookup akışı: önce anahtarları, sonra kategori ID'sini öğren, abone kaydet
category_types = ep.customer.lookup_query(lookupType="categoryType")
real_person_id = next(
    v["id"] for v in category_types["values"] if v["value"] == "REAL_PERSON"
)

new_customer = ep.customer.customer_register(
    categoryType=real_person_id,
    customerNo="12345678901",
    title="Ahmet Yılmaz",
    startDate="2026-01-01T00:00:00+03:00",
    consumptionPointEicCode="40X000000000002C",
    isAgreementChecked=True,
)
print(new_customer["id"], new_customer["customerStatus"]["value"])
```

```python
import epint as ep

ep.set_auth("kullanici", "sifre")

# 2) Sayfalı/sıralı abone sorgulama — status/category lookup ID listeleri ile filtre
result = ep.customer.customer_query(
    status=[1],     # ör. customerStatus lookup id'si (ACTIVE)
    category=[1],   # ör. categoryType lookup id'si (REAL_PERSON)
    startDate="2026-01-01T00:00:00+03:00",  # abonenin KAYIT (createDate) tarihine göre filtreler
    endDate="2026-06-30T00:00:00+03:00",
    page={"number": 1, "size": 50, "sort": {"field": "startDate", "direction": "DESC"}},
)

for item in result["items"]:
    print(item["id"], item["customerNo"], item["title"])

print("toplam kayıt:", result["page"]["total"])
```

```python
import epint as ep

ep.set_auth("kullanici", "sifre")

# 3) Aboneyi pasife alma — statusId'yi lookup'tan bulup gönder
passive_status_id = next(
    v["id"]
    for v in ep.customer.lookup_query(lookupType="customerStatus")["values"]
    if v["value"] == "PASSIVE"
)
result = ep.customer.customer_passivate(customerId=98765, statusId=passive_status_id)
print(result["completed"])
```

## Kaynaklar

- `refs/ (epint kaynak reposu; portalda yok) — customer/EPYS - Abone Servisleri.md`
- `epint/endpoints/customer/swagger.json`
