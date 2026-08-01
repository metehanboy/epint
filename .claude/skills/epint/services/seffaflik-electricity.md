<!-- epint kategori referansı: seffaflik-electricity — hub: ../SKILL.md -->

> **Portal:** `epint` pip ile kurulur (`requirements.txt` / Dockerfile). Swagger: kurulu pakette `epint/endpoints/<category>/swagger.json` (`python -c "import epint,pathlib; print(pathlib.Path(epint.__file__).parent)"`). Bu repoda `epint/src` veya `refs/` yok. Kurallar: `../overview.md`, `../usage-conventions.md`.

# seffaflik-electricity — Elektrik Şeffaflık Verileri

Bu kategori, EPİAŞ Şeffaflık Platformu'nun elektrik piyasasına ait verilerini sunan servis grubudur (`ep.seffaflik_electricity.*` veya kısa alias `ep.transparency.*`). Diğer EPYS servislerinden farklı olarak yarı-public bir API'dir: PTF/MCP fiyatları, üretim/tüketim verileri, dengesizlik, yan hizmetler, iletim sistemi, YEK-G, VEP gibi onlarca alt piyasa için toplam **300 endpoint** içerir — bu, `epint` paketindeki en büyük servis kategorisidir. Kaynak swagger dosyası `epint/endpoints/seffaflik-electricity/swagger.json` (~29.6k satır) ve Türkçe kullanım kılavuzu `refs/ (epint kaynak reposu; portalda yok) — seffaflik-electricity/transparency-electricity.md` (~50k satır, ağırlıklı olarak DTO şema referansı) çok büyük olduğundan asla tamamen okunmamalı; ihtiyaç halinde `Grep` ile hedefli arama yapılmalı (bkz. Kaynaklar).

## Ne zaman kullanılır

- Kullanıcı PTF (Piyasa Takas Fiyatı), MCP, GÖP/GİP/DGP/VEP/YEK-G piyasaları, üretim (KGÜP, EAK, gerçek zamanlı üretim), tüketim/talep (UEÇM, talep tahmini), dengesizlik, yan hizmetler (frekans kontrolü), baraj/hidrolik veya iletim sistemi (kapasite, kısıt maliyeti) ile ilgili elektrik şeffaflık verisi istediğinde.
- `ep.seffaflik_electricity.<method>(...)` veya `ep.transparency.<method>(...)` çağrısı yazarken doğru method/endpoint adını bulmak için.
- Kod, "seffaflik" kelimesindeki yazım hatalarını da (`seffalik`, `sffaflik`, `sefaflik` vb.) fuzzy matching ile tolere eder — kategori adını bulmakta zorlanma.

## Auth farkı

Diğer EPYS servislerinden farklı olarak:

- **Sadece `TGT` header'ı gönderilir, `ST` header'ı ASLA eklenmez.** Kod (`epint/models/endpoint_callable.py`): `if not ("gop" in self._category or "seffaflik" in self._category): request_model.headers["ST"] = ...` — yani kategori adı "seffaflik" içerdiğinde ST header hiç eklenmiyor, sadece TGT gidiyor.
- **TGT geçerlilik süresi 2 saat** (`TGT_EXPIRE_HOURS_TRANSPARENCY = 2`), diğer EPYS servislerinde 45 dakika. Ayrıca seffaflik'te süre her kullanımda **uzamıyor** (EPYS'te her kullanışta 45 dk'ya sıfırlanıyor, seffaflik'te uzamıyor — `auth_manager.py` satır 41-42).
- **Host her zaman `seffaflik.epias.com.tr`** — prod/test ayrımı yok (`_get_host`: `if "seffaflik" in self._category: return "seffaflik"`). Diğer servislerde olduğu gibi `test_mode` bu kategori için host'u etkilemiyor.
- Swagger'daki her operasyonun parametrelerinde `TGT` header açıkça `required: true` olarak tanımlı; `ST` parametresi swagger'da hiç yok.

## Endpoint kategorileri ve örnek endpoint'ler

Swagger'daki 300 endpoint, 17 controller tag'i (`data`/`export` çiftleri halinde) üzerinden mantıksal gruplara ayrılabilir. Her satırda `operationId | HTTP | path | açıklama` var. Bir konu için burada listelenmeyen bir endpoint aranıyorsa, swagger.json içinde ilgili grubun path önekine (örn. `/v1/markets/dam/`) veya controller tag'ine (örn. `markets-gop-data-controller`) göre Grep yapın.

### 1. Gün Öncesi Piyasası / PTF-MCP (`markets-gop-data-controller` + `-export-controller`, 34 endpoint)

Path öneki: `/v1/markets/dam/`. Piyasa Takas Fiyatı (PTF/MCP) burada.

| method_adi | HTTP | path | açıklama |
| --- | --- | --- | --- |
| `mcp_data` | POST | `/v1/markets/dam/data/mcp` | Piyasa Takas Fiyatı (PTF) listeleme |
| `interim_mcp_data` | POST | `/v1/markets/dam/data/interim-mcp` | Kesinleşmemiş PTF (K.PTF) |
| `gop_matching_quantity` | POST | `/v1/markets/dam/data/clearing-quantity` | GÖP eşleşme miktarı |
| `supply_demand` | POST | `/v1/markets/dam/data/supply-demand` | GÖP arz-talep |
| `day_ahead_market_trade` | POST | `/v1/markets/dam/data/day-ahead-market-trade-volume` | GÖP işlem hacmi |
| `amount_of_block_buying` / `amount_of_block_selling` | POST | `/v1/markets/dam/data/amount-of-block-{buying,selling}` | Blok alış/satış miktarı |
| `mcp_export` | POST | `/v1/markets/dam/export/mcp` | PTF export (XLSX/CSV/PDF) |

### 2. Tüketim / Talep Verileri (`consumption-data-controller` + `-export-controller`, 42 endpoint)

Path öneki: `/v1/consumption/`.

| method_adi | HTTP | path | açıklama |
| --- | --- | --- | --- |
| `consumption_quantity` | POST | `/v1/consumption/data/consumption-quantity` | Tüketim miktarları |
| `demand_forecast` | POST | `/v1/consumption/data/demand-forecast` | Talep tahmini |
| `uecm` | POST | `/v1/consumption/data/uecm` | Uzlaştırmaya Esas Çekiş Miktarı (UEÇM) |
| `realtime_consumption` | POST | `/v1/consumption/data/realtime-consumption` | Gerçek zamanlı tüketim |
| `consumer_quantity` | POST | `/v1/consumption/data/consumer-quantity` | Tüketici sayısı (il/profil grubu bazlı) |
| `planned_power_outage_data` | POST | `/v1/consumption/data/planned-power-outage-info` | Planlı kesinti bilgisi |
| `consumer_quantity_export` | POST | `/v1/consumption/export/consumer-quantity` | Export varyantı |

### 3. Üretim Verileri (`generation-data-controller` + `-export-controller`, 23 endpoint)

Path öneki: `/v1/generation/`.

| method_adi | HTTP | path | açıklama |
| --- | --- | --- | --- |
| `dpp` | POST | `/v1/generation/data/dpp` | Kesinleşmiş Günlük Üretim Planı (KGÜP) |
| `aic` | POST | `/v1/generation/data/aic` | Emre Amade Kapasite (EAK) |
| `realtime_generation` | POST | `/v1/generation/data/realtime-generation` | Gerçek zamanlı üretim |
| `sbfgp` | POST | `/v1/generation/data/sbfgp` | Kesinleştirilmiş Uzlaştırma Dönemi Üretim Planı (KUDÜP) |
| `injection_quantity` | POST | `/v1/generation/data/injection-quantity` | Uzlaştırma Esas Veriş Miktarı (UEVM) |
| `injection_quantity_powerplant_list` | GET | `/v1/generation/data/injection-quantity-powerplant-list` | UEVM Santral Listesi Servisi - `powerplant_list` gibi PARAMETRESİZ (swagger'da sadece TGT header, tarih YOK), her zaman GÜNCEL listeyi döner. |
| `powerplant_list` | GET | `/v1/generation/data/powerplant-list` | Santral listesi (parametresiz, ŞU AN aktif olanlar) |
| `powerplant_list_for_date_range` | POST | `/v1/generation/data/powerplant-list-for-date-range` | Santral listesi (tarih aralıklı — bkz. GOTCHA aşağıda, tarih parametreleri GÖRÜNÜŞTE çalışır ama davranışı beklenenden FARKLI) |
| `powerplant_generation` | POST | `/v1/generation/data/powerplant-generation` | Tek santral saatlik üretim (kaynak bazlı kırılım) |
| `powerplant_generation_bulk` | POST | `/v1/generation/data/powerplant-generation-bulk` | Çoklu santral saatlik üretim (bkz. GOTCHA — startDate FİİLEN yok sayılır) |
| `realtime_generation_export` | POST | `/v1/generation/export/realtime-generation` | Export varyantı |

### 4. Yenilenebilir Enerji / YEKDEM (`renewables-data-controller` + `-export-controller`, 36 endpoint)

Path öneki: `/v1/renewables/`. YEKDEM destekleme mekanizması, YEK bedeli, lisanssız üretim vb.

| method_adi | HTTP | path | açıklama |
| --- | --- | --- | --- |
| `licensed_generation_cost` | POST | `/v1/renewables/data/licensed-generation-cost` | YEK Bedeli (YEKBED) |
| `renewables_support_mechanism_income` | POST | `/v1/renewables/data/renewables-support-mechanism-income` | YEK Geliri (YG) |
| `licensed_realtime_generation` | POST | `/v1/renewables/data/licensed-realtime-generation` | YEKDEM gerçek zamanlı üretim |
| `unlicensed_generation_amount` / `unlicensed_generation_cost` | POST | `/v1/renewables/data/unlicensed-generation-{amount,cost}` | Lisanssız üretim miktarı/bedeli |
| `res_generation_and_forecast` | POST | `/v1/renewables/data/res-generation-and-forecast` | RES üretim ve tahmin |
| `total_cost` | POST | `/v1/renewables/data/total-cost` | Toplam gider (YEKTOB) |

### 5. İletim Sistemi (`transmission-data-controller` + `-export-controller`, 26 endpoint)

Path öneki: `/v1/transmission/`. Enterkonneksiyon, kapasite, kısıt maliyeti.

| method_adi | HTTP | path | açıklama |
| --- | --- | --- | --- |
| `capacity_demand` | POST | `/v1/transmission/data/capacity-demand` | Kapasite talepleri |
| `congestion_cost` | POST | `/v1/transmission/data/congestion-cost` | Kısıt maliyeti |
| `line_capacities` | POST | `/v1/transmission/data/line-capacities` | Hat kapasiteleri |
| `international_line_events` | POST | `/v1/transmission/data/international-line-events` | Enterkonneksiyon arıza/bakım bildirimleri |
| `nominal_capacity` | POST | `/v1/transmission/data/nominal-capacity` | Nomine kapasite |
| `zero_balance` | POST | `/v1/transmission/data/zero-balance` | Sıfır bakiye düzeltme tutarı |

### 6. YEK-G Piyasası (`markets-yekg-data-controller` + `-export-controller`, 20 endpoint)

Path öneki: `/v1/markets/yek-g/`.

| method_adi | HTTP | path | açıklama |
| --- | --- | --- | --- |
| `matching_quantity` | POST | `/v1/markets/yek-g/data/yekg-matching-quantity` | Org. YEK-G piyasa eşleşme miktarı |
| `trading_volume` | POST | `/v1/markets/yek-g/data/trading-volume` | YEK-G org. piyasa işlem hacmi |
| `bilateral_contract` | POST | `/v1/markets/yek-g/data/bilateral-contract-list` | YEK-G ikili anlaşma miktarları |
| `yekg_weighted_average_price` | POST | `/v1/markets/yek-g/data/weighted-average-price` | Ağırlıklı ortalama fiyat |

### 7. Vadeli Elektrik Piyasası - VEP (`markets-vep-data-controller` + `-export-controller`, 19 endpoint)

Path öneki: `/v1/markets/pfm/`.

| method_adi | HTTP | path | açıklama |
| --- | --- | --- | --- |
| `contract_price_summary` | POST | `/v1/markets/pfm/data/contract-price-summary` | VEP kontrat fiyatları özeti |
| `offer_price` | POST | `/v1/markets/pfm/data/offer-price` | VEP teklif fiyatları |
| `open_position` | POST | `/v1/markets/pfm/data/open-position` | VEP açık pozisyon |
| `vep_matching_quantity` | POST | `/v1/markets/pfm/data/vep-matching-quantity` | VEP eşleşme miktarı |
| `daily_index_price_data` | POST | `/v1/markets/pfm/data/ggf` | Günlük gösterge fiyatı (GGF) |

### 8. Barajlar / Hidrolik Veriler (`markets-dams-data-controller` + `-export-controller`, 18 endpoint)

Path öneki: `/v1/dams/`.

| method_adi | HTTP | path | açıklama |
| --- | --- | --- | --- |
| `active_fullness` | POST | `/v1/dams/data/active-fullness` | Aktif doluluk (%) |
| `active_volume` | POST | `/v1/dams/data/active-volume` | Aktif hacim (Hm³) |
| `dam_kot` | POST | `/v1/dams/data/dam-kot` | Kot listeleme |
| `water_energy_provision` | POST | `/v1/dams/data/water-energy-provision` | Suyun enerji karşılığı |
| `flow_rate_and_installed_power` | POST | `/v1/dams/data/flow-rate-and-installed-power` | Debi ve kurulu güç |

### 9. Gün İçi Piyasası - GİP (`markets-gip-data-controller` + `-export-controller`, 16 endpoint)

Path öneki: `/v1/markets/idm/`.

| method_adi | HTTP | path | açıklama |
| --- | --- | --- | --- |
| `gip_matching_quantity` | POST | `/v1/markets/idm/data/matching-quantity` | GİP eşleşme miktarı |
| `weighted_average_price` | POST | `/v1/markets/idm/data/weighted-average-price` | GİP ağırlıklı ortalama fiyat |
| `trade_value` | POST | `/v1/markets/idm/data/trade-value` | GİP işlem hacmi |
| `bid_offer_quantities` | POST | `/v1/markets/idm/data/bid-offer-quantities` | Teklif edilen alış/satış miktarları |

### 10. GDDK - Geriye Dönük Düzeltme (`markets-gddk-data-controller` + `-export-controller`, 10 endpoint)

Path öneki: `/v1/markets/retroactive-adjustment/`.

| method_adi | HTTP | path | açıklama |
| --- | --- | --- | --- |
| `retroactive_adjustment_sum` | POST | `/v1/markets/retroactive-adjustment/data/retroactive-adjustment-sum` | GDDK tutarı |
| `meter_count_subject_to_retroactive_adjustment` | POST | `.../meter-count-subject-to-retroactive-adjustment` | GDDK'ya konu sayaç sayısı |
| `meter_volume_subject_to_retroactive_adjustment` | POST | `.../meter-volume` | GDDK'ya konu sayaç hacim verileri |

### 11. Dengeleme Güç Piyasası - DGP/BPM (`markets-dgp-data-controller` + `-export-controller`, 8 endpoint)

Path öneki: `/v1/markets/bpm/`. (Not: burada "dgp" prefix'i epint kategori kodundaki `gop` özel işlemesinden ayrı — bu bir başka kontrolcü, `seffaflik` genel davranışı geçerli.)

| method_adi | HTTP | path | açıklama |
| --- | --- | --- | --- |
| `system_marginal_price` | POST | `/v1/markets/bpm/data/system-marginal-price` | Sistem marjinal fiyatı |
| `system_direction_data` | POST | `/v1/markets/bpm/data/system-direction` | Sistem yönü |
| `dgp_yal` | POST | `/v1/markets/bpm/data/order-summary-up` | Yük Alma (YAL) talimat miktarları |
| `dgp_yat` | POST | `/v1/markets/bpm/data/order-summary-down` | Yük Atma (YAT) talimat miktarı |

### 12. Yan Hizmetler - Frekans Kontrolü (`markets-ancillary-services-data-controller` + `-export-controller`, 8 endpoint)

Path öneki: `/v1/markets/ancillary-services/`.

| method_adi | HTTP | path | açıklama |
| --- | --- | --- | --- |
| `primary_frequency_capacity_amount` | POST | `.../primary-frequency-capacity-amount` | Primer frekans rezerv miktarı |
| `primary_frequency_capacity_price` | POST | `.../primary-frequency-capacity-price` | PFK fiyatı |
| `secondary_frequency_capacity_amount` | POST | `.../secondary-frequency-capacity-amount` | Sekonder frekans rezerv miktarı |
| `secondary_frequency_capacity_price` | POST | `.../secondary-frequency-capacity-price` | SFK fiyatı |

### 13. Dengesizlik (`markets-imbalance-data-controller` + `-export-controller`, 7 endpoint)

Path öneki: `/v1/markets/imbalance/`.

| method_adi | HTTP | path | açıklama |
| --- | --- | --- | --- |
| `imbalance_amount` | POST | `/v1/markets/imbalance/data/imbalance-amount` | Dengesizlik tutarı |
| `imbalance_quantity` | POST | `/v1/markets/imbalance/data/imbalance-quantity` | Dengesizlik miktarı |
| `dsg_imbalance_quantity` | POST | `/v1/markets/imbalance/data/dsg-imbalance-quantity` | DSG dengesizlik miktarı |

### 14. İkili Anlaşmalar (`markets-bilateral-contracts-data-controller` + `-export-controller`, 6 endpoint)

Path öneki: `/v1/markets/bilateral-contracts/`.

| method_adi | HTTP | path | açıklama |
| --- | --- | --- | --- |
| `amount_of_bilateral_contracts` | POST | `.../amount-of-bilateral-contracts` | EÜAŞ-GTŞ ikili anlaşmalar |
| `bilateral_contracts_bid_quantity` | POST | `.../bilateral-contracts-bid-quantity` | İA alış miktarı |
| `bilateral_contracts_offer_quantity` | POST | `.../bilateral-contracts-offer-quantity` | İA satış miktarı |

### 15. Dashboard / Özet Ekranlar (`dashboard-data-controller`, 8 endpoint, sadece GET)

Path öneki: `/v1/dashboard/`. Export varyantı yok.

| method_adi | HTTP | path | açıklama |
| --- | --- | --- | --- |
| `dashboard_day_ahead_market` | GET | `/v1/dashboard/day-ahead-market` | Dashboard GÖP özeti |
| `dashboard_realtime_generation` | GET | `/v1/dashboard/realtime-generation` | Dashboard gerçek zamanlı üretim |
| `dashboard_weighted_average_price` | GET | `/v1/dashboard/weighted-average-price` | Dashboard ağırlıklı ortalama fiyat |
| `intra_day_market` | GET | `/v1/dashboard/intra-day-market` | Dashboard GİP özeti |

### 16. Genel Referans & Piyasa Bilgileri (`main-data-controller`, `menu-controller`, `markets-data-controller`, `-export-controller`, `markets-general-data-*`, 19 endpoint)

Path önekleri: `/v1/main/`, `/v1/menu/`, `/v1/markets/data/`, `/v1/markets/general-data/`. Piyasa mesaj sistemi (UMM), AUF, katılımcı listeleri, şehir/ilçe listesi gibi lookup/referans servisleri.

| method_adi | HTTP | path | açıklama |
| --- | --- | --- | --- |
| `date_init` | GET | `/v1/main/date-init` | Ana tarih servisi |
| `province_list` | GET | `/v1/main/province-list` | Şehir listeleme |
| `market_message_system` | POST | `/v1/markets/data/market-message-system` | Piyasa Mesaj Sistemi (UMM) listeleme |
| `maximum_settlement_price` | POST | `/v1/markets/data/maximum-settlement-price` | Azami Uzlaştırma Fiyatı (AUF) |
| `market_participants` | POST | `/v1/markets/general-data/data/market-participants` | Piyasa katılımcıları |

## Önemli parametreler ve gotchalar

- **Tarih parametreleri**: Swagger'da alanlar `startDate`/`endDate` (bazı endpoint'lerde `period` gibi tek alan) olarak `date-time` formatında tanımlı, örnek değer `"2021-01-01T00:00:00+03:00"` (Türkiye saati +03:00). `epint`, README'de belgelendiği gibi kolaylık amaçlı `start`/`end` kwarg'larını otomatik olarak doğru alanlara eşler ve string ya da `datetime` objesi kabul edip ISO formatına çevirir.
- **Sayfalama (`page`)**: Çoğu `*RequestDto` şemasında opsiyonel `page: {"$ref": "#/definitions/Page"}` alanı var; response'larda da `items` + `page` birlikte döner. `epint` sayfalama parametrelerini otomatik varsayılan değerle doldurur (`page={'number': 1, 'size': 1000}`); büyük veri setlerinde `page` parametresini elle vererek sonraki sayfaları çekmek gerekebilir.
- **Export / binary response**: `*-export` operationId'li endpoint'ler (path'te `.../export/...`) request body'sinde `exportType: enum(XLSX, CSV, PDF)` alanı zorunlu (`required`) alır. Bu endpoint'lerin dönüşü binary'dir; `epint` bunu otomatik olarak `io.BytesIO` nesnesine çevirir (`xlsx_data.read()` ile okunabilir, `.write()` ile dosyaya yazılabilir).
- **Bölge/il/santral parametreleri**: Bazı endpoint'ler `provinceId`, `powerPlantId`, `organizationId`, `region` gibi opsiyonel filtre alanları alır (örn. talep tahmini `region` parametresi alır, varsayılan `'TR1'` epint tarafından otomatik doldurulur). Filtre uygulanmazsa genelde tüm kayıtlar / varsayılan bölge döner.
- **CamelCase/snake_case eşleştirme**: `epint`, Python tarafında `snake_case` verilen kwarg'ları swagger'daki `camelCase` alan adlarına otomatik eşler (örn. `power_plant_id` → `powerPlantId`).
- **Fuzzy method matching**: Method adında küçük yazım hataları (`mcpData` / `mcp_data`) tolere edilir; kategori adında da `seffaflik` yazım hataları (`seffalik`, `sefaflik` vb.) fuzzy olarak `seffaflik-electricity`'e eşlenir.
- **`ST` header YOK**: Bu kategoriye ait hiçbir endpoint'in swagger tanımında `ST` parametresi bulunmaz; sadece `TGT` header'ı zorunludur. Diğer EPYS kategorilerinde görülen ST-tabanlı hata ayıklama mantığı burada geçersizdir.
- **Response wrapper**: Bazı response şemaları `RestResponse` benzeri sarmalayıcı içerebilir; `epint` bunu otomatik açıp `body` alanını döndürür.

### GOTCHA: `powerplant_list_for_date_range` tarih parametreleri GÖRÜNÜŞTE çalışır, GERÇEKTE farklı davranır (canlı test, 2026-07-26)

Bu servisin `startDate`/`endDate` parametreleri **santral bazında günlük aktiflik filtresi
DEĞİLDİR** — "X santrali Y tarihinde aktif miydi" diye doğrudan sorulamaz. Canlı testle
doğrulanan gerçek davranış:

- **Dar pencere (tek gün, hatta TAM 1 AY) tarihi görmezden gelir**: `ids_for(2018-01-01,
  2018-02-01)` (gerçek 1 aylık pencere, tek gün DEĞİL) `powerplant_list()` (plain, parametresiz,
  "şu an aktif") ile **birebir aynı** id setini döndürür — 2018'i sorsanız bile bugünün listesini
  alırsınız.
- Bu "bugüne çökme" davranışı **`startDate=2018-01-01` sabitken `endDate` yaklaşık `2019-10-01`'e
  kadar** sürer (canlı bisection ile bulunan eşik). Bu tarihten SONRA endDate büyütüldükçe küme
  gerçekten farklılaşmaya/büyümeye başlar.
- **Model**: response = (ŞU AN AKTİF tüm roster, tarih parametrelerinden BAĞIMSIZ koşulsuz dahil)
  ∪ (pasif/kapanmış santraller için TEK bir "kapanma tarihi [startDate,endDate] içinde mi"
  filtresi). **Aktivasyon/komisyon tarihi için HİÇBİR sinyal yoktur** — aktif santraller her
  sorguda koşulsuz göründüğü için ne zaman başladıkları asla bu endpoint'ten tespit edilemez.
  Pasif bir santral için "ilk görüldüğü" endDate ≈ o santralin yaklaşık kapanma tarihi (ay
  çözünürlüğünde, eşikten SONRAsı için güvenilir — eşik ÖNCESİ tespitler güvenilmez, tüm o dönem
  "bugüne çökmüş" olabilir).

### GOTCHA: `powerplant_generation` (`realtime-generation`) / `powerplant_generation_bulk` (`realtime-generation-bulk`) — tek-gün sınırı VE 1000 id limiti (canlı test + swagger, 2026-07-26)

`epint`'in fuzzy method matching'i `powerplant_generation(_bulk)` adını gerçek operationId'lere
eşler: `realtime-generation` (tekli) ve `realtime-generation-bulk` (toplu). Swagger'a göre bu iki
endpoint'in ŞEMASI dahi farklı:

- **`realtime-generation`** (`RealtimeGenerationRequestDto`): `startDate`+`endDate` (ikisi de
  required) + `powerPlantId` (TEKİL). Swagger description'ı zaten uyarıyor: *"en son bir önceki
  günün verileri gelmekte, ilgili güne ait [bugünün] santral verileri çekilmek istendiğinde hatalı
  istek bilgisi dönmektedir"* — canlı testte doğrulandı: `endDate=bugün` → 400 `(BUS)SEF1149`.
  **`startDate`/`endDate` aralığı 3 AYDAN FAZLA olamaz** (canlı test, 2026-07-27): daha geniş
  aralık `400 (BUS)SEF1117` — *"Verilen tarihler tanımlanmış aralıktan (3 MONTH) fazla olamaz!"*
  ile reddedilir. Swagger'da bu sınır YAZMIYOR, sadece canlı denemede ortaya çıktı. Çok-yıllık
  bir aralık (ör. coldstart) çekilecekse ~89 günlük (3 takvim ayının güvenli altı) parçalara
  bölüp SIRALI çağrı yapılmalı (bulk'un günlük döngüsünden YİNE de çok daha az çağrı, ama TEK
  istek YETMEZ).
  **Bazı id'ler için `400 (BUS)SEF1122`** — *"Verilen Santral id(...) sistemde bulunamadı!"*
  döner (canlı test, 2026-07-27) - bu servisin bir pid'i TANIMADIĞI anlamına geliyor. Kök neden
  ARAŞTIRILDI ama KESİN bulunamadı: santralin güncel/tarihsel "aktif" durumuyla İLİŞKİLENDİRİLEMEDİ
  - bu servisin hangi id'leri tanıdığı harici bir santral kataloğundan TAHMİN EDİLEMİYOR.
  `realtime-generation-bulk` bu konuda FARKLI davranıyor - pasif/eski id'leri her zaman sorunsuz
  kabul ediyor (tasarım gereği "artık pasif olanlar dahil TÜM id'ler" için kullanılıyor). Pragmatik
  çözüm: ÖNCEDEN tahmin etmeye ÇALIŞMA, tekli servisi DENE, `SEF1122` gelirse (retry'siz, anında -
  bu KALICI bir red, transient değil) o pid/alt-aralığı bulk'a (her id'yi kabul eder) düşür.
- **`realtime-generation-bulk`** (`RealtimeGenerationBulkRequestDto`): startDate/endDate YOK,
  şemada SADECE TEKİL bir **`date`** alanı var (+ `powerPlantIds` dizisi). Yani bu servis
  TASARIM GEREĞİ tek-günlük — "aralık verip görmezden geliniyor" değil, aralık parametresi
  başından beri YOK. Çok-yıllık geriye dönük veri çekmek amacıyla **HER GÜN İÇİN AYRI ÇAĞRI**
  şart (bkz. 1000 id limiti aşağıda).
- **`powerPlantIds` en fazla 1000 olmalı** (swagger: *"1000'den fazla olmamalıdır. Mükerrer id
  girmemeye dikkat ediniz."*) — canlı testte 2229 id tek çağrıda verilince WAF 403 ("Erişim
  Talebiniz Engellendi") ile bloklandı, hata mesajı API'den DEĞİL kenar-WAF'tan geldiği için
  yanıltıcı olabilir (400/429 değil, düz 403+HTML). **Katalogdaki id'leri ≤1000'lik parçalara
  BÖLÜP her parça için ayrı çağrı yapın.**
- **Bugünün verisi YOK** (yukarıda): sadece dünden eskiye veri var, `endDate`/`date` en fazla
  dün olmalı.
- `realtime-generation-bulk` yanıtı **`powerPlantId` DEĞİL `powerPlantName`** ile döner (ör.
  `"ATATÜRK HES-40W000000000142N-641"`) — id'ye çevirmek için ayrı bir katalog (isim->id eşlemesi)
  gerekir. `realtime-generation` (tekli) ise zaten `powerPlantId` parametresiyle çağrıldığı için
  bu sorun yok, id caller'da zaten biliniyor.
- Response'ta hem kaynak-bazlı kırılım (`naturalGas`, `dammedHydro`, ... camelCase) hem de
  `total` (toplam) alanı birlikte gelir — `total` kaynak kırılımından türetilebilir.
- `page.total` bu endpoint'te de GÜVENİLMEZ bulundu (aynı sorgu farklı anlarda farklı toplam
  dönebiliyor) — diğer TPYS/EPYS pagination'larında olduğu gibi "items boş/page_size'dan kısa
  dönene kadar ilerle" deseni kullanılmalı, `page.total`'a asla güvenilmemeli.
- Rate limit bu endpoint'lerde DAHA SIKI: `RateLimit-Limit: 60;w=60` (60 istek/60sn) görüldü —
  `powerplant-list-for-date-range`'in 80/60sn'sinden düşük, pacing buna göre ayarlanmalı.

### GOTCHA: `injection_quantity` (UEVM) — AYNI 3-ay sınırı `realtime-generation`'la, ama farklı hata kodu (canlı test, 2026-07-28)

`injection_quantity` (`/v1/generation/data/injection-quantity`, tekli - `startDate`+`endDate`+
`powerplantId`+`page`) `realtime-generation` ailesiyle AYNI "generation-data-controller" grubunda
ve AYNI 3-ay sınırını taşıyor - canlı testte `export` varyantı (`/v1/generation/export/
injection-quantity`) ile doğrulandı: 6 aylık aralık (2026-01-01..2026-07-01) `400 (BUS)SEF1117`
*"Verilen tarihler tanımlanmış aralıktan (3 MONTH) fazla olamaz!"* ile reddedildi - normal (export
olmayan) `injection_quantity` da AYNI kısıtı miras alır (aynı backend kontrolü). Çözüm AYNI:
~89 günlük parçalara bölüp sıralı çağrı.

Response şeması `realtime-generation` (tekli) ile BİREBİR aynı: `date`+`hour`+`total`+kaynak
kırılımı (`naturalGas`, `dam`, ...) - `powerPlantName`/`powerPlantId` YOK (zaten tekli çağrıda id
biliniyor).

`date_init` (`/v1/main/date-init`) yanıtındaki `conciliationPeriod` alanı - "şu an FİNALİZE
EDİLMİŞ uzlaştırma dönemi" sınırını işaret eder (ör. bugün 2026-07-28 iken conciliationPeriod
2026-06-01 dönebilir - Haziran hâlâ "açık"/kesinleşmemiş demek). `injection_quantity` (UEVM =
Uzlaştırma Esas Veriş Miktarı, ismi zaten bunu ima ediyor) verisi bu döneme kadar FİNAL kabul
edilebilir - santral bazında checkpoint bu döneme ulaşmışsa servis tekrar çağrılmasına gerek yoktur
(aylık bazda doğal olarak ilerleyen bir "zaten güncel" eşiği).

## Örnek kullanım

```python
import epint as ep

# 1) PTF/MCP verisi (Gün Öncesi Piyasası)
mcp = ep.seffaflik_electricity.mcp_data(start='2025-12-10', end='2025-12-11')

# Alias ile aynı çağrı
mcp = ep.transparency.mcp_data(start='2025-12-10', end='2025-12-11')

# 2) Üretim verisi — Kesinleşmiş Günlük Üretim Planı (KGÜP)
kgup = ep.seffaflik_electricity.dpp(start='2025-12-10', end='2025-12-11')

# 3) Tüketim/talep verisi — gerçek zamanlı tüketim
realtime = ep.seffaflik_electricity.realtime_consumption(
    start='2025-12-10', end='2025-12-11'
)

# 4) Export (binary) örneği — sayaç adedi verisini XLSX olarak indirme
import io
xlsx_data: io.BytesIO = ep.seffaflik_electricity.meter_count_export(
    start='2025-12-01', end='2025-12-31', export_type='XLSX'
)
with open('sayac_adedi.xlsx', 'wb') as f:
    f.write(xlsx_data.read())

# 5) Referans/lookup servisi — bölge/il listesi (parametresiz)
provinces = ep.seffaflik_electricity.province_list()
```

## Kaynaklar

- `epint/endpoints/seffaflik-electricity/swagger.json` — asıl OpenAPI kaynağı (300 endpoint, 17 controller). Endpoint aramak için: `Grep -n '"operationId"'` veya `Grep -n '"tags"' -A 3` ile controller/endpoint eşlemesi çıkarılabilir. Belirli bir path öneki için doğrudan o path'i (`"/v1/markets/dam/`) grep'leyin.
- `refs/ (epint kaynak reposu; portalda yok) — seffaflik-electricity/transparency-electricity.md` — Türkçe kullanım kılavuzu (~50k satır, büyük kısmı DTO alan referansı, bölüm 6.x). Belirli bir DTO'nun alan açıklamalarını bulmak için `Grep -n '### 6\..*<DtoAdı>'`kullanın; genel kullanım/pagination/export bilgisi için `exportType`, `page`, `Page` terimlerini grep'leyin.
- kurulu paket `epint` README (site-packages) (satır ~83-219) — kwarg dönüşümü (`start`/`end`, `page`, `region`), binary export davranışı, fuzzy matching ve kategori alias'ları için somut örnekler.
- `epint/models/endpoint_callable.py` (satır ~47-63) — TGT/ST header ekleme mantığı, seffaflik kategorisinin ST header'ını atlaması.
- `epint/modules/authentication/auth_manager.py` (satır ~38-49) — TGT/ST geçerlilik süreleri (seffaflik: TGT 2 saat, uzamıyor).
- `epint/models/request_model.py` (satır ~61-70) — host seçimi (`seffaflik.epias.com.tr`, prod/test ayrımı yok).
