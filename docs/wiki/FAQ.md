# Sık Sorulan Sorular (SSS)

EPINT kütüphanesi hakkında sık sorulan sorular ve cevapları.

## Genel Sorular

### EPINT nedir?

EPINT, EPİAŞ (Enerji Piyasaları İşletme A.Ş.) API'lerine erişim sağlayan bir Python kütüphanesidir.

### Hangi Python versiyonları destekleniyor?

EPINT Python 3.11 ve üzeri versiyonları destekler.

### Nasıl kurulur?

```bash
pip install epint
```

### Kimlik bilgilerimi nasıl ayarlarım?

```python
import epint as ep
ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")  # veya "test"
```

## Kullanım Soruları

### Tarih formatı nasıl olmalı?

Tarih parametreleri string veya datetime objesi olarak verilebilir:

```python
# String format
ep.seffaflik_electricity.mcp_data(start='2025-12-10', end='2025-12-11')

# Datetime format
from datetime import datetime
ep.seffaflik_electricity.mcp_data(
    start=datetime(2025, 12, 10),
    end=datetime(2025, 12, 11)
)
```

### Binary dosyaları (XLSX, PDF) nasıl kaydederim?

```python
xlsx_data = ep.seffaflik_electricity.consumer_count_export(
    period='2025-10-01',
    export_type='XLSX'
)

with open('export.xlsx', 'wb') as f:
    f.write(xlsx_data.read())
```

### Method isimlerini tam olarak bilmem gerekiyor mu?

Hayır, EPINT fuzzy matching kullanır. Küçük yazım hataları tolere edilir:

```python
ep.seffaflik_electricity.mcp_data(...)
ep.seffaflik_electricity.mcpData(...)  # Aynı sonucu verir
```

### Kategori alias'ları nelerdir?

Bazı kategoriler için kısa alias'lar mevcuttur:

- `transparency` → `seffaflik_electricity`
- `naturalgas`, `cng`, `dogalgaz` → `seffaflik_natural_gas`
- `invoice` → `reconciliation_invoice`
- `bpm` → `reconciliation_bpm`

## Hata Sorunları

### "Authentication required" hatası alıyorum

Kimlik bilgilerinizi doğru ayarladığınızdan emin olun:

```python
ep.set_auth("kullanici_adi", "sifre")
```

### "Date range too large" hatası alıyorum

EPINT otomatik olarak büyük tarih aralıklarını küçük parçalara böler. Eğer hala sorun yaşıyorsanız, tarih aralığınızı manuel olarak küçültün.

### API rate limit hatası alıyorum

API rate limit'ine takıldıysanız, istekleriniz arasında bekleme süresi ekleyin:

```python
import time

for date_range in date_ranges:
    result = ep.seffaflik_electricity.mcp_data(...)
    time.sleep(1)  # 1 saniye bekle
```

## Geliştirme Soruları

### Nasıl katkıda bulunabilirim?

[CONTRIBUTING.md](https://github.com/epint/epint/blob/main/CONTRIBUTING.md) dosyasını inceleyin.

### Test nasıl çalıştırılır?

```bash
pytest
```

### Kod formatlaması nasıl yapılır?

```bash
black src/
isort src/
```

## Diğer Sorular

### Sorunuz burada yok mu?

- [GitHub Issues](https://github.com/epint/epint/issues) sayfasından yeni bir soru açın
- [Discussions](https://github.com/epint/epint/discussions) sayfasına bakın
- Dokümantasyonu kontrol edin

