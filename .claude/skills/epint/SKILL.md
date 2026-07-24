---
name: epint
description: |
  epint (EPİAŞ Python client) kaynak reposu. epint / EPİAŞ / EPYS / şeffaflık / GOP / GİP /
  registration / customer / demand / grid / balancing-group / reconciliation / gunici
  ile çalışırken kullan. Tek skill hub: kategori detayı services/<category>.md.
---

# epint (kaynak repo)

Bu repo (`metehanboy/epint`) epint'in kaynağı — kod burada yazılır. Portal/airflow gibi tüketici repolar epint'i pip ile kurar.

## Prereq

1. `overview.md`
2. Kod / yeni endpoint / test yazıyorsan → `usage-conventions.md`
3. Fuzzy / auth / tarih debug → `architecture.md`
4. Bu hub → ilgili `services/<category>.md`

## Agent akışı

1. Bu `SKILL.md` (hangi kategori?)
2. Aşağıdaki tablodan **tek** `services/*.md` aç
3. Kaynak: `src/epint/` — kategori swagger: `endpoints/<category>/swagger.json`

## Kategori → referans

| Kategori | Alias | Dosya |
|----------|-------|-------|
| balancing-group | `balancing_group` | [`services/balancing-group.md`](services/balancing-group.md) |
| customer | `customer` | [`services/customer.md`](services/customer.md) |
| demand | `demand` | [`services/demand.md`](services/demand.md) |
| gop | `gop` | [`services/gop.md`](services/gop.md) |
| grid | `grid` | [`services/grid.md`](services/grid.md) |
| gunici | `gunici` | [`services/gunici.md`](services/gunici.md) |
| gunici-trading | `gunici_trading` | [`services/gunici-trading.md`](services/gunici-trading.md) |
| index-ac | `index_ac` | [`services/index-ac.md`](services/index-ac.md) |
| pre-reconciliation | `pre_reconciliation` | [`services/pre-reconciliation.md`](services/pre-reconciliation.md) |
| reconciliation-bpm | `bpm`, `reconciliation_bpm` | [`services/reconciliation-bpm.md`](services/reconciliation-bpm.md) |
| reconciliation-imbalance | `imbalance`, `reconciliation_imbalance` | [`services/reconciliation-imbalance.md`](services/reconciliation-imbalance.md) |
| reconciliation-invoice | `invoice`, `reconciliation_invoice` | [`services/reconciliation-invoice.md`](services/reconciliation-invoice.md) |
| reconciliation-market | `market`, `reconciliation_market` | [`services/reconciliation-market.md`](services/reconciliation-market.md) |
| reconciliation-mof | `mof`, `reconciliation_mof` | [`services/reconciliation-mof.md`](services/reconciliation-mof.md) |
| reconciliation-res | `res`, `reconciliation_res` | [`services/reconciliation-res.md`](services/reconciliation-res.md) |
| registration | `registration` | [`services/registration.md`](services/registration.md) |
| seffaflik-electricity | `transparency`, `seffaflik_electricity` | [`services/seffaflik-electricity.md`](services/seffaflik-electricity.md) |
| seffaflik-natural-gas | `naturalgas`, `cng`, `dogalgaz` | [`services/seffaflik-natural-gas.md`](services/seffaflik-natural-gas.md) |
| seffaflik-reporting | `reporting`, `seffaflik_reporting` | [`services/seffaflik-reporting.md`](services/seffaflik-reporting.md) |

## Not

`services/*.md` dosyaları portal/airflow reposundakiyle ortak — sadece kategori/endpoint listesini anlatır, tüketici repo fark etmez. Bu dosyalar epint kaynağıyla birlikte değişir; kod değiştiğinde (özellikle `swagger.json` veya `models/swagger.py`'deki isimlendirme mantığı) ilgili `services/<category>.md` güncellenmeli.
