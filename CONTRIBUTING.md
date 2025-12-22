# Katkıda Bulunma Rehberi

EPINT projesine katkıda bulunmak istediğiniz için teşekkür ederiz! Bu belge, projeye nasıl katkıda bulunabileceğiniz konusunda rehberlik sağlar.

## İçindekiler

- [Davranış Kuralları](#davranış-kuralları)
- [Nasıl Katkıda Bulunabilirim?](#nasıl-katkıda-bulunabilirim)
- [Geliştirme Ortamı Kurulumu](#geliştirme-ortamı-kurulumu)
- [Kod Standartları](#kod-standartları)
- [Pull Request Süreci](#pull-request-süreci)
- [Issue Açma](#issue-açma)
- [Test Etme](#test-etme)

## Davranış Kuralları

Bu proje, tüm katkıda bulunanların saygılı ve kapsayıcı bir ortamda çalışmasını sağlamak için bir davranış kurallasına uymaktadır. Projeye katılarak, bu kurallara uymayı kabul edersiniz.

## Nasıl Katkıda Bulunabilirim?

### Hata Bildirimi (Bug Reports)

Bir hata bulduysanız:

1. **Mevcut issue'ları kontrol edin** - Aynı hata daha önce bildirilmiş olabilir
2. **Yeni bir issue oluşturun** - [Issues](https://github.com/epint/epint/issues) sayfasından yeni issue açın
3. **Detaylı bilgi verin**:
   - Hatanın açıklaması
   - Tekrarlanabilir adımlar
   - Beklenen davranış
   - Gerçek davranış
   - Python versiyonu ve işletim sistemi
   - Hata mesajları veya stack trace'ler

### Özellik İstekleri (Feature Requests)

Yeni bir özellik önermek için:

1. **Mevcut issue'ları kontrol edin** - Benzer bir istek zaten var mı?
2. **Yeni bir issue oluşturun** - Özelliğin amacını ve kullanım senaryosunu açıklayın
3. **Örnek kullanım** - Özelliğin nasıl kullanılacağına dair örnekler verin

### Kod Katkıları

Kod katkısında bulunmak için:

1. **Fork edin** - Projeyi kendi hesabınıza fork edin
2. **Branch oluşturun** - Yeni bir feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. **Değişikliklerinizi yapın** - Kod standartlarına uygun şekilde değişikliklerinizi yapın
4. **Test edin** - Değişikliklerinizin çalıştığından emin olun
5. **Commit edin** - Anlamlı commit mesajları yazın
6. **Push edin** - Değişikliklerinizi push edin (`git push origin feature/yeni-ozellik`)
7. **Pull Request açın** - GitHub'da pull request oluşturun

## Geliştirme Ortamı Kurulumu

### Gereksinimler

- Python 3.11 veya üzeri
- Git

### Kurulum Adımları

1. **Repository'yi clone edin**:
```bash
git clone https://github.com/epint/epint.git
cd epint
```

2. **Virtual environment oluşturun**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate  # Windows
```

3. **Bağımlılıkları yükleyin**:
```bash
pip install -e .
pip install -r requirements.txt
```

4. **Geliştirme bağımlılıklarını yükleyin** (opsiyonel):
```bash
pip install black isort pytest
```

## Kod Standartları

### Python Stil Rehberi

- **PEP 8** standartlarına uyun
- **Black** formatını kullanın (line-length: 88)
- **isort** ile import'ları sıralayın
- Type hints kullanın (mümkün olduğunca)
- Docstring'ler yazın (Google veya NumPy formatı)

### Kod Formatlama

Kodunuzu göndermeden önce formatlayın:

```bash
black src/
isort src/
```

### Dosya Yapısı

- Kod `src/epint/` dizini altında organize edilmiştir
- Her modül kendi dizininde bulunur
- Test dosyaları `tests/` dizininde olmalıdır

## Pull Request Süreci

### PR Açmadan Önce

- [ ] Kodunuzu formatladınız (`black`, `isort`)
- [ ] Mevcut testleri geçiyor
- [ ] Yeni testler eklediniz (eğer gerekiyorsa)
- [ ] Dokümantasyonu güncellediniz (eğer gerekiyorsa)
- [ ] Commit mesajlarınız açıklayıcı

### PR Başlığı ve Açıklaması

**Başlık formatı**: `[Tip] Kısa açıklama`

Örnekler:
- `[Bug] Tarih aralığı hatası düzeltmesi`
- `[Feature] Yeni endpoint desteği`
- `[Docs] README güncellemesi`
- `[Refactor] Kod temizliği`

**Açıklama içermeli**:
- Ne değişti?
- Neden değişti?
- Nasıl test edildi?
- İlgili issue numarası (varsa)

### Review Süreci

1. PR açıldıktan sonra maintainer'lar review yapacaktır
2. Geri bildirimler verilebilir - lütfen yapıcı eleştirileri kabul edin
3. Gerekli değişiklikler yapıldıktan sonra PR merge edilecektir

## Issue Açma

### İyi Bir Issue İçin

- **Açıklayıcı başlık** - Sorunun ne olduğunu kısaca özetleyin
- **Detaylı açıklama** - Sorunu veya özelliği detaylıca açıklayın
- **Örnekler** - Mümkünse kod örnekleri veya ekran görüntüleri ekleyin
- **Etiketler** - Uygun etiketleri seçin (bug, feature, question, vb.)

### Issue Şablonları

Issue açarken şablonları kullanın:
- Bug Report
- Feature Request
- Question
- Documentation

## Test Etme

### Test Yazma

- Yeni özellikler için test yazın
- Mevcut testleri bozmayın
- Test isimleri açıklayıcı olsun

### Test Çalıştırma

```bash
# Tüm testleri çalıştır
pytest

# Belirli bir test dosyasını çalıştır
pytest tests/test_specific.py

# Verbose modda çalıştır
pytest -v
```

## Dokümantasyon

### Dokümantasyon Güncellemeleri

- Yeni özellikler için dokümantasyon ekleyin
- README.md'yi güncelleyin (eğer gerekiyorsa)
- Docstring'leri güncel tutun
- Örnek kodlar ekleyin

### Dokümantasyon Formatı

- Markdown formatında yazın
- Kod örnekleri için syntax highlighting kullanın
- Bağlantıları güncel tutun

## Sorular?

Herhangi bir sorunuz varsa:

- [Issues](https://github.com/epint/epint/issues) sayfasından soru sorabilirsiniz
- Dokümantasyonu kontrol edin
- Mevcut issue'ları inceleyin

## Teşekkürler

Katkılarınız için teşekkür ederiz! EPINT projesini daha iyi hale getirmek için çalıştığınız için minnettarız.

