<!-- epint kategori referansı: pre-reconciliation — hub: ../SKILL.md -->

> **Portal:** `epint` pip ile kurulur (`requirements.txt` / Dockerfile). Swagger: kurulu pakette `epint/endpoints/<category>/swagger.json` (`python -c "import epint,pathlib; print(pathlib.Path(epint.__file__).parent)"`). Bu repoda `epint/src` veya `refs/` yok. Kurallar: `../overview.md`, `../usage-conventions.md`.

# pre-reconciliation — PRE Uzlaştırma Servisleri

Bu kategori, EPİAŞ uzlaştırma sürecinin **ön (pre-settlement) aşamasında** kullanılan sayaç verilerini kapsar: onaylı sayaçların saatlik ve üç/tek zamanlı (profil) veriş-çekiş değerleri, bu verilerin GDDK (geçmişe dönük düzeltme kaydı) süreciyle güncellenmesi, UEVÇB (Uzlaştırmaya Esas Veriş-Çekiş Birimi) verileri, kırpma (overproduction) miktarları, ISKK (İletim Sistemi Kayıp Katsayısı) ve santral kapasite artışı (power-increase) kayıtları. Diğer `reconciliation-*` kategorilerinden farklı olarak bu servis dizini `pre-reconciliation` adını taşır ve README'nin `CATEGORY_ALIASES` sözlüğünde ayrı bir kısa alias'ı **yoktur** — sadece `ep.pre_reconciliation.<method_adi>(**kwargs)` ile çağrılır, `reconciliation-*` prefix-stripping mantığına da girmez (çünkü `"pre-reconciliation"` bir `"reconciliation-..."` prefix'i değildir). Kaynak swagger: `epint/endpoints/pre-reconciliation/swagger.json` (host: `epys-prp.epias.com.tr`, basePath `/pre-reconciliation/`).

## Ne zaman kullanılır

- Onaylı sayaçların saatlik veya üç/tek zamanlı (profil) veriş-çekiş verilerini listeleme/export etme.
- Saatlik veya profil sayaç verisi kaydetme/toplu kaydetme, OSF/PSF/SVL excel/format dosyası ile içeri aktarma.
- GDDK (geçmişe dönük düzeltme — retrospective) sayaç verilerini listeleme, kaydetme ve durumunu (PENDING/APPROVED/REJECTED) güncelleme.
- UEVÇB verilerini, UEVÇB'ye bağlı sayaç detaylarını, kırpma (overproduction) miktarlarını veya ISKK verilerini sorgulama/export etme.
- Santral (power plant) kapasite artışı kayıtlarını listeleme, ekleme, güncelleme, silme veya MRP dosyasıyla içe aktarma.

## Endpoint'ler

Toplam **52 endpoint**. `<method_adi>` = swagger `operationId`'sindeki `-` karakterlerinin `_` ile değiştirilmiş hâlidir (bu kategoride camelCase çevrimi gerekmez — tek istisna "Santral Kapasite Artışı" grubu, bkz. not).

**1. Lookup (1 endpoint)**

| method_adi | HTTP | path | Açıklama |
|---|---|---|---|
| `pre_reconciliation_look_up_value` | GET | `/v1/lookup/list` | Onaylı sayaçlar sayfasında kullanılan lookup (okuma tipi, kullanım tipi, okuma durumu, profil abone grubu) referans değerleri — parametresiz |

**2. Onaylı Sayaç Verileri — Sorgu (13 endpoint)**

| method_adi | HTTP | path | Açıklama |
|---|---|---|---|
| `meter_data_approved_meter_data_export` | POST | `/v1/meter-data/approved-meter-data/export` | Sayaç veri listesi export |
| `export_hourly_meter_data_details` | POST | `/v1/meter-data/approved-meter-data/hourly/export` | Saatlik sayaç verileri detay export |
| `get_hourly_meter_data_details` | POST | `/v1/meter-data/approved-meter-data/hourly/get` | Sisteme yüklenen saatlik sayaç verilerini listeler |
| `list_hourly_meter_datas` | POST | `/v1/meter-data/approved-meter-data/hourly/list` | Katılımcı/sayaç okuyan kuruma ait saatlik veriş-çekiş değerleri (toplu) |
| `meter_data_approved_meter_data_list` | POST | `/v1/meter-data/approved-meter-data/list` | Onaylı sayaçların okunma durumları |
| `get_profile_coefficient_data_detail` | POST | `/v1/meter-data/approved-meter-data/profile-coefficient/get` | Sayaç katsayı detayları |
| `export_profile_meter_data_detail` | POST | `/v1/meter-data/approved-meter-data/profile/export` | Üç/tek zamanlı sayaç veri detay export |
| `get_profile_meter_data_detail` | POST | `/v1/meter-data/approved-meter-data/profile/get` | Üç/tek zamanlı sayaç veri detayı |
| `list_profile_meter_data` | POST | `/v1/meter-data/approved-meter-data/profile/list` | Üç ve tek zamanlı sayaç verileri listeleme |
| `get_total_data` | POST | `/v1/meter-data/approved-meter-data/total` | Toplam onaylı sayaç verileri |
| `meter_data_approved_profile_meter_data_export` | POST | `/v1/meter-data/approved-profile-meter-data/export` | Sayaç veri listesi export (profil varyantı) |
| `meter_data_approved_profile_meter_data_list` | POST | `/v1/meter-data/approved-profile-meter-data/list` | Onaylı sayaçların okunma durumları (profil varyantı) |
| `export_organized_industrial_zone_meter_data` | POST | `/v1/meter-data/main-meter/export` | Organize Sanayi Bölgesi ana sayaç verileri export |
| `list_organized_industrial_zone_meter_data` | POST | `/v1/meter-data/main-meter/list` | Organize Sanayi Bölgesi ana sayaç verileri listeleme |
| `export_transmission_meter_data` | POST | `/v1/meter-data/transmission-meter-data/export` | İletim bölgelerinin okuma yükümlü sayaç verileri export |
| `list_transmission_meter_datas` | POST | `/v1/meter-data/transmission-meter-data/list` | İletim bölgelerinin okumakla yükümlü olduğu sayaç verileri |

**3. Onaylı Sayaç Verileri — Kayıt / Yükleme (7 endpoint)**

| method_adi | HTTP | path | Açıklama |
|---|---|---|---|
| `file_template` | GET | `/v1/meter-data/file/template` | OSF/PSF/SVL şablon dosyası indirir (query param `file`: `OSF`\|`PSF`\|`SVL`) |
| `save_batch_hourly_meter_data` | POST | `/v1/meter-data/hourly/batch/save` | Saatlik sayaç verileri toplu kayıt |
| `meter_data_hourly_save` | POST | `/v1/meter-data/hourly/save` | Saatlik sayaç verisi kayıt (normal onaylı) |
| `import_osf_form` | POST (multipart) | `/v1/meter-data/osf/import` | Saatlik sayaç verilerini OSF excel ile yükler |
| `save_profile_meter_data` | POST | `/v1/meter-data/profile/save` | Üç ve tek zamanlı sayaç verileri kayıt |
| `psf_import` | POST (multipart) | `/v1/meter-data/psf/import` | Üç/tek zamanlı sayaç verilerini PSF excel ile yükler |
| `svl_import` | POST (multipart) | `/v1/meter-data/svl/import` | Üç/tek zamanlı sayaç verilerini SVL formatı ile yükler |

**4. Santral Kapasite Artışı — Power Increase (5 endpoint, tag/summary yok)**

| method_adi | HTTP | path | Açıklama |
|---|---|---|---|
| `power_increase_delete` | POST | `/v1/power-increase/delete` | Kapasite artışı kaydı siler |
| `power_increase_export` | POST | `/v1/power-increase/export` | Kapasite artışı listesini export eder |
| `power_increase_import` | POST (multipart) | `/v1/power-increase/import` | MRP dosyası ile kapasite artışı içe aktarır |
| `power_increase_list` | POST | `/v1/power-increase/list` | Kapasite artışı listesi |
| `power_increase_update` | POST | `/v1/power-increase/update` | Kapasite artışı kaydını günceller |

**5. GDDK (Retrospective) Sayaç Verileri (13 endpoint)**

| method_adi | HTTP | path | Açıklama |
|---|---|---|---|
| `list_correction_data_report_export` | POST | `/v1/retrospective-meter-data/correction-data-report/export` | GDDK veri değişim (aylık) raporu export |
| `list_correction_data_report` | POST | `/v1/retrospective-meter-data/correction-data-report/list` | GDDK veri değişim raporu |
| `export_retrospective_hourly_meter_data` | POST | `/v1/retrospective-meter-data/hourly/export` | GDDK saatlik sayaç bilgileri export |
| `list_retrospective_hourly_meter_data` | POST | `/v1/retrospective-meter-data/hourly/list` | GDDK saatlik sayaç bilgileri listeleme |
| `retrospective_meter_data_hourly_save` | POST | `/v1/retrospective-meter-data/hourly/save` | GDDK saatlik sayaç verisi kayıt |
| `update_retrospective_hourly_meter_data_status` | POST | `/v1/retrospective-meter-data/hourly/status/update` | GDDK saatlik sayaç durum güncelleme (`newStatus`: PENDING/APPROVED/REJECTED) |
| `retro_import_osf_form` | POST (multipart) | `/v1/retrospective-meter-data/osf/import` | GDDK saatlik sayaç verilerini OSF excel ile yükler |
| `export_retrospective_profile_meter_data` | POST | `/v1/retrospective-meter-data/profile/export` | GDDK profil sayaç bilgileri export |
| `list_retrospective_profile_meter_data` | POST | `/v1/retrospective-meter-data/profile/list` | GDDK profil sayaç bilgileri listeleme |
| `retro_save_profile_meter_data` | POST | `/v1/retrospective-meter-data/profile/save` | GDDK profil sayaç verileri kayıt |
| `update_retrospective_profile_meter_data_status` | POST | `/v1/retrospective-meter-data/profile/status/update` | GDDK profil sayaç durum güncelleme |
| `import_psf_form` | POST (multipart) | `/v1/retrospective-meter-data/psf/import` | GDDK üç/tek zamanlı sayaç verilerini PSF excel ile yükler |
| `import_svl_form` | POST (multipart) | `/v1/retrospective-meter-data/svl/import` | GDDK saatlik sayaç verilerini SVL formatı ile yükler |

**6. UEVÇB / Settlement Point (8 endpoint)**

| method_adi | HTTP | path | Açıklama |
|---|---|---|---|
| `list_settlement_point_data` | POST | `/v1/settlement-point/data` | UEVÇB verileri listeleme |
| `settlement_point_data_export` | POST | `/v1/settlement-point/data/export` | UEVÇB verileri export |
| `export_settlement_point_meter_details` | POST | `/v1/settlement-point/meter-data/export` | UEVÇB'ye bağlı sayaçların bilgileri (path/operationId "export" ama summary metni "Listeleme" der — bkz. gotcha #8) |
| `list_settlement_point_meter_details` | POST | `/v1/settlement-point/meter-data/list` | UEVÇB'ye bağlı sayaçların veriş-çekiş değerleri |
| `list_settlement_point_oiz_data` | POST | `/v1/settlement-point/oiz/data` | UEVÇB verileri listeleme (OSB/OIZ varyantı) |
| `settlement_point_oiz_data_export` | POST | `/v1/settlement-point/oiz/data/export` | UEVÇB verileri export (OSB/OIZ varyantı) |
| `export_overproduction_data` | POST | `/v1/settlement-point/overproduction-data/export` | Kırpma miktarı export |
| `list_overproduction_data` | POST | `/v1/settlement-point/overproduction-data/list` | Kırpma miktarı listeleme |

**7. ISKK — Transmission Loss Coefficient (2 endpoint)**

| method_adi | HTTP | path | Açıklama |
|---|---|---|---|
| `export` ⚠ | POST | `/v1/transmission-loss-coefficient/export` | ISKK export — method adı tek kelime **`export`**, çok genel, dikkatli kullanın |
| `list_records` | POST | `/v1/transmission-loss-coefficient/list` | ISKK veri listeleme |

## Önemli parametreler ve gotchalar

1. **Auth normal EPYS akışıdır**: kategori adında `gop`/`seffaflik` geçmediği için her çağrıya otomatik `TGT` + `ST` header'ları eklenir (bkz. [[01-epint-architecture]] §6). GOP'a özgü `gop-service-ticket` mantığı burada devreye girmez.

2. **Dosya yükleme (OSF/PSF/SVL/MRP import) endpoint'leri kwargs ile düzgün çalışmaz**: bu endpoint'lerin swagger parametresi `"in": "formData", "type": "file"`dır, ama `RequestModel._categorize_parameters` sadece `body`/`query`/`header`/`path` konumlarını tanır — `formData` hiçbir kategoriye girmez ve **tamamen atlanır**. Sonuç olarak `file=...` kwarg'ı normal body-yoksa-kwargs-json-olur mantığına düşer ve `self._json = {"file": <...>}` gibi anlamsız bir JSON body oluşur (gerçek multipart dosya yükleme olmaz). `import_osf_form`, `psf_import`, `svl_import`, `retro_import_osf_form`, `import_psf_form`, `import_svl_form` ve `power_increase_import` için bu SDK'yı kullanmayın — gerekiyorsa `requests` ile doğrudan `files=` parametresiyle multipart istek atın (TGT/ST header'larını `epint.modules.authentication.auth_manager.Authentication` ile elle alıp geçirerek).

3. **`region` ve `page` zorunlu görünse de otomatik dolduruluyor**: `MeterDataListReqDto`, `MeterDataExportReqDto`, `SettlementPointDataListReqDto` gibi birçok DTO'da `region` swagger'da `required` olsa da, `RequestModel.DEFAULT_PARAMS` sayesinde vermezseniz otomatik `'TR1'` atanır. `page` alanı olan endpoint'lerde de vermezseniz `{'number': 1, 'size': 1000, 'limit': 1000}` uygulanır. **TR1 dışı bölge** sorguluyorsanız `region` parametresini elle geçmeyi unutmayın; büyük veri setlerinde de sayfalama (`page={'number': n, 'size': ...}`) yapmanız gerekebilir, aksi hâlde sessizce ilk 1000 kayıtla sınırlı kalırsınız.

4. **`period` / `version` / `effectiveDateStart`+`effectiveDateEnd` farklı anlamlar taşır**: `period` genelde sorgulanan dönemi/günü (date-time), `version` o dönem için üretilmiş veri versiyon damgasını, `effectiveDateStart`/`effectiveDateEnd` ise tarih aralığı filtresini ifade eder. Örn. `MeterDataListReqDto` hem `period` hem `version` ister; `HourlyMeterDataReqDto` (`list_hourly_meter_datas`) ise `effectiveDateStart`+`effectiveDateEnd`+`version` ister. Endpoint'in gerçekte hangilerini beklediğini `print(ep.pre_reconciliation.<method>)` ile kontrol edin, hepsini aynı "tarih" alanı sanıp karıştırmayın.

5. **`isRetrospective` bayrağı, ayrı GDDK endpoint grubuyla karışmasın**: `list-hourly-meter-datas`, `list-meter-datas`, `export-meter-data` gibi "normal/onaylı" endpoint'lerin request DTO'larında da bir `isRetrospective` (boolean, "GDDK mı?") alanı vardır — bu alan `true` verilerek aynı endpoint üzerinden GDDK verisi de sorgulanabilir. Bu, ayrı `/v1/retrospective-meter-data/*` endpoint grubunun yerine geçmez; ikisi paralel iki mekanizmadır, hangisini kullandığınızı bilinçli seçin.

6. **Saatlik toplu kayıt yapısı (`save_batch_hourly_meter_data` / `HourlyMeterDataBatchSaveDto`)**: gövde `meters: [{eic, period, datas: [{period, supply, withdrawal}]}]` şeklindedir. Dıştaki `meters[].period` bir **tarih** (date-time, örn. ayın ilk günü), içteki `datas[].period` ise o dönem içindeki **sıralı saat indeksidir (integer, 1'den başlar)** — 31 günlük bir ay için 744'e (31×24) kadar gidebilir.

7. **GDDK durum güncelleme enum'u sınırlı**: `RetrospectiveMeterDataUpdateDto.newStatus` sadece `PENDING`, `APPROVED`, `REJECTED` değerlerini kabul eder (`update_retrospective_hourly_meter_data_status` / `update_retrospective_profile_meter_data_status`). Body `items: [{id, newStatus}]` listesi şeklindedir — toplu güncelleme yapılabilir.

8. **`export_settlement_point_meter_details` isim/işlev tutarsızlığı**: operationId `export-settlement-point-meter-details` ve path `.../meter-data/export` olsa da swagger summary metni "UEVÇB'ye Bağlı Sayaçların **Bilgilerini Listeleme** Servisi" der; response şeması ise diğer export'larda olduğu gibi `ModelAndView`. Gerçek "listeleme" (veriş-çekiş değerleri) işlevi ayrı bir endpoint olan `list_settlement_point_meter_details` (`.../meter-data/list`, `RestResponseSettPointMeterDataDetailRespDto` döner)'dedir — isimlere güvenmeyin, `print()`/`debug=True` ile response şemasını doğrulayın.

9. **SVL formatının hedef veri tipi canlı/GDDK arasında tutarsız görünüyor**: `/v1/meter-data/svl/import` (canlı) summary'si "**Üç ve Tek Zamanlı** Sayaç Verilerini SVL ... Yükleme" der, ama `/v1/retrospective-meter-data/svl/import` (GDDK) summary'si "**Saatlik** Sayaç Verilerini SVL ... Yükleme" der. Bu muhtemelen kaynak swagger'daki bir dokümantasyon tutarsızlığıdır — hangi formatı kullanacağınızdan önce path'e güvenin, gerekirse EPİAŞ ile teyitleşin.

10. **Referans md dosyası prose/parametre tablosu içermez**: `refs/ (epint kaynak reposu; portalda yok) — pre-reconciliation/EPYS - PRE Uzlaştırma Servisleri.md` (~7459 satır) baştan sona **tek bir kod bloğu** içinde tek bir örnek JSON'dur (2 sayaç, her biri 744 saatlik `datas` kaydı — muhtemelen `save_batch_hourly_meter_data` isteğine ait bir örnek). Diğer 51 endpoint için parametre/response bilgisi yalnızca `swagger.json`'dan çıkarılabilir; bu dosyayı "kullanım kılavuzu" olarak prose beklemeden, sadece toplu-kayıt gövde yapısı örneği olarak kullanın.

> **Not (çözüldü):** Bu kategoride önceden `export_meter_data`, `list_meter_datas`, `save_hourly_meter_data`, `export_settlement_point_data` operationId'leri birden fazla endpoint'te tekrarlanıyordu ve yalnızca biri erişilebilirdi (diğeri sessizce gölgeleniyordu); `power_increase_*` grubu da NestJS controller isimlendirmesiyle çok uzun/tahmin edilemez adlara sahipti. `epint/models/swagger.py`'deki `SwaggerModel` artık operationId çakışmalarını ve "güvenilmez" (Controller_x_VERB / şablon / bare-path) operationId'leri path'ten türetilen kısa, benzersiz isimlerle çözüyor — yukarıdaki tablodaki tüm adlar artık ayrı ayrı ve dolaysız erişilebilir.

## Örnek kullanım

```python
import epint as ep

ep.set_auth(username, password)
ep.set_mode("prod")

# 1) Belirli bir dönemde onaylı saatlik sayaç verilerini listele (sayfalayarak)
page_number = 1
all_items = []
while True:
    resp = ep.pre_reconciliation.list_hourly_meter_datas(
        effectiveDateStart="2024-01-01T00:00:00+03:00",
        effectiveDateEnd="2024-01-31T00:00:00+03:00",
        version="2024-02-05T00:00:00+03:00",
        isRetrospective=False,
        page={"number": page_number, "size": 1000},
    )
    all_items.extend(resp["items"])
    total = resp["page"]["total"]
    if page_number * 1000 >= total:
        break
    page_number += 1

# 2) Saatlik sayaç verisini toplu kaydet — meters[].period = ay başlangıcı,
#    datas[].period = ay içindeki sıralı saat indeksi (1..744)
result = ep.pre_reconciliation.save_batch_hourly_meter_data(
    meters=[
        {
            "eic": "40Z000000000001P",
            "period": "2024-01-01T00:00:00+03:00",
            "datas": [
                {"period": h, "supply": 0, "withdrawal": 8360.0}
                for h in range(1, 745)
            ],
        }
    ]
)
print(result["successSize"], "kayıt başarıyla eklendi")

# 3) GDDK saatlik sayaç kaydının durumunu toplu onayla
ep.pre_reconciliation.update_retrospective_hourly_meter_data_status(
    items=[
        {"id": 12345, "newStatus": "APPROVED"},
        {"id": 12346, "newStatus": "REJECTED"},
    ]
)

# 4) ISKK verilerini XLSX olarak export et (io.BytesIO döner)
xlsx_data = ep.pre_reconciliation.list_records(
    effectiveDateStart="2024-01-01T00:00:00+03:00",
    effectiveDateEnd="2024-01-31T00:00:00+03:00",
    region="TR1",
)
```

## Kaynaklar

- `refs/ (epint kaynak reposu; portalda yok) — pre-reconciliation/EPYS - PRE Uzlaştırma Servisleri.md` — tek örnek JSON (saatlik toplu kayıt gövdesi), bkz. gotcha #12.
- `epint/endpoints/pre-reconciliation/swagger.json` — asıl OpenAPI 2.0 kaynağı (paket bu kopyayı runtime'da yükler).
- `epint/models/swagger.py` — operationId → method_adi dönüşümü ve çakışma (gotcha #2) burada gerçekleşir.
- `epint/models/request_model.py` — `region`/`page` default değerleri, `formData` parametrelerinin işlenmediği yer (gotcha #4, #5).
- Genel mimari: [[01-epint-architecture]]. Kullanım kuralları: [[02-epint-usage-conventions]]. Kategori/alias eşlemesi: [[00-epint-overview]].
