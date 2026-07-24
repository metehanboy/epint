<!-- epint kategori referansı: index-ac — hub: ../SKILL.md -->

> Kaynak: `src/epint/endpoints/index-ac/swagger.json`. Kurallar: `../overview.md`, `../usage-conventions.md`.

# index-ac — Endeks / Ek Tüketim Servisi

EPYS Endeks/Ek Tüketim uygulaması. Sayaç okuma (endeks) kayıtları ve ek tüketim (endeks dışı, ör. arıza sonrası tahmini) kayıtlarını yönetir: kaydetme, güncelleme, pasife alma, sorgulama, dışa aktarma. Auth normal EPYS akışı (`TGT`+`ST`), host varsayılan `epys`/`epys-prp` ailesi (mimari §5/§6 — bu kategori `seffaflik*`/`gop`/`gunici` özel host'larına girmez).

## Ne zaman kullanılır

- Sayaç okuma (endeks) kaydı oluşturmak/güncellemek/sorgulamak/pasife almak.
- Ölçü devresi arızası vb. durumlarda ek tüketim (tahmini/manuel) kaydı oluşturmak/sorgulamak/pasife almak.
- Toplu endeks kaydı (batch, JSON veya XML, tek seferde ≤1000 kayıt).
- Okuma yükümlülük raporu veya endeks/ek tüketim özet raporu sorgulamak.
- Çoklu seçim (lookup) referans verilerini (enum/dropdown kaynakları) çekmek.

## Endpoint'ler

Swagger'da kayıtlı **14 endpoint** (hepsi `POST`, `available_lookups` hariç ki o `GET`):

| method_adı (snake_case) | HTTP | path | açıklama |
|---|---|---|---|
| `additional_consumption_passivate` | POST | `/v1/additional-consumption/passivate` | Ek tüketim kaydını pasife alır. |
| `additional_consumption_query` | POST | `/v1/additional-consumption/query` | Ek tüketim kayıtlarını sorgular (sayfalı, `items`+`page`). |
| `additional_consumption_save` | POST | `/v1/additional-consumption/save` | Yeni ek tüketim kaydı oluşturur. |
| `index_count` | POST | `/v1/index/count` | Filtreye uyan endeks kayıt sayısını döner (`content.count`). |
| `index_export` | POST | `/v1/index/export` | Endeks kayıtlarını dışa aktarır — **cursor tabanlı sayfalama** (aşağıya bak), binary değil JSON. |
| `index_passivate` | POST | `/v1/index/passivate` | Endeks kaydını pasife alır. |
| `index_query` | POST | `/v1/index/query` | Endeks kayıtlarını sorgular (sayfalı, `items`+`page`). |
| `index_save` | POST | `/v1/index/save` | Yeni endeks kaydı oluşturur. |
| `index_save_batch` | POST | `/v1/index/save-batch` | Toplu endeks kaydı (liste body, JSON veya XML; ≤1000 kayıt/istek). |
| `index_update` | POST | `/v1/index/update` | Var olan endeks kaydını (`indexId` ile) günceller. |
| `available_lookups` | GET | `/v1/lookup` | Mevcut çoklu seçim (lookup) anahtarlarının listesini döner. Yetki gerekmez. |
| `lookup_query` | POST | `/v1/lookup/query` | Belirli bir lookup anahtarının detay verisini sorgular. Yetki gerekmez. |
| `read_obligation_query` | POST | `/v1/read-obligation/query` | Okuma yükümlülük raporunu sorgular. |
| `summary_report_query` | POST | `/v1/summary-report/query` | Endeks + ek tüketim özet raporunu sorgular. |

## Önemli parametreler ve gotchalar

- **`index` ve `additional-consumption` iki ayrı kayıt tipidir, karıştırma**: `index*` = normal sayaç okuma (endeks); `additional-consumption*` = arıza/istisna sonrası ek tüketim. İkisinin `save`/`query`/`passivate` uçları ayrı, response şemaları benzer ama farklı (`indexId` vs `id`).
- **`indexId` ile güncelleme/pasife alma**: `index_update`/`index_passivate` mevcut kaydı `indexId` ile bulur; `index_save` sonucu dönen `indexId`'yi sakla. Ek tüketim tarafında karşılığı `id`.
- **`index_save_batch` iki gövde formatını da kabul eder**: JSON'da düz liste (`[{...}, {...}]`), XML'de `IndexSaveRequestWrapperDto > IndexSaveRequestDto[]` sarmalayıcısı. Tek seferde **en fazla 1000 kayıt**. Response her kayıt için `isSuccessful`/`errorMessage` döner — kısmi başarı mümkün, tüm listeyi `isSuccessful` alanına göre kontrol et, response'un genel `status: 200 OK` olması hepsinin başarılı olduğu anlamına gelmez.
- **`overrideFullOverlap`**: `index_save`'de var olan bir dönemle tam çakışan yeni kayıt eklerken eskisinin üzerine yazılmasını sağlar (`true`); belirtilmezse çakışma hata verebilir.
- **`index_export` sayfalaması `number`/`size` değil, cursor tabanlı**: `page: {"limit": 100, "offsetId": "<önceki response'un page.offsetId'i>", "size": null}`. İlk çağrıda `offsetId` boş/`None` bırak; sonraki her çağrıda bir önceki response'daki `page.offsetId` değerini gönder. Bu kategorideki tek cursor-pagination endpoint'i — diğerleri (`index_query`, `additional_consumption_query`) standart `{number, size}` sayfalama kullanır.
- **`firstReadDateAsPeriod`/`lastReadDateAsPeriod`, `createDateStartAsPeriod`/`createDateEndAsPeriod`**: hepsi `date-time`; sorgu filtreleridir, kayıt alanı olan `firstReadDate`/`lastReadDate`'ten farklıdır — isim benzerliğine aldanma.
- **Response'ta `content` sarmalayıcısı var** (mimari §8 genel kural): ham REST yanıtı `status`+`correlationId`+`body` içerir, epint `body`'yi otomatik soyar; ama soyulan `body`'nin içinde `content` alanı bir kat daha durur. `index_query`/`additional_consumption_query` sonucu `{"content": {"items": [...], "page": {...}}}` şeklinde gelir — direkt `result["items"]` bekleme.
- **`available_lookups`/`lookup_query` yetki gerektirmez**: diğer tüm endpoint'ler ST bazlı özel yetki (ör. `ST - Endeks İşlemleri - Endeks Kaydet`) ister; bu ikisi herkese açık referans/enum verisidir.
- **Enum alanları (`energyType`, `additionalConsumptionReason`, `firstReadType`/`lastReadType`, `firstLoadType`/`lastLoadType`, `indexStatus`, `portfolioType`) request'te sadece `id` (int) olarak gönderilir**, response'ta ise `{id, value, localizations}` objesi olarak döner — request/response şekli asimetrik, response'taki objeyi tekrar request'e olduğu gibi basma.
- **Host/basePath swagger'da `epys-prp.epias.com.tr` / `/index-ac` yazsa da hardcode etme**: epint gerçek host'u kategoriye göre kendi seçer (mimari §5) — bu kategori `seffaflik*`/`gop`/`gunici` değil, dolayısıyla `epys`/`epys-prp` ailesine düşer.

## Örnek kullanım

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# Endeks kaydı oluştur
sonuc = ep.index_ac.index_save(
    energyType=1,
    factor="1.0",
    digitCount=2,
    firstT1="10.0", firstT2="30.0", firstT3="50.0",
    lastT1="20.0", lastT2="40.0", lastT3="60.0",
    firstReadType=1, lastReadType=1,
    firstLoadType=1, lastLoadType=1,
    firstReadDate="2023-08-30T00:00:00+03:00",
    lastReadDate="2023-08-31T00:00:00+03:00",
    readingOrganizationId=1010,
    eic="40Z000200000266H",
    consumptionPointId=200000266,
    overrideFullOverlap=True,
)
index_id = sonuc["content"]["indexId"]

# Endeks sorgula (standart sayfalama)
result = ep.index_ac.index_query(
    eic="40Z000200000**54",
    consumptionPointId=200000**5,
    lastReadDateAsPeriod="2023-08-01T00:00:00+03:00",
    page={"number": 1, "size": 10},
)
kayitlar = result["content"]["items"]
```

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# Cursor tabanlı export — offsetId ile sayfa sayfa çek
offset_id = None
tum_kayitlar = []
while True:
    result = ep.index_ac.index_export(
        eic="40Z000200000**6H",
        consumptionPointId=200000**6,
        lastReadDateAsPeriod="2023-08-01T00:00:00+03:00",
        page={"limit": "100", "offsetId": offset_id, "size": None},
    )
    content = result["content"]
    tum_kayitlar.extend(content["items"])
    offset_id = content["page"].get("offsetId")
    if not content["items"] or offset_id is None:
        break
```

## Kaynaklar

- `docs/index-ac.md` (bu repoda) — EPİAŞ'ın orijinal Endeks/Ek Tüketim servis kılavuzu, tüm parametre/enum sözlüğü burada.
- `src/epint/endpoints/index-ac/swagger.json`
- Genel mimari: `../architecture.md`
- Genel kullanım kuralları: `../usage-conventions.md`
