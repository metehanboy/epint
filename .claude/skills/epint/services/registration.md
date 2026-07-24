<!-- epint kategori referansı: registration — hub: ../SKILL.md -->

> **Portal:** `epint` pip ile kurulur (`requirements.txt` / Dockerfile). Swagger: kurulu pakette `epint/endpoints/<category>/swagger.json` (`python -c "import epint,pathlib; print(pathlib.Path(epint.__file__).parent)"`). Bu repoda `epint/src` veya `refs/` yok. Kurallar: `../overview.md`, `../usage-conventions.md`.

# registration — Kayıt Servisleri

EPYS Kayıt Servisleri (`EPYS - Kayıt Servisleri`), EPİAŞ piyasasındaki organizasyon (şirket), santral, UEVÇB (Uzlaştırmaya Esas Veriş-Çekiş Birimi), aggregator portföyü, SAE (Sağlıklı Aktivasyon Enerjisi) depolama portföyü, piyasa katılımı ve talep katılımı kayıtlarının sorgulanıp bazı durumlarda güncellenebildiği REST tabanlı bir uygulamadır. JSON/XML isteği kabul eder, JSON/XML cevap döner. EPYS arayüzündeki "Kayıt" menüsü altında görülen organizasyon/santral/UEVÇB/portföy bilgilerinin kaynağı bu servislerdir; çağıran kullanıcının EKYS'de kayıtlı ve ilgili alt servise yetkili olması gerekir.

**Kaynak durumu:** `refs/ (epint kaynak reposu; portalda yok) — registration/EPYS - Kayıt Servisleri.md` (~20855 satır) sadece **§6 — Definitions/DTO alan tablolarını** içeriyor; endpoint (path/method/summary) seviyesinde ayrı bir bölüm **yok**. Bu yüzden aşağıdaki endpoint tablosu doğrudan `epint/endpoints/registration/swagger.json`'dan (39 path/operation) çıkarıldı, DTO alan detayları/zorunluluklar ise md dosyasından. Swagger'daki çoğu `summary`/`description` alanı da henüz Türkçe'ye çözülmemiş i18n placeholder'ı (örn. `${AGGREGATOR_PORTFOLIO_APPROVE_VALUE}`) — bu durumda tablodaki açıklama operationId/DTO alan adlarından çıkarımdır, EPİAŞ'ın resmi metni değildir.

## Ne zaman kullanılır

- Organizasyon (şirket) kaydı bilgilerini, lisanslarını, illerini, özetini veya tüm alt detaylarını (cascade) sorgulamak.
- Santral (power plant) veya UEVÇB (settlement-aggregation-entity) kayıtlarını filtreli sorgulamak.
- Piyasa katılımı (`market-participation`) bilgilerini sorgulamak/güncellemek.
- Talep katılımı (`organization-demand-participation`) bilgilerini sorgulamak/güncellemek.
- Aggregator portföyü veya SAE depolama portföyü için davet gönderme, onaylama, reddetme, iptal etme, portföyden çıkma/çıkarma gibi iş akışı (transition) adımlarını yürütmek.
- Diğer servislerdeki sayısal ID'lerin (statusIds, typeIds, subTypeIds vb.) karşılığını çözmek için çoklu seçim (`lookup`) servislerini kullanmak.

## Endpoint'ler

Swagger'da kayıtlı toplam **39 endpoint**, 8 mantıksal gruba ayrılmış (parantez içi swagger `tag`'i):

### Aggregator Portföy Servisleri (`aggregatorPortfolioController`) — 8

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `aggregator_portfolio_approve` | POST | `/v1/aggregator-portfolio/approve` | Aggregator portföy talebini (davet/transition) onaylar. |
| `aggregator_portfolio_cancel` | POST | `/v1/aggregator-portfolio/cancel` | Gönderilmiş aggregator portföy talebini iptal eder. |
| `aggregator_portfolio_invite` | POST | `/v1/aggregator-portfolio/invite` | Santral(ler) için aggregator portföy talebi (davet) gönderir. |
| `aggregator_portfolio_query` | POST | `/v1/aggregator-portfolio/query` | Aktif aggregator portföy kayıtlarını sorgular. |
| `aggregator_portfolio_query_invitation` | POST | `/v1/aggregator-portfolio/query/invitation` | Aggregator portföy taleplerini/transition kayıtlarını sorgular. |
| `aggregator_portfolio_quit` | POST | `/v1/aggregator-portfolio/quit` | Aggregator portföyünden çıkma (muhtemelen santral/lisans sahibi tarafından). |
| `aggregator_portfolio_reject` | POST | `/v1/aggregator-portfolio/reject` | Aggregator portföy talebini reddeder. |
| `aggregator_portfolio_remove` | POST | `/v1/aggregator-portfolio/remove` | Aggregator portföyünden santral çıkarma (toplu, `periodEnd` ile). |

### Çoklu Seçim (Lookup) Servisleri — 2

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `available_lookups` | GET | `/v1/lookup` | Tanımlı tüm çoklu seçim anahtarlarını (`lookupType` değerleri) listeler. |
| `lookup_query` | POST | `/v1/lookup/query` | Belirli bir `lookupType` için değer listesini (id+value+localization) sorgular. |

### Piyasa Katılımı Servisleri (`market-participation`) — 2

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `market_participation_query` | POST | `/v1/market-participation/query` | Piyasa katılımı bilgilerini sorgular. |
| `market_participation_update` | POST | `/v1/market-participation/update` | Piyasa katılımı açıklamalarını/durumunu günceller. |

### Talep Katılımı Servisleri (`organizationDemandParticipation`) — 2

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `organization_demand_participation_fetch` | POST | `/v1/organization-demand-participation/fetch` | Organizasyon talep katılımı kayıtlarını sorgular. |
| `organization_demand_participation_update` | POST | `/v1/organization-demand-participation/update` | Talep katılımı açıklamalarını (`descriptions`) günceller. |

### Organizasyon Servisleri (`organization`) — 11

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `organization_cascade_detail` | GET | `/v1/organization/cascade/{effectiveId}` | Organizasyonun tüm alt detaylarını (cascade — iletişim, lisans, vergi, VEP vb.) tek seferde sorgular. |
| `organization_fetch_active_organizations` | POST | `/v1/organization/fetch-active-organizations` | Aktif organizasyonları label/value (alt tip bilgisiyle) listeler. |
| `organization_fetch_main_organizations` | GET | `/v1/organization/fetch-main-organizations` | Ana organizasyonları label/value listeler (parametresiz). |
| `organization_fetch_organization_with_dam_participation` | POST | `/v1/organization/fetch-organizations-with-dam-participation` | GÖP (gün öncesi piyasası) katılımına göre organizasyonları sorgular. |
| `organization_fetch_organizations_with_licenses` | POST | `/v1/organization/fetch-organizations-with-licenses` | Organizasyonları lisans bilgisiyle birlikte sorgular. |
| `organization_fetch_single_organization` | POST | `/v1/organization/fetch-single-organization` | Tekil organizasyonu `effectiveId` ile (body üzerinden) sorgular. |
| `organization_fetch_summary` | POST | `/v1/organization/fetch-summary` | Organizasyon özet bilgilerini sorgular. |
| `organization_get_distribution_area_with_provinces` | GET | `/v1/organization/get-distribution-area-with-provinces` | Dağıtım bölgesi — il eşleşmelerini listeler (parametresiz). |
| `organization_get_organization_provinces` | GET | `/v1/organization/provinces/{effectiveId}` | Organizasyonun faaliyet gösterdiği illeri sorgular. |
| `organization_query` | POST | `/v1/organization/query` | Organizasyonları çok sayıda filtreyle (ad, kod, vergi no, il, durum vb.) sorgular. |
| `organization_detail` | GET | `/v1/organization/{effectiveId}` | Organizasyon detayını `effectiveId` (path param) ile sorgular. |

### Santral (Power Plant) Servisleri (`power-plant`) — 4

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `fetch_aggregators_with_limits` | POST | `/v1/power-plant/fetch-aggregators-with-limits` | Aggregator'ların bağlı organizasyon güç limitlerini sorgular. |
| `power_plant_query_lookup` | POST | `/v1/power-plant/fetch-power-plants` | Santralleri label/value (lookup) formatında sorgular. |
| `power_plant_regions` | POST | `/v1/power-plant/fetch-regions` | Belirli bir santralin bölge bilgilerini sorgular (`effectiveId` zorunlu). |
| `power_plant_query` | POST | `/v1/power-plant/query` | Santralleri çok sayıda filtreyle (kurulu güç, kaynak tipi, lisans vb.) sayfalı sorgular. |

### SAE Depolama Portföy Servisleri (`saeStoragePortfolioController`) — 8

Aggregator portföy grubuyla bire bir aynı iş akışı deseni (davet/onay/red/iptal/çıkma/çıkarma), UEVÇB (`sae`) bazlı:

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `sae_storage_portfolio_approve` | POST | `/v1/sae-storage-portfolio/approve` | SAE depolama portföy talebini onaylar. |
| `sae_storage_portfolio_cancel` | POST | `/v1/sae-storage-portfolio/cancel` | SAE depolama portföy talebini iptal eder. |
| `sae_storage_portfolio_invite` | POST | `/v1/sae-storage-portfolio/invite` | UEVÇB(ler) için SAE depolama portföy talebi gönderir. |
| `sae_storage_portfolio_query` | POST | `/v1/sae-storage-portfolio/query` | Aktif SAE depolama portföy kayıtlarını sorgular. |
| `sae_storage_portfolio_query_invitation` | POST | `/v1/sae-storage-portfolio/query/invitation` | SAE depolama portföy taleplerini/transition kayıtlarını sorgular. |
| `sae_storage_portfolio_quit` | POST | `/v1/sae-storage-portfolio/quit` | SAE depolama portföyünden çıkma. |
| `sae_storage_portfolio_reject` | POST | `/v1/sae-storage-portfolio/reject` | SAE depolama portföy talebini reddeder. |
| `sae_storage_portfolio_remove` | POST | `/v1/sae-storage-portfolio/remove` | SAE depolama portföyünden UEVÇB çıkarma (toplu, `periodEnd` ile). |

### UEVÇB (Settlement Aggregation Entity) Servisleri (`settlement-aggregation-entity`) — 2

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `settlement_aggregation_entity_detail` | POST | `/v1/sae/detail` | UEVÇB detayını `id`+`effectiveDate` ile sorgular. |
| `settlement_aggregation_entity_query` | POST | `/v1/sae/query` | UEVÇB kayıtlarını çok sayıda filtreyle sayfalı sorgular. |

**Not — iki tuhaf `operationId` (çözüldü):** `fetch-organizations-with-licenses` ve `get-distribution-area-with-provinces` endpoint'lerinin swagger `operationId`'si diğerlerinden farklı formattaydı (`OrganizationController_fetchOrganizationsWithLicenses_POST`, `OrganizationController_getDistributionAreaWithProvinces_GET` — Springfox'un özel nickname verilmediğinde ürettiği varsayılan controller stili) ve `summary`/`description` alanları da yok. `SwaggerModel` bu deseni "güvenilmez" sayıp method adını path'ten türetiyor (bkz. [[01-epint-architecture]]), bu yüzden tablodaki adlar (`organization_fetch_organizations_with_licenses`, `organization_get_distribution_area_with_provinces`) doğrudan kullanılabilir — tahmin/doğrulama gerekmez.

## Önemli parametreler ve gotchalar

- **Path parametreli 3 servis** (`organization_detail`, `organization_cascade_detail`, `organization_get_organization_provinces`) `effectiveId`'yi **body'de değil path'te** alır — `ep.registration.organization_detail(effectiveId=123)` şeklinde çağır, epint bunu otomatik path'e yerleştirir.
- **Zorunlu (`gerekli`) alanlar** (md dosyasından doğrulanmış, diğerleri opsiyonel):
  - `lookup_query` → `LookupRequest.lookupType` (string) **zorunlu**. Geçerli değerleri önce `available_lookups()` ile keşfet — swagger'da statik bir enum listesi yok.
  - `organization_fetch_single_organization` / `organization_fetch_summary` (ikisi de `OrganizationFetchDto` kullanır) → `effectiveId` **zorunlu**.
  - `organization_fetch_organization_with_dam_participation` (`OrganizationWithDamParticipationQueryRequestDto`) → `effectiveDate` **zorunlu**.
  - `power_plant_regions` (`PowerPlantRegionQueryRequestDto`) → `effectiveId` **zorunlu**.
  - `settlement_aggregation_entity_detail` (`SaeGetDetailRequestDto`) → `id` ve `effectiveDate` **her ikisi de zorunlu**.
  - `market_participation_update` (`MarketParticipationUpdateRequestDto`) → `organizationEffectiveId` ve `descriptions` (array, her elemanda `description`+`language` zorunlu) **zorunlu**.
- **Portföy transition body şekilleri asimetrik** — aggregator/SAE depolama portföy grubunda `approve`/`cancel`/`reject`/`quit` tek bir `id` alır (`AggregatorPortfolioRequestDto`/`SaeStoragePortfolioRequestDto: {id}`), ama `remove` bunun yerine `ids` (array) + `periodEnd` alır (`AggregatorPortfolioRemoveRequestDto`/`SaeStoragePortfolioRemoveRequestDto`), ve `invite` santral/UEVÇB ID listesi alır (`powerPlantEids`/`saeEids`). Yanlış şekilde tekil `id` yerine `ids` (veya tersi) göndermek sessizce yanlış alana düşebilir — çağırmadan önce `print(ep.registration.<method>)` ile repr'i kontrol et.
- **Response şekli de asimetrik**: `approve`/`cancel`/`reject`/`invite` → `RestResponse...TransitionDto` (transition kaydı) döner; `quit`/`remove`/`query` → `RestResponse...PortfolioDto` / paged liste döner. `query_invitation` transition kayıtlarını sayfalı döner. epint `RestResponse` sarmalayıcısını otomatik soyar (mimari kural §8) ama iç yapı (`Transition` vs düz `PortfolioDto`) endpoint'e göre değişir.
- **Durum/tip ID'leri (`statusIds`, `typeIds`, `subTypeIds`, `recordStatusIds`, `licenseTypeIds`, `sourceTypeIds`, `rsmStatusIds`, `trimmingStatusIds` vb.) için swagger'da statik enum yok** — bunlar `LookupDTO` (`id`+`value`+`localizations`) ile response'ta gelir; doğru ID'yi bulmak için ya `available_lookups`/`lookup_query` ile ilgili `lookupType`'ı sorgula ya da bir örnek kayıttan `id`→`value` eşlemesini örnekle.
- **`organization_query`** çok sayıda opsiyonel filtre alır: `name`, `shortName`, `code`, `taxNo`, `eic`, `effectiveId`/`effectiveIdContains`, `provinceId`, `mainOrganizationId`, `isAggregator`, `isCategory`, `licenseTypeIds`, `subTypeIds`, `typeIds`, `stateIds`, `recordStatusIds`, `effectiveDate`/`effectiveDateStart`/`effectiveDateEnd`, `page`. Response alanı `effectiveId` (organizasyon ID'si) — sonraki `organization_detail`/`organization_cascade_detail` çağrısında path param olarak bunu kullan.
- **`power_plant_query`** de benzer şekilde geniş filtre seti sunar: `id`/`idContains`/`ids`, `eic`, `licenseNumber`, `licenseTypeIds`, `installedPowerMin`/`installedPowerMax`, `organizationId`/`organizationIdContains`, `organizationOrLicenseOwnerId`, `sourceGroupIds`, `sourceTypeIds`, `statusIds`, `rsmStatusIds`, `trimmingStatusIds`, `recordStatusIds`, `effectiveDate`/`effectiveDateStart`/`effectiveDateEnd`, `observerDate`, `page`.
- **`settlement_aggregation_entity_query`** benzer geniş filtre seti sunar, ayrıca `balancingRegionId`, `balancingMarketParticipationStatusIds`, `greenTariffTypeIds` (YETA), `gridType`, `groupOwnerSaeEid`, `powerPlantEffectiveId(s)` gibi UEVÇB'ye özgü alanlar içerir.
- **`page` varsayılanı** — vermezsen epint otomatik `{'number': 1, 'size': 1000}` uygular (mimari kural §5); `organization_query`, `power_plant_query`, `settlement_aggregation_entity_query`, `*_portfolio_query*`, `organization_demand_participation_fetch` gibi tüm sayfalı servislerde büyük sonuç kümelerinde manuel sayfalama gerekebilir.
- **Auth/header**: Bu kategori `gop`/`seffaflik` değil → normal `TGT`+`ST` header'ları eklenir (mimari kural §6). Tarih formatı epys ailesi standardı: ISO + `+HH:MM` offset (örn. `2026-07-01T00:00:00+03:00`).
- **`organization_get_organization_provinces` ve `lookup_query`** ayrıca opsiyonel `accept-language` header parametresi kabul eder (localization dili seçimi için).

## Örnek kullanım

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# Organizasyonları ada göre sorgula, sonra tekil detayını al
result = ep.registration.organization_query(
    name="ENERJİ",
    isAggregator=True,
    page={"number": 1, "size": 100},
)
for org in result.get("items", []):
    detail = ep.registration.organization_detail(effectiveId=org["effectiveId"])
    print(org["effectiveId"], detail.get("name"))
```

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# Aggregator portföy talebi gönder, sonra bekleyen talepleri sorgula
ep.registration.aggregator_portfolio_invite(powerPlantEids=[123456, 234567])

pending = ep.registration.aggregator_portfolio_query_invitation(
    statusIds=[1],  # doğru ID'yi lookup_query ile teyit et
    page={"number": 1, "size": 50},
)

# Bekleyen bir talebi onayla (tekil id ile, ids listesiyle DEĞİL)
ep.registration.aggregator_portfolio_approve(id=pending["items"][0]["id"])
```

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# lookupType'ı önce keşfet, sonra değer listesini sorgula
available = ep.registration.available_lookups()
values = ep.registration.lookup_query(lookupType="ORGANIZATION_STATE")

# Gerçek isteği atmadan RequestModel'i incelemek için debug=True
req = ep.registration.power_plant_query(sourceTypeIds=[1, 2], debug=True)
print(req)
```

## Kaynaklar

- `refs/ (epint kaynak reposu; portalda yok) — registration/EPYS - Kayıt Servisleri.md` (sadece §6 — DTO/definitions tabloları; endpoint seviyesi doküman yok)
- `epint/endpoints/registration/swagger.json` (39 endpoint'in tek gerçek kaynağı)
- Genel mimari: `../architecture.md`
- Genel kullanım kuralları: `../usage-conventions.md`
