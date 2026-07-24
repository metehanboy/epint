<!-- epint kategori referansı: gunici-trading — hub: ../SKILL.md -->

> **Portal:** `epint` pip ile kurulur (`requirements.txt` / Dockerfile). Swagger: kurulu pakette `epint/endpoints/<category>/swagger.json` (`python -c "import epint,pathlib; print(pathlib.Path(epint.__file__).parent)"`). Bu repoda `epint/src` veya `refs/` yok. Kurallar: `../overview.md`, `../usage-conventions.md`.

# gunici-trading — GÜNİÇİ Ticaret Servisleri

`gunici-trading` kategorisi, EPİAŞ Gün İçi Piyasası'nda **teklif verme/güncelleme/iptal**, aktif kontrat ve blok kontrat listeleme, kontrat derinliği (order book), organizasyon teminat/limit bilgisi ve özet raporlama işlemlerini kapsar. Kaynak swagger: `epint/endpoints/gunici-trading/swagger.json` (`basePath: /rest/v1` altında `/gunici-trading-service`, 26 endpoint, 6 tag: `collateral`, `contract`, `dashboard`, `offer`, `parameter`, `report`).

Kullanım: `ep.gunici_trading.<method_adi>(**kwargs)`. `gunici_trading`, dizin adı `gunici-trading`'in `-`→`_` çevrimidir; ayrı bir alias tanımlı değildir (`epint/__init__.py` içinde `gunici` için özel bir `CATEGORY_ALIASES` girdisi yok).

**Karıştırma:** `gunici` ayrı bir kategoridir (farklı swagger, farklı host/tarih davranışı — bkz. aşağıdaki bölüm). Bu dosya sadece `gunici-trading` içindir.

## Ne zaman kullanılır

- Saatlik veya blok teklif girme/güncelleme/iptal etme (`save-hourly-offer`, `save-block-offer`, `update-offer`, `cancel-all-offer` vb.).
- Toplu (bulk) saatlik teklif girişi veya dosya ile teklif doğrulama.
- Aktif/blok kontrat listeleme, kontrat derinliği (order book) çekme.
- Organizasyonun kalan limit/teminat bilgisini veya bunların excel export'unu almak.
- Teklif/eşleşme/blok kontrat özet raporlarını listelemek veya excel'e aktarmak.
- Sistem parametrelerini veya sunucu saatini okumak.

## Dikkat: host ve tarih formatı davranışı

`epint/models/request_model.py` içindeki `_get_host` ve `_convert_value_by_format` metodları, `gunici` kategorisi için host/tarih davranışını **tam string eşitliği** (`"gunici" == self._category`) ile kontrol eder:

```python
def _get_host(self, test_mode: bool) -> str:
    if "seffaflik" in self._category:
        return "seffaflik"
    if "gop" == self._category:
        return "testgop" if test_mode else "gop"
    if "gunici" == self._category:
        return "gunici"
    return "epys-prp" if test_mode else "epys"
```

`self._category` değeri `"gunici-trading"` olduğu için bu koşul **sağlanmaz** (`"gunici" == "gunici-trading"` → `False`). Sonuç olarak:

- **Host**: `gunici-trading` istekleri `gunici.epias.com.tr` / `gunici-prp.epias.com.tr`'e gitmez — swagger.json'daki `"host": "gunici-prp.epias.com.tr"` alanı **kod tarafından hiç kullanılmaz** (sadece dokümantasyon amaçlıdır, `RequestModel` bu alanı okumaz). Gerçekte "epys ailesi" varsayılanına düşer: prod'da `epys.epias.com.tr`, test modda `epys-prp.epias.com.tr`.
- **Tarih formatı**: `_convert_value_by_format` içinde de aynı tam-eşleşme kontrolü var (`self._category == "gunici"`). `gunici-trading` bu koşula girmediği için `DateTimeUtils.to_gunici_iso_string` (saat dilimsiz `2016-04-22T00:00:00`) **kullanılmaz**; bunun yerine diğer kategorilerle aynı olan `DateTimeUtils.to_iso_string` uygulanır → `+HH:MM` offset'li normal ISO format: `2016-04-22T00:00:00+03:00`.
- **Auth header'ları**: `Endpoint.__call__` içindeki header mantığı da `"gop"` ve `"seffaflik"` string kontrolü yapar, `gunici` için özel bir dal yoktur. Yani `gunici-trading` normal `TGT` + `ST` header çiftini alır (GOP'un `gop-service-ticket`'ı veya şeffaflığın header-az davranışı geçerli değildir).

Kısacası: `gunici-trading`, isminde "gunici" geçmesine rağmen **davranışsal olarak "epys" ailesinden bir kategori gibi çalışır** — sadece host ve tarih formatı standart epys davranışını izler. Bunu swagger.json'daki `host` alanına bakarak veya "gunici" kelimesinden yola çıkarak tahmin etme; kod bu şekilde çalışır (doğrulama: `epint/models/request_model.py` satır 61-70 ve 94-109).

## Endpoint'ler

Toplam **26 endpoint** (bazı `operationId` alanları swagger'da tekrarlı — aşağıdaki gotcha'ya bak).

| method_adi | HTTP | path | Açıklama |
|---|---|---|---|
| `get_collateral` | GET | `/rest/v1/collateral/get` | Aktif teminat bilgisi |
| `export_active_contract` | POST | `/rest/v1/collateral/history/export` | Teminat geçmişini excel'e aktar |
| `list_history_collateral` | POST | `/rest/v1/collateral/history/list` | Teminat geçmişi listeleme |
| `list_block_contract_available_time_list` | POST | `/rest/v1/contract/block-contract/available-time` | Blok kontrat geçerli süre listeleme |
| `list_active_contract` | POST | `/rest/v1/contract/board/list` | Aktif kontrat listeleme |
| `export_list_active_contract` | POST | `/rest/v1/contract/board/list/export` | Aktif kontrat listesini dışa aktar |
| `list_contract_depths` | POST | `/rest/v1/contract/depth` | Kontrat derinliği (order book) |
| `list_org_remaining_limits` | POST | `/rest/v1/dashboard/remaining-limits` | Kalan limitler grafiği |
| `export_org_remaining_limits` | POST | `/rest/v1/dashboard/remaining-limits/export` | Kalan limitler grafiğini dışa aktar |
| `save_block_offer` | POST | `/rest/v1/offer/block/save` | Blok teklif kaydetme |
| `save_bulk_hourly_offer` | POST | `/rest/v1/offer/bulk/hourly/save` | Toplu saatlik teklif kaydetme (JSON body, liste) |
| `save_hourly_offer_validate` | POST | `/rest/v1/offer/bulk/hourly/validate` | Toplu teklif dosyasını doğrulama (`multipart/form-data`, `file` alanı) |
| `cancel_all_offer` | POST | `/rest/v1/offer/cancel-by-contract` | Kontrat bazında tüm güncellenebilir teklifleri iptal etme |
| `save_hourly_offer` | POST | `/rest/v1/offer/hourly/save` | Saatlik (tekil) teklif kaydetme |
| `list_offers` | POST | `/rest/v1/offer/list` | Aktif/eşleşme bekleyen teklifleri listeleme |
| `update_status_offer` | POST | `/rest/v1/offer/status/update` | Teklif durumu güncelleme (aktif/pasif/iptal) |
| `update_offer` | POST | `/rest/v1/offer/update` | Teklif fiyat/miktar güncelleme |
| `parameter_approved_list` | POST | `/rest/v1/parameter/approved/list` | Onaylı sistem parametreleri (`ParameterPKReqDto`) |
| `parameter_list` | POST | `/rest/v1/parameter/list` | Sistem parametreleri (`ParameterUserReqDto`) |
| `list_parameter_group` | GET | `/rest/v1/parameter/group/list` | Parametre grupları |
| `system_time` | GET | `/rest/v1/parameter/time` | Sunucu (sistem) zaman bilgisi |
| `list_block_contract_summary` | POST | `/rest/v1/report/block-contract-summary` | Blok kontrat özet raporu |
| `export_block_contract_summary` | POST | `/rest/v1/report/block-contract-summary/export` | Blok kontrat özet raporunu dışa aktar |
| `list_match_offer_summary` | POST | `/rest/v1/report/match-summary` | Eşleşme özet raporu |
| `export_match_offer_summary` | POST | `/rest/v1/report/match-summary/export` | Eşleşme özet raporunu dışa aktar |
| `list_offer_summary` | POST | `/rest/v1/report/offer-summary` | Teklif özet raporu |
| `export_offer_summary` | POST | `/rest/v1/report/offer-summary/export` | Teklif özet raporunu dışa aktar |

## Önemli parametreler ve gotchalar

- **`parameter_approved_list` / `parameter_list` aynı operationId'yi paylaşıyordu:** swagger'da hem `/rest/v1/parameter/approved/list` hem `/rest/v1/parameter/list` `operationId: "list-parameter"` kullanır (farklı body şemaları: `ParameterPKReqDto` vs `ParameterUserReqDto`). `SwaggerModel`, aynı operationId'ye düşen endpoint'leri artık path'ten türetilen isimlerle otomatik ayrıştırıyor (bkz. [[01-epint-architecture]]), bu yüzden ikisi de yukarıdaki adlarla ayrı ayrı erişilebilir — hangi şemayı beklediğinden emin değilsen `print(ep.gunici_trading.parameter_list)` ile doğrula.
- **Teklif zorunlu alanları** (`save_hourly_offer` / `save_block_offer` / bulk): `contractName`, `region`, `offerType` (`BUY`/`SELL`), `optionType`, `price`, `quantity`, `isActive` zorunludur (swagger `required`). `optionType` değerleri: `NORMAL`, `IOC`, `FOK`, `PRICE_LEVELED`, `ICEBERG`, `TIME_LEVELED`.
  - `PRICE_LEVELED` seçilirse `priceLeveledOfferDetails` (liste) zorunlu; diğer opsiyonlarda **gönderilmemeli**.
  - `TIME_LEVELED` seçilirse `timeLeveledOfferDetails` (liste) zorunlu; diğer opsiyonlarda **gönderilmemeli**.
  - `ICEBERG` seçilirse `levelQuantity` (buzdağı seviye miktarı) zorunlu ve `quantity`'den küçük olmalı (`OFFER058`/`OFFER063` hata kodları); diğer opsiyonlarda `levelQuantity` boş kalmalı (`OFFER062`).
  - Blok teklifte sadece `NORMAL` ve `TEYE` opsiyonları geçerlidir (`OFFER040`); toplu (bulk) teklifte `NORMAL`, `TEYE`, `OEYE` geçerlidir (`OFFER054`).
  - `isConfirmed=True` gönderilirse kullanıcı limit aşımına rağmen teklif kaydedilmesine izin verilir (limit uyarılarını bilerek bypass eder — dikkatli kullan).
  - Bir bölge+kontrat kombinasyonuna aynı anda birden fazla teklif girilemez (`OFFER053`); zaten güncellenebilir bir teklif varsa onu `update_offer`/`update_status_offer` ile değiştirmek gerekir.
- **`save_hourly_offer_validate`** diğer offer endpoint'lerinden farklı olarak JSON body almaz, `multipart/form-data` ile zorunlu bir `file` alanı bekler (toplu teklif dosyasının ön-doğrulaması için).
- **`update_offer` / `update_status_offer`**: `id` (teklif no) zorunludur; ayrıca teklif optimistic-lock ile versiyonlanmıştır — teklif başka bir işlemle güncellenmişse `OFFER048` ("son versiyonu değişmiştir") hatası alınır, güncel veriyi `list_offers` ile tekrar çekip tekrar denemek gerekir. Zaman/fiyat seviyeli tekliflerde güncelleme yerine sadece **iptal** (`status=CANCEL`) yapılabilir (`OFFER029`, `OFFER037`).
- **`cancel_all_offer`**: sadece `contractName` + `region` alır, o kontrattaki **tüm güncellenebilir** teklifleri iptal eder — tekil teklif iptali için `update_status_offer` kullanılmalı.
- **Tarih alanları** (`expireTime`, `effectiveDateStart` vb.) `format: date-time` — yukarıdaki host/tarih bölümünde açıklandığı gibi normal `+03:00` offset'li ISO string'e çevrilir, elle formatlama yapma.
- **Teminat/limit yetersizliği**: `COL002` (teminat yetersizliği) ve `LIMIT001-018` (kullanıcı/yönetici/organizasyon limitleri, PTF'ye göre fiyat sapma sınırları) teklif kaydetme/güncellemede en sık dönen iş hatalarıdır — kullanıcıya göstermeden yutma, mesajı olduğu gibi ilet.
- **Referans md dosyası tuzağı**: `refs/ (epint kaynak reposu; portalda yok) — gunici-trading/EPİAŞ - GÜNİÇİ Servisleri.md` dosyasının satır 1-733 arası hata kodları `gunici-trading-service`'e, 735. satırdan sonrası ise **farklı bir servise** (`gunici-service`, ayrı `gunici` kategorisi) ait. Bu dosyadan örnek/kural çıkarırken sadece `gunici-trading-service` etiketli blokları kullan.

## Örnek kullanım

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# 1) Basit saatlik teklif kaydetme
sonuc = ep.gunici_trading.save_hourly_offer(
    contractName="PH25071612",
    region="TR1",
    offerType="BUY",
    optionType="NORMAL",
    price=2500.0,
    quantity=50,
    isActive=True,
    clientOrderId="siparis-001",
)
print(sonuc.offerResponse.id, sonuc.offerResponse.status)

# 2) Buzdağı (ICEBERG) teklif — quantity toplam miktar, levelQuantity görünür seviye miktarı
buzdagi_teklif = ep.gunici_trading.save_hourly_offer(
    contractName="PH25071612",
    region="TR1",
    offerType="SELL",
    optionType="ICEBERG",
    price=2600.0,
    quantity=500,
    levelQuantity=50,   # quantity'den küçük olmalı
    isActive=True,
)

# 3) Kontrat bazında tüm güncellenebilir teklifleri iptal etme
ep.gunici_trading.cancel_all_offer(contractName="PH25071612", region="TR1")

# 4) Aktif teklifleri listeleme ve teklif güncelleme
teklifler = ep.gunici_trading.list_offers()
for t in teklifler.offers:
    if t.contractName == "PH25071612":
        ep.gunici_trading.update_offer(id=t.id, price=2550.0, quantity=t.quantity)

# 5) Kontrat derinliğini (order book) çekme
derinlik = ep.gunici_trading.list_contract_depths(contractName="PH25071612", region="TR1")

# 6) Gerçek isteği atmadan RequestModel'i incelemek (host/header/body doğrulamak için)
req = ep.gunici_trading.save_hourly_offer(
    contractName="PH25071612", region="TR1", offerType="BUY",
    optionType="NORMAL", price=2500.0, quantity=50, isActive=True,
    debug=True,
)
print(req._endpoint_data["host"])  # epys.epias.com.tr (epys-prp test modda) — gunici.epias.com.tr DEĞİL
```

## Kaynaklar

- Swagger kaynağı: `epint/endpoints/gunici-trading/swagger.json`
- Kullanım kılavuzu (sadece `gunici-trading-service` etiketli bölüm, satır 1-733): `refs/ (epint kaynak reposu; portalda yok) — gunici-trading/EPİAŞ - GÜNİÇİ Servisleri.md`
- Host/tarih/auth davranışının kaynağı: `epint/models/request_model.py` (`_get_host` satır 61-70, `_convert_value_by_format` satır 94-114), `epint/models/endpoint_callable.py` (`Endpoint.__call__` header mantığı)
- Swagger parse ve operationId çakışma davranışı: `epint/models/swagger.py` (`SwaggerModel._parse_endpoints`)
- Genel mimari ve kullanım kuralları: [[01-epint-architecture]], [[02-epint-usage-conventions]]
