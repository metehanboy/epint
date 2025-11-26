# EPINT Test Dokümantasyonu

## Test Ortamı

Testler Python 3.11 virtual environment'ında çalıştırılmaktadır:
```bash
/opt/envs/venv-python3.11/bin/python3.11
```

## Test Dosyaları

### `test_epint_methods.py`

EPINT method testleri. Swagger JSON'dan yüklenen endpoint'lerin method olarak kullanılabilirliğini test eder.

#### Test Sınıfları

1. **TestEpintMethods**: Ana method testleri
   - Kategori manager'ların varlığı
   - Namespace erişimi (`ep.gunici.method_name`)
   - Endpoint yükleme
   - Method isim sanitizasyonu
   - Swagger parsing
   - Endpoint info yapısı
   - Arama fonksiyonları
   - Kategori listeleme

2. **TestEpintSwaggerParsing**: Swagger parsing detaylı testleri
   - Swagger parser import
   - Method isim sanitizasyonu

## Test Çalıştırma

### Tüm Testleri Çalıştır
```bash
/opt/envs/venv-python3.11/bin/python3.11 -m pytest tests/test_epint_methods.py -v
```

### Belirli Bir Testi Çalıştır
```bash
/opt/envs/venv-python3.11/bin/python3.11 -m pytest tests/test_epint_methods.py::TestEpintMethods::test_namespace_access -v
```

### Test Sonuçlarını Detaylı Göster
```bash
/opt/envs/venv-python3.11/bin/python3.11 -m pytest tests/test_epint_methods.py -v -s
```

## Test Öncesi Hazırlık

Testler çalıştırılmadan önce:
1. Proje editable modda yüklenmiş olmalı: `pip install -e .`
2. Cache temizlenmiş olmalı (test içinde otomatik temizleniyor)
3. Auth bilgileri ayarlanmış olmalı (test içinde otomatik ayarlanıyor)

## Beklenen Sonuçlar

- ✅ 18 kategori yüklenmeli
- ✅ 1000+ endpoint bulunmalı
- ✅ Namespace erişimi çalışmalı (`ep.gunici.method_name`)
- ✅ Tüm kategori manager'lar erişilebilir olmalı

## Notlar

- Testler gerçek API çağrıları yapmaz, sadece yapıyı test eder
- Gerçek API testleri için ayrı bir test dosyası oluşturulabilir
- Cache mekanizması test edilir ve otomatik temizlenir

