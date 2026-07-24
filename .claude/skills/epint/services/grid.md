<!-- epint kategori referansı: grid — hub: ../SKILL.md -->

> **Portal:** `epint` pip ile kurulur (`requirements.txt` / Dockerfile). Swagger: kurulu pakette `epint/endpoints/<category>/swagger.json` (`python -c "import epint,pathlib; print(pathlib.Path(epint.__file__).parent)"`). Bu repoda `epint/src` veya `refs/` yok. Kurallar: `../overview.md`, `../usage-conventions.md`.

# grid — Sayaç ve Ölçüm Noktası Servisleri

EPYS'in "grid" kategorisi (`ep.grid.<method_adi>(**kwargs)`), dağıtım şebekesindeki **sayaçlar** (meter) ve **ölçüm noktaları** (ec-meter — "ec" = "exceptional case"/tüketim noktası) ile bunların **portföy** (tedarikçi/organizasyon ilişkisi) ve **bölge/trafo merkezi** ilişkilendirmelerini yönetir. Kaynak: `epint/endpoints/grid/swagger.json` (basePath `/grid`, host `epys-prp.epias.com.tr`), Türkçe kılavuz: `refs/ (epint kaynak reposu; portalda yok) — grid/Sayaç ve Ölçüm noktası Servisleri.md`.

Bu kategori normal bir **epys** ailesi servisidir (gop/şeffaflık değil) — `ep.set_auth()` ile TGT + `ST` header'ları epint tarafından otomatik eklenir, ekstra bir şey yapmana gerek yok (bkz. [[01-epint-architecture]] §6).

## Ne zaman kullanılır

- Sayaç (`meter*`) veya ölçüm noktası (`ec-meter*`) kaydı oluşturma/güncelleme/durum değiştirme.
- Sayaç, ölçüm noktası, LÜY sayaç, portföy, bölge veya trafo merkezi verilerini sorgulama/dışa aktarma.
- Bir kaydın hangi organizasyona/portföye ait olduğunu veya sayaç okuma yükümlülüğünü sorgulama.
- Filtre alanlarında kullanılacak enum/lookup değerlerini (durum tipi, tarife tipi, bölge tipi vb.) keşfetme.

## Endpoint'ler

Toplam **36 endpoint**, 7 controller altında (`ecMeterController`, `helperController`, `meterController`, `portfolioController`, `regionController`, `substationController`, `ulegMeterController`). Aşağıda mantıksal gruplara ayrılmıştır.

### Ölçüm noktası (ec-meter) yönetimi — 9

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `ec_meter_query` | POST | `/v1/ec-meter/query` | Ölçüm noktası sorgulama (sayfalı liste) |
| `ec_meter_count` | POST | `/v1/ec-meter/count` | Toplam ölçüm noktası **kayıt** adedi |
| `ec_meter_distinct_count` | POST | `/v1/ec-meter/count-meter` | Toplam **tekil** ölçüm noktası adedi |
| `ec_meter_export` | POST | `/v1/ec-meter/export` | Ölçüm noktası dışa aktarma (tam alan seti) |
| `ec_meter_plain_export` | POST | `/v1/ec-meter/plain-export` | Ölçüm noktası dışa aktarma (sade/hızlı — lookup açıklaması, isim vb. içermez) |
| `ec_meter_fetch_export_offset_ids` | POST | `/v1/ec-meter/fetch-export-offset-ids` | export/plain-export için gerekli `offsetId` listesini üretir |
| `ec_meter_save` | POST | `/v1/ec-meter/save` | Yeni ölçüm noktası kaydı |
| `ec_meter_update` | POST | `/v1/ec-meter/update` | Mevcut ölçüm noktasını (kısmi) güncelleme |
| `ec_meter_status_update` | POST | `/v1/ec-meter/status-update` | Ölçüm noktası durumunu güncelleme |

### Sayaç (meter) sorgulama/dışa aktarma — 7

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `meter_query` | POST | `/v1/meter/query` | Sayaç sorgulama (sayfalı liste) |
| `meter_query_main_meter` | POST | `/v1/meter/query-main-meter` | Ana sayaç sorgulama |
| `meter_count` | POST | `/v1/meter/count` | Toplam sayaç **kayıt** adedi |
| `meter_distinct_count` | POST | `/v1/meter/count-meter` | Toplam **tekil** sayaç adedi |
| `meter_export` | POST | `/v1/meter/export` | Sayaç dışa aktarma (tam alan seti) |
| `meter_plain_export` | POST | `/v1/meter/plain-export` | Sayaç dışa aktarma (sade/hızlı) |
| `meter_fetch_export_offset_ids` | POST | `/v1/meter/fetch-export-offset-ids` | export/plain-export için gerekli `offsetId` listesini üretir |

Sayaç (`meter*`) için bu kategoride kayıt oluşturma/güncelleme endpoint'i **yoktur** — sadece sorgulama/dışa aktarma vardır; yeni kayıt/güncelleme sadece ölçüm noktası (`ec_meter_*`) ve LÜY sayaç (`uleg_meter_*`, sadece güç güncelleme) tarafında mevcuttur.

### LÜY sayaç (Lisanssız Üretim Yönetmeliği kapsamı, net-metering) — 4

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `uleg_meter_query` | POST | `/v1/uleg-meter/query` | LÜY sayaç sorgulama |
| `uleg_meter_export` | POST | `/v1/uleg-meter/export` | LÜY sayaç dışa aktarma (tam alan seti) |
| `uleg_meter_plain_export` | POST | `/v1/uleg-meter/plain-export` | LÜY sayaç dışa aktarma (sade — lookup/isim alanları yok, büyük hacimli indirmede tercih edilmeli) |
| `uleg_meter_service_power_update` | POST | `/v1/uleg-meter/service-power-update` | LÜY sayacının işletmedeki gücünü (`servicePower`) güncelleme |

### Portföy / talep / okuma yükümlülüğü — 3

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `portfolio_query` | POST | `/v1/portfolio/query` | Sayacın portföy hareketlerini sorgulama |
| `reading_portfolio_query` | POST | `/v1/reading-portfolio/query` | Sayaç verisi yükleme yükümlülüğü (okuma organizasyonu) sorgulama |
| `exceptional_meter_portfolio_query` | POST | `/v1/exceptional-meter-portfolio/query` | Dönem içinde yaptırım kaynaklı portföy boşaltmada talep edilebilecek sayaçların listesi |

### Bölge / trafo merkezi — 5

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `region_query` | POST | `/v1/region/query` | Teklif bölgesi sorgulama |
| `region_field_fetch` | GET | `/v1/region-field/fetch` | Bölge sorgu/sıralama alan adlarını listeler |
| `region_conf_field_fetch` | GET | `/v1/region-conf-field/fetch` | Bölge konfigürasyon alan adlarını listeler |
| `substation_query` | POST | `/v1/substation/query` | Trafo merkezi sorgulama |
| `substation_field_fetch` | GET | `/v1/substation-field/fetch` | Trafo merkezi alan adlarını listeler |

### Yardımcı / lookup (enum keşfi) — 8

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `available_lookups` | GET | `/v1/lookup` | Mevcut tüm lookup (çoklu seçim) anahtarlarının listesi |
| `lookup_query` | POST | `/v1/lookup/query` | Bir `lookupType` için detay değerlerini getirir |
| `meter_field_fetch` | GET | `/v1/meter-field/fetch` | Sayaç sorgu/sıralama alan adlarını listeler |
| `meter_reading_type_fetch` | GET | `/v1/meter/reading-type/fetch` | Sayaç okuma tiplerini listeler |
| `meter_supply_position_type_fetch` | GET | `/v1/meter/supply-position-type/fetch` | Sayaç veriş pozisyon tiplerini listeler |
| `meter_usage_type_fetch` | GET | `/v1/meter/usage-type/fetch` | Sayaç kullanım tiplerini listeler (swagger `summary` alanı hatalı şekilde "veriş pozisyon" olarak kopyalanmış, path `usage-type`'a güven) |
| `meter_withdraw_position_type_fetch` | GET | `/v1/meter/withdraw-position-type/fetch` | Sayaç çekiş pozisyon tiplerini listeler |
| `profile_subscription_group_fetch` | GET | `/v1/profile-subscription-group/fetch` | Profil abone grubu tiplerini listeler |

Tam parametre/response şemasını görmek için (özellikle save/update body'lerindeki uzun zorunlu alan listeleri) çağırmadan önce `print(ep.grid.<method>)` çalıştır.

## Önemli parametreler ve gotchalar

- **Export sayfalama, query sayfalamasından farklıdır.** `*_query`/`*_count` endpoint'leri klasik `page: {number, size, sort}` kullanır (bkz. [[01-epint-architecture]] §5 varsayılanları: `{'number':1,'size':1000,'limit':1000}`). Ama `*_export`/`*_plain_export` endpoint'leri **`offsetIdStart`/`offsetIdEnd`** ile sayfalanır — `number`/`size` göndersen de işe yaramaz:
  1. Önce aynı filtrelerle ilgili `*_fetch_export_offset_ids` çağrısını yap (`page={'limit': 1000}` gibi bir limit ver) — cevapta `body.content.offsetIds` adında sıralı bir tam sayı listesi döner.
  2. Bu listeden ardışık ikili değerleri `page={'offsetIdStart': ..., 'offsetIdEnd': ...}` olarak export çağrısına ver; her sayfa bağımsız/paralel çağrılabilir.
  3. Son sayfada `offsetIdEnd=None` bırakılır (kalan tüm kayıtları döndürür). offset listesi hesaplandıktan sonra kayıtlar değişirse son sayfa `limit`'ten fazla kayıt içerebilir — normaldir.
  - `ec_meter_export`/`ec_meter_plain_export` ↔ offset kaynağı `ec_meter_fetch_export_offset_ids`; `meter_export`/`meter_plain_export` ↔ `meter_fetch_export_offset_ids`; `uleg_meter_export`/`uleg_meter_plain_export` ↔ `uleg_meter_fetch_export_offset_ids` (kendi çiftini kullan, karıştırma).
- **`plain` varyantları** (`ec_meter_plain_export`, `meter_plain_export`, `uleg_meter_plain_export`) lookup açıklaması/isim/abone gibi türetilmiş alanları içermez — sadece ham sayaç alanlarını döner; bu yüzden normal export'a göre daha hızlıdır ve büyük hacimli indirmelerde tercih edilmelidir.
- **Uzun/karmaşık parametre adı örneği**: `readingOrganizationId` (Sayaç Okuyan Kurum ID) hemen hemen her query/export DTO'sunda tekrar eder; epint'in fuzzy param eşleştirmesi sayesinde `readingorganizationid` / `reading_organization_id` gibi varyasyonlar da kabul edilir, ama swagger'daki gerçek camelCase adı budur.
- **Kısmi güncelleme + `deletedFields`**: `ec_meter_update` gibi update endpoint'lerinde sadece değişen alanları gönder; bir alanı **silmek/null'lamak** için o alanı body'de göndermek yetmez, alan adını ayrıca `deletedFields: ["addressCode", ...]` listesine eklemen gerekir.
- **`ec_meter_save` çok sayıda zorunlu alan ister** (`EcMeterRequestDto.required`): `address`, `annualAverageConsumption`, `annualEstimatedConsumptionT1/T2/T3`, `busbarVoltageTypeId`, `consumptionPointTypeId`, `contractPower`, `descriptions`, `districtId`, `effectiveDateStart`, `exceptionalSubstationStatus`, `facilityTypeId`, `loadProfileFeature`, `mainTariffGroupId`, `meteringVoltageTypeId`, `profileSubscriptionGroupId`, `readingDataTypeId`, `readingOrganizationId`, `readingPeriod`, `readingTypeId`, `remoteReadingStatusId`, `substationId`, `tariffClassTypeId`, `uniqueCode`, `usageStatusTypeId`, `withdrawPositionTypeId`. `ec_meter_status_update` sadece `descriptions` ister (+ `effectiveId`/`statusId` mantıken zorunlu). `ec_meter_update` sadece `effectiveDateStart` + `effectiveId` şemada zorunlu, gerisi opsiyonel/kısmi.
- **`descriptions` alanı** her save/update body'sinde `[{"language": "tr-TR", "description": "..."}]` şeklinde bir `DescriptionDto` dizisidir — düz string kabul etmez.
- **Çoğu `*_id` parametresi bir lookup değeridir** (statusId, districtId, facilityTypeId, tariffClassTypeId, withdrawPositionTypeId vb.). Elle sayı tahmin etmek yerine önce `available_lookups()` ile mevcut `lookupType` anahtarlarını, sonra `lookup_query(lookup_type='...')` ile o tipin geçerli ID/değer eşlemesini çek. Sayaç'a özgü tip listeleri için ayrıca `meter_reading_type_fetch`, `meter_supply_position_type_fetch`, `meter_usage_type_fetch`, `meter_withdraw_position_type_fetch`, `profile_subscription_group_fetch` doğrudan kullanılabilir.
- **Yetki (authorization) çok granüler**: Kılavuzda her endpoint için ayrı bir "Yetkiler" listesi var (örn. `ST - Ölçüm Noktası Manuel Kayıt - Manuel Kayıt Yap`). Sürekli 401/403 alıyorsan TGT/ST sorunu değil, kullanıcı hesabına o spesifik işlem için yetki tanımlanmamış olabilir — bkz. [[02-epint-usage-conventions]] hata yönetimi notu.
- **Katılımcı tipine göre farklı davranış**: Aynı endpoint, çağıran organizasyonun tipine (Sayaç Okuyan Kurum, K1/K2 Görevli Tedarik Şirketi, PK/OSB - DAĞITIM, Piyasa Katılımcısı vb.) göre farklı cevap kapsamı/response şeması döndürebilir (bkz. md §5, "Katılımcılar" tabloları) — aynı kod farklı hesaplarla farklı sonuç dönebilir, bu epint'in değil servisin davranışıdır.
- **Response sarmalayıcı**: Tüm cevaplar `status/correlationId/body.content` sarmalayıcısıyla döner; epint bunu otomatik soyar (bkz. [[01-epint-architecture]] §8), yani `ep.grid.ec_meter_query(...)` doğrudan `content` içeriğini döner, `.body.content` diye erişmeye çalışma.

## Örnek kullanım

```python
import epint as ep

ep.set_auth(username, password)
ep.set_mode("prod")

# 1) Aktif (statusId=2) ölçüm noktalarını Geçerlilik Tarihine göre sorgula
result = ep.grid.ec_meter_query(
    statusId=2,
    effectiveDate="2026-07-15T00:00:00+03:00",
    page={"number": 1, "size": 100},
)
for item in result["items"]:
    print(item["eic"], item["uniqueCode"])

# 2) Büyük hacimli sayaç verisini export ile indirme: önce offsetId'leri al
offsets = ep.grid.meter_fetch_export_offset_ids(
    readingOrganizationId=1023,
    page={"limit": 1000},
)["offsetIds"]

# ardışık ikili offsetId'lerle sayfa sayfa (paralel de yapılabilir) indir
for start, end in zip(offsets, offsets[1:] + [None]):
    page = ep.grid.meter_plain_export(
        readingOrganizationId=1023,
        page={"offsetIdStart": start, "offsetIdEnd": end},
    )
    # page["items"] / page["content"] işlenir

# 3) Yeni bir ölçüm noktası kaydet
new_ec_meter = ep.grid.ec_meter_save(
    effectiveDateStart="2026-08-01T00:00:00+03:00",
    usageStatusTypeId=2,
    consumptionPointTypeId=1,
    districtId=1186,
    address="Örnek adres",
    lastResortConsumerGroupId=1,
    bilateralConsumerGroupId=1,
    mainTariffGroupId=2,
    tariffClassTypeId=1,
    contractPower=10,
    readingTypeId=2,
    profileSubscriptionGroupId=112,
    readingDataTypeId=1,
    readingPeriod=30,
    facilityTypeId=1,
    remoteReadingStatusId=1,
    loadProfileFeature=False,
    annualAverageConsumption=12,
    substationId=20004,
    meteringVoltageTypeId=7,
    busbarVoltageTypeId=7,
    exceptionalSubstationStatus=False,
    withdrawPositionTypeId=7,
    uniqueCode="123456",
    readingOrganizationId=1023,
    descriptions=[{"language": "tr-TR", "description": "Test kayıt"}],
    annualEstimatedConsumptionT1=0,
    annualEstimatedConsumptionT2=0,
    annualEstimatedConsumptionT3=0,
)
print(new_ec_meter["id"], new_ec_meter["text"])

# 4) Mevcut ölçüm noktasının bir alanını sil (partial update + deletedFields)
ep.grid.ec_meter_update(
    effectiveId=new_ec_meter["id"],
    effectiveDateStart="2026-08-02T00:00:00+03:00",
    contractPower=12,
    deletedFields=["addressCode"],
    descriptions=[{"language": "tr-TR", "description": "Güncelleme"}],
)
```

## Kaynaklar

- `epint/endpoints/grid/swagger.json` — çalışma zamanında yüklenen asıl OpenAPI kaynağı (36 endpoint, basePath `/grid`).
- `refs/ (epint kaynak reposu; portalda yok) — grid/Sayaç ve Ölçüm noktası Servisleri.md` — Türkçe kullanım kılavuzu (auth akışı, sayfalama açıklaması §4, her endpoint için katılımcı/yetki/örnek istek-cevap §5, alan/lookup detayları §6-7).
- Genel mimari ve çağrı kuralları için [[01-epint-architecture]] ve [[02-epint-usage-conventions]].
