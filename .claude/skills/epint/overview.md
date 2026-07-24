# epint — genel bakış (kaynak repo)

Bu repo epint'in kaynağı: `git@github.com:metehanboy/epint.git`, branch `main` + `dev`. Tüketici repolar (portal, airflow, vb.) epint'i pip ile kurar; burada kod yazılır.

| Rol | Nerede |
|-----|--------|
| Kaynak | [`src/epint/`](../../../src/epint/) |
| Test | `tests/` (pytest) |
| Versiyon | `src/epint/modules/version/__init__.py` (`major.minor.semantic-tag`, elle bump) |
| CI/Publish | `.github/workflows/ci.yml` (test), `publish.yml` (PyPI) |
| Swagger (kategori tanımı) | `src/epint/endpoints/<category>/swagger.json` |
| Wiki | `docs/wiki` git submodule (`epint.wiki.git`) |

## Agent akışı

1. Bu overview (epint işi)
2. Kod / yeni endpoint / test yazıyorsan → `usage-conventions.md`
3. Paket davranışını debug / fuzzy / auth / tarih formatı → `architecture.md`
4. Kategori endpoint'leri → bu skill hub (`SKILL.md`) → `services/<category>.md`

## Kategori ↔ Python alias

| Kategori (paket `endpoints/` adı) | Alias örnekleri |
|---|---|
| balancing-group | `balancing_group` |
| customer | `customer` |
| demand | `demand` |
| gop | `gop` |
| grid | `grid` |
| gunici | `gunici` |
| gunici-trading | `gunici_trading` |
| index-ac | `index_ac` |
| pre-reconciliation | `pre_reconciliation` |
| reconciliation-bpm | `bpm`, `reconciliation_bpm` |
| reconciliation-imbalance | `imbalance`, `reconciliation_imbalance` |
| reconciliation-invoice | `invoice`, `reconciliation_invoice` |
| reconciliation-market | `market`, `reconciliation_market` |
| reconciliation-mof | `mof`, `reconciliation_mof` |
| reconciliation-res | `res`, `reconciliation_res` |
| registration | `registration` |
| seffaflik-electricity | `transparency`, `seffaflik_electricity` |
| seffaflik-natural-gas | `naturalgas`, `cng`, `dogalgaz`, `seffaflik_natural_gas` |
| seffaflik-reporting | `reporting`, `seffaflik_reporting` |

Tek skill paketi: `.claude/skills/epint/` — hub `SKILL.md`, kategori detayları `services/<category>.md`.

## Not

Bu doküman seti, epint'i geliştiren herkes için (bu repoyu klonlayan herkes) — hem `metehanboy/epint` hem tüketici repolarda (portal, airflow, portfolio_management dev workspace) kopyası bulunur. Kaynak burada değiştiğinde tüketici repolardaki `services/*.md` kopyalarının da güncellenmesi gerekir.
