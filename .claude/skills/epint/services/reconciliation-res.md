<!-- epint kategori referansı: reconciliation-res — hub: ../SKILL.md -->

> **Portal:** `epint` pip ile kurulur (`requirements.txt` / Dockerfile). Swagger: kurulu pakette `epint/endpoints/<category>/swagger.json` (`python -c "import epint,pathlib; print(pathlib.Path(epint.__file__).parent)"`). Bu repoda `epint/src` veya `refs/` yok. Kurallar: `../overview.md`, `../usage-conventions.md`.

# reconciliation-res — YEKDEM Uzlaştırma Servisleri

RES = YEKDEM (Yenilenebilir Enerji Kaynaklarını Destekleme Mekanizması) uzlaştırma servisidir. Santral tipine göre YEKDEM birim/destek fiyatlarını, ödeme yükümlülüğü ve katılım bedeli (KB) faturalarını, LUY (Lisanssız Üretim) UEVCB faturalarını, K3 yaptırımı kayıtlarını, YETA (zaman dilimli tarife adımları) kayıtlarını ve bunların retrospektif (geçmişe dönük) yeniden hesaplarını kapsar. Swagger'da toplam **44 path** tanımlı, hepsine ayrı ayrı erişilebilir (bkz. §1 — eskiden 4 path operationId çakışması yüzünden erişilemezdi, artık çözüldü).

## Ne zaman kullanılır

- YEKDEM birim/destek fiyatlarını (min/max fiyat, destek fiyatı, yerli katkı destek fiyatı) santral tipine göre sorgulamak veya dışa aktarmak.
- LUY UEVCB faturalarını listelemek, onaylamak, iptal etmek, güncellemek veya versiyon geçmişini görmek.
- Ödeme yükümlülüğü, katılım bedeli (KB) veya yeşil tarife farkı faturalarını sorgulamak/dışa aktarmak.
- Retrospektif (geçmişe dönük, "diff-recon-*") olarak green-tariff/payment-obligation/cost-settlement yeniden hesaplarını incelemek.
- K3 yaptırımı kayıtlarını CRUD ile yönetmek veya GÖP bazlı sorgulamak.
- YETA (tek zamanlı/gündüz/puant/gece tarife adımları) kayıtlarını içe/dışa aktarmak veya listelemek.
- Bu kategori GOP/şeffaflık **değildir** — normal EPYS `TGT`+`ST` header akışı kullanılır, host `mode`'a göre `epys.epias.com.tr`/`epys-prp.epias.com.tr` olur (mimari kuralı §5-6).

## Endpoint'ler

### 1) Operasyonel öncelik — operationId çakışmaları (çözüldü)

Swagger'da **4 operationId string'i ikişer path'te tekrar ediyor**. `SwaggerModel` artık bu tür çakışmaları tespit edip path'ten türetilen isimlerle otomatik ayrıştırıyor (bkz. [[01-epint-architecture]]) — aşağıdaki 8 endpoint'in tamamı ayrı ayrı ve doğrudan path'i yansıtan adlarla erişilebilir:

| Eski (çakışan) operationId | method_adı (path'ten türetilmiş) | path |
|---|---|---|
| `export-res-reconciliation-details` | `payment_obligation_details_export` | `POST /v1/payment-obligation/details/export` |
| `export-res-reconciliation-details` | `payment_obligation_kb_export` | `POST /v1/payment-obligation/kb/export` |
| `list-res-reconciliation-details` | `payment_obligation_details_list` | `POST /v1/payment-obligation/details/list` |
| `list-res-reconciliation-details` | `payment_obligation_kb_list` | `POST /v1/payment-obligation/kb/list` |
| `list-diff-recon-green-tariffs` | `res_retrospective_green_tariff_details_export` | `POST /v1/res/retrospective/green-tariff/details/export` |
| `list-diff-recon-green-tariffs` | `res_retrospective_kb_export` | `POST /v1/res/retrospective/kb/export` |
| `export-diff-recon-green-tariffs` | `res_retrospective_green_tariff_details_list` | `POST /v1/res/retrospective/green-tariff/details/list` |
| `export-diff-recon-green-tariffs` | `res_retrospective_kb_list` | `POST /v1/res/retrospective/kb/list` |

Eskiden bu 4 operationId çakışması yüzünden 4 path'e hiçbir isimle ulaşılamıyordu ve kazanan 2 method adı ("list" adında olup export path'ine, "export" adında olup list path'ine gitmesi) yanıltıcıydı — path-türetilmiş yeni adlar artık ne yaptıklarını doğrudan söylüyor, isim/işlev tutarsızlığı kalmadı.

### 2) LUY Fatura (`luy-invoice`) — 10 endpoint

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `export_upr_retro_correction` | POST | `/v1/luy-invoice/export/upr/retro/correction` | LUY GDDK (geçmişe dönük değişiklik) raporunu XLSX/CSV/PDF dışa aktarır. |
| `approve_luy_invoice` | POST | `/v1/luy-invoice/invoice/approve` | LUY UEVCB faturasını onaylar. |
| `luy_invoice_cancelled` | POST | `/v1/luy-invoice/invoice/cancel` | LUY UEVCB faturasını iptal eder. |
| `export_luy_invoices` | POST | `/v1/luy-invoice/invoice/export` | LUY UEVCB faturalarını dışa aktarır. |
| `export_luy_invoice_history` | POST | `/v1/luy-invoice/invoice/history/export` | LUY fatura versiyon geçmişini dışa aktarır. |
| `get_luy_invoice_history` | POST | `/v1/luy-invoice/invoice/history/list` | LUY fatura versiyon geçmişini sayfalı listeler. |
| `get_luy_invoices` | POST | `/v1/luy-invoice/invoice/list` | LUY UEVCB faturalarını sayfalı listeler. |
| `update_or_create_new_luy_invoice` | POST | `/v1/luy-invoice/invoice/save` | LUY fatura tutar/açıklamasını günceller veya kaydeder. |
| `list_upr_retro_correction` | POST | `/v1/luy-invoice/list/upr/retro/correction` | LUY GDDK değişim raporunu sayfalı listeler. |
| `get_luy_invoice_statuses` | GET | `/v1/luy-invoice/lkp-invoice-status` | LUY fatura durum lookup listesini döner (parametresiz). |

### 3) Yeşil Tarife Farkı (`recon-green-tariff`) — 2 endpoint

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `export_recon_green_tariffs` | POST | `/v1/green-tariff/details/export` | Yeşil tarife farkı fatura detaylarını dışa aktarır. |
| `list_recon_green_tariffs` | POST | `/v1/green-tariff/details/list` | Yeşil tarife farkı fatura detaylarını listeler (`totalAmount` özetiyle). |

### 4) Ödeme Yükümlülüğü / Katılım Bedeli (`recon-payment-obligation`) — 6 endpoint

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `payment_obligation_details_export` | POST | `/v1/payment-obligation/details/export` | Ödeme yükümlülüğü detaylarını dışa aktarır. |
| `payment_obligation_details_list` | POST | `/v1/payment-obligation/details/list` | Ödeme yükümlülüğü detaylarını sayfalı listeler. |
| `export_recon_payment_obligations` | POST | `/v1/payment-obligation/export` | Ödeme yükümlülüğü faturalarını dışa aktarır. |
| `payment_obligation_kb_export` | POST | `/v1/payment-obligation/kb/export` | Katılım bedeli (KB) kayıtlarını dışa aktarır. |
| `payment_obligation_kb_list` | POST | `/v1/payment-obligation/kb/list` | Katılım bedeli (KB) kayıtlarını sayfalı listeler. |
| `list_recon_payment_obligations` | POST | `/v1/payment-obligation/list` | Ödeme yükümlülüğü kayıtlarını (YEK alacak/borç, YEKBED, katılım bedeli vb.) sayfalı listeler. |

### 5) RES Birim Fiyat / Santral Tipi (`res`) — 6 endpoint

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `get_power_plant_types` | POST | `/v1/res/power-plant-type/list` | Tarih aralığında geçerli YEKDEM santral tiplerini (key/value lookup) döner. |
| `calculate_unit_prices` | POST | `/v1/res/unit-price/calculate` | Belirtilen dönem için birim fiyat hesaplamasını tetikler (`BooleanDTO` döner; sonucu okumak için ayrı liste endpoint'i gerekir). |
| `get_calculation_details` | POST | `/v1/res/unit-price/coefficient-detail/list` | Birim fiyat hesaplamasında kullanılan katsayı detaylarını (TÜFE/ÜFE/döviz kuru) tarih aralığına göre sayfalı listeler. |
| `get_external_url_configurations` | POST | `/v1/res/unit-price/configuration/list` | Birim fiyat hesaplaması için dış URL/konfigürasyon lookup listesini döner. |
| `unit_prices` | POST | `/v1/res/unit-price/export` | Santral tipine göre YEKDEM birim/destek fiyatlarını dışa aktarır. |
| `get_unit_prices` | POST | `/v1/res/unit-price/list` | Santral tipine göre YEKDEM birim/destek fiyatlarını sayfalı listeler — `refs/ (epint kaynak reposu; portalda yok) — reconciliation-res/...md` dosyasındaki **tek örnek yanıt** bu endpoint'e ait (bkz. Önemli parametreler). |

### 6) Retrospektif Uzlaştırma (`res-retrospective`) — 8 endpoint

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `export_diff_recon_res_cost_settlement_point_details` | POST | `/v1/res/retrospective/detail-export` | Retrospektif RES maliyet uzlaştırma detaylarını dışa aktarır. |
| `list_diff_recon_res_cost_settlement_point_details` | POST | `/v1/res/retrospective/detail-list` | Retrospektif RES maliyet uzlaştırma detaylarını (santral/yerleşim noktası bazında) sayfalı listeler. |
| `export_diff_recon_payment_obligation` | POST | `/v1/res/retrospective/export` | Retrospektif ödeme yükümlülüğü hesabını dışa aktarır. |
| `res_retrospective_green_tariff_details_export` | POST | `/v1/res/retrospective/green-tariff/details/export` | Retrospektif yeşil tarife farkı detaylarını dışa aktarır. |
| `res_retrospective_green_tariff_details_list` | POST | `/v1/res/retrospective/green-tariff/details/list` | Retrospektif yeşil tarife farkı detaylarını sayfalı listeler. |
| `res_retrospective_kb_export` | POST | `/v1/res/retrospective/kb/export` | Retrospektif KB (katılım bedeli) kayıtlarını dışa aktarır. |
| `res_retrospective_kb_list` | POST | `/v1/res/retrospective/kb/list` | Retrospektif KB (katılım bedeli) kayıtlarını sayfalı listeler. |
| `list_diff_recon_payment_obligation` | POST | `/v1/res/retrospective/list` | Retrospektif ödeme yükümlülüğü kayıtlarını sayfalı listeler. |

### 7) RES Maliyet Uzlaştırma Toplulaştırma (`recon-res-cost-settlement-agg`) — 2 endpoint

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `export_loss_generation` | POST | `/v1/rescostsettlement/export` | Kırpılan üretim/kapasite oranı/aşağı regülasyon (`category` filtresiyle) kayıtlarını **binary** (`application/octet-stream`) dışa aktarır. |
| `list_loss_generation` | POST | `/v1/rescostsettlement/list` | Aynı kayıtları sayfalı listeler; `summary` alanında toplam Yekg üretim/maliyet/gelir döner. |

### 8) K3 Yaptırımı — 6 endpoint (swagger'da `tags` yok)

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `delete_k3_sanction` | POST | `/v1/k3-sanction/delete` | K3 yaptırımı kaydını `id` ile siler (HTTP metodu POST, DELETE değil). |
| `export_k3_sanction` | POST | `/v1/k3-sanction/export` | K3 yaptırımı kayıtlarını dışa aktarır. |
| `day_ahead_query_for_k3_sanction` | POST | `/v1/k3-sanction/gop-query` | Organizasyonun GÖP (gün öncesi piyasası) bazında K3 yaptırım durumunu sorgular. |
| `list_k3_sanction` | POST | `/v1/k3-sanction/list` | K3 yaptırımı kayıtlarını sayfalı listeler. |
| `save_k3_sanction` | POST | `/v1/k3-sanction/save` | Yeni K3 yaptırımı kaydı oluşturur. |
| `update_k3_sanction` | POST | `/v1/k3-sanction/update` | Mevcut K3 yaptırımı kaydını günceller. |

### 9) YETA — zaman dilimli tarife adımları — 4 endpoint

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `export_all_yeta_records` | POST | `/v1/yeta/export` | YETA (tek zamanlı/gündüz/puant/gece) kayıtlarını **binary** dışa aktarır. |
| `export_template_excel` | GET | `/v1/yeta/exportTemplateFile` | YETA toplu yükleme için boş Excel şablonunu döner (parametresiz). |
| `import_yeta_records` | POST | `/v1/yeta/import` | YETA kayıtlarını Excel dosyasından içe aktarır — **`multipart/form-data`**, muhtemelen epint'te çalışmıyor (bkz. gotcha #2). |
| `list_all_yeta_records` | POST | `/v1/yeta/list` | YETA kayıtlarını sayfalı listeler. |

## Önemli parametreler ve gotchalar

1. **OperationId çakışması (çözüldü)** — yukarıdaki §1 tablosuna bak. Eskiden 4 path'e hiçbir isimle ulaşılamıyordu, artık path-türetilmiş adlarla (`payment_obligation_details_*` / `payment_obligation_kb_*` / `res_retrospective_green_tariff_details_*` / `res_retrospective_kb_*`) hepsi ayrı ayrı erişilebilir ve isimler gerçekte yaptıkları işi doğru yansıtır.
2. **`import_yeta_records` muhtemelen bozuk** — swagger parametreleri `in: "formData"` (`file`, `isPreview`). `RequestModel._categorize_parameters` (`epint/models/request_model.py:516-530`) sadece `body`/`query`/`header`/`path` gruplarını tanıyor; `formData` hiçbir gruba girmiyor, dolayısıyla kullanıcının verdiği `file=`/`isPreview=` kwargs'ları hiçbir zaman gerçek isteğe eklenmiyor. Bu endpoint'i kullanmadan önce `debug=True` ile `RequestModel`'in gerçekten dosya içerdiğini doğrula; içermiyorsa bu endpoint epint üzerinden **kullanılamaz**, EPYS arayüzünden yükleme yapılmalı.
3. **`settlementPointId` tipi swagger'da yanlış** — LUY invoice DTO'larında (`LuyInvoiceApprovedReqDto`, `LuyInvoiceHistoryReqDto`, `LuyInvoiceUpdateReqDto` vb.) `settlementPointId` `type: integer, format: int64` olarak tanımlı ama `example` değeri `"40W000000000001V"` gibi bir **EIC kodu (string)**. epint format dönüşümünde (`_convert_value_by_format`) int64 alanlara `int()` uygulanır — EIC string'i gönderirsen `ValueError` alma riskin var. Gerçek değerin sayısal ID mi EIC string mi olduğunu `debug=True` ile veya küçük bir deneme çağrısıyla doğrula.
4. **`powerPlantTypes` enum'u** (`ResUnitPriceListReqDto`/`ResUnitPriceExportReqDto`) 14 değer içerir: `HYDRO`, `WIND`, `GEOTHERMAL`, `BIOMASS_LANDFILL_GAS`, `BIOMASS_BIOMETHANATION`, `BIOMASS_THERMAL_TREATMENT`, `SOLAR`, `HYDRO_RESERVOIR`, `HYDRO_RIVER`, `HYDRO_PUMPED_STORAGE`, `WIND_ONSHORE`, `WIND_OFFSHORE`, `WIND_OR_SOLAR_INTEGRATED_STORAGE`, `WAVE_OR_TIDAL`. Referans örnekte (2023 verisi) hem eski (`HYDRO`, `WIND`) hem yeni (`HYDRO_RIVER`, `WIND_ONSHORE` vb.) tipler aynı response içinde görülüyor — dönem/versiyona göre santral tipi taksonomisi değişmiş, filtreleme yaparken tek bir eski/yeni tip adına güvenme.
5. **`get_unit_prices` yanıt şekli** (referans dokümandaki tek örnekten doğrulanmış): `body` otomatik soyulduktan sonra `{"content": {"items": [...], "page": {...}}}` şeklinde bir kat daha `content` sarmalayıcısı var (mimari kuralı §8'deki genel "bir seviye soyma" yetmez). Her `items[i]`: `period`, `version`, `powerPlantType` (`{key, value}`), `minPriceTl`, `maxPriceTl`, `supportPrice`, `domesticMaterialSupportPrice`. Direkt `result["items"]` bekleme, `result["content"]["items"]` olabilir.
6. **`getPowerPlantTypes` / `get_external_url_configurations` / `get_luy_invoice_statuses`** response şemaları (`RestResponseKeyValueDto`, `RestResponseLabelValueDTO`) swagger'da `body.content` tekil bir `KeyValueDto`/`LabelValueDTO` gibi tanımlı, ama pratikte muhtemelen bir liste (`items` dizisi) döner — swagger burada otomatik/şablon üretilmiş ve isabetsiz. Gerçek şekli görmeden `result["key"]` gibi tekil alan erişimi yazma, önce çağırıp incele.
7. **`page` varsayılanı** (mimari kuralı §5): `page` parametresi olan tüm liste endpoint'lerinde (LUY liste/geçmiş, K3 liste, payment-obligation/KB liste, retrospective liste, unit-price liste, YETA liste, coefficient-detail liste, rescostsettlement liste, res-cost-settlement-agg detay liste) vermezsen otomatik `{'number': 1, 'size': 1000}` uygulanır — büyük veri setlerinde tüm sonuçları almadığını unutma.
8. **`exportType` enum'u** hemen her export endpoint'inde `XLSX`/`CSV`/`PDF` değerlerini alır (bazılarında `versions`/`periodList` gibi liste parametreleriyle birlikte, tekil `version`/`period` değil — örn. `DiffReconPaymentObligationExportReqDto.periodList`, `ReconPaymentObligationExportRequestDto.versions`). `export_loss_generation` ve `export_all_yeta_records` ise `produces: application/octet-stream` ile doğrudan binary döner — epint bunu `io.BytesIO` olarak verir (mimari kuralı §8).
9. **Türkçe iş terimleri sözlüğü** (definitions'daki Türkçe `description` alanlarından): LUY = Lisanssız Üretim, GDDK = Geçmişe Dönük Değişiklik/Düzeltme Kaydı (retro correction), OYO = Ödeme Yükümlülüğü Oranı (`ratio`), YEKBED = YEK Birim Enerji Destek fiyatı (`resPrice`), KB = Katılım Bedeli (`participantCost`/`participationCost`), YEK Alacak/Borç = `resReceivable`/`resDebt`, UEVM = Uzlaştırmaya Esas Veriş Miktarı (`generation`), KBUEVM = Katılım Bedeli UEVM'i (`participationGeneration`), YETA = zaman dilimli tarife adımları (`tekZamanli`/`gunduz`/`puant`/`gece`).
10. **K3 yaptırımı grubu** swagger'da `tags` boş, `summary`/`description` yok; alan adlarından (`effectiveDateStart/End`, `organizationId`, `description`) çıkarılan işlevler yukarıdaki tabloda verildi — resmi Türkçe açıklama swagger'da mevcut değil, EPYS arayüzünden teyit etmek gerekebilir.
11. **Host/path'i elle hardcode etme** — swagger dosyasındaki `"host": "epys-qa.epias.com.tr"` alanı **kullanılmaz**; gerçek host `ep.set_mode()`'a göre epint tarafından seçilir (mimari kuralı §5).

## Örnek kullanım

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# Belirli tarih aralığında ve santral tipinde YEKDEM birim/destek fiyatlarını listele
result = ep.res.get_unit_prices(
    effectiveDateStart="2023-04-01T00:00:00+03:00",
    effectiveDateEnd="2023-12-31T00:00:00+03:00",
    powerPlantTypes=["SOLAR", "WIND_ONSHORE"],
)
items = result.get("content", {}).get("items", result.get("items", []))
for row in items:
    print(row["period"], row["powerPlantType"]["value"], row["supportPrice"])
```

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# LUY UEVCB faturalarını sorgula ve onayla
faturalar = ep.reconciliation_res.get_luy_invoices(
    period="2026-06-01T00:00:00+03:00",
    region="TR1",
)
ep.reconciliation_res.approve_luy_invoice(
    period="2026-06-01T00:00:00+03:00",
    settlementPointId="40W000000000001V",  # EIC string olabilir, bkz. gotcha #3
)
```

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# Gerçek isteği atmadan hangi path/method'a gittiğini doğrula
req = ep.res.res_retrospective_green_tariff_details_export(period="2026-01-01T00:00:00+03:00", debug=True)
print(req)
```

## Kaynaklar

- `refs/ (epint kaynak reposu; portalda yok) — reconciliation-res/EPYS - YEKDEM Uzlaştırma Servisleri.md` — bu dosya bir kullanım kılavuzu değil, tek bir örnek JSON yanıt içeriyor (bkz. Önemli parametreler §5); ana kaynak swagger.
- `epint/endpoints/reconciliation-res/swagger.json`
- Endpoint kayıt mantığı (operationId çakışması çözümü, path-türetilmiş isimlendirme): `epint/models/swagger.py`
- Parametre kategorileme (formData desteği eksikliği kaynağı): `epint/models/request_model.py`
- Genel mimari: `../architecture.md`
- Genel kullanım kuralları: `../usage-conventions.md`
