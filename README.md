# EPINT - EPIAS API Integration Package

EPINT, EPIAS (Enerji Piyasaları İşletme A.Ş.) API'lerine entegrasyon sağlayan bir Python kütüphanesidir. Türk enerji piyasaları için geliştirilmiş olan bu paket, EPIAS servislerine kolay erişim imkanı sunar.

## Özellikler

- **CAS Authentication**: EPIAS CAS (Central Authentication Service) entegrasyonu
- **HTTP Client**: WAF bypass özellikli gelişmiş HTTP istemcisi
- **Endpoint Validation**: API endpoint'leri için tip güvenli parametre doğrulama
- **Session Management**: Otomatik ticket yönetimi ve yenileme
- **Configuration**: YAML tabanlı konfigürasyon sistemi

## Kurulum

```bash
pip install epint
```

### Geliştirme Kurulumu

```bash
git clone https://github.com/epint/epint.git
cd epint
pip install -r requirements-dev.txt
pip install -e .
```

## Kullanım

### Temel Authentication

```python
from epint import Authentication

# EPIAS kullanıcı bilgileri ile authentication
auth = Authentication(
    username="your_username",
    password="your_password",
    mode="epys"  # veya "transparency"
)

# Service ticket al
st_code, expire_date = auth.get_st("https://epys.epias.com.tr/api/service")
```

### HTTP Client Kullanımı

```python
from epint import HTTPClient

# Normal HTTP client
with HTTPClient() as client:
    response = client.get("https://api.example.com/data")
    print(response.json())

# WAF bypass ile HTTP client
with HTTPClient(waf_bypass=True) as client:
    response = client.post("https://api.example.com/data", json={"key": "value"})
```

### Endpoint Validation

```python
from epint import EndpointManager

# Endpoint manager oluştur
manager = EndpointManager("path/to/endpoints.yaml")

# Endpoint kullan
result = manager.invoice_services(
    exportType="csv",
    period="2024-01-01"
)
```

## Konfigürasyon

EPINT, `web_agent.params.yml` dosyası üzerinden konfigüre edilebilir:

```yaml
# Default HTTP headers
default_headers:
  accept: "application/json"
  user-agent: "EPINT/0.1.0"

# WAF bypass ayarları
waf_bypass_headers:
  X-Forwarded-For: "127.0.0.1"
  X-Real-IP: "127.0.0.1"

# Timeout ayarları
timeouts:
  default: 10
  long: 30
```

## Geliştirme

### Test Çalıştırma

```bash
make test
```

### Kod Formatlama

```bash
make format
```

### Linting

```bash
make lint
```

### Paket Oluşturma

```bash
make build
```

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## Destek

Sorularınız için:
- GitHub Issues: https://github.com/epint/epint/issues
- Email: epint@example.com

## Changelog

### v0.1.0
- İlk sürüm
- CAS authentication desteği
- HTTP client with WAF bypass
- Endpoint validation sistemi
