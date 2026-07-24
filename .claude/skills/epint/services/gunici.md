<!-- epint kategori referansı: gunici — hub: ../SKILL.md -->

> **Portal:** `epint` pip ile kurulur (`requirements.txt` / Dockerfile). Swagger: kurulu pakette `epint/endpoints/<category>/swagger.json` (`python -c "import epint,pathlib; print(pathlib.Path(epint.__file__).parent)"`). Bu repoda `epint/src` veya `refs/` yok. Kurallar: `../overview.md`, `../usage-conventions.md`.

# gunici — GÜNİÇİ Servisleri

`gunici` kategorisi, EPİAŞ Gün İçi Piyasası (GİP) REST servislerini kapsar: teklif (offer) girme/listeleme, kontrat listeleme, eşleşme (match) sorgulama, katılımcı limitleri, itiraz (objection), duyuru, dashboard/grafik verileri ve işlem geçmişi. Kaynak swagger'ın `info.title` alanı da "EPİAŞ - GÜNİÇİ Servisleri"dir.

Toplam **149 endpoint** kayıtlı (`epint/endpoints/gunici/swagger.json`), bunların **118'i** iş mantığı servisidir (kebab-case `operationId`, çoğunda `summary`/`description` var); kalan **31'i** `XController_yöntem_POST/GET` şeklinde `operationId`'ye sahip, **swagger `summary`'si olmayan** dahili/admin-panel uçlarıdır (bkz. "Dahili/admin uçları" bölümü) — bunlar EPİAŞ'ın kendi arayüzü için, normal kullanım senaryosunda muhtemelen gerek yoktur.

`refs/ (epint kaynak reposu; portalda yok) — gunici/EPİAŞ - GÜNİÇİ Servisleri.md` dosyası klasik bir kullanım kılavuzu **değildir** — içeriği tek bir GraphQL introspection şeması dökümüdür (yaklaşık 40 tip). Asıl endpoint/parametre kaynağı `swagger.json`'dur; md dosyasından sadece bazı enum/domain değerleri (`OfferStatus`, `OfferOptionType` vb.) doğrulandı ve aşağıya alındı.

## Ne zaman kullanılır

- `ep.gunici.<method_adi>(**kwargs)` çağrısı yazarken veya debug ederken.
- GİP teklif/kontrat/eşleşme/limit/itiraz/dashboard verisi çekilecek bir Python kodu üretirken.
- `gunici` ile `gunici-trading` kategorilerini birbirine karıştırmamak için: ikisinin de `refs/ (epint kaynak reposu; portalda yok) — ` altındaki md dosya adı "EPİAŞ - GÜNİÇİ Servisleri.md" olsa da, içerikleri ve swagger'ları tamamen farklıdır. Bu dosya sadece `gunici` kategorisini kapsar.

## Endpoint'ler

Path'ler `https://gunici.epias.com.tr` host'una, swagger'daki `basePath` (`/gunici-service`) ile birleştirilerek istek atılır (örn. `list-offers` → `https://gunici.epias.com.tr/gunici-service/rest/v1/offer/list`). `method_adi` sütunu, gerçek registry anahtarının (`operationId` içindeki `-` → `_`) `to_python_method_name` ile normalize edilmiş halidir — kodda bunu kullan.

### Teklif (offer) — 10 uç

| method_adi | HTTP | path | açıklama |
|---|---|---|---|
| `export_offers` | POST | `/rest/v1/offer/list/export` | Teklif listesini export eder |
| `export_offers_by_exist` | POST | `/rest/v1/offer/list/by-exist/export` | Teklif listeleme (exist/admin) export |
| `export_offers_by_participant` | POST | `/rest/v1/offer/list/by-participant/export` | Katılımcıya göre teklif export |
| `list_offer_history` | POST | `/rest/v1/offer/history/list` | Teklif geçmiş listeleme |
| `list_offer_organizations` | GET | `/rest/v1/offer/organization/list` | Organizasyon listeleme |
| `list_offers` | POST | `/rest/v1/offer/list` | Teklif listeleme (ana servis) |
| `list_offers_by_exist` | POST | `/rest/v1/offer/list/by-exist` | Teklif listeleme (exist/admin) |
| `list_offers_by_participant` | POST | `/rest/v1/offer/list/by-participant` | Katılımcıya göre teklif listeleme |
| `list_offers_history` | POST | `/rest/v1/offer/multiple/history/list` | Teklifler geçmiş listeleme |
| `offer_template` | GET | `/rest/v1/offer/file/template` | Toplu teklif yükleme Excel şablonu |

### Teklif detay/derinlik (offer-exist) — 6 uç

| method_adi | HTTP | path | açıklama |
|---|---|---|---|
| `list_buy_offer_depths` | POST | `/rest/v1/offer/exist/buy-offer/depth` | Alış teklif derinliği |
| `list_match_offer_detail` | POST | `/rest/v1/offer/exist/match-offer/detail` | Eşleşen teklifler detayı |
| `list_match_offers` | POST | `/rest/v1/offer/exist/match-offers` | Eşleşen teklifler |
| `list_matching_detail` | POST | `/rest/v1/offer/exist/matching/detail` | Eşleşen teklifler detayı |
| `list_offer_depth_detail` | POST | `/rest/v1/offer/exist/offer-depth/detail` | Teklif derinliği |
| `list_sell_offer_depths` | POST | `/rest/v1/offer/exist/sell-offer/depth` | Satış teklif derinliği |

### Kontrat (contract) — 7 uç

| method_adi | HTTP | path | açıklama |
|---|---|---|---|
| `contracts_freeze_filter` | POST | `/rest/v1/contract/filter` | İleri tarihli kontrat dondurma arama |
| `list_active_contracts_lookup` | POST | `/rest/v1/contract/offer-contract/list` | Kontrat listeleme |
| `list_active_contracts_lookup_buy_offer` | POST | `/rest/v1/contract/offer-contract/lookup` | Güncellenebilir kontrat listesi |
| `list_all_active_contracts_lookup` | POST | `/rest/v1/contract/actives` | Aktif kontrat listeleme |
| `list_contracts` | POST | `/rest/v1/contract/list` | Kontrat listeleme (ana servis) |
| `list_contracts_lookup` | POST | `/rest/v1/contract/lookup` | Kontrat listeleme (lookup) |
| `list_exist_contracts_lookup` | POST | `/rest/v1/contract/offer-exist/lookup` | Kontrat listeleme (exist) |
| `list_trade_history` | POST | `/rest/v1/contract/trade-history/list` | İşlem akışı |

### Eşleşme / uzlaştırma (match-detail) — 11 uç

| method_adi | HTTP | path | açıklama |
|---|---|---|---|
| `export_matches_by_exist` | POST | `/rest/v1/match/by-exist/export` | Eşleşme listeleme (exist) export |
| `export_matches_by_organization` | POST | `/rest/v1/match/by-organization/export` | Organizasyona ait eşleşme export |
| `export_matches_by_participant` | POST | `/rest/v1/match/by-participant/export` | Katılımcıya ait eşleşme export |
| `list_match_count` | POST | `/rest/v1/match/match-count/list` | Eşleşme sayısı listesi |
| `list_matches_by_exist` | POST | `/rest/v1/match/by-exist` | Eşleşme listeleme (exist) |
| `list_matches_by_organization` | POST | `/rest/v1/match/by-organization` | Organizasyona ait eşleşme listeleme |
| `list_matches_by_participant` | POST | `/rest/v1/match/by-participant` | Katılımcıya ait eşleşme listeleme |
| `list_organization_otr_report` | POST | `/rest/v1/match/otr/report` | Teklif Eşleşme Oran (TEO) raporu |
| `list_organization_otr_report_export` | POST | `/rest/v1/match/otr/report/export` | TEO raporu export |
| `list_recon_hourly` | POST | `/rest/v1/match/hourly/reconciliation` | GİP uzlaştırma raporu |
| `list_recon_hourly_export` | POST | `/rest/v1/match/hourly/reconciliation/export` | GİP uzlaştırma raporu export |

### Limit yönetimi (limit) — 24 uç

| method_adi | HTTP | path | açıklama |
|---|---|---|---|
| `approve_organization_limit_demand` | POST | `/rest/v1/limit/organization-demand/approve` | Limit değişiklik talebi onaylama |
| `cancel_organization_limit_demand` | POST | `/rest/v1/limit/organization-demand/cancel` | Limit değişiklik talebi iptal etme |
| `check_organization_waiting_demands` | POST | `/rest/v1/limit/organization-demand/check-waiting` | Onayda bekleyen talep var mı kontrolü |
| `export_organization_limit_history` | POST | `/rest/v1/limit/organization-demand/history/export` | Organizasyon limit talep geçmişi export |
| `export_organization_upper_limit_history` | POST | `/rest/v1/limit/organization-upper/history/export` | Organizasyon üst limit geçmişi export |
| `export_user_limit_history` | POST | `/rest/v1/limit/user/history/export` | Kullanıcı limit geçmişi export |
| `export_user_upper_limit_history` | POST | `/rest/v1/limit/user-upper/history/export` | Kullanıcı üst limit geçmişi export |
| `get_organization_limit` | POST | `/rest/v1/limit/organization/list` | Organizasyon limitlerini listeleme |
| `get_organization_upper_limits` | POST | `/rest/v1/limit/organization-upper/list` | Organizasyon üst limitlerini listeleme |
| `list_exist_organization_limit_demands` | POST | `/rest/v1/limit/organization-demand/exist/list` | Organizasyon limit talepleri listeleme (EPİAŞ/exist) |
| `list_exist_organization_limit_demands_export` | POST | `/rest/v1/limit/organization-demand/exist/export` | Organizasyon limit talepleri export (EPİAŞ/exist) |
| `list_organization_demand_status` | POST | `/rest/v1/limit/organization-demand/status/list` | Limit değişiklik talep durumu listeleme |
| `list_organization_limit_demand_history` | POST | `/rest/v1/limit/organization-demand/history/list` | Organizasyon limit talep geçmişi listeleme |
| `list_organization_limit_demands` | POST | `/rest/v1/limit/organization-demand/list` | Organizasyon limit talepleri listeleme |
| `list_organization_upper_limit_history` | POST | `/rest/v1/limit/organization-upper/history/list` | Organizasyon üst limit geçmişi listeleme |
| `list_user_limit_history` | POST | `/rest/v1/limit/user/history/list` | Kullanıcı limit geçmişi listeleme |
| `list_user_limits` | POST | `/rest/v1/limit/user/list` | Kullanıcı limitleri listeleme |
| `list_user_upper_limit_history` | POST | `/rest/v1/limit/user-upper/history/list` | Kullanıcı üst limit geçmişi listeleme |
| `list_user_upper_limits` | POST | `/rest/v1/limit/user-upper/list` | Kullanıcı üst limitleri listeleme |
| `save_and_approve_organization_limit_demand` | POST | `/rest/v1/limit/organization-demand/save-approve` | Limit değişikliği kaydet + onayla |
| `save_organization_limit_demands` | POST | `/rest/v1/limit/organization-demand/save` | Limit değişiklik talebi kaydetme |
| `save_organization_upper_limits` | POST | `/rest/v1/limit/organization-upper/save` | Organizasyon üst limitleri kaydetme |
| `save_user_limits` | POST | `/rest/v1/limit/user/save` | Kullanıcı limitleri kaydetme |
| `save_user_upper_limits` | POST | `/rest/v1/limit/user-upper/save` | Kullanıcı üst limitleri kaydetme |

### Dashboard / grafik (dashboard, dashboard-configs) — 19 uç

| method_adi | HTTP | path | açıklama |
|---|---|---|---|
| `contract_indicators` | POST | `/rest/v1/dashboard/contract-indicators` | Kontrat göstergeleri |
| `contract_indicators_export` | POST | `/rest/v1/dashboard/contract-indicators/export` | Kontrat göstergeleri export |
| `dashboard_configs_get` | GET | `/rest/v1/dashboard-configs` | Dashboard konfigürasyonları sorgulama |
| `dashboard_configs_save` | POST | `/rest/v1/dashboard-configs/update` | Dashboard konfigürasyon güncelleme |
| `export_daily_matches_by_exist` | POST | `/rest/v1/dashboard/daily/reconciliation/export` | Özet tablo grafiği export |
| `get_system_messages` | GET | `/rest/v1/dashboard/get-system-messages` | Sistem mesajları (swagger summary'si `${SYSTEM_MESSAGES}` placeholder — çözülmemiş i18n key) |
| `hourly_block_match` | POST | `/rest/v1/dashboard/hourly-block-match` | Saatlik blok eşleşme grafiği |
| `hourly_block_match_export` | POST | `/rest/v1/dashboard/hourly-block-match/export` | Saatlik blok eşleşme grafiği export |
| `list_announcement_message` | GET | `/rest/v1/dashboard/announcement/get` | Okunmayan mesajlar (dashboard widget'ı) |
| `list_avg_price_gap_chart` | POST | `/rest/v1/dashboard/avg-price-gap-chart` | AOF-Fiyat farkı grafiği |
| `list_avg_price_gap_chart_export` | POST | `/rest/v1/dashboard/avg-price-gap-chart/export` | AOF-Fiyat farkı grafiği export |
| `list_contract_top_ten_otr_dashboard` | POST | `/rest/v1/dashboard/contract-otr/top-ten` | Kontrat top-10 TEO dashboard'u (summary placeholder) |
| `list_daily_matches_by_exist` | POST | `/rest/v1/dashboard/daily/reconciliation` | Özet tablo grafiği |
| `list_organization_avg_price_chart` | POST | `/rest/v1/dashboard/organization-avg-price-chart` | Organizasyonun AOF-PTF grafiği |
| `list_organization_avg_price_chart_export` | POST | `/rest/v1/dashboard/organization-avg-price-chart/export` | Organizasyonun AOF-PTF grafiği export |
| `list_organization_otr_dashboard` | POST | `/rest/v1/dashboard/otr/dashboard` | Teklif Eşleşme Oran (TEO) dashboard'u |
| `list_organization_otr_dashboard_export` | POST | `/rest/v1/dashboard/otr/dashboard/export` | TEO raporu export |
| `list_top_ten_otr_dashboard` | POST | `/rest/v1/dashboard/otr/top-ten` | Top-10 TEO dashboard'u (summary placeholder) |
| `matching_max_quantity` | POST | `/rest/v1/dashboard/matching-max-quantities` | En yüksek eşleşmeler grafiği |
| `matching_min_max_price` | POST | `/rest/v1/dashboard/matching-price` | En yüksek/en düşük eşleşmeler |
| `matching_min_max_quantity` | POST | `/rest/v1/dashboard/matching-quantity/max-min` | Min/max eşleşme miktarı (summary placeholder) |
| `offer_max_quantity` | POST | `/rest/v1/dashboard/offer-max-quantities` | En yüksek teklifler grafiği |

*(Not: yukarıdaki liste 22 satır — dashboard 17 + dashboard-configs 2 tag'li olsa da bazı özet/export çiftleri tabloyu genişletti; tam sayım için swagger.json tek doğru kaynaktır.)*

### İtiraz (objection) — 9 uç

| method_adi | HTTP | path | açıklama |
|---|---|---|---|
| `get_objection_inspection` | POST | `/rest/v1/objection/admin/inspection` | İtiraz inceleme |
| `objection_export` | POST | `/rest/v1/objection/export` | İtiraz dışa aktarım |
| `objection_export_admin` | POST | `/rest/v1/objection/admin/export` | İtiraz dışa aktarım (admin) |
| `objection_list` | POST | `/rest/v1/objection/list` | İtiraz listeleme |
| `objection_list_admin` | POST | `/rest/v1/objection/admin/list` | İtiraz listeleme (admin) |
| `objection_lookup_list` | POST | `/rest/v1/objection/lookup/list` | İtiraz durum lookup listeleme |
| `objection_organization_list` | POST | `/rest/v1/objection/organization/list` | İtirazı olan organizasyonları listeleme |
| `objection_reply_screen` | POST | `/rest/v1/objection/admin/reply` | İtiraz cevabı |
| `objection_save` | POST | `/rest/v1/objection/save` | İtiraz kaydetme |

### Duyuru ve bildirim (announcement) — 8 uç

| method_adi | HTTP | path | açıklama |
|---|---|---|---|
| `create_notification` | POST | `/rest/v1/notifications/create` | SMS/mail bildirimi oluşturma |
| `delete_notification` | POST | `/rest/v1/notifications/delete` | SMS/mail bildirimi silme |
| `export_announcement` | POST | `/rest/v1/announcement/export` | Duyuru listeleme (export) |
| `filter_notification` | POST | `/rest/v1/notifications/filter` | SMS/mail bildirimleri filtreleme |
| `list_announcement` | POST | `/rest/v1/announcement/list` | Duyuru listeleme |
| `list_announcement_category` | GET | `/rest/v1/announcement/category/list` | Duyuru kategorileri |
| `list_unread_message` | GET | `/rest/v1/announcement/unread/get` | Okunmayan mesajlar |
| `read_announcement` | POST | `/rest/v1/announcement/read` | Duyuru mesajları okuma |

### Kullanıcı/organizasyon bilgisi ve lookup — 10 uç

| method_adi | HTTP | path | açıklama | grup |
|---|---|---|---|---|
| `find_user_info` | POST | `/rest/v1/user/info/detail` | Kullanıcı bilgileri | user-info |
| `get_user_info` | GET | `/rest/v1/user/info` | Kullanıcı bilgileri | user-info |
| `list_user_by_organization` | POST | `/rest/v1/user/list/by-organization` | Organizasyona göre kullanıcı listesi | user-info |
| `list_user_lookup` | POST | `/rest/v1/user/lookup` | Kullanıcı lookup | user-info |
| `logout` | GET | `/rest/v1/user/logout` | Oturum kapatma | user-info |
| `list_intraday_status` | POST | `/rest/v1/organization/intraday-status/list` | GİP katılım anlaşması durumu | organization-info |
| `list_exist_organizations` | POST | `/rest/v1/lookup/organization/exist/list` | Tanım parametre listeleme | lookup-detail |
| `list_lookup` | POST | `/rest/v1/lookup/list` | Tanım parametre listeleme | lookup-detail |
| `list_organizations` | POST | `/rest/v1/lookup/organization/list` | Tanım parametre listeleme | lookup-detail |
| `list_regions` | POST | `/rest/v1/lookup/region/list` | Tanım parametre listeleme | lookup-detail |

### İşlem geçmişi (operation-history) — 4 uç

| method_adi | HTTP | path | açıklama |
|---|---|---|---|
| `list_error_messaging` | POST | `/rest/v1/operation-history/error-messaging/list` | Hata mesajı listesi |
| `list_operation_code` | GET | `/rest/v1/operation-history/code/list` | İşlem geçmişi kategori kodları |
| `list_operation_history` | POST | `/rest/v1/operation-history/list` | İşlem geçmişi listeleme |
| `list_user` | GET | `/rest/v1/operation-history/user/list` | Kullanıcı listesi |

### TGS raporu (tgs-report) — 2 uç

| method_adi | HTTP | path | açıklama |
|---|---|---|---|
| `tgs_report_export` | POST | `/rest/v1/tgs/report/export` | TGS raporu export |
| `tgs_report_list` | POST | `/rest/v1/tgs/report/list` | TGS raporu listeleme |

İki path aynı `operationId`'yi (`list-tgs-report`) taşıyor; `SwaggerModel` bu çakışmayı path'ten türetilen isimlerle otomatik ayrıştırıyor (bkz. [[01-epint-architecture]]), ikisi de yukarıdaki adlarla ayrı ayrı erişilebilir.

### Ayarlar (configs) — 3 uç

| method_adi | HTTP | path | açıklama |
|---|---|---|---|
| `configs_get` | GET | `/rest/v1/configs` | Ayarları sorgulama |
| `configs_save` | POST | `/rest/v1/configs/update` | Ayarları güncelleme |
| `contract_table_config_update` | POST | `/rest/v1/configs/contract-table/update` | Saatlik defter konfigürasyonu güncelleme |

### Dahili / admin-panel uçları — 31 uç

Swagger'da `operationId`'si `XController_yöntem_POST/GET` desenindeydi (özel nickname verilmemiş Springfox varsayılanı), `summary`/`description` alanı **yok**. EPİAŞ'ın kendi GÜNİÇİ arayüzünün back-office ekranlarına ait olduğu düşünülüyor; `ep.gunici.*` üzerinden teknik olarak çağrılabilir ama iş senaryolarında muhtemelen ihtiyaç olmaz. `SwaggerModel` bu `Controller_yöntem_VERB` desenini "güvenilmez" sayıp method adını path'ten türetiyor (uzun `integration_controller_cancel_future_integration_system_process_post` yerine kısa `integration_cancel` gibi — bkz. [[01-epint-architecture]]).

| Eski Controller grubu | path öneki | Yeni method adı öneki | uç sayısı |
|---|---|---|---|
| `IntegrationController_*` | `/rest/v1/integration/*` | `integration_*` | 9 |
| `MenuController_*` | `/rest/v1/menu/*` | `menu_*` | 8 |
| `AnnouncementAdminController_*` | `/rest/v1/announcement/exist/*` | `announcement_exist_*` | 6 |
| `PageController_*` | `/rest/v1/page/*` | `page_*` | 5 |
| `AuthorizationController_*` | `/rest/v1/authorization/auth-info-label` | `authorization_auth_info_label` | 1 |
| `ParticipationStatusController_*` | `/rest/v1/participation/update` | `participation_update` | 1 |
| `UserController_webSocketModels_POST` | `/rest/v1/user/websocket-models` | `user_websocket_models` | 1 |

Kesin isim için `[m for m in dir(ep.gunici) if "integration" in m]` gibi filtreli `dir()` kullan ya da `print(ep.gunici.<tahmin>)` ile doğrula.

## Önemli parametreler ve gotchalar

- **Tarih formatı — timezone yok.** `gunici` kategorisinde `format: date-time` parametreleri diğer epys/şeffaflık kategorilerinden **farklı** serileştirilir: saat dilimi eklenmez, sadece `2016-04-22T00:00:00` formatı kullanılır (bkz. `DateTimeUtils.to_gunici_iso_string`, [[01-epint-architecture]] §7). `gop` kategorisinin `+0300` offset'li formatıyla veya epys/şeffaflığın `+03:00` offset'li formatıyla **karıştırma**. Elle string formatlama yapma, `str`/`datetime`/`date` ver, epint dönüştürür.
- **`tgs_report_export` / `tgs_report_list` aynı operationId'yi paylaşıyordu** (`list-tgs-report`); `SwaggerModel` artık bu tür çakışmaları path'ten türetilen isimlerle otomatik ayrıştırıyor, ikisi de yukarıdaki adlarla ayrı ayrı çağrılabilir.
- **Zorunlu body alanları endpoint'e göre değişir**, ör.:
  - `list-offers` (`OfferListReqDto`): `region`, `effectiveDateStart`, `effectiveDateEnd`, `pageInfo` **zorunlu**. Opsiyonel: `contractTypes` (`HOURLY`/`BLOCK`/`PRIVATE`), `contractStatuses` (`ACTIVE`/`PASSIVE`/`EXPIRE`), `offerType` (`BUY`/`SELL`), `offerStatuses` (`ACTIVE`/`PASSIVE`/`MATCHING`/`CANCEL`), `offerId`, `contractNames`.
  - `list-contracts` (`ContractListReqDto`): `startDate`, `endDate`, `pageInfo` **zorunlu**. Opsiyonel: `region`, `contractType`, `statuses`.
- **Teklif domain enum'ları** (swagger'da birden fazla teklif endpoint'inde tekrarlanır, md'deki GraphQL şemasıyla da doğrulandı):
  - `OfferType`: `BUY`, `SELL`
  - `OfferStatus`: `ACTIVE`, `PASSIVE`, `MATCHING`, `CANCEL`
  - `OfferOptionType`: `NORMAL`, `IOC`, `FOK`, `PRICE_LEVELED`, `ICEBERG`, `TIME_LEVELED`
  - `OfferStatusDetail`: `YE`, `GU`, `PA`, `KE`, `ZA`, `TY`, `KA`, `IP`, `TE`, `IK` (kısaltılmış durum kodları — açılımları swagger/md'de yok, ekranda gösterilen Türkçe etiketlerle eşleşir)
- **`region` parametresi vermezsen** otomatik `'TR1'` doldurulur ([[01-epint-architecture]] §5 / DEFAULT_PARAMS) — GİP'te çoklu bölge sorgusu gerekiyorsa parametreyi açıkça ver.
- **Host sabit.** `_get_host` içinde `gunici` için test/prod ayrımı **yok**, `ep.set_mode("test")` ayarlasan da her zaman `gunici.epias.com.tr` kullanılır (epys/gop kategorilerinin aksine). Test ortamına atmayı beklersen bunu unutma.
- **Auth normal.** `gunici` ne `gop` ne de `seffaflik*` olduğu için standart `TGT` + `ST` header çifti eklenir (GOP'un özel `gop-service-ticket`'ı veya şeffaflığın sadece-`TGT` davranışı **yok**).
- **Response sarmalayıcı.** Çoğu response `RestResponse<...>` şeklinde sarmalanmıştır (`status` + `correlationId` + `body`); epint bunu otomatik soyar, dönen değer doğrudan `body` içeriğidir (örn. `list-offers` → `OfferListResponseDto`: `offers` listesi + `queryInformation`).
- **Placeholder summary'ler.** Bazı dashboard endpoint'lerinin swagger `summary` alanı çözülmemiş bir i18n key'i (`${SYSTEM_MESSAGES}`, `${TOP_TEN_TEO_DASHBOARD}` vb.) — bunlar EPİAŞ tarafında bir çeviri hatası, endpoint'in kendisi çalışır durumda.

## Örnek kullanım

```python
import epint as ep

ep.set_auth(username, password)
ep.set_mode("prod")  # gunici için test/prod host aynı, ama mode başka kategorileri etkiler

# 1) Belirli tarih aralığında, TR1 bölgesinde aktif alış tekliflerini listele
offers = ep.gunici.list_offers(
    effectiveDateStart="2026-07-15T00:00:00",   # timezone YOK — gunici'ye özel
    effectiveDateEnd="2026-07-16T00:00:00",
    region="TR1",
    offerType="BUY",
    offerStatuses=["ACTIVE"],
    pageInfo={"page": 0, "size": 100},
)
for offer in offers["offers"]:
    print(offer["contractName"], offer["price"], offer["quantity"])

# 2) Belirli tarih aralığındaki saatlik kontratları listele
contracts = ep.gunici.list_contracts(
    startDate="2026-07-15T00:00:00",
    endDate="2026-07-16T00:00:00",
    contractType="HOURLY",
    pageInfo={"page": 0, "size": 500},
)

# 3) Gerçek isteği atmadan üretilen RequestModel'i incele (host/body/header doğrulama)
debug_request = ep.gunici.list_offers(
    effectiveDateStart="2026-07-15T00:00:00",
    effectiveDateEnd="2026-07-16T00:00:00",
    region="TR1",
    pageInfo={"page": 0, "size": 10},
    debug=True,
)
print(debug_request.json)   # gönderilecek JSON body
print(debug_request.headers)
```

## Kaynaklar

- Swagger (asıl kaynak, kod tarafından yüklenen): `epint/endpoints/gunici/swagger.json`
- İnsan tarafından okunabilir doküman (bu kategoride bir GraphQL introspection dökümü içeriyor, klasik kılavuz değil): `refs/ (epint kaynak reposu; portalda yok) — gunici/EPİAŞ - GÜNİÇİ Servisleri.md`
- İç mimari ve tarih formatı tablosu: [[01-epint-architecture]] (özellikle §5 host seçimi, §6 auth, §7 tarih formatları)
- Genel kullanım kuralları: [[02-epint-usage-conventions]]
- Kategori ↔ dizin eşlemesi ve `gunici` / `gunici-trading` ayrımı: [[00-epint-overview]]
