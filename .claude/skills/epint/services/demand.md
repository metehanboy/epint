<!-- epint kategori referansı: demand — hub: ../SKILL.md -->

> **Portal:** `epint` pip ile kurulur (`requirements.txt` / Dockerfile). Swagger: kurulu pakette `epint/endpoints/<category>/swagger.json` (`python -c "import epint,pathlib; print(pathlib.Path(epint.__file__).parent)"`). Bu repoda `epint/src` veya `refs/` yok. Kurallar: `../overview.md`, `../usage-conventions.md`.

# demand — Serbest Tüketici Talep Servisleri

EPYS altındaki "Serbest Tüketici Talep Servisleri" (`basePath: /demand`), serbest tüketici piyasasında bir tüketim noktasının tedarikçi/portföy değişikliklerini yöneten servis grubudur: bir tüketim noktasını bir tedarikçinin/talep toplayıcının/otoprodüktörün portföyüne ekleme veya çıkarma talebi açma, bu taleplerin durumunu takip etme, tahliye (evacuation) süreçlerini yönetme ve serbest tüketici/lookup verilerini sorgulama işlevlerini kapsar. Servis `epint` içinde normal bir "epys" ailesi kategorisidir (gop/şeffaflık değildir) — TGT + `ST` header'ları epint tarafından otomatik eklenir, ek bir auth işlemi gerekmez.

Bu dosya sadece `demand` kategorisine özgü endpoint/parametre bilgisini içerir. Genel çağrı mekaniği, auth akışı, tarih formatı ve fuzzy matching kuralları için `../architecture.md` ve `../usage-conventions.md`'ye bakın, burada tekrarlanmamıştır.

## Ne zaman kullanılır

- Bir tüketim noktasının serbest tüketici / EIC / abone bilgilerini sorgulamak gerektiğinde (`eligible_customer_query`).
- Bir tüketim noktasını bir tedarikçinin, talep toplayıcının (aggregator) veya otoprodüktörün portföyüne **ekleme/çıkarma talebi** açmak, ön sorgu yapmak, güncellemek veya durumunu sorgulamak gerektiğinde.
- OSB (Organize Sanayi Bölgesi) ana sayaç üzerinden bağlı tüketim noktalarının portföy ekleme/çıkarma taleplerini yönetmek gerektiğinde.
- **Tahliye (evacuation)** — bir tüketim noktasının şebekeden tahliye edilmesi talebini kaydetmek, onaylamak, reddetmek, pasife almak veya bu taleplerin bilgilendirme (ack) kayıtlarını yönetmek gerektiğinde.
- Kayıtsız ölçüm noktası (KMO / non-registered metering point) başvurusu yapmak, sorgulamak, reddetmek veya geri çekmek gerektiğinde.
- Talep toplayıcı/tedarikçi/dağıtım firması için **ön bildirim** listelerini veya bir katılımcının **yaptırım (sanction)** kayıtlarını sorgulamak gerektiğinde.
- Talep/durum/kategori gibi alanlardaki **lookup (çoklu seçim) ID'lerinin** karşılığını (insan tarafından okunabilir değer) öğrenmek gerektiğinde.

## Endpoint'ler

Swagger'da toplam **59 endpoint** var (`epint/endpoints/demand/swagger.json`). Aşağıda `operationId`'den türetilen Python method adı (`ep.demand.<method_adi>`), HTTP metodu, path ve kısa açıklama, mantıksal gruplar halinde listelenmiştir.

### Serbest tüketici (1)

| method_adi | HTTP | path | Açıklama |
|---|---|---|---|
| `eligible_customer_query` | POST | `/v1/eligible-customer/query` | Tüketim noktası bilgileriyle serbest tüketici bilgilerini sorgular |

### Talep — genel (demand-controller) (9)

| method_adi | HTTP | path | Açıklama |
|---|---|---|---|
| `demand_self_get` | POST | `v1/demand/self/get` | Kendi/bağlı organizasyonların yaptığı talepleri listeler |
| `demand_counter_get` | POST | `v1/demand/counter/get` | Portföyümü etkileyen karşı talepleri sorgular |
| `demand_distribution_counter_get` | POST | `v1/demand/distribution/counter/get` | Karşı talepleri sorgular (dağıtım firması bakış açısı) |
| `demand_history_get` | GET | `v1/demand/getDemandHistory` | Bir talebin geçtiği aşamaların tarihçesini getirir |
| `demand_portfolio_add_create` | POST | `v1/demand/portfolio-add/create` | Portföye ekleme talebi kaydeder |
| `demand_portfolio_add_update` | POST | `v1/demand/portfolio-add/update` | Portföye ekleme talebini günceller |
| `demand_portfolio_out_create` | POST | `v1/demand/portfolio-out/create` | Portföyden çıkarma talebi kaydeder |
| `demand_portfolio_out_update` | POST | `v1/demand/portfolio-out/update` | Portföyden çıkarma talebini günceller |
| `demand_re_energisation_create` | POST | `v1/demand/re-energisation/create` | Yeniden enerjilendirme talebi kaydeder |

### Talep toplayıcı — aggregator (11)

| method_adi | HTTP | path | Açıklama |
|---|---|---|---|
| `aggregator_query` | POST | `v1/demand/aggregator/query` | Talep toplayıcı sorgusu oluşturur |
| `aggregator_counter_query` | POST | `v1/demand/aggregator/counterQuery` | Portföyümü etkileyen diğer organizasyonların karşı taleplerini listeler |
| `aggregator_history_query` | GET | `v1/demand/aggregator/getDemandHistory` | Talep toplayıcı talep tarihçesini sorgular |
| `aggregator_status` | POST | `v1/demand/aggregator/updateStatus` | Talep toplayıcı taleplerinin durumunu günceller |
| `aggregator_portfolio_add` | POST | `v1/demand/aggregator/portfolio-add/create` | Talep toplayıcı ekleme talebi kaydeder |
| `aggregator_portfolio_add_query` | POST | `v1/demand/aggregator/portfolio-add/query` | Ekleme talebi **ön sorgusu** (kayıttan önce ön kontrol) |
| `aggregator_portfolio_add_update` | POST | `v1/demand/aggregator/portfolio-add/update` | Ekleme talebini günceller |
| `aggregator_portfolio_add_update_query` | POST | `v1/demand/aggregator/portfolio-add/updateQuery` | Ekleme talebi güncelleme **ön sorgusu** |
| `aggregator_portfolio_out` | POST | `v1/demand/aggregator/portfolio-out/create` | Talep toplayıcı portföyden çıkarma talebi kaydeder |
| `aggregator_portfolio_out_query` | POST | `v1/demand/aggregator/portfolio-out/query` | Çıkarma talebi **ön sorgusu** |
| `aggregator_portfolio_out_update` | POST | `v1/demand/aggregator/portfolio-out/update` | Çıkarma talebini günceller |

### Otoprodüktör — auto-productor (5)

| method_adi | HTTP | path | Açıklama |
|---|---|---|---|
| `demand_auto_productor_portfolio_add_create` | POST | `v1/demand/auto-productor/portfolio-add/create` | Otoprodüktör sayacı portföye ekleme talebi kaydeder |
| `demand_auto_productor_portfolio_add_update_status` | POST | `v1/demand/auto-productor/portfolio-add/updateStatus` | Ekleme talebi durumunu günceller |
| `demand_auto_productor_portfolio_out_create` | POST | `v1/demand/auto-productor/portfolio-out/create` | Otoprodüktör sayacı portföyden çıkarma talebi kaydeder |
| `demand_auto_productor_portfolio_out_update_status` | POST | `v1/demand/auto-productor/portfolio-out/updateStatus` | Çıkarma talebi durumunu günceller |
| `demand_auto_productor_portfolio_out_update_supplier` | POST | `v1/demand/auto-productor/portfolio-out/updateSupplier` | Çıkarma talebinde son kaynak tedarikçi durumunu günceller |

### OSB ana sayaç — oiz-main-meter (8)

| method_adi | HTTP | path | Açıklama |
|---|---|---|---|
| `get_oiz_main_meter_related_demand_nickname` | GET | `v1/demand/oiz-main-meter/getRelatedDemand` | Ana sayaç talebine bağlı alt talepleri sorgular |
| `demand_oiz_main_meter_add_nickname` | POST | `v1/demand/oiz-main-meter/portfolio-add/create` | OSB ana sayaç ekleme talebi kaydeder |
| `demand_oiz_main_meter_add_query_nickname` | POST | `v1/demand/oiz-main-meter/portfolio-add/query` | Ekleme talebi **ön sorgusu** (organizasyon/sayaç bilgisiyle) |
| `demand_oiz_main_meter_add_update_nickname` | POST | `v1/demand/oiz-main-meter/portfolio-add/update` | Ekleme talebinde abone bilgilerini günceller |
| `demand_oiz_main_meter_add_update_status_nickname` | POST | `v1/demand/oiz-main-meter/portfolio-add/updateStatus` | Ekleme talebi durumunu günceller |
| `demand_oiz_main_meter_out_create_nickname` | POST | `v1/demand/oiz-main-meter/portfolio-out/create` | OSB ana sayaç çıkarma talebi kaydeder |
| `demand_oiz_main_meter_out_query_nickname` | POST | `v1/demand/oiz-main-meter/portfolio-out/query` | Çıkarma talebi **ön sorgusu** |
| `demand_oiz_main_meter_out_update_status_nickname` | POST | `v1/demand/oiz-main-meter/portfolio-out/updateStatus` | Çıkarma talebi durumunu günceller |

### Tahliye — evacuation (8)

| method_adi | HTTP | path | Açıklama |
|---|---|---|---|
| `evacuation_save` | POST | `/v1/evacuation/save` | Tahliye talebi kaydeder |
| `evacuation_batch_save` | POST | `/v1/evacuation/save-batch` | Toplu tahliye talebi kaydeder |
| `evacuation_query` | POST | `/v1/evacuation/query` | Tahliye taleplerimi sorgular |
| `evacuation_update` | POST | `/v1/evacuation/update` | Tahliye talebini günceller |
| `evacuation_passivate` | POST | `/v1/evacuation/passivate` | Tahliye talebini pasife alır |
| `evacuation_batch_passivate` | POST | `/v1/evacuation/passivate-batch` | Toplu tahliye talebini pasife alır |
| `evacuation_reject` | POST | `/v1/evacuation/reject` | Tahliye talebini reddeder |
| `evacuation_reactivate` | POST | `/v1/evacuation/reactivate` | Reddedilen tahliye talebini geri çeker (yeniden aktifleştirir) |

### Tahliye bilgilendirme — evacuation-ack (5)

| method_adi | HTTP | path | Açıklama |
|---|---|---|---|
| `evacuation_ack_save` | POST | `/v1/evacuation-ack/save` | Tahliye bilgilendirme kaydı oluşturur |
| `evacuation_ack_query` | POST | `/v1/evacuation-ack/query` | Tahliye bilgilendirme kayıtlarını listeler |
| `evacuation_ack_approve` | POST | `/v1/evacuation-ack/approve` | Tahliye bilgilendirmesini onaylar |
| `evacuation_ack_reject` | POST | `/v1/evacuation-ack/reject` | Tahliye bilgilendirmesini reddeder |
| `evacuation_ack_passivate` | POST | `/v1/evacuation-ack/passivate` | Tahliye bilgilendirme kaydını pasife alır |

### KMO — kayıtsız ölçüm noktası başvurusu (4)

| method_adi | HTTP | path | Açıklama |
|---|---|---|---|
| `non_registered_metering_point_application_apply` | POST | `/v1/non-registered-metering-point-application/apply` | KMO başvurusu yapar |
| `non_registered_metering_point_application_query` | POST | `/v1/non-registered-metering-point-application/query` | KMO taleplerini sorgular |
| `non_registered_metering_point_application_reject` | POST | `/v1/non-registered-metering-point-application/reject` | KMO başvurusunu reddeder |
| `non_registered_metering_point_application_withdraw` | POST | `/v1/non-registered-metering-point-application/withdraw` | KMO başvurusunu geri çeker |

### Dönem, ön bildirim, yaptırım, lookup (10)

| method_adi | HTTP | path | Açıklama |
|---|---|---|---|
| `get_active_period` | GET | `/v1/period/getActivePeriod` | Aktif dönemi getirir |
| `get_all_period` | GET | `/v1/period/getPeriods` | Geçmiş ve aktif tüm dönemleri getirir |
| `pre_notification_aggregator_query` | POST | `/v1/pre-notification/aggregator/query` | Toplayıcılık ön bildirim listesini sorgular |
| `pre_notification_distributor_query_v2` | POST | `/v1/pre-notification/distributor/query` | Dağıtım firması ön bildirim listesini sorgular (operationId: `pre-notification-distributor-queryV2`) |
| `pre_notification_supplier_query_v2` | POST | `/v1/pre-notification/supplier/query` | Tedarik firması ön bildirim listesini sorgular (operationId: `pre-notification-supplier-queryV2`) |
| `sanction_query_participant` | POST | `/v1/sanction/queryParticipant` | Katılımcının yaptırım kayıtlarını listeler |
| `available_lookups` | GET | `/v1/lookup` | Mevcut lookup (çoklu seçim) anahtarlarının listesini döner |
| `lookup_query` | POST | `/v1/lookup/query` | Bir lookup anahtarına ait detay değerleri döner |

> Not: `queryV2` gibi operationId parçaları için nihai Python method adı `to_python_method_name` normalizasyonundan geçer; tam adından emin olmak için çağırmadan önce `print(ep.demand)` ile mevcut methodları veya `print(ep.demand.<tahmini_ad>)` ile repr'i kontrol edin — fuzzy matching yazım farklarını tolere eder.

## Önemli parametreler ve gotchalar

- **Lookup ID pattern**: `status`, `type`, `category` gibi çoğu alan (`demandStatus`, `demandTypes`, `categoryType`, `evacuationType`, `bilateralConsumerGroup`, `usageStatusType`, ...) düz metin enum değil, **lookup ID'sine referans veren `integer`** alanlardır. Bu ID'lerin insan tarafından okunabilir karşılığını öğrenmek için önce `ep.demand.available_lookups()` ile mevcut `lookupType` anahtarlarını, sonra `ep.demand.lookup_query(lookup_type='<anahtar>')` ile o anahtarın değer listesini (`id`/`value` çiftleri) çekin. `lookup_query` çağrısında **`lookupType` zorunludur** (swagger `required`).
- **Ön sorgu (query) → kayıt (create/update) akışı**: `aggregator_portfolio_add_query`, `aggregator_portfolio_out_query`, `aggregator_portfolio_add_update_query`, `demand_oiz_main_meter_add_query_nickname`, `demand_oiz_main_meter_out_query_nickname` gibi `*_query` uçları, gerçek kayıt/güncelleme işleminden **önce** önyüz için ön kontrol amaçlıdır (`isPreCheckOperation` alanı bu davranışı tetikler) — asıl talebi oluşturmadan uyarı/çakışma durumlarını görmek için önce bunları çağırın.
- **Zorunlu alanlar servise göre değişir** (swagger `required` dizisi, body şemasına göre), örnekler:
  - `evacuation_ack_reject`, `evacuation_reject`, `non_registered_metering_point_application_reject` → `rejectReason` zorunlu.
  - Durum güncelleme uçları (`aggregator_status`, `demand_auto_productor_*_update_status`, `demand_oiz_main_meter_*_update_status*`) → genelde `demandId` + `demandStatusId` zorunlu.
  - `evacuation_save` / `evacuation_ack_save` gibi kayıt uçları → `consumptionPointId` + `evacuationType` zorunlu.
  - Portföy ekleme/güncelleme uçlarının çoğunda `isCustomerInformationChange` ve/veya `isPreCheckOperation` (`boolean`) zorunlu — göndermezseniz `400` hatası alırsınız.
  - Bir endpoint'in tam zorunlu alan listesini görmek için **çağırmadan** `print(ep.demand.<method>)` ile repr'i inceleyin (mimari kural §2, `RequestModel`'in kullandığı şema budur).
- **Sayfalama (`page`)**: `demand_self_get`, `aggregator_query`, `evacuation_query`, `evacuation_ack_query`, `non_registered_metering_point_application_query`, `pre_notification_*_query`, `sanction_query_participant` gibi liste/sorgu uçları `Page` nesnesi (`{number, size, total, sort}`) kabul eder. Vermezseniz epint otomatik `{'number': 1, 'size': 1000}` uygular — **büyük sonuç kümelerinde sayfalama yapmayı unutmayın**.
- **`region`/`regionCode` varsayılanı burada devreye girmez**: Bu kategorideki DTO'larda `region`/`regionCode`/`counterRegionCode` adında bir alan **yoktur** (yalnızca `balancingRegionId`/`biddingRegionId` gibi farklı isimli alanlar var); dolayısıyla mimari kuraldaki otomatik `'TR1'` varsayılanı `demand` uçlarının hiçbirinde tetiklenmez — bölgeyle ilgili bir filtre gerekiyorsa `balancingRegionId` gibi gerçek alan adını kullanmanız gerekir.
- **Tarih alanları** (`periodDates`, `periodDate` vb.) `date-time` formatındadır ve epys ailesi formatını kullanır (`+03:00` offset'li ISO, mimari kural §7) — `str` veya `datetime` verin, elle formatlamayın.
- **Toplu (`batch`) uçlar**: `evacuation_batch_save` / `evacuation_batch_passivate` tekil kayıt yerine talep **listesi** (array body) bekler; yanıt olarak `EvacuationBatchSummaryDto` (özet/başarı-hata sayıları) döner, tekil `evacuation_save`'in döndürdüğü tekil talep nesnesiyle karıştırmayın.
- **`demand_history_get` / `aggregator_history_query`**: GET metodu kullanır (çoğu uç POST'tur) — parametreler query string olarak gider, body değil.

## Örnek kullanım

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# 1. Bir tüketim noktasının serbest tüketici bilgilerini sorgula
sonuc = ep.demand.eligible_customer_query(consumptionPointEic="40X000000000002C")

# 2. Lookup akışı: önce mevcut anahtarları, sonra "demand status" değerlerini çek
anahtarlar = ep.demand.available_lookups()
durumlar = ep.demand.lookup_query(lookup_type="DEMAND_STATUS")  # gerçek anahtar adı ortama göre değişir

# 3. Kendi taleplerimi, belirli bir döneme ve durumlara göre sayfalayarak sorgula
taleplerim = ep.demand.demand_self_get(
    periodDates=["2026-07-01T00:00:00+03:00"],
    demandStatus=1,
    page={"number": 1, "size": 200},
)

# 4. Tahliye talebi kaydet, sonra durumunu sorgula
try:
    yeni_talep = ep.demand.evacuation_save(
        consumptionPointId=123456,
        evacuationType=2,
    )
except Exception as e:
    print(f"Hata: {e}")
else:
    tahliyeler = ep.demand.evacuation_query(page={"number": 1, "size": 50})
```

## Kaynaklar

- `C:\Users\m3T3-\Desktop\epys\refs\demand\EPYS - Serbest Tüketici Talep Servisleri.md` — bu dosya sadece DTO/model referans tablolarını içerir (bölüm 6, `### 6.1`–`### 6.168`); endpoint path/summary/description bilgisi bulunmuyor, bu bilgi swagger.json'dan alındı.
- `C:\Users\m3T3-\Desktop\epys\epint\src\epint\endpoints\demand\swagger.json` — asıl OpenAPI (Swagger 2.0) kaynağı; `title`: "EPYS - Serbest Tüketici Talep Servisleri", `basePath`: `/demand`, 10 controller tag'i, 59 endpoint.
