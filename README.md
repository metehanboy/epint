# EPINT - EPIAS API Integration Package

Python paketi olarak Türkiye Enerji Piyasaları İşletme A.Ş. (EPİAŞ) API'lerine entegrasyon sağlar.

## Özellikler

- EPİAŞ platformlarına (GOP, EPYS, GÜNİCİ, vb.) kolay erişim
- Test ve prodüksiyon ortamları için otomatik yapılandırma
- CAS (Central Authentication Service) kimlik doğrulama desteği
- Çoklu servis entegrasyonu

## Kurulum

```bash
pip install -e .
```

## Kullanım

```python
import epint as ep

# Kimlik doğrulama
ep.set_auth('kullanici_adi', 'sifre')

# Veri çekme
data = ep.get_total_data(period='2024-01-01', region='TR1', organization=1)
```

## Desteklenen Servisler

- **GOP**: Gün Öncesi Piyasası
- **EPYS**: Elektrik Piyasası Yönetim Sistemi
- **GÜNİCİ**: Gün İçi Piyasası
- **Dengeleme Grubu**: Balancing Group servisleri
- **Grid**: Şebeke servisleri
- **Reconciliation**: Mutabakat servisleri
- **Registration**: Kayıt servisleri

## Gereksinimler

- Python >= 3.8
- requests >= 2.31.0
- urllib3 >= 2.0.0
- pyyaml >= 6.0.1

## Geliştirme

```bash
# Development bağımlılıklarını kur
pip install -e ".[dev]"

# Testleri çalıştır
pytest

# Kod formatla
black src/
isort src/
```

## Lisans

MIT License - Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## Katkıda Bulunma

Pull request'ler kabul edilmektedir. Büyük değişiklikler için önce bir issue açarak değişikliği tartışın.

## İletişim

- Repository: https://github.com/metehanboy/epint
- Issues: https://github.com/metehanboy/epint/issues

