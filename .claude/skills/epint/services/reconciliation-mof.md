<!-- epint kategori referansı: reconciliation-mof — hub: ../SKILL.md -->

> **Portal:** `epint` pip ile kurulur (`requirements.txt` / Dockerfile). Swagger: kurulu pakette `epint/endpoints/<category>/swagger.json` (`python -c "import epint,pathlib; print(pathlib.Path(epint.__file__).parent)"`). Bu repoda `epint/src` veya `refs/` yok. Kurallar: `../overview.md`, `../usage-conventions.md`.

# reconciliation-mof — Piyasa İşletim Ücreti Uzlaştırma Servisi

PİÜ (Piyasa İşletim Ücreti / Market Operation Fee), EPİAŞ'ın GÖP (DAM), DGP (BPM), EDM (dengesizlik) ve GİP (IDM) piyasalarındaki işlemler üzerinden organizasyonlara uyguladığı işletim ücretidir. Bu servis kategorisi, belirli bir dönem (`period`) ve katsayı versiyonu (`version`) için organizasyona ait PİÜ tutarlarını (sabit/değişken/toplam kırılımıyla) sorgulamayı ve export etmeyi sağlar. Ayrıca GDDK Tutarı içerisinde, geçmişe dönük (retrospektif) bir revizyona ait PİÜ detaylarını görüntülemek için ayrı bir uç nokta seti içerir. Servis REST üzerine kuruludur, JSON/XML isteği kabul eder ve isteğe göre JSON/XML cevap döner.

## Ne zaman kullanılır

- Bir organizasyonun belirli bir dönem için ödediği/alacağı PİÜ tutarını (GÖP/DGP/EDM/GİP kırılımıyla, günlük detaylı veya dönem toplamı olarak) sorgulamak.
- PİÜ hesaplamasında kullanılan katsayı setini (`mofCoefficient`: dam/bpm/imbalance/idm katsayıları) ve bu setin hangi tarihten itibaren (`effectiveDate`/`version`) geçerli olduğunu görmek.
- Aynı PİÜ detayını Excel benzeri bir dosya olarak indirmek (export uç noktaları).
- GDDK Tutarı içerisinde, geçmişe dönük bir revizyon/versiyona ait PİÜ detaylarını (ve dönem özetini) görüntülemek — normal (güncel) PİÜ detayından farklı, belirli bir `version`'a kilitli retrospektif görünüm.
- PİÜ talebi oluşturma/itiraz gibi yazma işlemleri için bu servis kategorisi **kullanılamaz** — swagger'da sadece sorgulama (`list`) ve `export` uç noktaları tanımlı, talep/itiraz/onay gibi işlemler yok.

## Endpoint'ler

Swagger'da kayıtlı toplam **4 endpoint** (hepsi `POST`, tag: `recon-organization-mof-detail`):

| method_adı (snake_case) | HTTP | path | açıklama |
|---|---|---|---|
| `get_organization_mof_details` | POST | `/v1/reconciliation/mof/organization/list` | Dönemlik organizasyon PİÜ detayını JSON döner: katsayı seti (`mofCoefficient`), günlük detaylar (`details[]`) ve dönem toplamı (`total`). |
| `export_organization_mof_details` | POST | `/v1/reconciliation/mof/organization/export` | Aynı dönemlik organizasyon PİÜ detayını dosya olarak export eder (swagger şeması generic `ModelAndView`, aşağıdaki gotcha'ya bak). |
| `list_retrospective_organization_mof_details` | POST | `/v1/reconciliation/mof/organization/retrospective/list` | GDDK Tutarı içerisindeki, seçili dönem+versiyona ait PİÜ detaylarını (`details[]` + `summary`) JSON döner. |
| `export_retrospective_organization_mof_details` | POST | `/v1/reconciliation/mof/organization/retrospective/export` | Aynı retrospektif PİÜ detayını dosya olarak export eder. |

## Önemli parametreler ve gotchalar

- **Body parametreleri** — `get_organization_mof_details`/`export_organization_mof_details` için `OrganizationMofDetailReqDto`, `list_retrospective_organization_mof_details`/`export_retrospective_organization_mof_details` için `OrganizationMofDetailDiffReqDto`. İkisinin de alan seti **aynı ve tek**:
  - `period` (`date-time`, örn. `"2020-01-01T00:00:00+03:00"`) — Dönem.
  - `version` (`date-time`, örn. `"2020-01-01T00:00:00+03:00"`) — Versiyon.
  Swagger'da ikisi de `required: false` görünüyor ama pratikte `version`'sız/`period`'suz sorgu muhtemelen anlamsız/hata döner — özellikle `version`, "hangi katsayı setinin (`mofCoefficient`) uygulanacağını" belirlediği için kritik.
- **`version` bir sıra numarası değil, tarih-saat'tir**: PİÜ katsayı setleri zaman içinde revize edilir, her revizyonun `effectiveDate`'i aynı zamanda o setin `version` değeridir (örnek response'ta `mofCoefficient.version == mofCoefficient.effectiveDate == "2022-11-01T00:00:00+03:00"`). Hangi versiyonların mevcut olduğunu bilmiyorsan önce `get_organization_mof_details` ile geniş bir `period` sorgusu yapıp dönen `mofCoefficient.version` alanından öğren; rastgele bir tarih uydurma.
- **Alan grupları ve kısaltmalar** (`MarketOperationFeeDetailRespDto` / `MarketOperationFeeSummaryDto` / `MarketOperationFeeCoefficientDto`): `dam*` = GÖP (Gün Öncesi Piyasası / DAM), `bpm*` = DGP (Dengeleme Güç Piyasası / BPM), `imbalance*` = EDM (Enerji Dengesizlik Miktarı/Tutarı), `idm*` = GİP (Gün İçi Piyasası / IDM). Her grupta `Constant` (sabit tutar) + `Changeable` (değişken tutar) + `Total` (grup toplamı) üçlüsü var; **sadece `idm` grubunda ekstra `idmObjection`** (GİP ceza/itiraz tutarı) alanı bulunur, diğer gruplarda karşılığı yoktur. `total` alanı günün/dönemin dört grubun toplamıdır.
- **`details[]` günlük kırılımdır**: bir aylık dönem sorgusunda genelde ayın gün sayısı kadar (örnekte Kasım 2022 için 30) satır döner, her satırın kendi `effectiveDate`'i (o gün) vardır ama `version` alanı hepsinde **aynı** kalır (uygulanan katsayı setinin versiyonu) — `effectiveDate` ile `version`'ı birbirine karıştırma.
- **Response'ta ekstra `content` sarmalayıcısı var**: Ham REST yanıtı `status`+`correlationId`+`body` üçlüsünü içerir, epint bunu otomatik soyar (mimari kural §8), ama soyulan `body`'nin içinde bir kat daha `content` alanı bulunur (`RestResponseBodyOrganizationMofDetailRespDto.content` → `OrganizationMofDetailRespDto`, retrospektif tarafta `RestResponseBodyMofRetrospectiveDetailRespDto.content` → `MofRetrospectiveDetailRespDto`). Yani `get_organization_mof_details` sonucu genelde `{"content": {"mofCoefficient": {...}, "details": [...], "total": {...}}}` şeklinde gelir — direkt `result["details"]` bekleme, `result["content"]["details"]` olabilir; belirsizse küçük bir çağrıyla veya `debug=True` ile doğrula.
- **Retrospektif liste farklı şekil döner**: `list_retrospective_organization_mof_details` sonucu `content.details[]` (günlük, `get_organization_mof_details` ile aynı `MarketOperationFeeDetailRespDto` şeması) yanında ayrıca `content.summary` (dönem özeti, `Constant`/`Changeable`/`Total`/`idmObjection`/`total` alanları var ama `effectiveDate`/`version` yok) içerir — `mofCoefficient` alanı bu uç noktada **yok**.
- **Export uç noktaları JSON değil, dosya döndürebilir**: `export_organization_mof_details`/`export_retrospective_organization_mof_details` swagger'da generic `ModelAndView` şeması ile tanımlı (gerçek response şekli swagger'da modellenmemiş) — bu paket genelinde "export" suffix'li uç noktaların gerçek HTTP yanıtı genelde binary (XLSX/PDF) olur ve epint bunu otomatik `io.BytesIO` olarak döner (mimari kural §8, kullanım kuralı "Binary response'lar" bölümü). JSON parse edilebilir bir sonuç bekleme; ilk çağrıda `debug=True` ile veya `print(ep.mof.export_organization_mof_details)` ile şemayı doğrulamadan üretim kodunda güvenme.
- **Host/basePath'i swagger'dan okuyup hardcode etme**: bu swagger dosyasında `host: epys-qa.epias.com.tr` ve `basePath: /reconciliation-mof/servis/` yazsa da, epint gerçek host'u kategoriye göre kendisi seçer (`reconciliation-mof` → epys ailesi → `epys.epias.com.tr`, test modunda `epys-prp.epias.com.tr`) — mimari kural §5.
- **Sayfalama yok**: bu kategoride hiçbir endpoint'te `page`/`pageInfo` parametresi tanımlı değil, dolayısıyla epint'in varsayılan sayfalama davranışı (`{'number': 1, 'size': 1000}`) burada devreye girmez; `details[]` dönemdeki tüm günleri tek response'ta döner.
- **Auth**: normal EPYS akışı — `TGT` + `ST` header'ları otomatik eklenir (bu kategori `gop` veya `seffaflik*` değil, dolayısıyla GOP'un özel `gop-service-ticket`'ı veya şeffaflığın header-siz `ST` istisnası geçerli değil).

## Örnek kullanım

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# Kasım 2022 dönemi için organizasyon PİÜ detayını sorgula
result = ep.mof.get_organization_mof_details(
    period="2022-11-01T00:00:00+03:00",
    version="2022-11-01T00:00:00+03:00",
)
detail = result.get("content", result)
coefficient = detail["mofCoefficient"]
gunluk_detaylar = detail["details"]
donem_toplami = detail["total"]
```

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# GDDK Tutarı içerisindeki retrospektif (geçmişe dönük revizyon) PİÜ detayını sorgula
result = ep.reconciliation_mof.list_retrospective_organization_mof_details(
    period="2022-11-01T00:00:00+03:00",
    version="2022-11-01T00:00:00+03:00",
)
content = result.get("content", result)
details = content["details"]
summary = content["summary"]
```

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# PİÜ detayını dosya olarak export et (binary/io.BytesIO bekle)
dosya = ep.mof.export_organization_mof_details(
    period="2022-11-01T00:00:00+03:00",
    version="2022-11-01T00:00:00+03:00",
)
with open("piu_detay.xlsx", "wb") as f:
    f.write(dosya.read())
```

## Kaynaklar

- `refs/ (epint kaynak reposu; portalda yok) — reconciliation-mof/Piyasa İşletim Ücreti Uzlaştırma Servisi.md`
- `epint/endpoints/reconciliation-mof/swagger.json`
- Genel mimari: `../architecture.md`
- Genel kullanım kuralları: `../usage-conventions.md`
