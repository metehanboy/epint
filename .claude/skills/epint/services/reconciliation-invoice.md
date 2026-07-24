<!-- epint kategori referansı: reconciliation-invoice — hub: ../SKILL.md -->

> **Portal:** `epint` pip ile kurulur (`requirements.txt` / Dockerfile). Swagger: kurulu pakette `epint/endpoints/<category>/swagger.json` (`python -c "import epint,pathlib; print(pathlib.Path(epint.__file__).parent)"`). Bu repoda `epint/src` veya `refs/` yok. Kurallar: `../overview.md`, `../usage-conventions.md`.

# reconciliation-invoice — Faturalama Servisleri

EPYS'nin faturalama (billing/invoice) uygulamasıdır; piyasa katılımcılarına kesilen aylık uzlaştırma faturalarının bildirimini, faturaya esas kalem detaylarını (KDV'li/KDV'siz), GDDK (Geriye Dönük Düzeltme Kalemi — retrospective/retro correction) tutarlarını ve cari bakiye/ekstre gibi muhasebe (Logo) entegrasyon export'larını sağlar. Ayrıca günlük/saatlik uzlaştırma özetlerini (GÖP/GİP/DSG dengesizlik tutarları, PTF/SMF vb.) döndüren ayrı bir "reconciliation-summary" alt grubu vardır. Servis REST üzerine kuruludur, JSON/XML isteği kabul eder; export uçları XLSX/CSV/PDF üretir.

## Ne zaman kullanılır

- Belirli bir dönemin aylık uzlaştırma bildirimini (fatura tebliğ/son ödeme tarihi, alacak/borç kalemleri) sorgulamak veya excel/csv/pdf olarak dışa aktarmak.
- Faturaya esas kalemlerin (KDV'li veya KDV'siz) detaylı tutarlarını listelemek/dışa aktarmak.
- GDDK (geçmişe dönük düzeltme) kalemlerinin tanımlarını veya dönemlik tutarlarını (alacak/borç, özet) sorgulamak/dışa aktarmak.
- Cari bakiye, cari ekstre veya e-arşiv fatura bilgilerini Logo (muhasebe) formatında export etmek.
- Günlük veya saatlik bazda uzlaştırma detayını (GÖP/GİP/İA/VEP/DSG dengesizlik hacim-tutar, PTF/SMF) sorgulamak/dışa aktarmak.
- Fatura talebi oluşturma, itiraz, onay gibi **yazma işlemleri için bu servis kategorisi kullanılmaz** — swagger'da sadece sorgulama (`list`/`GET` amaçlı `POST`) ve export uçları var, hepsi salt-okunur niteliktedir.

## Endpoint'ler

Swagger'da kayıtlı toplam **15 endpoint** (11'i `reconciliation-invoice-notice-controller`, 4'ü `reconciliation-summary-controller` altında). Hepsi `POST`.

| method_adı (snake_case) | HTTP | path | açıklama |
|---|---|---|---|
| `arp_balance_export` | POST | `/v1/invoice-notice/arp-balance/export` | Cari Bakiye Servisi — Logo formatında cari bakiye bilgisi export eder (binary). |
| `arp_extract_export` | POST | `/v1/invoice-notice/arp-extract/export` | Cari Ekstre Servisi — Logo formatında cari ekstre bilgisi export eder (binary). |
| `earchive_invoice_export` | POST | `/v1/invoice-notice/earchive-invoice/export` | E-Arşiv Fatura Servisi — e-arşiv fatura bilgisi export eder (binary). |
| `excel_export_reconciliation_notice` | POST | `/v1/invoice-notice/export` | Aylık uzlaştırma bildirimini excel/csv/pdf olarak dışa aktarır (binary). |
| `get_invoice_item_details_with_tax` | POST | `/v1/invoice-notice/invoice-item-with-tax/list` | Fatura Bildirimi Servisi — faturaya esas kalemlerin KDV dahil tutarlarını döner. |
| `export_invoice_item_details_with_tax` | POST | `/v1/invoice-notice/invoice-item-with-tax/list/export` | Fatura Bildirimi (KDV dahil) kalemlerini dışa aktarır (binary). |
| `get_invoice_item_details` | POST | `/v1/invoice-notice/invoice-item/list` | Fatura Kalem Tanımları — fatura kalemlerinin (KDV'siz) tanım/tutarlarını döner. |
| `get_reconciliation_notice` | POST | `/v1/invoice-notice/list` | Aylık Uzlaştırma Bildirimi — dönem bazlı bildirim listeleme servisi. |
| `get_retrospective_item_details` | POST | `/v1/invoice-notice/retrospective-item/list` | GDDK Kalem Tanımları — GDDK kalemlerinin tanımlarını döner. |
| `export_reconciliation_retrospective_notice` | POST | `/v1/invoice-notice/retrospective/export` | Dönemlik GDDK tutarlarını excel olarak dışa aktarır (binary). |
| `get_reconciliation_retrospective_notice` | POST | `/v1/invoice-notice/retrospective/list` | Dönemlik GDDK Listeleme — GDDK alacak/borç detay ve özetini döner. |
| `get_reconciliation_summary_daily` | POST | `/v1/reconciliation/detail/daily` | Günlük Uzlaştırma Detayı — günlük bazda uzlaştırma özet kalemlerini döner. |
| `get_reconciliation_summary_daily_export` | POST | `/v1/reconciliation/detail/daily/export` | Günlük Uzlaştırma Detayını excel/csv/pdf olarak dışa aktarır (binary). |
| `get_reconciliation_summary_hourly` | POST | `/v1/reconciliation/detail/hourly` | Saatlik Uzlaştırma Detayı — saatlik bazda uzlaştırma özet kalemlerini (PTF/SMF dahil) döner. |
| `get_reconciliation_summary_hourly_export` | POST | `/v1/reconciliation/detail/hourly/export` | Saatlik Uzlaştırma Detayını excel/csv/pdf olarak dışa aktarır (binary). |

**Not:** Swagger'daki `summary` metinleri (Türkçe kısa açıklamalar) kaynakta hatalı kopyalanmış — örn. `.../daily/export` ve `.../hourly/export` uçlarının `summary` alanı da "Aylık Uzlaştırma Bildirimi" yazıyor; yukarıdaki tablodaki açıklamalar path/schema'ya göre düzeltilmiştir, swagger'daki `summary` metnine güvenme.

README'deki `ep.invoice.list(...)` örneği **kısaltılmış/gösterimsel** bir örnektir — bu kategoride operationId'si tam olarak `list` olan bir endpoint **yok**. `/list` ile biten path'lerin gerçek method adları `get_reconciliation_notice`, `get_reconciliation_retrospective_notice`, `get_invoice_item_details`, `get_invoice_item_details_with_tax`, `get_retrospective_item_details`'tır.

## Önemli parametreler ve gotchalar

- **Body şemaları çok az parametrelidir**, çoğu tek bir tarih alanı ister:
  - `arp_balance_export` / `arp_extract_export` / `earchive_invoice_export` → `LogoInvoiceReqDto`: sadece `period` (date-time). **`exportType` alanı yok** — format sunucu tarafında sabit, bu üç uç için XLSX/CSV/PDF seçimi yapılamaz (diğer export uçlarından farklı).
  - `get_invoice_item_details`, `get_invoice_item_details_with_tax`, `get_retrospective_item_details`, `export_reconciliation_retrospective_notice`, `get_reconciliation_retrospective_notice` → `EffectiveDateDto`: sadece `effectiveDate` (date-time). Bu tarih tek bir dönemi değil, dönmesi beklenen **rolling pencereyi belirleyen referans tarihidir** — örn. GDDK listeleme örneğinde tek bir `effectiveDate` ile 12 aylık (`2021-10` → `2022-09`) dönem listesi dönmüştür; tek dönem beklemeyip response'taki `details[].period` alanlarını kontrol et.
  - `excel_export_reconciliation_notice`, `get_reconciliation_notice` → `ReconciliationNoticeListReqDto`: `period` + `exportType` (`XLSX`/`CSV`/`PDF`).
  - `export_invoice_item_details_with_tax` → `InvoiceItemWithTaxExportReqDto`: `effectiveDate` + `exportType`.
  - `get_reconciliation_summary_daily(_export)` / `get_reconciliation_summary_hourly(_export)` → `ReconciliationSummaryReqDto`: `period`, `version`, `region`, `effectiveDateStart`, `effectiveDateEnd`, `exportType`. Bu şemada **`page` alanı tanımlı değil** — epint'in otomatik `page` varsayılanı (`{'number': 1, 'size': 1000}`, mimari kural §5) bu body'de tetiklenmez çünkü swagger'da öyle bir alan yok; response'ta `page` (`Page`) alanı olsa da bunu client'tan kontrol eden bir parametre yok.
  - `region` alanı literal `region` adını taşıdığı için epint'in varsayılan bölge davranışı (`region`/`regionCode` verilmezse otomatik `'TR1'`, mimari kural §5) burada geçerlidir — vermezsen sessizce `'TR1'` kullanılır.
  - `version` alanı, aynı dönemin farklı hesaplama/kesinleşme çalışmalarını (finalizasyon, düzeltme) ayırt etmek için kullanılır — `period`'den bağımsız ayrı bir date-time'dır, dönemin "hangi çalıştırma"sını görmek istediğini belirtir.
- **`RestResponse` sarmalayıcısı ekstra bir kat derindir.** Mimari kural §8'e göre epint `status`+`correlationId`+`body` üçlüsünü görünce `body`'yi otomatik soyar, ama bu servislerde `body` içindeki gerçek veri de bir kat daha `content` altındadır (örn. `RestResponseRetrospectiveDetailResponseDto.body.content` → `RetrospectiveDetailResponseDto`). Yani epint'in döndürdüğü Python sonucu genelde `{"content": {...asıl veri...}}` şeklindedir — direkt `result["receivableDetails"]` bekleme, `result["content"]["receivableDetails"]` olabilir. Belirsizse `debug=True` yerine küçük bir gerçek çağrı ile şekli doğrula (`debug=True` sadece isteği gösterir, response şeklini göstermez).
- **GDDK (`get_reconciliation_retrospective_notice`) kalem kodları sabit değildir** — `refs/ (epint kaynak reposu; portalda yok) — reconciliation-invoice/EPYS - Faturalama Servisleri.md` içindeki örnek response'a göre her dönemin `details` sözlüğünde şu anahtarlar görülür: `RES_OYT` (YEK OYT), `YETA`, `MOF` (PİÜ), `RES_COST` (YEKBED), `IMBALANCE` (EDT), `RES_INCOME` (YEK Gelir), `BPM_REGULATION` (DGP), `KUPST` (KÜPST), `SUB_TOTAL` (Dönem Toplamı, `isDetail: false`), `MONTHLY_ZERO_BALANCE_ADJUSTMENT` (SBDT, `isDetail: false`), `SURPLUS_BALANCE` (Artık Bakiye, `isDetail: false`). `RBS` (Destekleme Bedeli, `isDetail: false`) örnekte **sadece 2022-04'ten sonraki dönemlerde** belirir, önceki dönemlerde hiç yok. `summary` sözlüğünde ayrıca `TOTAL_SUM` (Genel Toplam) bulunur ama bu, dönem bazlı `details` içinde **yer almaz**. Bu alanlar sabit şemayla tanımlı değil (`additionalProperties`), dolayısıyla kod yazarken belirli bir kalem koduna `[]` ile değil `.get(...)` ile eriş — dönemler arasında hangi kalemlerin bulunacağı garanti değildir.
- **`isDetail` alanı** (`InvoiceItemKeyValueDto`/`InvoiceItemDetailDto` vb.): `true` ise gerçek bir uzlaştırma kalemi, `false` ise ara/alt toplam (subtotal) satırıdır — toplama yaparken `isDetail: false` satırlarını ayrıca toplamaya dahil edip çift sayma riskine dikkat et.
- **Export uçları** (isimleri `export` içerenler veya path'i `/export` ile bitenler — toplam 8 uç: `arp_balance_export`, `arp_extract_export`, `earchive_invoice_export`, `excel_export_reconciliation_notice`, `export_invoice_item_details_with_tax`, `export_reconciliation_retrospective_notice`, `get_reconciliation_summary_daily_export`, `get_reconciliation_summary_hourly_export`) `ModelAndView` şeması dönse de gerçek response Content-Type'ı binary'dir (XLSX/CSV/PDF); epint bunları `io.BytesIO` olarak döner (mimari kural §8), swagger'daki `ModelAndView` alanlarına (`view`, `model`, `status` vb.) bakma.
- **Host/mode**: Swagger dosyasındaki `"host": "epys-prp.epias.com.tr"` sadece kaynağın üretildiği test ortamının kaydıdır — gerçek host seçimi `ep.set_mode("prod"|"test")`'e göre epint tarafından dinamik yapılır (`epys.epias.com.tr` / `epys-prp.epias.com.tr`), swagger'daki `host` alanını elle kullanma.
- **Auth**: Bu kategori `gop`/`seffaflik` değildir, dolayısıyla normal `TGT` + `ST` header çifti eklenir (mimari kural §6) — GOP'a özgü `gop-service-ticket` mantığı burada geçerli değildir.

## Örnek kullanım

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# Belirli bir dönemin aylık uzlaştırma bildirimini sorgula
result = ep.invoice.get_reconciliation_notice(period="2026-06-01T00:00:00+03:00")
notice = result.get("content", result)  # RestResponse body bir kat daha "content" içinde olabilir
print(notice.get("status"), notice.get("invoiceDate"))
```

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# GDDK dönemlik listeleme — belirli bir effectiveDate'e göre rolling pencere döner
result = ep.reconciliation_invoice.get_reconciliation_retrospective_notice(
    effectiveDate="2022-09-01T00:00:00+03:00",
)
content = result.get("content", result)
for period_row in content["receivableDetails"]["details"]:
    rbs = period_row["details"].get("RBS")  # bazı dönemlerde yok, .get kullan
    print(period_row["period"], rbs["amount"] if rbs else None)
```

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# Günlük uzlaştırma detayını XLSX olarak dışa aktar (binary -> io.BytesIO)
xlsx_data = ep.invoice.get_reconciliation_summary_daily_export(
    period="2026-06-01T00:00:00+03:00",
    version="2026-07-01T00:00:00+03:00",
    region="TR1",
    exportType="XLSX",
)
with open("gunluk_uzlastirma.xlsx", "wb") as f:
    f.write(xlsx_data.read())
```

## Kaynaklar

- `refs/ (epint kaynak reposu; portalda yok) — reconciliation-invoice/EPYS - Faturalama Servisleri.md` (tek bir örnek GDDK response JSON'u içerir, ayrıntılı prosa yoktur)
- `epint/endpoints/reconciliation-invoice/swagger.json`
- Genel mimari: `../architecture.md`
- Genel kullanım kuralları: `../usage-conventions.md`
