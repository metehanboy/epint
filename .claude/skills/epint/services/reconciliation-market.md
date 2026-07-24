<!-- epint kategori referansı: reconciliation-market — hub: ../SKILL.md -->

> **Portal:** `epint` pip ile kurulur (`requirements.txt` / Dockerfile). Swagger: kurulu pakette `epint/endpoints/<category>/swagger.json` (`python -c "import epint,pathlib; print(pathlib.Path(epint.__file__).parent)"`). Bu repoda `epint/src` veya `refs/` yok. Kurallar: `../overview.md`, `../usage-conventions.md`.

# reconciliation-market — Market Servisleri

Bu kategori, piyasa katılımcılarının GÖP (Gün Öncesi Piyasası) ve GİP (Gün İçi Piyasası) uzlaştırma bildirimlerini, PTF (Piyasa Takas Fiyatı) / SMF (Sistem Marjinal Fiyatı) verilerini, fark tutarı (gap amount) hesaplarını, ikili anlaşma (bilateral contract) kayıtlarını ve avans bildirimlerini sorgulama/excel export etme servislerini kapsar. Uygulama REST üzerine kuruludur, JSON/XML isteği kabul eder; tüm endpoint'ler **POST**'tur (swagger'da GET yok). Çağıran kullanıcının EKYS'de kayıtlı ve ilgili servise yetkili bir piyasa katılımcısı organizasyonu olması gerekir.

**Önemli:** Referans dokümanı (`refs/ (epint kaynak reposu; portalda yok) — reconciliation-market/EPYS - Market Servisleri.md`, 12685 satır) **düz metin/prose içermiyor** — dosyanın tamamı tek bir fenced code block içinde, `get_organization_dam_daily_transactions` (`/v1/market/day-ahead-market/daily/list`) endpoint'inin tek bir örnek yanıtından ibaret (Ekim 2021 ayı için saatlik 744 kayıt: `mcp`/`smp` + `marketParticipationTransaction`/`efmDefaultTransaction`). Endpoint açıklaması, parametre tablosu veya başka bir örnek **yok**. Bu yüzden aşağıdaki endpoint/parametre bilgisi ağırlıklı olarak `epint/endpoints/reconciliation-market/swagger.json`'dan (alan `description`'ları ve response şemaları) çıkarılmıştır; md dosyası sadece gerçek bir response'un neye benzediğini doğrulamak için kullanılabilir.

## Ne zaman kullanılır

- Bir organizasyonun GÖP/GİP'te yaptığı eşleşmelerin miktar/tutar bilgilerini (günlük veya saatlik detay) sorgulamak veya excel'e aktarmak.
- Gün öncesi piyasasına ait PTF (piyasa takas fiyatı) verilerini listelemek.
- GÖP'te oluşan fark tutarı (fark fonu) detaylarını sorgulamak.
- Organizasyonlar arası ikili anlaşma (bilateral contract) kayıtlarını — toplam, detay veya versiyon bazında — sorgulamak/export etmek.
- Avans bildirimi (avans alacak/borç) detaylarını sorgulamak/export etmek.
- Bu kategori **yazma işlemi içermez** — hepsi sorgulama (`list`/`get`) veya excel export'tur, talep/onay/iptal gibi işlem yoktur.

## Endpoint'ler

Swagger'da kayıtlı toplam **21 endpoint**, hepsi `POST`. Üç grup (`tags`): `advance-payment`, `bilateral-contract`, `reconciliation-transaction`.

### Avans (advance-payment) — 3

| method_adı (snake_case) | HTTP | path | açıklama |
|---|---|---|---|
| `get_organization_advance_details` | POST | `/v1/advance/detail/list` | Organizasyonun avans alacak/borç **detayını** (dispatch/ödeme tarihi bazında kırılım) döner. |
| `export_organization_advance_details` | POST | `/v1/advance/export` | Aynı avans detayını excel export eder. |
| `get_organization_advance` | POST | `/v1/advance/list` | Organizasyonun avans alacak/borç **özet listesini** döner. |

### İkili Anlaşma (bilateral-contract) — 8

| method_adı (snake_case) | HTTP | path | açıklama |
|---|---|---|---|
| `list_organization_bilateral_contracts` | POST | `/v1/bilateral-contract/list` | Uzlaştırma dönemi bazında günlük toplam ikili anlaşma alış/satış miktarlarını listeler. |
| `export_organization_bilateral_contract` | POST | `/v1/bilateral-contract/export` | Aynı listeyi excel export eder. |
| `list_organization_bilateral_contract_details` | POST | `/v1/bilateral-contract/detail/list` | Organizasyonlar arası ikili anlaşma **detaylarını** (karşı taraf, kontrat id, işlem hacmi) döner. |
| `export_organization_bilateral_contract_details` | POST | `/v1/bilateral-contract/detail/export` | Aynı detay listeyi excel export eder. |
| `list_organization_bilateral_contract_versions` | POST | `/v1/bilateral-contract/version/list` | İkili anlaşma toplam kayıtlarının **versiyonlarını** listeler. |
| `export_organization_bilateral_contract_versions` | POST | `/v1/bilateral-contract/version/export` | Aynı versiyon listesini excel export eder. |
| `list_organization_bilateral_contract_detail_versions` | POST | `/v1/bilateral-contract/detail/version/list` | İkili anlaşma detay kayıtlarının versiyonlarını listeler. |
| `export_organization_bilateral_contract_detail_versions` | POST | `/v1/bilateral-contract/detail/version/export` | Aynı detay versiyon listesini excel export eder. |

### Piyasa Uzlaştırma İşlemleri — GÖP / GİP / Fark Tutarı / PTF (reconciliation-transaction) — 10

| method_adı (snake_case) | HTTP | path | açıklama |
|---|---|---|---|
| `get_organization_dam_transactions` | POST | `/v1/market/day-ahead-market/list` | GÖP Uzlaştırma Bildirimi — organizasyonun GÖP işlemlerine ait miktar/tutarı **günlük** bazda listeler; VEP temerrüt kaynaklı değerler de dahil edilebilir. |
| `export_organization_dam_transaction_details` | POST | `/v1/market/day-ahead-market/export` | Aynı günlük GÖP bildirimini excel export eder. |
| `get_organization_dam_daily_transactions` | POST | `/v1/market/day-ahead-market/daily/list` | GÖP Uzlaştırma Bildirimi — **saatlik detay** ekranı; her saat için `mcp`(PTF)/`smp`(SMF) + işlem detayı. |
| `export_organization_dam_daily_transactions` | POST | `/v1/market/day-ahead-market/daily/export` | Aynı saatlik GÖP detayını excel export eder. |
| `get_organization_gap_amount_detail` | POST | `/v1/market/day-ahead-market/gap-amount/list` | GÖP fark tutarı (fark fonu) bilgilerini günlük bazda döner. |
| `get_market_clearing_prices` | POST | `/v1/market/day-ahead-market/mcp/list` | Gün öncesi piyasasına ait PTF (piyasa takas fiyatı) listesini döner — **sayfalı değildir**. |
| `get_organization_idm_transactions` | POST | `/v1/market/intraday-market/list` | GİP'teki eşleşme sonuçlarını **günlük** bazda döner. |
| `export_organization_idm_transactions` | POST | `/v1/market/intraday-market/export` | Aynı günlük GİP sonucunu excel export eder. |
| `get_organization_daily_idm_transactions` | POST | `/v1/market/intraday-market/daily/list` | GİP'teki eşleşme sonuçlarını **saatlik** bazda döner. |
| `export_organization_daily_idm_transactions` | POST | `/v1/market/intraday-market/daily/export` | Aynı saatlik GİP sonucunu excel export eder. |

## Önemli parametreler ve gotchalar

- **Kısaltmalar**: PTF = Piyasa Takas Fiyatı (response'ta `mcp` alanı), SMF = Sistem Marjinal Fiyatı (`smp` alanı), GÖP = Gün Öncesi Piyasası (`day-ahead-market`), GİP = Gün İçi Piyasası (`intraday-market`). `efmDefault*` alanları **VEP Temerrüt Kaynaklı** işlemleri temsil eder (normal piyasa katılımı işlemlerinden ayrı bir alt-obje olarak döner), `marketParticipation*` alanları ise normal piyasa katılımcısı işlemlerini temsil eder — bu ayrım hemen hemen tüm response DTO'larında (`DailyTransactionDto`, `DamTransactionDto`, `IdmTransactionDto`, `GapAmountDailyDetailDto`, `AdvanceTotalDto`) tekrarlanır.
- **Request body şemaları büyük ölçüde ortak**: çoğu `list`/`export` endpoint'i `DeliveryDayQueryDto`/`DeliveryDayExportDto` veya `DeliveryHourlyQueryDto`/`DeliveryHourlyExportDto` kullanır — hepsinde `period`, `deliveryDayStart`, `deliveryDayEnd`, `region` alanları var; `*QueryDto` (list) varyantında ayrıca `page` var, `*ExportDto` varyantında **`page` yok** (export tüm sonucu döner, sayfalama yapılmaz).
  - `get_market_clearing_prices` istisna: `GetMarketClearingPricesRequest` sadece `effectiveDateStart`/`effectiveDateEnd`/`region` alır, `period`/`page` **yok**.
  - Avans endpoint'leri (`AdvancePaymentDetailReqDto`/`ExportReqDto`) `deliveryDay*` değil, `paymentDateStart`/`paymentDateEnd` kullanır.
  - İkili anlaşma endpoint'leri `period`/`effectiveDateStart`/`effectiveDateEnd` (toplam/versiyon) veya `period`/`effectiveDate` (detay/detay-versiyon) kullanır; `detail/list` ayrıca `targetOrganizationId` (karşı taraf filtresi), `detail/version/list` ise `buyerOrganizationId`/`sellerOrganizationId` filtreleri sunar.
- **`region` parametresi**: swagger'da `example: "TR1"` — vermezsen epint mimari kuralı gereği (§5) otomatik `'TR1'` uygular. Bölge bazlı ayrım gerekiyorsa (`TR2`, `TR3` vb.) elle geçmen gerekir, swagger'da bölge lookup/enum endpoint'i yok.
- **`page` varsayılanı**: `page` alanı olan endpoint'lerde vermezsen `{'number': 1, 'size': 1000}` uygulanır (mimari kuralı §5) — büyük veri setlerinde (örn. bir yıllık saatlik veri) tüm sonuçları almadığını unutma, `page.size` artırman veya manuel sayfalama yapman gerekebilir. `get_market_clearing_prices` ve export endpoint'lerinde `page` **yok**, bu kural onlara uygulanmaz.
- **Response şekilleri** — `RestResponse` sarmalayıcı (`status`+`correlationId`+`body`) epint tarafından otomatik soyulur (mimari kuralı §8), yani dönen değer doğrudan `body` içeriğidir:
  - Çoğu `list` endpoint'i `{"items": [...], "page": {...}, "summary": {...}}` şeklinde döner (bazılarında `summary` yok, örn. `list_organization_bilateral_contract_details`/`_detail_versions`/`_versions`).
  - `get_market_clearing_prices` **istisna**: `items`/`page` yapısı yok, düz `{"marketClearingPrices": [{"effectiveDate", "mcp", "region"}, ...]}` döner — `result["marketClearingPrices"]` ile eriş, `result["items"]` bekleme.
  - `get_organization_dam_daily_transactions` gerçek örneği (`refs/ (epint kaynak reposu; portalda yok) — .../EPYS - Market Servisleri.md`'deki tek örnekten doğrulanmış): `body["items"][i]` = `{"effectiveDate", "mcp", "smp", "marketParticipationTransaction": {"purchaseVolume","salesVolume","purchaseAmount","salesAmount"}, "efmDefaultTransaction": {...aynı alanlar...}}`, `body["page"]` = `{"number","size","total","sort"}`, `body["summary"]` = aylık toplamlar (aynı iki alt-obje).
  - `get_organization_gap_amount_detail` yanıtındaki her kayıt `totalOfPurchasingAmount`/`totalOfSalesAmount`/`purchaseMatchingQuantity`/`salesMatchingQuantity`/`purchaseGapAmount`/`salesGapAmount`/`roundingGapAmount` + `marketParticipationGapAmountDetail`/`efmDefaultGapAmountDetail` (`GapAmountDetailSummaryDto`: `purchaseCapacity`, `salesCapacity`, `purchaseGapAmount`, `salesGapAmount`, `roundingGapAmount`) içerir.
- **Export endpoint'leri binary döner**: swagger şeması `ModelAndView` gösterse de (bu sadece Spring MVC'nin export controller dönüş tipi), gerçek HTTP yanıtı XLSX dosyasıdır — epint bunu Content-Type'a göre tespit edip `io.BytesIO` olarak döner (mimari kuralı §8). `ModelAndView` şemasındaki `status`/`view`/`model` alanlarını response'ta bekleme.
- **Tarih formatı**: Bu kategori `epys` ailesinden, ISO-8601 + `+HH:MM` offset kullanılır (örn. `2021-10-01T00:00:00+03:00`); epint bunu otomatik yapar (mimari kuralı §7), elle formatlama.
- **Auth**: `gop`/`seffaflik*` değil, dolayısıyla normal `TGT` + `ST` header ikilisi eklenir (GOP'un özel `gop-service-ticket`'ı veya şeffaflığın sadece-`TGT` davranışı burada geçerli değil). Host: prod'da `epys.epias.com.tr`, test'te `epys-prp.epias.com.tr`.
- **Hata kodları**: `VAL-` ile başlayanlar istek/iş kuralı hatası (isteği/parametreleri gözden geçir), `APP-` ile başlayanlar sistem hatası (EPİAŞ ile iletişime geçilmeli). Kalıcı 401/403 alıyorsan büyük olasılıkla organizasyonun ilgili servise (avans/ikili anlaşma/GÖP-GİP uzlaştırma görüntüleme) yetkisi yoktur — ticket sorunu değildir.

## Örnek kullanım

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# GÖP saatlik uzlaştırma detayını sorgula (bölge vermezsen otomatik TR1)
result = ep.market.get_organization_dam_daily_transactions(
    deliveryDayStart="2026-07-01T00:00:00+03:00",
    deliveryDayEnd="2026-07-31T23:00:00+03:00",
)
items = result["items"]
ozet = result["summary"]
```

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# PTF (piyasa takas fiyatı) listesi — sayfalı değil, düz "marketClearingPrices" dizisi döner
result = ep.reconciliation_market.get_market_clearing_prices(
    effectiveDateStart="2026-07-01T00:00:00+03:00",
    effectiveDateEnd="2026-07-07T00:00:00+03:00",
    region="TR1",
)
for row in result["marketClearingPrices"]:
    print(row["effectiveDate"], row["mcp"])
```

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# İkili anlaşma detaylarını karşı taraf organizasyonuna göre filtrele, sayfalamayı elle kontrol et
result = ep.market.list_organization_bilateral_contract_details(
    period="2026-07-01T00:00:00+03:00",
    targetOrganizationId=123456,
    page={"number": 1, "size": 500},
)
```

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# GÖP günlük bildirimini excel'e aktar — io.BytesIO döner
xlsx_data = ep.market.export_organization_dam_transaction_details(
    deliveryDayStart="2026-07-01T00:00:00+03:00",
    deliveryDayEnd="2026-07-31T00:00:00+03:00",
    region="TR1",
)
with open("gop_uzlastirma_temmuz2026.xlsx", "wb") as f:
    f.write(xlsx_data.read())
```

## Kaynaklar

- `refs/ (epint kaynak reposu; portalda yok) — reconciliation-market/EPYS - Market Servisleri.md` (tek bir örnek response'tan ibaret, doğrulama için kullan — prose/parametre tablosu içermiyor)
- `epint/endpoints/reconciliation-market/swagger.json` (endpoint/parametre/response bilgisinin asıl kaynağı)
- Genel mimari: `../architecture.md`
- Genel kullanım kuralları: `../usage-conventions.md`
