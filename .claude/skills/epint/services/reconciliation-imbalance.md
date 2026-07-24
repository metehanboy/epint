<!-- epint kategori referansı: reconciliation-imbalance — hub: ../SKILL.md -->

> **Portal:** `epint` pip ile kurulur (`requirements.txt` / Dockerfile). Swagger: kurulu pakette `epint/endpoints/<category>/swagger.json` (`python -c "import epint,pathlib; print(pathlib.Path(epint.__file__).parent)"`). Bu repoda `epint/src` veya `refs/` yok. Kurallar: `../overview.md`, `../usage-conventions.md`.

# reconciliation-imbalance — Enerji Dengesizlik Uzlaştırma Servisleri

Bu kategori, organizasyonların (ve dengeden sorumlu grup/DSG üyelerinin) saatlik/aylık **enerji dengesizlik miktarı (DM)** ve **dengesizlik tutarını (DT)** döndüren EPYS uzlaştırma servislerini kapsar. Ayrıca vadeli elektrik piyasası (VEP/EFM) limit kontrolü, geçmişe dönük değişikliklere (GDDK) bağlı dengesizlik revizyonları ve EPİAŞ iç kullanımına yönelik özet/uzlaştırma servislerini içerir. Tüm endpoint'ler `POST` metodu ve JSON body ile çalışır (query/path parametresi yoktur).

Dizin adı: `reconciliation-imbalance`. Python alias'ları: `imbalance`, `reconciliation_imbalance` (bkz. [[00-epint-overview]]). Auth: normal EPYS akışı — `TGT` + `ST` header'ları eklenir (GOP'un `gop-service-ticket`'ı veya şeffaflığın header-az akışı **değil**); host `epys.epias.com.tr` (test: `epys-prp.epias.com.tr`).

## Ne zaman kullanılır

- Bir organizasyonun veya DSG üyelerinin saatlik/aylık enerji dengesizlik miktarı/tutarını sorgularken veya export ederken.
- Geçmişe dönük değişiklik kaydı (GDDK) sonrası revize edilmiş dengesizlik farklarını incelerken.
- VEP (vadeli elektrik piyasası / EFM) limit/oran verilerini çekerken.
- İç uzlaştırma özet servislerinin (SBDT, organizasyon özeti, AOSMF) kullanıldığı senaryolarda.

## Endpoint'ler

Toplam **15 endpoint**, tamamı `POST`. Swagger `tags` alanına göre 4 grup:

### VEP / EFM limitleri (`electricity-futures-market`)

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `list_organization_efm_limits` | POST | `/v1/efm/get/limit-data` | Organizasyon bazında VEP (vadeli elektrik piyasası) limit verilerini listeler |
| `list_total_rate_efm_limits` | POST | `/v1/efm/get/limit-data/rate` | Toplam VEP limit **oranını** listeler |
| `list_total_efm_limits` | POST | `/v1/efm/get/limit-data/total` | Toplam VEP limit verilerini listeler |

### Organizasyon / DSG enerji dengesizliği (`imbalance-controller`)

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `get_organization_imbalance_details` | POST | `/v1/imbalance/list` | Organizasyonların **saatlik** dengesizlik detaylarını döner |
| `export_organization_imbalance_details` | POST | `/v1/imbalance/export` | Organizasyonların saatlik dengesizlik detaylarını dışarı aktarır (dosya) |
| `get_balance_group_imbalance_details` | POST | `/v1/imbalance/balance-group-organization/detail/list` | DSG üyelerinin enerji dengesizlik bilgilerini döner |
| `export_balance_group_organization_detail` | POST | `/v1/imbalance/balance-group-organization/detail/export` | DSG üyelerinin dengesizlik detaylarını dışarı aktarır |
| `get_balance_group_imbalance_monthly_details` | POST | `/v1/imbalance/balance-group-organization/detail/monthly/list` | DSG üyelerinin **aylık** dengesizlik bilgilerini döner |
| `export_balance_group_organization_monthly_and_hourly_details` | POST | `/v1/imbalance/balance-group-organization/detail/monthly/export` | DSG üyelerinin aylık dengesizlik bilgilerini dışarı aktarır |

### Geçmişe dönük dengesizlik / GDDK (`retrospective-imbalance-controller`)

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `get_balance_group_imbalance_difference_details` | POST | `/v1/retrospective-imbalance/list-balance-group-detail` | DSG üyelerinin aylık **GDDK** (geçmişe dönük değişiklik kaydı) değişimlerine ait dengesizlik bilgilerini döner |
| `export_balance_group_detail` | POST | `/v1/retrospective-imbalance/list-balance-group-detail/export` | Yukarıdaki GDDK detaylarını dışarı aktarır |

### İç uzlaştırma / özet servisleri (`reconciliation-internal-controller`)

Bu grubun swagger `description`'ları boş/placeholder (`"Get X Value"` / `"Get X Notes"`) — EPİAŞ iç kullanımına yönelik olabilirler, organizasyon kullanıcısı erişiminde kısıtlı olabileceklerini unutma.

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `get_organization_imbalances` | POST | `/v1/internal/reconciliation/organization/imbalance/list` | Organizasyon dengesizlik değerlerini `resolution` (HOUR/DAY/MONTH) çözünürlüğünde döner |
| `get_organization_imbalances_for_aosmf` | POST | `/v1/internal/reconciliation/organization/imbalance/aosmf` | AOSMF için organizasyon dengesizlik değerini döner (aynı `ResolutionReqDto` şeması) |
| `get_organization_summary` | POST | `/v1/internal/reconciliation/organization/summary/list` | Organizasyon uzlaştırma özetini (GÖP/GİP/VEP/regülasyon/dengesizlik kalemleri) `resolution` bazında döner |
| `get_sbdt_imbalance_amount` | POST | `/v1/internal/reconciliation/sbdt/imbalance` | SBDT dengesizlik tutarını (bölge bazlı pozitif/negatif hacim + tutar) döner |

## Önemli parametreler ve gotchalar

- **Tarih çifti + versiyon deseni**: Neredeyse tüm istek DTO'larında `effectiveDateStart`/`effectiveDateEnd` (veya tekil `period`) ve `version` alanı birlikte gelir. `version`, dengesizlik hesabının **hangi revizyonu** olduğunu belirtir — EPYS dengesizlik hesapları geçmişe dönük yeniden hesaplanabilir (bkz. GDDK grubu), dolayısıyla aynı `effectiveDate` için farklı `version` değerlerine sahip birden fazla kayıt dönebilir. `version` vermezsen genelde en güncel (son) versiyon döner; belirli bir revizyonu görmek istiyorsan açıkça geçmelisin.
- **`region` varsayılanı**: Vermezsen epint otomatik `'TR1'` kullanır (bkz. [[02-epint-usage-conventions]] §"Parametre varsayılanları"). Diğer bölgeler için (varsa) açıkça geç.
- **`resolution` enum'u**: `HOUR` / `DAY` / `MONTH` — `get_organization_imbalances`, `get_organization_imbalances_for_aosmf`, `get_organization_summary` gibi internal servislerde zorunlu ayrım noktası; yanlış resolution ile sorgulamak veri hacmini/agregasyon seviyesini tamamen değiştirir (saatlik veri isterken `MONTH` geçmek gibi hatalar sessizce yanlış granülaritede sonuç döner, hata fırlatmaz).
- **Sayfalama**: `page` (`{'number', 'size'}`) vermezsen `{'number': 1, 'size': 1000}` kullanılır (epint varsayılanı). Örnek response'da (`refs/ (epint kaynak reposu; portalda yok) — reconciliation-imbalance/*.md`) 30 günlük saatlik bir sorgu `page.total = 720` (24×30) döndürüyor — geniş tarih aralıklarında (özellikle `HOUR` resolution ile aylar/yıllar sorgularken) varsayılan `size=1000`'in yetmeyebileceğini, `page.total`'a bakıp gerekirse sayfalama yapman gerektiğini unutma.
- **Pozitif/negatif ayrımı mahsup edilmemiş halde gelir**: Response DTO'larında `positiveImbalanceVolume`/`negativeImbalanceVolume` ve `positiveBalanceGroupImbalanceVolume`/`negativeBalanceGroupImbalanceVolume` (+ karşılık gelen `...Amount` alanları) **ayrı ayrı** raporlanır, birbirine mahsup edilmemiştir. Net değeri hesaplamak istiyorsan pozitif − negatif işlemini kendin yap veya (varsa) DTO'daki hazır net alanı kullan (örn. `ImbalanceDetailDto.positiveBalanceGroupImbalanceVolume`/`negativeBalanceGroupImbalanceVolume` çifti net değil; `BalanceGroupOrganizationImbalanceDto.imbalanceVolume`/`imbalanceAmount` ise zaten nettir).
- **Sinerji (synergy) ayrımı**: DSG üyesi bazlı DTO'larda (`BalanceGroupOrganizationImbalanceDto`, `RetroBalanceGroupImbalanceDetailDto`) `positiveSynergyImbalanceVolume`/`negativeSynergyImbalanceVolume` (DSG içinde mahsuplaşmaya **dahil edilen** miktar) ile `positiveSynergyExcludeImbalanceVolume`/`negativeSynergyExcludeImbalanceVolume` (mahsuplaşma **dışında** tutulan miktar, + `...Amount` karşılıkları) ayrımı vardır — DSG'nin toplam dengesizliğini organizasyon bazlı dengesizlikten ayıran temel mekanizma budur, ikisini birbirine karıştırma.
- **Kısaltmalar** (swagger `description` alanlarından): `UEÇM` = çekiş (withdrawal, MWh), `UEVM` = üretim/veriş (generation, MWh), `DM`/`DT` = Dengesizlik Miktarı/Tutarı, `EDM DSG`/`EDT DSG` = DSG bazlı Enerji Dengesizlik Miktarı/Tutarı, `GÖP SAM/SSM` = Gün Öncesi Piyasası satın alma/satış miktarı, `İA` = İkili Anlaşma (bilateral contract) alış/satış, `GİPAM/GİPSM` = Gün İçi Piyasası alım/satış miktarı, `KEYALM/KEYATM` = yukarı/aşağı regülasyon (up/down regulation) miktarı, `VEPAM/VEPSM` = Vadeli Elektrik Piyasası (EFM) alım/satış miktarı, `NSM/NAM` = Net Satış/Alış Miktarı, `PH` = Piyasa Hacmi, `KUPSM/KUPST` = özet DTO'da geçen piyasa uzlaştırma kalemleri (KUPSM/KUPST — miktar/tutar çifti).
- **`export_*` endpoint'leri `ModelAndView` şeması döner** — pratikte binary dosya (XLSX vb.) demektir; epint bunu `io.BytesIO` olarak döndürür (bkz. [[02-epint-usage-conventions]] §"Binary response'lar"), JSON şema dönüşümü uygulanmaz.
- **`summary` bloğu**: Liste endpoint'lerinin (`get_organization_imbalance_details` vb.) response'unda `items` (satır bazlı) yanında bir de `summary` alanı gelir — sorgulanan **tüm dönem/sayfanın toplamı**dır, tek tek `items` toplayarak tekrar hesaplama yapmana gerek yok.
- **İç servisler (`reconciliation-internal-controller`)** swagger'da açıklamasız/placeholder — bu servisleri organizasyon kullanıcısı bağlamında çağırırken kalıcı 401/403 alırsan büyük olasılıkla yetki sorunudur (EPİAŞ iç kullanım için tasarlanmış olabilirler), endpoint/parametre hatası değil.

## Örnek kullanım

```python
import epint as ep

ep.set_auth(username, password)
ep.set_mode("prod")

# 1) Organizasyonun saatlik enerji dengesizlik detaylarını sorgula (TR1 varsayılan bölge)
result = ep.imbalance.get_organization_imbalance_details(
    period="2025-06-01T00:00:00+03:00",
    effectiveDateStart="2025-06-01",
    effectiveDateEnd="2025-06-30",
    page={"number": 1, "size": 1000},
)
items = result["body"]["content"]["items"]
summary = result["body"]["content"]["summary"]
toplam_sayfa = result["body"]["content"]["page"]["total"]
if toplam_sayfa > len(items):
    print("Uyarı: tüm sonuçlar alınmadı, sayfalama gerekiyor")

# 2) DSG üyelerinin aylık dengesizlik raporunu XLSX olarak dışarı aktar
xlsx_data = ep.reconciliation_imbalance.export_balance_group_organization_monthly_and_hourly_details(
    period="2025-06-01T00:00:00+03:00",
    region="TR1",
)
with open("dsg_aylik_dengesizlik.xlsx", "wb") as f:
    f.write(xlsx_data.read())

# 3) GDDK (geçmişe dönük değişiklik) sonrası revize edilmiş DSG dengesizlik farklarını incele
gddk = ep.imbalance.get_balance_group_imbalance_difference_details(
    effectiveDateStart="2025-05-01",
    effectiveDateEnd="2025-05-31",
    region="TR1",
)

# 4) İç özet servisi ile saatlik/günlük/aylık çözünürlükte organizasyon uzlaştırma özeti
ozet = ep.imbalance.get_organization_summary(
    organizationId=12345,
    effectiveDateStart="2025-06-01",
    effectiveDateEnd="2025-06-30",
    resolution="DAY",  # HOUR | DAY | MONTH
)
```

## Kaynaklar

- `refs/ (epint kaynak reposu; portalda yok) — reconciliation-imbalance/swagger.json` — insan tarafından okunabilir pretty-print swagger (paket kopyasıyla aynı içerik).
- `refs/ (epint kaynak reposu; portalda yok) — reconciliation-imbalance/EPYS - Enerji Dengesizlik Uzlaştırma Servisleri.md` — bu kategori için "kullanım kılavuzu" olarak adlandırılmış dosya; **not**: içeriği prose/endpoint açıklaması değil, `/v1/imbalance/list` benzeri bir servisin tek bir örnek JSON response'undan (saatlik, 30 günlük, `page.total=720`) ibarettir — asıl endpoint/parametre bilgisi için swagger'a güven, bu dosyayı sadece response alan adları/örnek değerleri için referans al.
- `epint/endpoints/reconciliation-imbalance/swagger.json` — paketin çalışma zamanında yüklediği asıl kaynak (15 endpoint, 4 tag: `electricity-futures-market`, `imbalance-controller`, `reconciliation-internal-controller`, `retrospective-imbalance-controller`).
- Genel epint mimarisi ve çağrı kuralları için [[01-epint-architecture]] ve [[02-epint-usage-conventions]].
