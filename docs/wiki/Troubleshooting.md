# Sorun Giderme

EPINT kullanırken karşılaşabileceğiniz yaygın sorunlar ve çözümleri.

## Kimlik Doğrulama Sorunları

### "Authentication required" Hatası

**Sorun**: API çağrılarında kimlik doğrulama hatası alıyorsunuz.

**Çözüm**:
```python
# Kimlik bilgilerinizi kontrol edin
ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")  # veya "test"

# Kimlik bilgilerinin ayarlandığını doğrulayın
print(ep.get_auth())  # Eğer bu metod varsa
```

### "Invalid credentials" Hatası

**Sorun**: Geçersiz kimlik bilgileri hatası.

**Çözüm**:
- Kullanıcı adı ve şifrenizi kontrol edin
- Test ve prod ortamları için farklı kimlik bilgileri gerekebilir
- Şifrenizde özel karakterler varsa, düzgün escape edildiğinden emin olun

## Tarih Aralığı Sorunları

### "Date range too large" Hatası

**Sorun**: Tarih aralığı çok büyük.

**Çözüm**:
EPINT otomatik olarak büyük tarih aralıklarını böler. Eğer hala sorun yaşıyorsanız:

```python
# Tarih aralığınızı manuel olarak küçültün
from datetime import datetime, timedelta

start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 1, 31)  # 1 aylık aralık

result = ep.seffaflik_electricity.mcp_data(
    start=start_date,
    end=end_date
)
```

### Tarih Formatı Hataları

**Sorun**: Tarih formatı kabul edilmiyor.

**Çözüm**:
```python
# ISO formatını kullanın
ep.seffaflik_electricity.mcp_data(
    start='2025-12-10',  # YYYY-MM-DD
    end='2025-12-11'
)

# Veya datetime objesi kullanın
from datetime import datetime
ep.seffaflik_electricity.mcp_data(
    start=datetime(2025, 12, 10),
    end=datetime(2025, 12, 11)
)
```

## API Çağrı Sorunları

### "Connection timeout" Hatası

**Sorun**: Bağlantı zaman aşımına uğruyor.

**Çözüm**:
- İnternet bağlantınızı kontrol edin
- API sunucularının erişilebilir olduğundan emin olun
- Proxy ayarlarınızı kontrol edin (eğer varsa)

### "Rate limit exceeded" Hatası

**Sorun**: API rate limit'ine takıldınız.

**Çözüm**:
```python
import time

# İstekler arasında bekleme ekleyin
for date_range in date_ranges:
    result = ep.seffaflik_electricity.mcp_data(...)
    time.sleep(1)  # 1 saniye bekle
```

### "Method not found" Hatası

**Sorun**: Method bulunamıyor.

**Çözüm**:
```python
# Method ismini kontrol edin
# Fuzzy matching kullanılır ama tam isim daha güvenilirdir

# Mevcut metodları listeleyin (eğer bu özellik varsa)
print(dir(ep.seffaflik_electricity))

# Method bilgisini görüntüleyin
print(ep.seffaflik_electricity.mcp_data)
```

## Response İşleme Sorunları

### Binary Dosya Okunamıyor

**Sorun**: XLSX veya PDF dosyaları okunamıyor.

**Çözüm**:
```python
# BytesIO objesi olarak döndürülür
xlsx_data = ep.seffaflik_electricity.consumer_count_export(
    period='2025-10-01',
    export_type='XLSX'
)

# Dosyaya kaydedin
with open('export.xlsx', 'wb') as f:
    f.write(xlsx_data.read())

# Veya pandas ile direkt okuyun
import pandas as pd
df = pd.read_excel(xlsx_data)
```

### JSON Parse Hatası

**Sorun**: JSON response parse edilemiyor.

**Çözüm**:
```python
try:
    result = ep.seffaflik_electricity.mcp_data(...)
    print(result)
except Exception as e:
    print(f"Hata: {e}")
    # Hata detaylarını inceleyin
```

## Performans Sorunları

### Yavaş API Çağrıları

**Sorun**: API çağrıları çok yavaş.

**Çözüm**:
- Tarih aralığınızı küçültün
- Paralel işlemler kullanın (dikkatli olun, rate limit'e takılabilirsiniz)
- Gereksiz parametreleri kaldırın

### Bellek Kullanımı

**Sorun**: Çok fazla bellek kullanılıyor.

**Çözüm**:
- Büyük veri setlerini parçalara bölün
- Generator kullanın (eğer destekleniyorsa)
- Kullanılmayan verileri temizleyin

## Kurulum Sorunları

### "Module not found" Hatası

**Sorun**: EPINT modülü bulunamıyor.

**Çözüm**:
```bash
# EPINT'in kurulu olduğundan emin olun
pip install epint

# Virtual environment kullanıyorsanız aktif olduğundan emin olun
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Versiyon Uyumsuzluğu

**Sorun**: Python versiyonu uyumsuz.

**Çözüm**:
EPINT Python 3.11+ gerektirir. Python versiyonunuzu kontrol edin:

```bash
python --version
```

## Yardım Alma

Sorununuzu çözemediyseniz:

1. [[SSS|FAQ]] sayfasına bakın
2. [GitHub Issues](https://github.com/epint/epint/issues) sayfasında benzer sorunları arayın
3. Yeni bir [issue](https://github.com/epint/epint/issues/new) açın ve şu bilgileri ekleyin:
   - Python versiyonu
   - EPINT versiyonu
   - Hata mesajı
   - Tekrarlanabilir kod örneği
   - İşletim sistemi

