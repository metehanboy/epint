# Örnekler

EPINT kütüphanesini kullanarak çeşitli senaryolar için örnekler.

## Temel Örnekler

### Elektrik Şeffaflık Verileri

```python
import epint as ep

# Kimlik doğrulama
ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")

# MCP verileri sorgulama
result = ep.seffaflik_electricity.mcp_data(
    start='2025-12-10',
    end='2025-12-11'
)

print(result)
```

### Doğalgaz Şeffaflık Verileri

```python
# Tüketici sayısı export
xlsx_data = ep.seffaflik_natural_gas.consumer_count_export(
    period='2025-10-01',
    export_type='XLSX'
)

# Dosyaya kaydet
with open('consumer_count.xlsx', 'wb') as f:
    f.write(xlsx_data.read())
```

### Müşteri Listesi

```python
# Müşteri listesi sorgulama
customers = ep.customer.customer_list()

# Sayfalama ile
customers = ep.customer.customer_list(page={'number': 1, 'size': 100})
```

## Gelişmiş Örnekler

### Tarih Aralığı ile Veri Çekme

```python
from datetime import datetime, timedelta

# Son 30 günün verilerini çek
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

result = ep.seffaflik_electricity.mcp_data(
    start=start_date,
    end=end_date
)
```

### Hata Yönetimi

```python
try:
    result = ep.seffaflik_electricity.mcp_data(
        start='2025-12-10',
        end='2025-12-11'
    )
except Exception as e:
    print(f"Hata oluştu: {e}")
    # Hata detaylarını işle
```

### Binary Dosya İşleme

```python
# XLSX export
xlsx_data = ep.seffaflik_electricity.consumer_count_export(
    period='2025-10-01',
    export_type='XLSX'
)

# Pandas ile okuma
import pandas as pd
df = pd.read_excel(xlsx_data)
print(df.head())
```

### Paralel İşlemler

```python
import concurrent.futures

def fetch_data(start_date, end_date):
    return ep.seffaflik_electricity.mcp_data(
        start=start_date,
        end=end_date
    )

# Tarih aralıklarını böl
date_ranges = [
    ('2025-01-01', '2025-01-31'),
    ('2025-02-01', '2025-02-28'),
    ('2025-03-01', '2025-03-31'),
]

# Paralel olarak çek
with concurrent.futures.ThreadPoolExecutor() as executor:
    results = executor.map(
        lambda r: fetch_data(r[0], r[1]),
        date_ranges
    )
```

## Kategori Alias Kullanımı

```python
# Kısa alias'lar kullanarak
ep.transparency.mcp_data(...)  # seffaflik_electricity
ep.naturalgas.mcp_data(...)    # seffaflik_natural_gas
ep.invoice.list(...)           # reconciliation_invoice
ep.bpm.list(...)               # reconciliation_bpm
```

## Fuzzy Matching

Method isimleri fuzzy matching ile bulunur:

```python
# Bu çağrılar aynı sonucu verir
ep.seffaflik_electricity.mcp_data(...)
ep.seffaflik_electricity.mcpData(...)
ep.seffaflik_electricity.mcp_data(...)
```

## Daha Fazla Örnek

Daha fazla örnek için [examples](https://github.com/epint/epint/tree/main/examples) klasörüne bakın.

