<!-- epint kategori referansı: seffaflik-reporting — hub: ../SKILL.md -->

> **Portal:** `epint` pip ile kurulur (`requirements.txt` / Dockerfile). Swagger: kurulu pakette `epint/endpoints/<category>/swagger.json` (`python -c "import epint,pathlib; print(pathlib.Path(epint.__file__).parent)"`). Bu repoda `epint/src` veya `refs/` yok. Kurallar: `../overview.md`, `../usage-conventions.md`.

# seffaflik-reporting — Raporlama Servisleri

EPİAŞ Şeffaflık Platformu'nun "reporting-service" alt uygulamasıdır (swagger `basePath`: `/reporting-service`, `host`: `seffaflik.epias.com.tr`). PTF/SMF/AOF gibi piyasa fiyatlarının günlük/haftalık/aylık/çeyreklik/yıllık aritmetik ve ağırlıklı ortalamalarını, günlük raporları (KGÜP, YAL/YAT, PTF/SMF), DGP talimatlarını, GİP kontrat/teklif listelerini, elektrik piyasası fiziksel hacimlerini, YEKDEM birim maliyetini ve serbest tüketici/sayaç istatistiklerini döner. Servislerin büyük çoğunluğu aynı zamanda XLSX/CSV/PDF **export** karşılığına sahiptir (path'i `/v1/export/...` olan ayrı bir uç). Tamamı salt-okunur (sorgulama) niteliktedir, yazma/oluşturma işlemi yoktur.

## Ne zaman kullanılır

- PTF (piyasa takas fiyatı / GÖP) veya SMF (sistem marjinal fiyatı) için günlük, haftalık, aylık, çeyreklik/yarı-yıllık/yıllık aritmetik ortalama veya ağırlıklı ortalama sorgulamak.
- AOF (gün içi piyasası ağırlıklı ortalama fiyatı) için aynı periyot kırılımlarında aritmetik ortalama sorgulamak.
- Günlük fiyat serisini (saatlik PTF/SMF, 1 ay öncekiyle karşılaştırmalı), günlük min/maks fiyatları veya günlük raporu (KGÜP/YAL/YAT dahil) sorgulamak/dışa aktarmak.
- DGP (dengeleme güç piyasası) talimatlarını (YAL/YAT fiyat-miktar) veya bunların ağırlıklı ortalamasını sorgulamak/dışa aktarmak.
- GİP (gün içi piyasası) kontrat listesini, kontrat özetini (istatistik) veya belirli bir kontrata ait teklif listesini sorgulamak/dışa aktarmak.
- Elektrik piyasası fiziksel hacimlerini (İA/GÖP/DGP/GİP/VEP, kamu-özel kırılımlı) veya dönemlik piyasa hacimlerini sorgulamak/dışa aktarmak.
- YEKDEM birim maliyeti (ve PTF'li YEKDEM birim maliyeti) veya AOPTF+YEKDEM birim maliyeti (EPDK raporlama amaçlı) sorgulamak.
- Serbest tüketici sayaç adedi / artış oranı verilerini sorgulamak.
- **Yazma/başvuru/itiraz gibi işlemler için bu kategori kullanılmaz** — swagger'da sadece listeleme (`POST` ile query, tek istisna bir `GET`) ve export uçları var.

## Auth farkı

- Bu kategori **sadece `TGT` header'ı alır**, normal `ST` (service ticket) header'ı **eklenmez** (mimari kural §6 — `seffaflik*` kategorileri GOP gibi ST/`gop-service-ticket` almaz).
- **TGT geçerliliği 2 saat sabittir ve kullanımla uzamaz** (EPYS ailesindeki 45 dk + her kullanımda yenilenen TGT davranışından farklı).
- **Host her zaman `seffaflik.epias.com.tr`'dir**, `ep.set_mode("prod"|"test")` bu kategoriyi etkilemez — test/prod ayrımı yalnızca `epys*`/`gop`/`gunici` kategorilerinde host değiştirir.
- Swagger'da 52 endpoint'in 24'ünde (data uçları) `TGT` parametre listesinde açıkça yazılıdır; **export uçlarının (17 adet) swagger parametre listesinde `TGT` hiç görünmez** (sadece `body` var) — buna bakıp TGT gerekmediğini düşünme, epint header eklemesini swagger'ın o endpoint'te listeleyip listelememesine değil **kategoriye** göre yapar (mimari §6), export çağrılarında da TGT otomatik eklenir ve zorunludur.

## Endpoint'ler

Swagger'da kayıtlı toplam **52 endpoint** (51'i `POST`, 1'i `GET`). Path prefix'e göre 4 grup halinde:

**A. Sorgulama (data) uçları — 24 adet, hepsi `POST` (1 istisna `GET`)**

| method_adı (snake_case) | HTTP | path | açıklama |
|---|---|---|---|
| `aof_average_daily_data` | POST | `/v1/aof-average/data/daily` | AOF günlük aritmetik ortalama (Epiaş web sitesi için). |
| `aof_average_default_data` | POST | `/v1/aof-average/data/default` | AOF çeyreklik/yarı-yıllık/yıllık aritmetik ortalama (üçü birlikte döner). |
| `aof_average_monthly_data` | POST | `/v1/aof-average/data/monthly` | AOF aylık aritmetik ortalama. |
| `aof_average_weekly_data` | POST | `/v1/aof-average/data/weekly` | AOF haftalık aritmetik ortalama. |
| `daily_prices` | POST | `/v1/data/daily-prices` | Günlük fiyatlar (saatlik PTF/SMF, 1 ay öncekiyle karşılaştırmalı). |
| `daily_prices_average` | POST | `/v1/data/daily-prices-average` | Günlük fiyatlar ortalama verisi. |
| `daily_prices_min_max` | POST | `/v1/data/daily-prices-min-max` | Günlük fiyatlar min/maks fiyat. |
| `daily_prices_min_max_monthly` | POST | `/v1/data/daily-prices-min-max-monthly` | Aylık min/maks fiyat. |
| `daily_prices_min_max_yearly` | POST | `/v1/data/daily-prices-min-max-yearly` | Yıllık min/maks fiyat. |
| `daily_report` | POST | `/v1/data/daily-report` | Günlük rapor (KGÜP, ikili anlaşma, YAL/YAT, PTF/SMF vb.). |
| `dgp_talimat` | POST | `/v1/data/dgp-talimat` | DGP talimatları (YAL/YAT fiyat-miktar, yerine getirilen YAL/YAT). |
| `dgp_talimat_agr_ort` | POST | `/v1/data/dgp-talimat-agr-ort` | DGP talimatları ağırlıklı ortalama. |
| `electricity_market_volume_physically` | POST | `/v1/data/electricity-market-volume-physically` | Elektrik piyasa hacimleri (fiziksel, İA kamu/özel, GÖP/DGP/GİP/VEP, toplam). |
| `eligible_consumer_and_meter_increases` | **GET** | `/v1/data/eligible-consumer-and-meter-increases` | Serbest tüketici ve sayaç artış miktarı — tarih filtresi yok. |
| `gip_kontrat` | POST | `/v1/data/gip-kontrat` | GİP kontrat listesi (kontrat id/tür/ad). |
| `idm_contract_summary` | POST | `/v1/data/idm-contract-summary` | GİP kontrat özeti (min/maks alış-satış-eşleşme fiyatı, hacim, ağırlıklı ortalama). |
| `idm_order_list` | POST | `/v1/data/idm-order-list` | GİP teklif listesi — belirli bir `contractId` için emirler. |
| `mcp_smp_arithmetic_averages` | POST | `/v1/data/mcp-smp-arithmetic-averages` | SMF ve PTF aritmetik ortalamaları (dönem bazlı, min/maks tarih dahil). |
| `mcp_smp_averages` | POST | `/v1/data/mcp-smp-averages` | SMF ve PTF günlük ağırlıklı ortalamaları. |
| `ptf_smf_periodic_price_averages` | POST | `/v1/data/periodic-price-averages` | Dönemlik (3 zamanlı: gündüz/puant/gece) fiyat ortalamaları — tarih filtresi yok. |
| `periodic_price_volume` | POST | `/v1/data/periodic-price-volume` | Dönemlik piyasa hacimleri — tarih filtresi yok. |
| `ptf_sm_sdf` | POST | `/v1/data/ptf-smf-sdf` | PTF, SMF ve SDF (pozitif/negatif dengesizlik fiyatı, sistem yönü). |
| `smp_mcp_multiple_daytime_avg` | POST | `/v1/data/smp-mcp-multiple-daytime-avg` | PTF/SMF 3 zamanlı (gündüz/puant/gece) ortalama raporu — tarih filtresi yok. |
| `stsa` | POST | `/v1/data/stsa` | Serbest tüketici sayaç adedi/artış oranı — tarih filtresi yok. |

**B. Export uçları — 17 adet, hepsi `POST`, path'leri `/v1/export/...`, karşılığı A grubundaki aynı isimli servistir**

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `daily_prices_export` | POST | `/v1/export/daily-prices` | `daily_prices`'ın export'u. |
| `daily_prices_average_export` | POST | `/v1/export/daily-prices-average` | `daily_prices_average`'ın export'u. |
| `daily_prices_min_max_export` | POST | `/v1/export/daily-prices-min-max` | `daily_prices_min_max`'ın export'u. |
| `daily_prices_min_max_monthly_export` | POST | `/v1/export/daily-prices-min-max-monthly` | `daily_prices_min_max_monthly`'ın export'u. |
| `daily_prices_min_max_yearly_export` | POST | `/v1/export/daily-prices-min-max-yearly` | `daily_prices_min_max_yearly`'ın export'u. |
| `daily_report_export` | POST | `/v1/export/daily-report` | `daily_report`'ın export'u. |
| `dgp_talimat_export` | POST | `/v1/export/dgp-talimat` | `dgp_talimat`'ın export'u. |
| `dgp_talimat_agr_ort_export` | POST | `/v1/export/dgp-talimat-agr-ort` | `dgp_talimat_agr_ort`'ın export'u. |
| `electricity_market_volume_physically_export` | POST | `/v1/export/electricity-market-volume-physically` | `electricity_market_volume_physically`'ın export'u. |
| `eligible_consumer_and_meter_increases_export` | POST | `/v1/export/eligible-consumer-and-meter-increases` | `eligible_consumer_and_meter_increases`'ın export'u (bu export'un kendisi `POST`'tur, data uçtaki `GET`'ten farklı). |
| `idm_contract_summary_export` | POST | `/v1/export/idm-contract-summary` | `idm_contract_summary`'ın export'u. |
| `idm_order_list_export` | POST | `/v1/export/idm-order-list` | `idm_order_list`'ın export'u — `contractId` zorunlu. |
| `mcp_smp_averages_export` | POST | `/v1/export/mcp-smp-averages` | `mcp_smp_averages`'ın export'u. |
| `ptf_smf_periodic_price_averages_export` | POST | `/v1/export/periodic-price-averages` | `ptf_smf_periodic_price_averages`'ın export'u. |
| `periodic_price_volume_export` | POST | `/v1/export/periodic-price-volume` | `periodic_price_volume`'ın export'u. |
| `ptf_sm_sdf_export` | POST | `/v1/export/ptf-smf-sdf` | `ptf_sm_sdf`'ın export'u. |
| `smp_mcp_multiple_daytime_avg_export` | POST | `/v1/export/smp-mcp-multiple-daytime-avg` | `smp_mcp_multiple_daytime_avg`'ın export'u. |

**C. GÖP (MCP) / SMF ortalama ve YEKDEM uçları — 11 adet, hepsi `POST`**

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `aoptf_and_yek_unit_cost_data` | POST | `/v1/market/data/avg-mcp-and-renewables-unit-cost` | AOPTF ve YEKDEM birim maliyeti (EPDK için). |
| `mcp_average_daily_data` | POST | `/v1/mcp-average/data/daily` | GÖP takas fiyatı (PTF) günlük aritmetik ortalama (Epiaş web sitesi için). |
| `mcp_average_default_data` | POST | `/v1/mcp-average/data/default` | GÖP takas fiyatı çeyreklik/yarı-yıllık/yıllık aritmetik ortalama. |
| `mcp_average_monthly_data` | POST | `/v1/mcp-average/data/monthly` | GÖP takas fiyatı aylık aritmetik ortalama. |
| `mcp_average_weekly_data` | POST | `/v1/mcp-average/data/weekly` | GÖP takas fiyatı haftalık aritmetik ortalama. |
| `renewables_unit_cost_data` | POST | `/v1/renewables/data/renewables-unit-cost` | YEKDEM birim maliyeti (EPDK için). |
| `renewables_unit_cost_mcp_data` | POST | `/v1/renewables/data/renewables-unit-cost-mcp` | YEKDEM birim maliyeti PTF (EPDK için). |
| `smp_average_daily_data` | POST | `/v1/smp-average/data/daily` | SMF günlük aritmetik ortalama (Epiaş web sitesi için). |
| `smp_average_default_data` | POST | `/v1/smp-average/data/default` | SMF çeyreklik/yarı-yıllık/yıllık aritmetik ortalama. |
| `smp_average_monthly_data` | POST | `/v1/smp-average/data/monthly` | SMF aylık aritmetik ortalama. |
| `smp_average_weekly_data` | POST | `/v1/smp-average/data/weekly` | SMF haftalık aritmetik ortalama. |

**Not — MCP/SMP isimlendirmesi:** Swagger'da "mcp" = PTF (piyasa takas fiyatı/GÖP), "smp" = SMF (sistem marjinal fiyatı) karşılığıdır; İngilizce ad ile Türkçe kısaltma birebir örtüşmez, path/method adına bakıp "mcp" gördüğünde PTF verisi geldiğini unutma.

## Önemli parametreler ve gotchalar

- **Bu kategoride `region`/`regionCode` alanı yoktur** — swagger'daki hiçbir DTO'da böyle bir property tanımlı değil, dolayısıyla epint'in "vermezsen otomatik `TR1`" davranışı (mimari §5) burada hiç tetiklenmez; bölgeye göre filtreleme imkanı bu kategoride mevcut değildir.
- **İsim yanıltıcı olabilir — "min-max-monthly"/"min-max-yearly" bir tarih ARALIĞI almaz.** `daily_prices*` ailesi (`daily_prices`, `daily_prices_average`, `daily_prices_min_max`, `daily_prices_min_max_monthly`, `daily_prices_min_max_yearly`) hepsi aynı `GunlukFiyatRequestDto` şemasını kullanır: sadece **tek bir `date`** alanı + opsiyonel `page`. `startDate`/`endDate` YOK. Aynı durum `dgp_talimat` ve `dgp_talimat_agr_ort` için de geçerlidir (`DgpTalimatRequestDto`/`DgpTalimatAgrOrtRequestDto`: sadece `date`). Aylık/yıllık kırılımı server-side hesaplanır, sen tek bir referans tarih verirsin.
- **Bazı uçlar HİÇBİR tarih parametresi almaz** (sadece opsiyonel `page`): `periodic_price_volume`, `ptf_smf_periodic_price_averages`, `smp_mcp_multiple_daytime_avg`, `stsa`. `eligible_consumer_and_meter_increases` ise body'nin kendisi de yok (GET, sadece TGT header). Bunlarda client tarafından tarih filtreleme mümkün değildir — servis muhtemelen elindeki tüm dönemleri döner.
- **`page` alanı olmayan iki istisna**: `gip_kontrat` (`GipKontratRequestDto`: sadece `startDate`/`endDate`) ve `mcp_smp_arithmetic_averages` (`SmfPtfAritmetikOrtalamaRequest`: sadece `startDate`/`endDate`) — request şemasında sayfalama parametresi tanımlı değil, epint'in otomatik `page` varsayılanı (mimari §5) burada tetiklenmez; response şemasında `page` alanı olsa da bunu request'ten kontrol edemezsin.
- **Export alanı adı her yerde `exportType`'tır** (bazı diğer kategorilerde `format` olabiliyor, burada değil), enum değerleri her export DTO'sunda aynı: `XLSX`, `CSV`, `PDF`. `exportType` tüm export uçlarında zorunlu (`required`).
- **`idm_order_list`/`idm_order_list_export` için `contractId` zorunludur** (`GipKontratTekliflerRequestDto`/`ExportRequestDto`, `integer int64`) — önce `gip_kontrat` çağrısıyla kontrat listesini çekip ilgili `kontratId`'yi almanız gerekir, elle tahmini bir id vermeyin.
- **`ptf_sm_sdf` / `ptf_sm_sdf_export` isimleri "smf" değil "sm" içerir** — bu swagger'daki `operationId: "ptf-sm-sdf"` yazımının doğrudan yansımasıdır (muhtemelen orijinal kaynakta bir yazım eksikliği), `ptf_smf_sdf` diye çağırırsan epint fuzzy matching (mimari §4) ile yine bulur ama doğru/beklenen ad `ptf_sm_sdf`'tır.
- **`-default` varyantları (`aof_average_default_data`, `mcp_average_default_data`, `smp_average_default_data`) üç periyodu birlikte döner**: verilen `startDate`/`endDate` aralığına göre QUARTERLY + HALF_YEAR + YEARLY ortalamalarının tümü aynı response içinde gelir (`items[].periodType` alanına bak), ayrı bir "hangi periyot" seçim parametresi yoktur.
- **`-daily` varyantları (`aof_average_daily_data`, `mcp_average_daily_data`, `smp_average_daily_data`) "Epiaş Web Sitesi İçin" etiketlidir** — işlevsel olarak `-weekly`/`-monthly` ile aynı `BaseStartEndDateRequestDto` şemasını (`startDate`+`endDate`) kullanır, sadece EPİAŞ'ın kendi web sitesi gösterimi için ayrılmış bir varyanttır; davranış farkı yoktur.
- **Export uçları `ModelAndView` şeması dönse de gerçek response binary'dir** — epint bunu `io.BytesIO` olarak döner (mimari §8), swagger'daki `view`/`model`/`status` gibi `ModelAndView` alanlarına bakma.
- **Tüm date-time alanları epint tarafından `+HH:MM` offset'li ISO formatına çevrilir** (mimari §7, örn. `2023-01-01T00:00:00+03:00`) — `str` veya `datetime` objesi verebilirsin, elle formatlamaya çalışma.
- **Host swagger'da `seffaflik.epias.com.tr` olarak sabit yazılıdır ve gerçekten de her zaman budur** (diğer kategorilerdeki gibi test/prod ayrımı yok) — `ep.set_mode()` bu kategori için hiçbir host değişikliği yapmaz.

## Örnek kullanım

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")  # seffaflik-reporting için host değişmez ama auth akışı için gerekli

# PTF/SMF günlük ağırlıklı ortalamaları belirli bir tarih aralığında sorgula
result = ep.reporting.mcp_smp_averages(
    startDate="2026-06-01T00:00:00+03:00",
    endDate="2026-06-30T00:00:00+03:00",
)
for row in result.get("items", []):
    print(row.get("tarih"), row.get("ptfOrtalama"), row.get("smfOrtalama"))
```

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# DGP talimatlarını tek bir referans tarih ile sorgula (startDate/endDate YOK, sadece date)
result = ep.seffaflik_reporting.dgp_talimat(date="2026-07-10T00:00:00+03:00")
for row in result.get("items", []):
    print(row.get("date"), row.get("time"), row.get("ptf"), row.get("smf"))
```

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# Günlük raporu XLSX olarak dışa aktar (binary -> io.BytesIO)
xlsx_data = ep.reporting.daily_report_export(
    startDate="2026-06-01T00:00:00+03:00",
    endDate="2026-06-30T00:00:00+03:00",
    exportType="XLSX",
)
with open("gunluk_rapor.xlsx", "wb") as f:
    f.write(xlsx_data.read())
```

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# GİP kontrat listesini çek, sonra bir kontrata ait teklif listesini sorgula (contractId zorunlu)
contracts = ep.reporting.gip_kontrat(
    startDate="2026-06-01T00:00:00+03:00",
    endDate="2026-06-30T00:00:00+03:00",
)
kontrat_id = contracts["items"][0]["kontratId"]

orders = ep.reporting.idm_order_list(
    startDate="2026-06-01T00:00:00+03:00",
    endDate="2026-06-30T00:00:00+03:00",
    contractId=kontrat_id,
)
print(len(orders.get("items", [])), "teklif bulundu")
```

## Kaynaklar

- `refs/ (epint kaynak reposu; portalda yok) — seffaflik-reporting/transparency-reporting.md` (yalnızca "6. Definitions" bölümünü içerir — DTO şema/alan açıklamaları, endpoint/operationId listesi yok; asıl endpoint kaynağı swagger.json'dur)
- `epint/endpoints/seffaflik-reporting/swagger.json`
- Genel mimari: `../architecture.md`
- Genel kullanım kuralları: `../usage-conventions.md`
