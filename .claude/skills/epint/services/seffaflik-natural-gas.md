<!-- epint kategori referansı: seffaflik-natural-gas — hub: ../SKILL.md -->

> **Portal:** `epint` pip ile kurulur (`requirements.txt` / Dockerfile). Swagger: kurulu pakette `epint/endpoints/<category>/swagger.json` (`python -c "import epint,pathlib; print(pathlib.Path(epint.__file__).parent)"`). Bu repoda `epint/src` veya `refs/` yok. Kurallar: `../overview.md`, `../usage-conventions.md`.

# seffaflik-natural-gas — Doğalgaz Şeffaflık Verileri

EPİAŞ Şeffaflık Platformu'nun doğalgaz servis grubu; BOTAŞ duyuruları, Serbest Gaz Piyasası (SGP: dengesizlik, işlem hacmi/fiyatı, kodlu işlemler), Vadeli Gaz Piyasası (VGP: kontrat fiyatları, teklif fiyatları, işlem hacmi) ve iletim/depolama (transmission: kapasite, nominasyon, stok, transfer) verilerini kapsar. Swagger kaynağı `epint/endpoints/seffaflik-natural-gas/swagger.json` (`basePath: /natural-gas-service`, tamamı `v1`), 101 operasyon içerir. Çoğu operasyonun bir de `*-export` (XLSX/CSV/PDF dışa aktarma) karşılığı vardır.

## Ne zaman kullanılır

- `ep.seffaflik_natural_gas.<method_adi>(**kwargs)` veya alias'lar (`ep.naturalgas`, `ep.cng`, `ep.dogalgaz`) ile doğalgaz şeffaflık verisi çekilirken.
- Yeni bir method çağrısı yazarken doğru operationId/parametre adını bulmak için (method adları swagger `operationId` alanından üretilir, kebab-case → snake_case: `daily-reference-price` → `daily_reference_price`).
- Bir export metodunun hangi `export_type` değerlerini kabul ettiğini veya hangi tarih/period alanını beklediğini doğrularken.

## Auth farkı

- Şeffaflık servisleri (bu servis dahil) **sadece `TGT` header'ı** kullanır; normal EPYS servislerindeki `ST` header'ı burada **yoktur/geçersizdir**. Swagger'daki her operasyonun `parameters` listesinde `name: "TGT", in: "header", required: true` vardır (GET'lerde de dahil).
- Host her zaman **`seffaflik.epias.com.tr`**, basePath `/natural-gas-service` (swagger `host`/`basePath` alanları — normal EPYS host'undan farklıdır).
- TGT geçerlilik süresi şeffaflık için **2 saat** (`TGT_EXPIRE_HOURS_TRANSPARENCY = 2`, bkz. `epint/modules/authentication/auth_manager.py`). Normal EPYS TGT'si her istekte 45 dk uzarken, **şeffaflık TGT'si kullanımla uzamaz** — 2 saat dolunca yeniden TGT alınması gerekir.
- `ep.set_auth(...)` / `ep.set_mode(...)` genel kimlik doğrulama akışı aynıdır; bu servise özel ekstra bir auth adımı yoktur.

## Endpoint'ler

Toplam **101 operasyon** (50 "listeleme/data" + 50 "dışa aktarım/export" + 1 export'u olmayan GET-lookup). HTTP metodu neredeyse tamamında `POST` (body ile filtre gönderilir); sadece 5 tanesi parametresiz `GET` lookup'tır: `participant_list`, `stp_last_reconciliation_date`, `delivery_period`, `delivery_year`, `storage_facility`.

### Duyurular / Katılımcı (4)

| method_adı | HTTP | path | açıklama |
| --- | --- | --- | --- |
| `announcements` | POST | `/v1/announcements/data` | BOTAŞ duyuruları listeleme |
| `market_participant` | POST | `/v1/markets/general-data/data/market-participant` | Doğal gaz piyasa katılımcıları (SGP/VGP kayıt durumu) |
| `participant_list` | GET | `/v1/markets/general-data/data/participant-list` | Katılımcı listesi (lookup, parametresiz) |
| `market_participant_export` | POST | `/v1/markets/general-data/export/market-participant` | Piyasa katılımcıları dışa aktarım |

### SGP — Serbest Gaz Piyasası (31 listeleme + 26 export = 57)

| method_adı | HTTP | path | açıklama |
| --- | --- | --- | --- |
| `additional_notifications` | POST | `/v1/markets/sgp/data/additional-notifications` | İlave dengeleyici bildirimleri |
| `balancing_gas_price` | POST | `/v1/markets/sgp/data/balancing-gas-price` | Dengeleme Gazı Fiyatları (DGF) |
| `bast` | POST | `/v1/markets/sgp/data/bast` | Bakiye Sıfırlama Tutarı (BAST) |
| `blue_code_operation` | POST | `/v1/markets/sgp/data/blue-code-operation` | 2 kodlu işlemler |
| `daily_matched_quantity` | POST | `/v1/markets/sgp/data/daily-matched-quantity` | SGP günlük eşleşme miktarı |
| `daily_reference_price` | POST | `/v1/markets/sgp/data/daily-reference-price` | Günlük Referans Fiyatı (GRF) |
| `daily_trade_volume` | POST | `/v1/markets/sgp/data/daily-trade-volume` | SGP günlük işlem hacmi |
| `four_code_operation` | POST | `/v1/markets/sgp/data/four-code-operation` | 4 kodlu işlemler |
| `gddk_amount` | POST | `/v1/markets/sgp/data/gddk-amount` | GDDK (geriye dönük düzeltme kalemi) tutarı |
| `green_code_operation` | POST | `/v1/markets/sgp/data/green-code-operation` | 1 kodlu işlemler |
| `grf_match_quantity` | POST | `/v1/markets/sgp/data/grf-match-quantity` | GRF eşleşme miktarı |
| `grf_trade_volume` | POST | `/v1/markets/sgp/data/grf-trade-volume` | GRF işlem hacmi |
| `imbalance_amount` | POST | `/v1/markets/sgp/data/imbalance-amount` | SGP dengesizlik tutarı |
| `imbalance_system` | POST | `/v1/markets/sgp/data/imbalance-system` | Dengesizlik sistem yönü |
| `stp_last_reconciliation_date` | GET | `/v1/markets/sgp/data/last-reconciliation-date` | SGP son uzlaştırma tarihi (lookup) |
| `total_match_quantity` | POST | `/v1/markets/sgp/data/match-quantity` | SGP toplam eşleşme miktarı |
| `orange_code_operation` | POST | `/v1/markets/sgp/data/orange-code-operation` | 3 kodlu işlemler |
| `physical_realization` | POST | `/v1/markets/sgp/data/physical-realization` | Fiziki gerçekleşme |
| `sgp_price` | POST | `/v1/markets/sgp/data/sgp-price` | SGP fiyatlar |
| `shippers_imbalance_quantity` | POST | `/v1/markets/sgp/data/shippers-imbalance-quantity` | Dengesizlik taşıtan bazında miktar |
| `system_direction` | POST | `/v1/markets/sgp/data/system-direction` | Sistem yönü |
| `total_trade_volume` | POST | `/v1/markets/sgp/data/total-trade-volume` | SGP toplam işlem hacmi |
| `transaction_history` | POST | `/v1/markets/sgp/data/transaction-history` | SGP işlem akışı |
| `virtual_realization` | POST | `/v1/markets/sgp/data/virtual-realization` | Sanal gerçekleşme |
| `weekly_matched_quantity` | POST | `/v1/markets/sgp/data/weekly-matched-quantity` | SGP haftalık eşleşme miktarı |
| `weekly_ref_price` | POST | `/v1/markets/sgp/data/weekly-ref-price` | Haftalık Referans Fiyatı (HRF) |
| `weekly_trade_volume` | POST | `/v1/markets/sgp/data/weekly-trade-volume` | SGP haftalık işlem hacmi |

Yukarıdaki her `data` endpoint'i (last-reconciliation-date hariç) için birebir `*_export` karşılığı vardır: örn. `additional_notifications_export`, `balancing_gas_price_export`, `bast_export`, `blue_code_operation_export`, `daily_matched_quantity_export`, `daily_reference_price_export`, `daily_trade_volume_export`, `four_code_operation_export`, `gddk_amount_export`, `green_code_operation_export`, `grf_match_quantity_export`, `grf_trade_volume_export`, `imbalance_amount_export`, `imbalance_system_export`, `total_match_quantity_export`, `orange_code_operation_export`, `physical_realization_export`, `sgp_price_export`, `shippers_imbalance_quantity_export`, `system_direction_export`, `total_trade_volume_export`, `transaction_history_export`, `virtual_realization_export`, `weekly_matched_quantity_export`, `weekly_ref_price_export`, `weekly_trade_volume_export` (path'ler aynı, `/data/` → `/export/`).

### VGP — Vadeli Gaz Piyasası (8 listeleme + 7 export = 15)

| method_adı | HTTP | path | açıklama |
| --- | --- | --- | --- |
| `contract_price_summary` | POST | `/v1/markets/vgp/data/contract-price-summary` | VGP kontrat fiyatları özeti |
| `delivery_period` | GET | `/v1/markets/vgp/data/delivery-period` | Geçerli teslimat dönemi (Q1 vb.) listesi — lookup |
| `delivery_year` | GET | `/v1/markets/vgp/data/delivery-year` | Geçerli teslimat yılı listesi — lookup |
| `ggf` | POST | `/v1/markets/vgp/data/ggf` | VGP günlük gösterge fiyatı |
| `matching_quantity` | POST | `/v1/markets/vgp/data/matching-quantity` | VGP piyasa eşleşme miktarı (1000 Sm³/gün) |
| `open_position` | POST | `/v1/markets/vgp/data/open-position` | VGP açık pozisyon miktarı (1000 Sm³/gün) |
| `vgp_offer_price` | POST | `/v1/markets/vgp/data/vgp-offer-price` | VGP teklif fiyatları |
| `vgp_transaction_history` | POST | `/v1/markets/vgp/data/vgp-transaction-history` | VGP işlem akışı |
| `vgp_volume` | POST | `/v1/markets/vgp/data/vgp-volume` | VGP işlem hacmi |

Export karşılıkları: `contract_price_summary_export`, `ggf_export`, `matching_quantity_export`, `open_position_export`, `vgp_offer_price_export`, `vgp_transaction_history_export`, `vgp_volume_export` (delivery_period/delivery_year'ın export'u yok).

### Transmission — İletim / Depolama (14 listeleme + 13 export = 27)

| method_adı | HTTP | path | açıklama |
| --- | --- | --- | --- |
| `capacity_point` | POST | `/v1/transmission/data/capacity-point` | Kapasite nokta bilgisi (INPUT/OUTPUT) |
| `daily_actualization_amount` | POST | `/v1/transmission/data/daily-actualization-amount` | Günlük gerçekleşme miktarı |
| `day_ahead` | POST | `/v1/transmission/data/day-ahead` | Gün öncesi (UDN) ikili anlaşma miktarı |
| `day_end` | POST | `/v1/transmission/data/day-end` | Gün sonu (UDN) |
| `entry_nomination` | POST | `/v1/transmission/data/entry-nomination` | Taşıma giriş miktarı bildirimi (TMB) |
| `exit_nomination` | POST | `/v1/transmission/data/exit-nomination` | Taşıma çıkış miktarı bildirimi (TMB) |
| `max_entry_amount` | POST | `/v1/transmission/data/max-entry-amount` | Maks giriş kapasite miktarı |
| `max_exit_amount` | POST | `/v1/transmission/data/max-exit-amount` | Maks çıkış kapasite miktarı |
| `actual_realization_entry_amount` | POST | `/v1/transmission/data/realization-entry-amount` | Fiili gerçekleşme giriş miktarı |
| `actual_realization_exit_amount` | POST | `/v1/transmission/data/realization-exit-amount` | Fiili gerçekleşme çıkış miktarı |
| `rezerve_entry_amount` | POST | `/v1/transmission/data/rezerve-entry-amount` | Rezerve giriş kapasite miktarı |
| `rezerve_exit_amount` | POST | `/v1/transmission/data/rezerve-exit-amount` | Rezerve çıkış kapasite miktarı |
| `stock_amount` | POST | `/v1/transmission/data/stock-amount` | Stok miktarı |
| `storage_facility` | GET | `/v1/transmission/data/storage-facility` | Depolama tesisi listesi — lookup, parametresiz |
| `transfer` | POST | `/v1/transmission/data/transfer` | Transfer listeleme |

Export karşılıkları (`storage_facility` hariç hepsi): `daily_actualization_amount_export`, `day_ahead_export`, `day_end_export`, `entry_nomination_export`, `exit_nomination_export`, `max_entry_amount_export`, `max_exit_amount_export`, `actual_realization_entry_amount_export`, `actual_realization_exit_amount_export`, `rezerve_entry_amount_export`, `rezerve_exit_amount_export`, `stock_amount_export`, `transfer_export`.

## Önemli parametreler ve gotchalar

- **İki farklı tarih filtresi kalıbı var — karıştırma:**
  - Çoğu SGP/VGP/transmission endpoint'i `start_date` + `end_date` bekler (ISO 8601 + timezone, örn. `2023-01-01T00:00:00+03:00`).
  - Bir grup endpoint tek bir **`period`** alanı bekler (aralık değil, tek dönem/ay): `bast`, `bast_export`, `imbalance_amount`, `imbalance_amount_export`, `shippers_imbalance_quantity`, `shippers_imbalance_quantity_export`, `market_participant`, `market_participant_export`. `market_participant`/`market_participant_export` ayrıca opsiyonel `organization_id` (int) alır.
  - VGP tarafındaki bazı endpoint'ler (`contract_price_summary`, `vgp_transaction_history` ve export'ları) `is_transaction_period` (bool, **required**) + opsiyonel `delivery_year` (örn. `"2001"`) + `delivery_period` (örn. `"Q1"`) kombinasyonu kullanır — geçerli `delivery_period`/`delivery_year` değerlerini önce lookup endpoint'lerinden (`delivery_period()`, `delivery_year()`) çekmek güvenlidir.
- **Export metodları:** `*_export` operasyonları body'de ek olarak **`export_type`** ister (enum: `XLSX`, `CSV`, `PDF`, required). Response `ModelAndView` şemasıyla tanımlı olsa da fiilen binary içerik döner; epint bunu ayrıştırıp `io.BytesIO` olarak döndürür — `xlsx_data.read()` ile dosyaya yazılabilir. Export operasyonlarının çoğunda body'deki `TGT` header'ı yine zorunludur (export DTO'larında ayrıca TGT parametre tanımı yoksa da genel header kuralı geçerlidir; swagger'da bazı export operasyonlarının `parameters` listesinde TGT header'ı **açıkça yer almaz** — auth_manager/http_client katmanı header'ı otomatik ekler, kwargs'a `tgt` geçmeniz gerekmez).
- **`capacity_point`** için `point_type` (enum: `INPUT`, `OUTPUT`, required) — kapasite yönünü belirtir.
- **Sayfalama:** Birçok `data` DTO'sunda opsiyonel `page` alanı (`Page` şeması: `number`, `size`) var; README'deki genel davranışa göre varsayılan `page={'number': 1, 'size': 1000}` otomatik doldurulur, özel sayfalama için `page={'number': 2, 'size': 100}` gibi geçilebilir.
- **Parametresiz GET lookup'lar** (`participant_list`, `stp_last_reconciliation_date`, `delivery_period`, `delivery_year`, `storage_facility`) sadece TGT header'ı ister; body/tarih parametresi geçmeye çalışmak gereksizdir.
- **CamelCase/snake_case otomatik eşleşir** (epint genel özelliği): swagger'daki `startDate`, `endDate`, `exportType`, `organizationId`, `pointType`, `isTransactionPeriod`, `deliveryPeriod`, `deliveryYear` alanları Python tarafında `start_date`, `end_date`, `export_type`, `organization_id`, `point_type`, `is_transaction_period`, `delivery_period`, `delivery_year` olarak kullanılır.
- **README'deki `consumer_count_export(period=..., export_type=...)` örneği bu serviste birebir yoktur** (o örnek elektrik servisinden aktarılmış görünüyor) — bu serviste `period`+`export_type` kalıbına uyan gerçek metodlar `bast_export`, `imbalance_amount_export`, `shippers_imbalance_quantity_export`, `market_participant_export`'tur.
- `refs/ (epint kaynak reposu; portalda yok) — seffaflik-natural-gas/transparency-natural-gas.md` dosyası sadece swagger `definitions` (DTO alan açıklamaları) bölümünün Türkçe tablo halidir; path/method/auth bilgisi içermez — güncel path/method bilgisi için tek doğru kaynak `swagger.json`'dır.

## Örnek kullanım

```python
import epint as ep
from datetime import datetime

ep.set_auth("username", "password")
ep.set_mode("prod")

# 1) Tarih aralığıyla SGP dengesizlik tutarı sorgusu (start_date/end_date kalıbı)
result = ep.seffaflik_natural_gas.imbalance_system(
    start_date="2025-10-01T00:00:00+03:00",
    end_date="2025-10-31T00:00:00+03:00",
)

# 2) period + export_type kalıbı — BAST'ı XLSX olarak dışa aktar (io.BytesIO döner)
xlsx_data = ep.naturalgas.bast_export(
    period="2025-10-01T00:00:00+03:00",
    export_type="XLSX",
)
with open("bast_2025_10.xlsx", "wb") as f:
    f.write(xlsx_data.read())

# 3) VGP kontrat fiyatları — teslimat dönemi filtresi (önce geçerli değerleri lookup'la)
periods = ep.dogalgaz.delivery_period()
years = ep.dogalgaz.delivery_year()
contracts = ep.cng.contract_price_summary(
    is_transaction_period=True,
    delivery_year="2025",
    delivery_period="Q4",
)

# 4) Parametresiz lookup — depolama tesisleri
facilities = ep.seffaflik_natural_gas.storage_facility()
```

## Kaynaklar

- `epint/endpoints/seffaflik-natural-gas/swagger.json` — asıl OpenAPI kaynağı (path/method/parametre/DTO tanımları, 101 operasyon).
- `refs/ (epint kaynak reposu; portalda yok) — seffaflik-natural-gas/transparency-natural-gas.md` — DTO alanlarının Türkçe açıklama tablosu (yalnızca `definitions` bölümü; path/auth bilgisi yok).
- kurulu paket `epint` README (site-packages) — genel kullanım kalıpları (kategori alias'ları, fuzzy matching, tarih/sayfalama/export dönüşümleri, `io.BytesIO` davranışı).
- `epint/modules/authentication/auth_manager.py` — TGT/ST üretimi ve `TGT_EXPIRE_HOURS_TRANSPARENCY` (2 saat) tanımı.
