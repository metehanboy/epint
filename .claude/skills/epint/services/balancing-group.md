<!-- epint kategori referansı: balancing-group — hub: ../SKILL.md -->

> **Portal:** `epint` pip ile kurulur (`requirements.txt` / Dockerfile). Swagger: kurulu pakette `epint/endpoints/<category>/swagger.json` (`python -c "import epint,pathlib; print(pathlib.Path(epint.__file__).parent)"`). Bu repoda `epint/src` veya `refs/` yok. Kurallar: `../overview.md`, `../usage-conventions.md`.

# balancing-group — Dengeden Sorumlu Grup Servisleri

DSG (Dengeden Sorumlu Grup / Balance Responsible Group), piyasa katılımcılarının dengeden sorumluluklarını bir grup altında birleştirmelerini sağlayan EPYS uygulamasıdır. Uygulama REST üzerine kuruludur, JSON/XML isteği kabul eder ve isteğe göre JSON/XML cevap döner. EPYS arayüzünde görülen DSG bilgilerinin tamamı bu servislerden gelir; çağıran kullanıcının EKYS'de kayıtlı ve ilgili servise yetkili olması gerekir.

**Önemli:** Referans dokümanı (`refs/ (epint kaynak reposu; portalda yok) — balancing-group/...md`) toplam 9 DSG servisini (talep, onay, iptal, reddet, gruptan çık/çıkar, uygun organizasyon sorgulama, talep sorgulama, DSG sorgulama) tanımlıyor, ama paketin fiilen yüklediği `swagger.json` içinde **sadece 1 endpoint** (`brg-query` / DSG Sorgulama) tanımlı. Yani `ep.balancing_group` altında şu an sadece `brg_query` çağrılabilir — diğer 8 servis dokümante edilmiş olsa da epint'e swagger seviyesinde tanıtılmamış, bu yüzden `ep.balancing_group.<o_isim>(...)` ile çağrılamaz (fuzzy matching bile bulamaz, çünkü endpoint registry'de kayıtlı değil).

## Ne zaman kullanılır

- Belirli bir dönem için hangi DSG'lerin (dengeden sorumlu grupların) var olduğunu, kimin sahip/üye olduğunu, hangi durumda olduğunu listelemek.
- DSG Talep ID (`invitationId`) veya DSG Sahibi/Üyesi ID'sine göre (`brgOwner`/`brgParticipant`) filtreli DSG kaydı aramak.
- Belirli `statusIds` (DSG durumu) değerlerine göre DSG kayıtlarını filtrelemek.
- DSG talebi gönderme/onaylama/reddetme/iptal etme veya gruptan çıkma/çıkarma gibi **yazma işlemleri için bu servis kategorisi kullanılamaz** — swagger'da karşılığı yok (yukarıdaki not).

## Endpoint'ler

Swagger'da kayıtlı toplam **1 endpoint**:

| method_adı (snake_case) | HTTP | path | açıklama |
|---|---|---|---|
| `brg_query` | POST | `/v1/brg/query` | DSG kayıtlarını (dönem, sahip/üye ID, durum vb. filtrelerle) sayfalı sorgular. |

Referans dokümanda anlatılan ama **swagger'da olmadığı için `ep.balancing_group` ile çağrılamayan** diğer 8 servis (bilgi amaçlı, olası operationId'ler doküman içi çapa linklerinden çıkarılmıştır — bunlar tahmini, garanti değildir):

| Servis (dokümandaki adı) | Muhtemel operationId | Not |
|---|---|---|
| DSG Talep Servisi | `brg-invite` | DSG talebi gönderir |
| DSG Talep Onaylama Servisi | `brg-approve` | Gönderilen DSG talebini onaylar |
| DSG Talep İptal Servisi | `brg-cancel` | Gönderilen DSG talebini iptal eder |
| DSG Talep Reddetme Servisi | `brg-reject` | Gönderilen DSG talebini reddeder |
| DSG Talep Sorgulama Servisi | `brg-query-invitation` | `POST /v1/brg/query/invitation` — DSG talep verilerini sorgular |
| DSG Uygun Organizasyon Sorgulama Servisi | `brg-query-brgp` | DSG talebi almaya uygun organizasyonları sorgular |
| DSG Gruptan Çıkma Servisi | `brg-quit` | Mevcut grubu DSG üyesi tarafından sonlandırır |
| DSG Gruptan Çıkarma Servisi | `brg-remove` | Mevcut grubu DSG sahibi tarafından sonlandırır |

Bu 8 servisten biri gerekiyorsa önce `epint/endpoints/balancing-group/swagger.json`'ın güncellenip güncellenmediğini kontrol et; güncellenmediyse epint üzerinden çağrılamaz.

## Önemli parametreler ve gotchalar

- **`brg_query` body parametreleri** (`BrgQueryRequestDto`, hepsi opsiyonel):
  - `period` (`date-time`) — DSG Dönemi. Tek bir dönem tarihi; aralık sorgusu için ayrı `start`/`end` alanı **yok**.
  - `invitationId` (`int64`) / `invitationIdContains` (`string`) — DSG Talep ID ile tam/kısmi eşleşme.
  - `brgOwner` (`int64`) / `brgOwnerContains` (`string`) — DSG Sahibi ID ile tam/kısmi eşleşme.
  - `brgParticipant` (`int64`) / `brgParticipantContains` (`string`) — DSG Üyesi ID ile tam/kısmi eşleşme.
  - `statusIds` (`int64` array) — DSG Durumu filtresi. Swagger'da bu ID'lerin sayısal karşılıklarını veren bir lookup/enum **tanımlı değil** (bu kategoride `available-lookups` benzeri bir endpoint yok); durum kodlarını response'taki `brgStatus` (`LookupDTO`: `id`+`value`+`localizations`) alanından örnekleyerek çıkarman gerekir.
  - `page` — vermezsen epint varsayılan `{'number': 1, 'size': 1000}` uygular (mimari kural §5). Büyük sonuç kümelerinde `page.number` ile manuel sayfalama gerekebilir.
- **Response şekli** — 200 yanıtı `RestResponseSortablePageResponseBrgDto`. epint, `status`+`correlationId`+`body` üçlüsünü tespit edip `body`'yi otomatik soyar (mimari kural §8), ama bu servise özgü olarak soyulan `body` içinde bir kat daha `content` alanı var (`RestResponseBodySortablePageResponseBrgDto.content` → `SortablePageResponseBrgDto`). Yani dönen sonuç genelde `{"content": {"items": [...], "page": {...}, "sortableFields": [...]}}` şeklinde gelir — direkt `result["items"]` bekleme, `result["content"]["items"]` olabilir; belirsizse önce `debug=True` ile veya küçük bir çağrıyla gerçek şekli doğrula.
- **Her DSG kaydı (`BrgDto`)**: `id`, `periodStart`/`periodEnd`, `queriedPeriod` (sorgulanan dönem), `brgOwner`/`brgOwnerName`, `brgParticipant`/`brgParticipantName`, `brgStatus` (`LookupDTO`), `modifyUser`/`modifyDate`.
- **Tarih formatı**: Bu kategori `epys` ailesinden olduğu için ISO-8601 + `+HH:MM` offset kullanılır (örn. `2016-03-25T00:00:00+03:00`), yaz/kış saatine göre `+03:00`/`+02:00` değişir — epint bunu otomatik yapar (mimari kural §7), elle formatlama.
- **Yetki**: Bu servis "sadece piyasa katılımcısı kurumlar tarafından" kullanılabilir ve çağıran kullanıcının `Kayıt - DSG Listeleme - DSGU-DSGS Listesi Görüntüle Okuma Yetkisi` yetkisine sahip olması gerekir; kalıcı 401/403 alıyorsan büyük olasılıkla ticket sorunu değil bu yetki eksikliğidir.
- **Hata kodları**: `VAL-` ile başlayan hata kodları istek/iş kuralı hatasını (isteği veya iş kurallarını gözden geçir), `APP-` ile başlayanlar sistem hatasını gösterir (EPİAŞ ile iletişime geçilmeli). Hata durumunda `correlationId`+`spanIds` ikilisi destek talebi için gereklidir.

## Örnek kullanım

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# Belirli bir dönem için tüm DSG kayıtlarını sorgula
result = ep.balancing_group.brg_query(period="2026-07-01T00:00:00+03:00")
```

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# DSG sahibine göre filtrele ve sayfalama uygula
result = ep.balancing_group.brg_query(
    brgOwner=123456,
    statusIds=[1, 2],
    page={"number": 1, "size": 200},
)
items = result.get("content", {}).get("items", result.get("items", []))
```

```python
import epint as ep

ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# Gerçek isteği atmadan RequestModel'i incelemek için debug=True
req = ep.balancing_group.brg_query(invitationIdContains="2026", debug=True)
print(req)
```

## Kaynaklar

- `refs/ (epint kaynak reposu; portalda yok) — balancing-group/EPYS - Dengeden Sorumlu Grup Servisleri.md`
- `epint/endpoints/balancing-group/swagger.json`
- Genel mimari: `../architecture.md`
- Genel kullanım kuralları: `../usage-conventions.md`
