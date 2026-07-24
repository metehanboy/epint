<!-- epint kategori referansı: gop — hub: ../SKILL.md -->

> **Portal:** `epint` pip ile kurulur (`requirements.txt` / Dockerfile). Swagger: kurulu pakette `epint/endpoints/<category>/swagger.json` (`python -c "import epint,pathlib; print(pathlib.Path(epint.__file__).parent)"`). Bu repoda `epint/src` veya `refs/` yok. Kurallar: `../overview.md`, `../usage-conventions.md`.

# gop — Gün Öncesi Piyasası Servisleri

`ep.gop` (alias: `gop`), EPİAŞ Gün Öncesi Piyasası (GÖP) için ikili anlaşma (bilateral agreement), teklif (offer), teminat (collateral), itiraz (objection), ticaret artış bildirimi ve piyasa sonucu/istatistik servislerini kapsar. Kaynak swagger `GOP Rest Services` v1, `basePath: /gop-servis/rest`, tamamı **POST** metoduyla çalışan 48 endpoint içerir (isim "REST" olsa da fiilen RPC-tarzıdır — "list" işlemleri de filtre body'si ile POST edilir).

GOP, epint'in diğer tüm kategorilerinden (EPYS ailesi, şeffaflık, günici) **auth ve tarih formatı açısından farklı** davranır — bu dosya o farkları somutlaştırır. Genel mimari için [[01-epint-architecture]], genel kullanım kuralları için [[02-epint-usage-conventions]].

## Ne zaman kullanılır

- İkili anlaşma (bilateral agreement) oluşturma/iptal/listeleme (`ep.gop.contract_*`)
- Saatlik/bloklu/esnek teklif oluşturma, iptal, listeleme (`ep.gop.offer_*`)
- PTF'e itiraz oluşturma/listeleme/cevaplama (`ep.gop.objection_*`)
- Teminat listeleme (`ep.gop.collateral_organization`)
- Ticaret artış bildirimi oluşturma/güncelleme/silme/listeleme (`ep.gop.trade_increase_*`)
- Piyasa sonucu, PTF istatistikleri, min/max teklif fiyatı, trading limit, gate (süreç) durumu sorgulama

## GOP'a özgü davranış

### 1. Auth: `TGT` + `gop-service-ticket` (normal `ST` değil)

- Diğer EPYS kategorileri `TGT` + `ST` header çifti kullanır; GOP `TGT` + **`gop-service-ticket`** header çifti kullanır (normal `ST` header'ı GOP'a **eklenmez**).
- Service Ticket (ST) genel olarak 15 saniye geçerlidir; **GOP için 30 saniye** geçerlidir.
- Swagger'da bu header her endpoint'in `parameters` listesinde `"name": "gop-service-ticket", "in": "header"` olarak tanımlıdır (48 endpoint'ten 46'sında açıkça deklare edilmiş; `objection/reply` ve `minmaxprice/list/all` swagger'da bu parametreyi listelemiyor ama epint header'ı **kategoriye göre** (path bazlı değil) unconditional ekler, dolayısıyla davranış farkı yoktur).
- Bunu elle taklit etmeye çalışma — `ep.set_auth(...)` + `ep.gop.<method>(...)` çağrısı yeterli, epint TGT/ST/gop-service-ticket akışını kendi yönetir.

### 2. Tarih formatı: milisaniye + `:` olmayan offset

Diğer kategoriler `2016-04-22T00:00:00+03:00` formatını kullanırken GOP için format:

```
2016-04-22T00:00:00.000+0300
```

yani `.SSS` (milisaniye) eklenir ve offset `+HH:MM` değil `+HHMM` (iki nokta yok). `refs/ (epint kaynak reposu; portalda yok) — gop/GOP Rest Servisleri.md` içindeki örnekler bu formatı doğrular (bazı eski örnekler Türkiye'nin eski DST'sinden kalma `+0200` gösteriyor, örn. `"2016-03-27T00:00:00.000+0200"`; günümüzde Türkiye sabit `+03:00`'da olduğu için pratikte her zaman `+0300` üretilir). Tarih parametrelerini `str` veya `datetime`/`date` olarak ver — epint formatı otomatik uygular, elle string formatlama yapma.

### 3. Body "service wrapper" yapısı: `header` + `body`

GOP'un body şeması olan endpoint'lerinin **tamamı** (`Service<X>Request` adlı definition'lar) şu şekildedir:

```json
"ServiceQueryContractCountRequest": {
  "type": "object",
  "properties": {
    "header": {
      "type": "array",
      "description": "Request header bilgisini tutar.",
      "items": { "$ref": "#/definitions/Header" }
    },
    "body": {
      "description": "Request body bilgisini tutar.",
      "$ref": "#/definitions/QueryContractCountRequest"
    }
  }
}
```

`Header` = `{"key": string, "value": string}`. `QueryContractCountRequest` (asıl body) örneğin `{startDate, endDate, organizationCode, status[APPROVED|WAITING_FOR_APPROVAL|INVALID]}` alanlarını içerir.

epint kullanıcıdan gelen kwargs'ları otomatik `body` altına yerleştirir ve `header` array'ine kendisi iki eleman ekler: `transactionId` (rastgele üretilmiş) ve `application` (`epint.__fullname__`). Yani şu çağrı:

```python
ep.gop.contract_count(startDate="2026-07-01", endDate="2026-07-31", organizationCode=12345, status=["APPROVED"])
```

tel üzerinde şu gövdeyi üretir:

```json
{
  "header": [
    {"key": "transactionId", "value": "<uuid-benzeri>"},
    {"key": "application", "value": "epint/<versiyon>"}
  ],
  "body": {
    "startDate": "2026-07-01T00:00:00.000+0300",
    "endDate": "2026-07-31T00:00:00.000+0300",
    "organizationCode": 12345,
    "status": ["APPROVED"]
  }
}
```

Kullanıcı `header`/`body` ayrımını **elle yapmaz** — düz kwarg verir, epint gerekeni yapar. Yanıt tarafında da aynı şekilde: response şeması `header`+`body` içeriyorsa epint `body`'yi otomatik çıkarır, sana ham içerik döner (bkz. [[01-epint-architecture]] §8).

### 4. Host

`gop.epias.com.tr` (prod) / `testgop.epias.com.tr` (`ep.set_mode("test")`). `basePath: /gop-servis/rest` swagger'dan gelir, elle hardcode etme.

### 5. Kullanım şekli

```python
ep.gop.<method_adi>(**kwargs)     # kategori alias'ı: gop
```

## Endpoint'ler

Toplam **48 endpoint**, hepsi **POST**. Method adları, swagger'daki `operationId`'nin (genelde path'in kendisiyle aynı) `to_python_method_name` ile snake_case'e çevrilmiş halidir.

### Contract — İkili Anlaşmalar (tag: `contract`)

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `contract_create` | POST | `/contract/create` | İkili anlaşma oluşturur |
| `contract_delete` | POST | `/contract/delete` | İkili anlaşma iptal eder |
| `contract_list` | POST | `/contract/list` | İkili anlaşmaları listeler |
| `contract_list_history` | POST | `/contract/list/history` | İkili anlaşma geçmişini listeler |
| `contract_listcontractstatuses` | POST | `/contract/listcontractstatuses` | Kullanılabilir statüleri listeler |
| `contract_listhourblocks` | POST | `/contract/listhourblocks` | Teslim günü için periyotları listeler |
| `contract_organization_list` | POST | `/contract/organization/list` | İkili anlaşma organizasyon listesini döner |
| `contract_regions` | POST | `/contract/regions` | Kullanılabilir bölgeleri listeler |
| `contract_validatedeliveryday` | POST | `/contract/validatedeliveryday` | Teslim günü geçerliliğini doğrular |
| `contract_bad_list` | POST | `/contract/bad/list` | Karşılığı olmayan (kötü) satış kontrolü listesi |
| `contract_count` | POST | `/contract/count` | İkili anlaşma sayısını döner |

Bu iki endpoint'in swagger `operationId` alanı doldurulmamış bir şablon değişkeniydi (`#{BAD_CONTRACT_LIST_NICKNAME}`, `#{CONTRACT_COUNT_NICKNAME}`) — epint artık böyle "güvenilmez" operationId'leri tespit edip path'ten isim türetiyor (`SwaggerModel._is_unreliable_operation_id`), bu yüzden method adları yukarıdaki gibi path'le tutarlı.

### Contract Objection — İkili Anlaşma İtirazları (tag: `contractObjection`)

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `contract_objection_create` | POST | `/contract-objection/create` | Karşılığı olmayan satış için itiraz oluşturur |
| `contract_objection_list` | POST | `/contract-objection/list` | İtirazları listeler |

### Collateral — Teminat (tag: `collateral`)

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `collateral_organization` | POST | `/collateral/organization` | Organizasyona göre teminat listeler |

### Gate — Süreç/Kapı Durumu (tag: `gate-operation`)

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `gate_operation_active` | POST | `/gate/operation/active` | Aktif süreçleri (gate) listeler |

### Market — Piyasa Sonucu / İstatistik (tag: `market`)

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `market_finalresults` | POST | `/market/finalresults` | Bölgeye göre piyasa (PTF) sonucu döner |
| `market_stats` | POST | `/market/stats` | Günlük/haftalık/aylık/yıllık PTF istatistiği döner |

### Min-Max Price (tag: `minmaxprice`)

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `minmaxprice_list_all` | POST | `/minmaxprice/list/all` | Tüm min/max teklif fiyat bilgisini listeler |
| `minmaxprice_list_effective` | POST | `/minmaxprice/list/effective` | Teslim günü için min/max teklif fiyatlarını listeler |

### Objection — MCP'ye İtiraz (tag: `objection`)

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `objection_create` | POST | `/objection/create` | Piyasa takas fiyatına (MCP) itiraz oluşturur |
| `objection_list` | POST | `/objection/list` | İtirazları listeler |
| `objection_reply` | POST | `/objection/reply` | İtiraza cevap verir |

### Offer — Teklif (tag: `offer`)

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `offer_advance` | POST | `/offer/advance` | Teslim günü için gereken avansları döner |
| `offer_create_block` | POST | `/offer/create/block` | Blok teklif oluşturur |
| `offer_create_flexible` | POST | `/offer/create/flexible` | Esnek teklif oluşturur |
| `offer_create_hourly` | POST | `/offer/create/hourly` | Saatlik teklif oluşturur |
| `offer_currencies` | POST | `/offer/currencies` | Kullanılabilir para birimlerini listeler |
| `offer_delete_block` | POST | `/offer/delete/block` | Blok teklifi iptal eder |
| `offer_delete_flexible` | POST | `/offer/delete/flexible` | Esnek teklifi iptal eder |
| `offer_delete_hourly` | POST | `/offer/delete/hourly` | Saatlik teklifi iptal eder |
| `offer_list_block` | POST | `/offer/list/block` | Blok teklifleri listeler |
| `offer_list_flexible` | POST | `/offer/list/flexible` | Esnek teklifleri listeler |
| `offer_list_history_block` | POST | `/offer/list/history/block` | Blok teklif geçmişini listeler |
| `offer_list_history_flexible` | POST | `/offer/list/history/flexible` | Esnek teklif geçmişini listeler |
| `offer_list_history_hourly` | POST | `/offer/list/history/hourly` | Saatlik teklif geçmişini listeler |
| `offer_list_hourly` | POST | `/offer/list/hourly` | Saatlik teklifleri listeler |
| `offer_listhourblocks` | POST | `/offer/listhourblocks` | Teklif tipi/teslim günü için periyotları listeler |
| `offer_offerresult` | POST | `/offer/offerresult` | Organizasyona göre piyasa sonucunu döner |
| `offer_regions` | POST | `/offer/regions` | Teklif için kullanılabilir bölgeleri listeler |
| `offer_validatedeliveryday` | POST | `/offer/validatedeliveryday` | Teslim günü geçerliliğini doğrular |

### Operation History (tag: `operationhistory`)

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `operationhistory_list` | POST | `/operationhistory/list` | İşlem geçmişi kayıtlarını listeler |
| `operationhistory_operationcodes` | POST | `/operationhistory/operationcodes` | Sorgulanabilir işlem kodlarını listeler |

### Trade Increase — Ticaret Artış Bildirimi (tag: `tradeincrease`)

Path'ler `/tradeIncrease/...` (camelCase) olduğu için method adları `trade_increase_*` şeklinde ayrılır (`tradeincrease_*` **değil**):

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `trade_increase_create` | POST | `/tradeIncrease/create` | Ticaret artış bildirimi oluşturur |
| `trade_increase_delete` | POST | `/tradeIncrease/delete` | Ticaret artış bildirimini siler |
| `trade_increase_list` | POST | `/tradeIncrease/list` | Ticaret artış bildirimlerini listeler |
| `trade_increase_update` | POST | `/tradeIncrease/update` | Ticaret artış bildirimini günceller |

### Trading Limits (tag: `tradinglimits`)

| method_adı | HTTP | path | açıklama |
|---|---|---|---|
| `tradinglimits_detail_list` | POST | `/tradinglimits/detail/list` | Trading limit detaylarını listeler |
| `tradinglimits_list` | POST | `/tradinglimits/list` | Trading limitlerini listeler |

## Önemli parametreler ve gotchalar

- **Tüm endpoint'ler POST'tur** — GOP'ta GET/PUT/DELETE yoktur; "list"/"query" işlemleri de filtre kriterlerini body ile POST eder.
- **Yanıt sarmalayıcısı ve `resultType`**: Çoğu response şeması (`*ServiceResponse`) `resultCode` (`"0"` = başarı, diğerleri hataya özgü), `resultText` ve `resultType` alanları içerir. `resultType` enum'u: `SUCCESS`, `BUSINESSERROR`, `SYSTEMERROR`, `SECURITYERROR`. **HTTP 200 dönse bile** `resultType` `BUSINESSERROR`/`SYSTEMERROR` olabilir — sadece HTTP status'a bakmak yeterli değildir, dönen veri içinde bu alanı da kontrol et.
- **Yaygın enum'lar** (swagger'da 41 enum tanımı var, tekrar edenler hariç başlıcaları):
  - Sözleşme statüsü (`status`): `APPROVED`, `WAITING_FOR_APPROVAL`, `INVALID`
  - İptal tipi (`cancellationType`): `UNILITERAL`, `BILATERAL`, `COLLATERAL_SANCTION`, `BMO_SANCTION` — **varsayılan `BILATERAL`**
  - Teklif tipi (`offerType`): `HOURLY`, `BLOCK`, `FLEXIBLE`
  - İtiraz durumu (`objectionStatus`/`status`): `ACTIVE`, `ACCEPTED`, `REJECTED`
  - Gate (süreç) adı: 19 değerli enum, örn. `OFFER_DECLARATION`, `OFFER_CONFIRMATION`, `PRICE_DETERMINATION`, `OBJECTION`, `FINAL_RESULTS`, `ATC_NTC`, `BILATERAL_AGREEMENTS`, `CONTRACT_CONFIRMATION`, `CONTROLLED_CONTRACT` vb.
  - Gate durumu (`gateStatus`): `OPEN`, `WAITING`, `CLOSE`
  - Sözleşme aksiyonu: `CREATABLE`, `EDITABLE`, `CANCELABLE`, `READONLY`
  - Operasyon kaynağı: `USER`, `SYSTEM`; öncelik (`operationPriority`): `INFO`, `WARNING`, `ERROR`
- **Zorunlu alan örüntüsü**: create/delete servislerinde tarih ve kimlik alanları (`deliveryDay`, `counterEic`, `counterRegionCode`, `offer`, `deliveryStartDay`/`deliveryEndDay`, `regionCode`) genelde **gerekli**dir; list/query servislerinde aynı alanlar genelde **opsiyonel**dir (verilmezse geniş kapsamlı sorgu yapılır). Örnek: `QueryOfferRequest` (offer list) JSON-schema seviyesinde `required: [end, offerType, regionCode, start, version]` — bu 5 alanı vermezsen 400 alırsın.
- **`version` alanı** (`QueryOfferRequest`): verilmezse servis sadece aktif teklifleri döner; verilirse o versiyona ait aktif/pasif teklifi getirir — geçmiş teklif sorgularken unutma.
- **Tarih formatı**: elle formatlama yapma, `str`/`datetime`/`date` ver, epint `+0300` (milisaniye + `:` olmayan offset) formatına otomatik çevirir (bkz. GOP'a özgü davranış §2).
- **`dst` alanı** (`OfferDetail`): Daylight Saving göstergesi, `boolean`, varsayılan `false` — Türkiye artık DST kullanmadığı için genelde `false` bırakılabilir.

## Örnek kullanım

```python
import epint as ep

ep.set_auth("kullanici", "sifre")
ep.set_mode("prod")   # test ortamı için "test" -> testgop.epias.com.tr

# 1) İkili anlaşma sayısını sorgula
result = ep.gop.contract_count(
    startDate="2026-07-01",
    endDate="2026-07-31",
    organizationCode=12345,
    status=["APPROVED"],
)

# 2) Saatlik teklif oluştur — offerDetails/offerPrices nested array
result = ep.gop.offer_create_hourly(
    deliveryDay="2026-07-20",
    regionCode="TR1",
    offerType="HOURLY",
    currencyCode="TRY",
    offerDetails=[
        {
            "startPeriod": 1,
            "endPeriod": 24,
            "duration": 24,
            "offerPrices": [{"index": 1, "price": 2500.0, "amount": 10.0}],
        }
    ],
)

# 3) İkili anlaşmaları listele (filtreler opsiyonel)
contracts = ep.gop.contract_list(
    deliveryDay="2026-07-15",
    regionCode="TR1",
    status=["APPROVED"],
)

# 4) Gerçek isteği atmadan RequestModel'i incele (header/body wrapper'ı görmek için)
req = ep.gop.trade_increase_list(
    regionCode="TR1",
    deliveryStartDay="2026-07-01",
    deliveryEndDay="2026-07-31",
    debug=True,
)
print(req.body)   # {"header": [...], "body": {...}} şeklini doğrulamak için
```

## Kaynaklar

- `epint/endpoints/gop/swagger.json` — asıl OpenAPI 2.0 kaynağı (paket bunu yükler)
- `refs/ (epint kaynak reposu; portalda yok) — gop/GOP Rest Servisleri.md` — Türkçe alan/model sözlüğü (zorunlu/opsiyonel, enum, örnek değer bilgisi; 9509 satır, sadece "9. Models" bölümünü içerir, ayrı bir endpoint/auth anlatımı yoktur)
- `../architecture.md` §5–§7 — body wrapper, host seçimi, auth header mantığı, tarih format tablosu
- `../usage-conventions.md` — genel çağrım kuralları
