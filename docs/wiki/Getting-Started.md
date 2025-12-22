# Başlangıç Rehberi

EPINT kütüphanesini kullanmaya başlamak için bu rehberi takip edin.

## Kurulum

EPINT'i pip ile kurabilirsiniz:

```bash
pip install epint
```

## İlk Adımlar

### 1. Kütüphaneyi İçe Aktarın

```python
import epint as ep
```

### 2. Kimlik Doğrulama Ayarları

API'ye erişim için kullanıcı adı ve şifrenizi ayarlayın:

```python
ep.set_auth("kullanici_adi", "sifre")
ep.set_mode("prod")  # veya "test"
```

### 3. İlk API Çağrısı

```python
# Elektrik şeffaflık verileri
result = ep.seffaflik_electricity.mcp_data(
    start='2025-12-10',
    end='2025-12-11'
)

print(result)
```

## Sonraki Adımlar

- [[API Referansı|API-Reference]] - Tüm API metodlarını keşfedin
- [[Örnekler|Examples]] - Daha fazla örnek görün
- [[Gelişmiş Kullanım|Advanced-Usage]] - Gelişmiş özellikleri öğrenin

## Yardım

Sorunuz mu var? [[SSS|FAQ]] sayfasına bakın veya bir [issue](https://github.com/epint/epint/issues) açın.

