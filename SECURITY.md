# Güvenlik Politikası

## Desteklenen Versiyonlar

Aşağıdaki versiyonlar güvenlik güncellemeleri ile desteklenmektedir:

| Versiyon | Destekleniyor          |
| -------- | ---------------------- |
| >= 0.1.0 | :white_check_mark:     |

## Güvenlik Açığı Bildirimi

Güvenlik açığı bulduysanız, lütfen doğrudan GitHub Issues üzerinden bildirmek yerine, güvenlik açığını özel olarak bildirin.

### Bildirme Süreci

1. **Güvenlik açığını bildirin**: Güvenlik açığınızı [GitHub Security Advisories](https://github.com/epint/epint/security/advisories/new) üzerinden bildirin veya e-posta ile iletişime geçin.

2. **Bekleme süresi**: Güvenlik açığını bildirdikten sonra, sorunu çözmek ve bir yama hazırlamak için makul bir süre bekleyin.

3. **Açıklama**: Güvenlik açığının detaylarını ve etkisini açıklayın:
   - Açığın türü (örn: SQL injection, XSS, authentication bypass)
   - Etkilenen bileşenler veya dosyalar
   - Açığın nasıl sömürülebileceği
   - Potansiyel etki (veri sızıntısı, yetkisiz erişim, vb.)

4. **Öneriler**: Mümkünse, sorunu çözmek için önerilerinizi paylaşın.

### Bildirme İçeriği

Güvenlik açığı bildiriminizde şunları içermelidir:

- **Açığın açıklaması**: Sorunun ne olduğunu açıklayın
- **Etkilenen versiyonlar**: Hangi versiyonların etkilendiğini belirtin
- **Tekrarlanabilir adımlar**: Açığı nasıl tekrarlayabileceğinizi gösterin
- **Etki analizi**: Açığın potansiyel etkisini açıklayın
- **Önerilen çözüm**: Varsa, çözüm önerilerinizi paylaşın

### Yanıt Süresi

- **İlk yanıt**: 48 saat içinde bildiriminizi aldığımızı onaylayacağız
- **Değerlendirme**: 7 gün içinde açığı değerlendireceğiz
- **Yama**: Kritik açıklar için 30 gün içinde yama yayınlayacağız

### Güvenlik Açığı Türleri

Aşağıdaki güvenlik açığı türlerini bildirmenizi özellikle öneriyoruz:

- **Kimlik doğrulama ve yetkilendirme**: Yetkisiz erişim, kimlik doğrulama bypass
- **Veri sızıntısı**: Hassas bilgilerin açığa çıkması
- **Kod enjeksiyonu**: SQL injection, command injection
- **XSS (Cross-Site Scripting)**: Web tabanlı saldırılar
- **CSRF (Cross-Site Request Forgery)**: Yetkisiz işlemler
- **API güvenliği**: API endpoint'lerindeki güvenlik açıkları
- **Bağımlılık açıkları**: Kullanılan kütüphanelerdeki güvenlik açıkları

### Güvenlik Açığı Olmayan Durumlar

Aşağıdaki durumlar güvenlik açığı olarak kabul edilmez:

- API rate limiting sorunları
- Performans sorunları
- Genel kullanılabilirlik sorunları
- Belgelendirme hataları
- Kod stil sorunları

## Güvenlik Önlemleri

### Önerilen Güvenlik Uygulamaları

1. **Kimlik Bilgilerini Güvenli Tutun**: API kimlik bilgilerinizi kod içinde saklamayın, environment variable'lar kullanın
2. **HTTPS Kullanın**: Tüm API çağrılarında HTTPS kullanın
3. **Bağımlılıkları Güncel Tutun**: Düzenli olarak bağımlılıkları güncelleyin
4. **Güvenlik Güncellemelerini Takip Edin**: Proje güncellemelerini takip edin

### Güvenlik Kontrol Listesi

Kod katkısında bulunurken:

- [ ] Hassas bilgileri kod içinde saklamadım
- [ ] API endpoint'lerinde güvenlik kontrolleri ekledim
- [ ] Kullanıcı girdilerini doğruladım
- [ ] SQL injection risklerini kontrol ettim
- [ ] XSS risklerini kontrol ettim
- [ ] Güvenlik açığı testleri yaptım

## Teşekkürler

Güvenlik açıklarını bildirdiğiniz için teşekkür ederiz. Bildirimleriniz projeyi daha güvenli hale getirmemize yardımcı olur.

