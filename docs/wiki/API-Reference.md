# API Referansı

EPINT kütüphanesinin tüm API metodları ve kullanımları.

## Kategoriler

### Şeffaflık (Seffaflik) Kategorileri

#### seffaflik_electricity (transparency)

Elektrik şeffaflık verileri için metodlar.

```python
# MCP verileri
result = ep.seffaflik_electricity.mcp_data(
    start='2025-12-10',
    end='2025-12-11'
)

# Tüketici sayısı export
xlsx_data = ep.seffaflik_electricity.consumer_count_export(
    period='2025-10-01',
    export_type='XLSX'
)
```

#### seffaflik_natural_gas (naturalgas, cng, dogalgaz)

Doğalgaz şeffaflık verileri için metodlar.

```python
result = ep.seffaflik_natural_gas.consumer_count_export(
    period='2025-10-01',
    export_type='XLSX'
)
```

#### seffaflik_reporting (reporting)

Raporlama verileri için metodlar.

### Uzlaştırma (Reconciliation) Kategorileri

#### reconciliation_invoice (invoice)

Fatura uzlaştırma metodları.

#### reconciliation_bpm (bpm)

BPM uzlaştırma metodları.

#### reconciliation_imbalance (imbalance)

Dengesizlik uzlaştırma metodları.

#### reconciliation_market (market)

Piyasa uzlaştırma metodları.

#### reconciliation_mof (mof)

MOF uzlaştırma metodları.

#### reconciliation_res (res)

RES uzlaştırma metodları.

#### pre_reconciliation

Ön uzlaştırma metodları.

### Diğer Kategoriler

- **gop**: GOP servisleri
- **customer**: Müşteri servisleri
- **demand**: Talep servisleri
- **grid**: Şebeke servisleri
- **registration**: Kayıt servisleri
- **balancing_group**: Dengeleme grubu servisleri
- **gunici**: Gün içi servisleri
- **gunici_trading**: Gün içi ticaret servisleri

## Parametreler

### Tarih Parametreleri

Tarih parametreleri string veya datetime objesi olarak verilebilir:

```python
from datetime import datetime

# String format
ep.seffaflik_electricity.mcp_data(start='2025-12-10', end='2025-12-11')

# Datetime format
ep.seffaflik_electricity.mcp_data(
    start=datetime(2025, 12, 10),
    end=datetime(2025, 12, 11)
)
```

### Sayfalama (Pagination)

Sayfalama parametreleri otomatik olarak varsayılan değerlerle doldurulur:

```python
# Varsayılan: page={'number': 1, 'size': 1000}
result = ep.customer.customer_list()

# Özel sayfalama
result = ep.customer.customer_list(page={'number': 2, 'size': 100})
```

### Bölge Parametreleri

Bölge parametreleri otomatik olarak varsayılan değerlerle doldurulur:

```python
# Varsayılan: region='TR1'
result = ep.demand.demand_forecast()

# Özel bölge
result = ep.demand.demand_forecast(region='TR2')
```

## Response Tipleri

### JSON Response'lar

JSON response'lar otomatik olarak parse edilir ve schema'ya göre dönüştürülür.

### Binary Response'lar

XLSX, PDF gibi binary içerikler `io.BytesIO` objesi olarak döndürülür:

```python
xlsx_data = ep.seffaflik_electricity.consumer_count_export(
    period='2025-10-01',
    export_type='XLSX'
)

with open('export.xlsx', 'wb') as f:
    f.write(xlsx_data.read())
```

## Method Bilgisi Görüntüleme

Endpoint bilgilerini görmek için:

```python
print(ep.seffaflik_electricity.mcp_data)
```

Bu komut şunları gösterir:
- Method ve path bilgisi
- Parametreler ve tipleri
- Response yapısı
- Örnek değerler

