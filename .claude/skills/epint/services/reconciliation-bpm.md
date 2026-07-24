<!-- epint kategori referansı: reconciliation-bpm — hub: ../SKILL.md -->

> **Portal:** `epint` pip ile kurulur (`requirements.txt` / Dockerfile). Swagger: kurulu pakette `epint/endpoints/<category>/swagger.json` (`python -c "import epint,pathlib; print(pathlib.Path(epint.__file__).parent)"`). Bu repoda `epint/src` veya `refs/` yok. Kurallar: `../overview.md`, `../usage-conventions.md`.

# reconciliation-bpm — BPM Uzlaştırma Servisleri

"BPM" bu servis ailesinde **DGP (Dengeleme Güç Piyasası — Balancing Power Market)** karşılığıdır; swagger içindeki tüm talimat (`instruction`) uç noktalarının summary/description metinlerinde "DGP" adı geçer. Servis; DGP YAL/YAT talimatlarını, bu talimatların uzlaştırma (reconciliation) sonuçlarını, EAK (Emre Amade Kapasite), KGÜP (Kesinleşmiş Günlük Üretim/Tüketim Programı), KÜPST (SBFGP — Settlement Based Final Generation Plan) ve SMF (Sistem Marjinal Fiyatı) verilerini sorgulama/export etme imkanı verir. Kaynak swagger: `epint/endpoints/reconciliation-bpm/swagger.json` (host: `epys-qa.epias.com.tr`, basePath `/reconciliation-bpm/` — gerçek host/mode seçimi epint'in "epys ailesi" mantığına göre otomatiktir, bkz. [[01-epint-architecture]] §5).

## Ne zaman kullanılır

- DGP talimat listesi/versiyonları, talimat uzlaştırma detayları (santral veya organizasyon bazında) ile ilgili kod yazarken.
- Teslim edilemeyen (undeliverable) talimat maliyet/ceza hesapları için.
- EAK, KGÜP (üretim/tüketim programı), KÜPST (SBFGP) veya SMF verisi çekerken.
- Bu verileri Excel/CSV/PDF olarak export eden akışlarda.

## Endpoint'ler

Toplam **30 endpoint** (`get-`/`list-`/`bpm-` ile başlayanlar veri döner, `export-` ile başlayanlar dosya döner). `<method_adi>` operationId'den türetilmiştir (`-`→`_`, camelCase'ler snake_case'e çevrilir).

| method_adi | HTTP | path | Açıklama |
|---|---|---|---|
| `export_available_installed_capacity_details` | POST | `/v1/aic/export` | EAK listesini export eder |
| `get_available_installed_capacity_details` | POST | `/v1/aic/list` | EAK (Emre Amade Kapasite) listesini döner |
| `export_available_installed_capacity_version_details` | POST | `/v1/aic/version/export` | Seçilen UEVCB'nin versiyonlu EAK listesini export eder |
| `get_available_installed_capacity_versions` | POST | `/v1/aic/version/list` | Seçilen UEVCB'nin versiyonlu EAK listesini döner |
| `export_final_daily_consumption_program_details` | POST | `/v1/fdcp/export` | Kesinleşmiş günlük tüketim programı (FDCP) detaylarını export eder |
| `get_final_daily_consumption_program_details` | POST | `/v1/fdcp/list` | FDCP (tüketim programı) detaylarını listeler |
| `export_final_daily_production_program_details` | POST | `/v1/fddp/export` | KGÜP (kesinleşmiş günlük üretim programı) detaylarını export eder |
| `get_final_daily_production_program_details` | POST | `/v1/fddp/list` | KGÜP detaylarını listeler |
| `export_final_daily_production_program_version_details` | POST | `/v1/fddp/version/export` | KGÜP'ün versiyon bazlı detaylarını export eder |
| `get_final_daily_production_program_versions` | POST | `/v1/fddp/version/list` | KGÜP'ün versiyon bazlı detaylarını listeler |
| `get_bpm_instruction_list` | POST | `/v1/instruction/list` | DGP talimatlarını listeler |
| `export_bpm_instruction_list` | POST | `/v1/instruction/list/export` | DGP talimat listesini export eder |
| `get_bpm_instruction_versions` | POST | `/v1/instruction/version` | Bir talimatın (`instructionId`) versiyonlarını döner |
| `export_bpm_instruction_versions` | POST | `/v1/instruction/version/export` | Talimat versiyonlarını export eder |
| `bpm_look_up_value` | GET | `/v1/lookup/list` | Ekranlarda kullanılan lookup (label/value) referans değerlerini döner — parametresiz |
| `export_bpm_instruction_detail_response_dto` | POST | `/v1/reconciliation/detail/export` | Talimat detay uzlaştırma sonuçlarını export eder |
| `get_bpm_instruction_reconciliation_details` | POST | `/v1/reconciliation/detail/list` | Talimat detay uzlaştırma sonuçlarını (santral/UEVCB bazında) listeler |
| `get_instruction_undeliverable_details` | POST | `/v1/reconciliation/instruction/undeliverable` | Teslim edilemeyen (undeliverable) talimat maliyet detaylarını listeler |
| `export_instruction_undeliverable_details` | POST | `/v1/reconciliation/instruction/undeliverable/export` | Teslim edilemeyen talimat maliyet detaylarını export eder |
| `reconciliation_organization_export` | POST | `/v1/reconciliation/organization/export` | Organizasyon bazlı DGP uzlaştırma sonuçlarını export eder |
| `get_bpm_instruction_reconciliation` | POST | `/v1/reconciliation/organization/list` | Organizasyon bazlı DGP uzlaştırma sonuçlarını listeler |
| `list_difference_settlement_entity_instruction_response_dto` | POST | `/v1/reconciliation/retrospective/bpm/list` | Organizasyonların UEVCB'lerine ait fatura dönemi farklarını (GDDK) listeler |
| `export_bpm_retrospective_list` | POST | `/v1/reconciliation/retrospective/bpm/list/export` | UEVCB fark (GDDK) listesini export eder |
| `list_diff_recon_organization_settlement_based_final_generation_plan_response_dto` | POST | `/v1/reconciliation/retrospective/sbfgp` | KÜPST'e ait geçmişe dönük (GDDK) fark detaylarını listeler |
| `bpm_reconciliation_retrospective` | POST | `/v1/reconciliation/retrospective/sbfgp/export` | KÜPST GDDK detaylarını export eder |
| `get_sbfgp_reconciliation_detail_response_dtos_list` | POST | `/v1/reconciliation/sbfgp` | KÜPST uzlaştırma detaylarını (özet dahil) listeler |
| `export_sbfgp_reconciliation_detail_response_dtos_list` | POST | `/v1/reconciliation/sbfgp/export` | KÜPST uzlaştırma detaylarını export eder |
| `get_recon_kupst_by_source_type` | POST | `/v1/reconciliation/sbfgp/source-tpye/detail` | KÜPST sonuçlarını kaynak tipine (`sourceTypeId`) göre listeler |
| `reconciliation_sbfgp_source_tpye_detail_export` | POST | `/v1/reconciliation/sbfgp/source-tpye/detail/export` | KÜPST'i kaynak tipine göre export eder |
| `list_system_marginal_price_list` | POST | `/v1/smp/list` | SMF (Sistem Marjinal Fiyatı) ve yön (deficit/balance/surplus) listesini döner |

## Önemli parametreler ve gotchalar

1. **Auth normal EPYS akışıdır**: bu kategori adında `gop`/`seffaflik` geçmediği için `TGT` + `ST` header'ları otomatik eklenir (bkz. [[01-epint-architecture]] §6). `retrospective/bpm/list` ve `retrospective/bpm/list/export` swagger'da ayrıca `TGT` header'ını `required: true` body-dışı parametre olarak da tanımlar — epint bunu zaten otomatik dolduruyor, elle geçmeyin.
2. **`reconciliation_organization_export` / `reconciliation_sbfgp_source_tpye_detail_export` aynı operationId'yi paylaşıyordu** (`export-bpm-instruction-reconciliation-details`, farklı body şemaları: `BpmReconciliationDetailRequestDto` vs `ReconKupstQueryBySourceTypeDto`). `SwaggerModel` bu tür çakışmaları path'ten türetilen isimlerle otomatik ayrıştırıyor, ikisi de yukarıdaki adlarla ayrı ayrı erişilebilir.
3. **`direction` alanının şekli endpoint'e göre değişir**: talimat/organizasyon detay DTO'larında (`BpmInstructionUndeliverableDetailDto`, vb.) `{label, value}` şeklinde bir `LabelValueDTO` nesnesidir (`value`: `ENERGY_DEFICIT`/`ENERGY_SURPLUS`, `label`: "Enerji Açığı"/"Enerji Fazlası"). `list_system_marginal_price_list` (`/v1/smp/list`) yanıtındaki `SmpDto.direction` ise düz bir string enum'dur ve **üçüncü bir değer** içerir: `ENERGY_DEFICIT` / `IN_BALANCE` / `ENERGY_SURPLUS`. Response parse ederken bu ikisini birbirine karıştırmayın.
4. **`period` / `effectiveDateStart`+`effectiveDateEnd` / `version`+`versions` farklı şeylerdir**: `period` genelde fatura/uzlaştırma dönemini, `effectiveDateStart`/`effectiveDateEnd` saatlik/günlük tarih aralığı filtresini, `version`/`versions` o dönem için üretilmiş uzlaştırma versiyon damgalarını temsil eder. Bazı DTO'lar (örn. `BpmReconInstructionDetailRequestDto`) üçünü birden kabul eder — endpoint'in gerçekten hangilerini beklediğini `print(ep.bpm.<method>)` ile kontrol edin, hepsini "tarih" sanıp karıştırmayın.
5. **En yaygın filtre çifti**: `powerPlantId` (Enerji Santrali Id) ve `settlementPointId` (Anlaşma Id / UEVCB). `region` verilmezse epint otomatik `'TR1'` kullanır (bkz. [[02-epint-usage-conventions]]).
6. **`exportType` enum'u** (`XLSX`/`CSV`/`PDF`) neredeyse tüm `/export` uç noktalarında body parametresi olarak zorunlu değil ama pratikte belirtilmesi gerekir; swagger response şeması jenerik `ModelAndView` olsa da gerçek HTTP yanıtı binary'dir — epint bunu `io.BytesIO` olarak döner (bkz. [[02-epint-usage-conventions]] "Binary response'lar").
7. **Undeliverable/ceza alanları**: `undeliverableRatio`, `totalUndeliverableAmount`, `undeliverableUpRegulationAmount`, `undeliverableDownRegulationAmount` — talimatın ne kadarının fiilen yerine getirilemediğini gösterir; bu alanlar 0'dan büyükse santralin uzlaştırma maliyeti/cezası etkilenir, uzlaştırma sonuçlarını yorumlarken özellikle bu alanları kontrol edin.
8. **Sayfalama**: `page` parametresi olan tüm liste endpoint'lerinde vermezseniz epint varsayılan `{'number': 1, 'size': 1000}` kullanır; `page.total` yanıttaki gerçek kayıt sayısını verir — büyük tarih aralıklarında tek sayfada her şeyi almadığınızı unutmayın.
9. **Kaynak dokümandaki tutarsızlık**: `/v1/fdcp/*` (final-daily-**consumption**-program) endpoint'lerinin summary/description metinleri hatalı biçimde "KGÜP" (üretim programı terimi) kullanır, ama gerçek response alanı `dcp` (tüketim) — `dpp` (üretim, `/v1/fddp/*`) ile karıştırmayın, koddaki alan adına güvenin.
10. **`refs/ (epint kaynak reposu; portalda yok) — reconciliation-bpm/EPYS - BPM Uzlaştırma Servisleri.md`** (~1051 satır) prose/parametre tablosu içermez — dosyanın tamamı `get_instruction_undeliverable_details` (`/v1/reconciliation/instruction/undeliverable`) endpoint'inin tek bir örnek JSON response'udur (`direction`, `dpp`, `smp`, `reconciliationSmp`, `upRegulationTotal`/`downRegulationTotal`, `systemUpRegulationTotal`/`systemDownRegulationTotal`, `undeliverableRatio` alanlarını gösterir). Diğer 29 endpoint için parametre/response bilgisi yalnızca `swagger.json`'dan çıkarılabilir.

## Örnek kullanım

```python
import epint as ep

ep.set_auth(username, password)
ep.set_mode("prod")

# 1) Belirli bir santral/UEVCB için teslim edilemeyen (undeliverable) talimat
#    maliyet detaylarını çek — md örneğindeki endpoint budur.
result = ep.bpm.get_instruction_undeliverable_details(
    effectiveDateStart="2023-01-01T00:00:00+03:00",
    effectiveDateEnd="2023-01-05T00:00:00+03:00",
    region="TR1",
    powerPlantId=101,
    settlementPointId=102,
)
for item in result["items"]:
    if item["undeliverableRatio"] > 0:
        print(item["effectiveDate"], item["direction"]["label"], item["undeliverableRatio"])

# 2) Organizasyon bazlı DGP uzlaştırma sonuçlarını sayfalayarak çek
page_number = 1
all_items = []
while True:
    resp = ep.reconciliation_bpm.get_bpm_instruction_reconciliation(
        effectiveDateStart="2023-01-01T00:00:00+03:00",
        effectiveDateEnd="2023-01-31T00:00:00+03:00",
        region="TR1",
        page={"number": page_number, "size": 500},
    )
    all_items.extend(resp["items"])
    if page_number >= resp["page"]["total"] // 500 + 1:
        break
    page_number += 1

# 3) KÜPST detaylarını XLSX olarak export et (io.BytesIO döner)
xlsx_data = ep.bpm.export_sbfgp_reconciliation_detail_response_dtos_list(
    period="2023-01-01T00:00:00+03:00",
    effectiveDateStart="2023-01-01T00:00:00+03:00",
    effectiveDateEnd="2023-01-31T00:00:00+03:00",
    exportType="XLSX",
)
with open("kupst.xlsx", "wb") as f:
    f.write(xlsx_data.read())
```

## Kaynaklar

- `refs/ (epint kaynak reposu; portalda yok) — reconciliation-bpm/EPYS - BPM Uzlaştırma Servisleri.md` — tek örnek JSON response (bkz. gotcha #10).
- `refs/ (epint kaynak reposu; portalda yok) — reconciliation-bpm/swagger.json` / `epint/endpoints/reconciliation-bpm/swagger.json` — asıl OpenAPI 2.0 kaynağı (paket bu kopyayı runtime'da yükler).
- Genel mimari: [[01-epint-architecture]]. Kullanım kuralları: [[02-epint-usage-conventions]]. Kategori/alias eşlemesi: [[00-epint-overview]].
