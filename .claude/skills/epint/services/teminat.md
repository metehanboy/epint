<!-- epint kategori referansı: teminat — hub: ../SKILL.md -->

> Kaynak: `src/epint/endpoints/teminat/swagger.json`. Kurallar: `../overview.md`, `../usage-conventions.md`.

# teminat — Teminat Servisleri

EPYS Teminat modülü. Piyasa katılımcısının teminat yükümlülüğünü kalem kalem (başlangıç, GÖGİ, ek, dengesizlik, risk, YEK, destekleme bedeli) ve rapor olarak listeler. Tüm uçlar salt okunur `POST` sorgularıdır. Auth normal EPYS akışı (`TGT`+`ST`), host varsayılan `epys`/`epys-prp` ailesi (mimari §5/§6; bu kategori `seffaflik*`/`gop`/`gunici` özel host'larına girmez).

## Swagger'ın yapısı (değiştirmeden önce oku)

- EPİAŞ tarafında teminat tek servis değil, 6 ayrı mikroservis: `gogi-collateral`, `collateral`, `imbalance-collateral`, `risk-collateral`, `rbs-collateral`, `res-collateral`. epint'te tek `teminat` kategorisinde birleştirildi; swagger `tags` alanı servisi gösterir.
- **`basePath` yok, path'ler servis önekini içerir** (`/gogi-collateral/rest/v1/...`). Bir swagger yalnızca tek basePath taşıyabildiği için böyle. `basePath: "/"` ekleme: `HTTPClient.buildurl` URL'de `//` üretir.
- Kaynak: `https://epys.epias.com.tr/<servis>/v2/api-docs` (canlı). Yalnızca "EPYS Teminat Modülü Web Servis Dokümanı v1.0"da (EPİAŞ, 26.09.2023) belgelenen 21 uç alındı; api-docs'taki dahili uçlar (actuator, takasbank, default/status vb.) bilerek dışarıda.
- `index-ac` ile aynı dönüşümler: header parametreleri (`TGT`, `ST`, `Accept-Language`, dahili `mockedorganizationid`) çıkarıldı (epint auth header'larını kendi ekler; `mockedorganizationid` fuzzy eşleştirmede kwargs yutabilirdi), body parametresi `body`, operationId'ler kebab-case (Springfox'un `listUsingPOST` adları yerine), `RestResponse«X»` → `RestResponseX`, çözülmemiş `${...}` i18n şablonlu `description`/`example` değerleri atıldı.
- İstek DTO'larına test ortamında olup canlıda olmayan alanlar da eklendi (şu an yalnızca `risk_collateral_detail_list.paymentDate`). Yanıt şemaları canlıdan.

## Ne zaman kullanılır

- Bir ödeme/geçerlilik tarihi için teminat kalemlerinin tutarını çekmek (başlangıç, GÖGİ, ek, dengesizlik, risk, YEK, destekleme bedeli).
- Bir kalemin hesaplama detayını görmek (günlük risk kırılımı, GÖP/GİP alacak-borç, santral bazında destekleme bedeli, sayaç okuyan kurum bazında tüketim vb.).
- Organizasyonun tüm teminat kalemlerini ve gerekli/mevcut teminatı tek tabloda görmek: `collateral_report`.

## Endpoint'ler

Swagger'da **21 endpoint**, hepsi `POST`:

| method_adı | path | açıklama | istek alanları |
|---|---|---|---|
| `initial_collateral_list` | `/gogi-collateral/rest/v1/initial-collateral/list` | Başlangıç teminatı tutarı | `validityDate` |
| `gogi_collateral_list` | `/gogi-collateral/rest/v1/calculation/calculated/details` | GÖGİ teminatı (GÖP/GİP alacak-borç-net, k günü) | `validityDate` |
| `gogi_collateral_detail_list` | `/gogi-collateral/rest/v1/data/details` | GÖGİ detay (GÖP/GİP alacak ve borç) | `validityDate` |
| `additional_collateral_list` | `/collateral/rest/v1/additional/list` | Ek teminat (avanslı/avanssız) | `paymentDate`, `controlHour` |
| `imbalance_collateral_list` | `/imbalance-collateral/v1/imbalance-collateral/list` | Dengesizlik teminatı | `effectiveDateStart` |
| `imbalance_collateral_detail_list` | `/imbalance-collateral/v1/imbalance-collateral/list/detail` | Dengesizlik teminatı detayı (dönem bazında EDM, SFK DM, AOSMF) | `effectiveDateStart` |
| `aosmf_detail_list` | `/imbalance-collateral/v1/imbalance-collateral/list/aosmf` | SMF ortalamaları (AOSMF) | `effectiveDateStart`, `monthCount` |
| `risk_collateral_list` | `/risk-collateral/rest/v1/list/risk-collateral-by-org` | Risk teminatı | `paymentDate` |
| `risk_collateral_detail_list` | `/risk-collateral/rest/v1/list/risk-daily-by-validity-date` | Risk teminatı detayı (hesaplamaya giren günlük kalemler) | `validityDate` |
| `daily_generation_detail_list` | `/risk-collateral/rest/v1/list/dsg-risk-daily-generation` | Günlük üretim detayı (YTBS, kurulu güç, asenkron, manuel) | `validityDate` |
| `daily_portfolio_detail_list` | `/risk-collateral/v1/portfolio/dsg/list` | Günlük portföy detayı (kurum bazında tüketim, mevsimsellik) | `effectiveDate` |
| `rbs_collateral_list` | `/rbs-collateral/rest/v1/list` | Destekleme bedeli teminatı | `paymentDate`, `controlHour` |
| `rbs_collateral_powerplant_list` | `/rbs-collateral/rest/v1/powerplant/list` | Destekleme bedeli, santral bazında | `paymentDate` |
| `rbs_collateral_powerplant_detail_list` | `/rbs-collateral/rest/v1/powerplant/detail` | Destekleme bedeli, santralin günlük tutarları | `paymentDate`, `powerPlantId` |
| `rbs_collateral_powerplant_hourly_list` | `/rbs-collateral/rest/v1/powerplant/hourly` | Destekleme bedeli, santralin saatlik detayı (sayfalı) | `paymentDate`, `effectiveDate`, `powerPlantId`, `page` |
| `res_collateral_list` | `/res-collateral/rest/v1/list` | YEK teminatı | `paymentDate`, `controlHour` |
| `res_collateral_daily_detail_list` | `/res-collateral/rest/v1/list/res-daily-detail` | YEK teminatı günlük detayı | `paymentDate` |
| `res_collateral_withdrawal_detail_list` | `/res-collateral/rest/v1/withdrawal-details/list` | YEK teminatı tüketim detayı (kurum bazında) | `effectiveDate`, `paymentDate` |
| `risk_daily_detail_report` | `/risk-collateral/rest/v1/list/risk-daily-detail` | Rapor: günlük risk detayı (son versiyon) | `startDate`, `endDate` |
| `seasonal_constant_report` | `/risk-collateral/seasonal/v1/list/seasonal` | Rapor: mevsimsellik katsayıları | `effectiveDateStart`, `effectiveDateEnd` |
| `collateral_report` | `/collateral/rest/v1/report/list` | Rapor: organizasyon bazında tüm teminat kalemleri (sayfalı) | `effectiveDateStart`, `effectiveDateEnd`, `controlHour` |

"İstek alanları" sütunu EPİAŞ dokümanındaki örnek isteklerdir. Swagger'da bazı DTO'larda ek alanlar da var (`organizationId`, `exportType`, `meterReadingOrgId`, `controlHour`); dokümanda kullanılmadıkları için etkileri doğrulanmadı, gerekmedikçe gönderme.

## Önemli parametreler ve gotchalar

- **Tarih alanı adları uç başına değişir: `validityDate` / `paymentDate` / `effectiveDate` / `effectiveDateStart` / `startDate`.** Tablodaki adı kullan. Uçta olmayan bir tarih alanı gönderirsen epint'in fuzzy parametre eşleştirmesi onu sessizce mevcut tarih alanına yazar. Örneğin `initial_collateral_list(paymentDate=...)` isteği `{"validityDate": ...}` olarak gider, hata vermez.
- **GÖGİ'de geçerlilik tarihi ≠ ekrandaki tarih** (`gogi_collateral_list`, `gogi_collateral_detail_list`): servis `validityDate` ile sorgulanır, EPYS ekranı ise ödeme tarihini gösterir. Bugün hesaplanan değerin ödeme tarihi bir sonraki iş günüdür. Ekranda 2023-09-28 saat 11 kontrolünde görülen değer için `validityDate="2023-09-27"` gönder.
- **`controlHour` yalnızca `"HOUR_11"` veya `"HOUR_17"`** (string enum). `additional_collateral_list`'te `HOUR_17` seçilirse sorgulanan tarihten sonraki ödeme tarihinin değeri döner.
- **Dengesizlik detayı iki adımlıdır**: `imbalance_collateral_detail_list`'e `effectiveDateStart` olarak, `imbalance_collateral_list` yanıtındaki `aosmfQueryPeriod` değerini (teminatın hesaplandığı uzlaştırma dönemi) gönder.
- **`risk_collateral_detail_list` ile `risk_daily_detail_report` aynı kalemleri döner ama farklı versiyonları**: ilki tek gün (`validityDate`) için hesaplamaya giren versiyonu, rapor ise tarih aralığı (`startDate`/`endDate`) için ilgili günün son versiyonunu verir. Raporda `totalAmount` kullanılmaz.
- **Yanıtta `content` sarmalayıcısı var** (mimari §8): epint `RestResponse` zarfını (`status`+`correlationId`+`body`) soyar, ama `body` içinde `content` bir kat daha durur, yani sonuç `result["content"]` altındadır. Liste uçlarında liste `content` altında uca özel bir anahtardadır: `items` (`rbs_collateral_powerplant*`, `collateral_report`), `dailyRiskCollateralList`, `dsgRiskCollateralGenerationList`, `portfolioDetails`, `resDailyCollateralResponseDtoList`, `details`, `resultList`. Bu yapı api-docs şemasından alındı, canlı çağrıyla henüz doğrulanmadı.
- **Sayfalama**: `rbs_collateral_powerplant_hourly_list` ve `collateral_report` `page={"number": .., "size": ..}` alır. Verilmezse epint `{number: 1, size: 1000, limit: 1000}` ekler.
- **Yetkiler (EKYS)**: çoğu uç "Teminat - Teminat Bilgileri Okuma Yetkisi" ister. İstisnalar: `risk_daily_detail_report` → "Teminat - Günlük Risk Detay Okuma Yetkisi", `seasonal_constant_report` → "Teminat - Mevsimsellik Katsayısı Okuma Yetkisi", `collateral_report` → "Teminat - Teminat Raporu Okuma Yetkisi". Test ortamı yetkileri `test-ekys.epias.com.tr` üzerinden tanımlanır.

## Örnek kullanım

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# Başlangıç teminatı
sonuc = ep.teminat.initial_collateral_list(validityDate="2023-09-28")
tutar = sonuc["content"]["amount"]

# Ek teminat, saat 11 kontrolü
ek = ep.teminat.additional_collateral_list(paymentDate="2023-09-28", controlHour="HOUR_11")

# Dengesizlik teminatı → hesaplandığı dönemin detayı
dt = ep.teminat.imbalance_collateral_list(effectiveDateStart="2023-09-28")
detay = ep.teminat.imbalance_collateral_detail_list(
    effectiveDateStart=dt["content"]["aosmfQueryPeriod"],
)

# Teminat raporu (sayfalı)
rapor = ep.teminat.collateral_report(
    effectiveDateStart="2023-10-09",
    effectiveDateEnd="2023-10-09",
    controlHour="HOUR_11",
    page={"number": 1, "size": 100},
)
satirlar = rapor["content"]["items"]
```

## Kaynaklar

- EPYS Teminat Modülü Web Servis Dokümanı v1.0 (EPİAŞ, 26.09.2023): uç listesi, örnek istekler, alan açıklamaları, yetkiler.
- `https://epys.epias.com.tr/<servis>/v2/api-docs` (servis: `gogi-collateral`, `collateral`, `imbalance-collateral`, `risk-collateral`, `rbs-collateral`, `res-collateral`): şemaların kaynağı. Test ortamı: `epys-prp.epias.com.tr`.
- `src/epint/endpoints/teminat/swagger.json`, test: `tests/test_teminat_category.py`
- Genel mimari: `../architecture.md`
- Genel kullanım kuralları: `../usage-conventions.md`
