# Epiaş Şeffaflık Profil Katsayıları Sorgulama

Öncelikle Epiaş API üzerinden işlem yapabilmek için kimlik doğrulaması gereklidir. Bunun için aşağıdaki gibi kullanıcı adınızı ve şifrenizi girerek oturum açmanız gerekir:

```python
ep.set_auth("kullanici_adiniz", "sifreniz")
```



Profil katsayıları, elektrik tüketiminin zaman içindeki dağılımını gösteren çarpanlardır. Bu katsayılar, belirli bir dönem için saatlik tüketim dağılımını hesaplamak için kullanılır. Profil katsayıları sorgulama işlemi, aşağıdaki adımlar takip edilerek gerçekleştirilir:

1. **Okuma tipi** belirlenir (Tek Zamanlı veya Üç Zamanlı)
2. **Dağıtım organizasyonu** seçilir
3. **Abone grubu** belirlenir
4. **Profil katsayıları** sorgulanır

## 1. Okuma Tipi Listeleme

Sayaç okuma tiplerini listeleyen servis. Profil katsayıları sorgulamasında kullanılacak okuma tipini belirlemek için kullanılır.

```python
read_types = ep.seffaflik._meter_reading_type()
print(read_types)
```

**Dönen Değerler:**

|   id | name        |
|-----:|:------------|
|    3 | Tek Zamanlı |
|    1 | Üç Zamanlı  |

**Açıklama:**
- **Tek Zamanlı (id: 3)**: Tüm gün boyunca aynı tarifeden elektrik tüketen aboneler
- **Üç Zamanlı (id: 1)**: Gün içinde farklı zaman dilimlerinde farklı tarifelerden elektrik tüketen aboneler

## 2. Dağıtım Organizasyonları Listeleme

Belirli bir dönem için profil katsayısı verisi bulunan dağıtım organizasyonlarını listeleyen servis.

```python
orgs = ep.seffaflik.multiple_factor_distribution(period='2026-01-01')
print(orgs)
```

**Parametreler:**
- `period` (string, zorunlu): Sorgulanacak dönem (format: 'YYYY-MM-DD')

**Dönen Değerler:**

|   id | name                                              |
|-----:|:--------------------------------------------------|
| 1005 | ADM ELEKTRİK DAĞITIM A.Ş.(ED)                     |
| 1006 | AKDENİZ ELEKTRİK DAĞITIM A.Ş.(ED)                 |
| 1004 | AKEDAŞ ELEKTRİK DAĞITIM A.Ş.(ED)                  |
| 1012 | ARAS ELEKTRİK DAĞITIM A.Ş.(ED)                    |
| 1010 | BAŞKENT ELEKTRİK DAĞITIM A.Ş.(ED)                 |
| 1023 | BOĞAZİÇİ ELEKTRİK DAĞITIM A.Ş.(ED)                |
| 1007 | DİCLE ELEKTRİK DAĞITIM A.Ş.(ED)                   |
| 1008 | FIRAT ELEKTRİK DAĞITIM A.Ş.(ED)                   |
| 1024 | GDZ ELEKTRİK DAĞITIM A.Ş.(ED)                     |
| 1011 | KAYSERİ VE CİVARI ELEKTRİK T.A.Ş.(ED)             |
| 1021 | MERAM ELEKTRİK DAĞITIM A.Ş.(ED)                   |
| 1014 | OSMANGAZİ ELEKTRİK DAĞITIM A.Ş.(ED)               |
| 1013 | SAKARYA ELEKTRİK DAĞITIM A.Ş.(ED)                 |
| 1017 | TOROSLAR ELEKTRİK DAĞITIM A.Ş.(ED)                |
| 1022 | TRAKYA ELEKTRİK DAĞITIM A.Ş.(ED)                  |
| 1016 | ULUDAĞ ELEKTRİK DAĞITIM A.Ş.(ED)                  |
| 1015 | VAN GÖLÜ ELEKTRİK DAĞITIM A.Ş.(ED)                |
| 1019 | YEŞİLIRMAK ELEKTRİK DAĞITIM A.Ş.(ED)              |
| 1020 | ÇAMLIBEL ELEKTRİK DAĞITIM A.Ş.(ED)                |
| 1018 | ÇORUH ELEKTRİK DAĞITIM A.Ş(ED)                    |
| 1009 | İSTANBUL ANADOLU YAKASI ELEKTRİK DAĞITIM A.Ş.(ED) |

**Not:** Dönen listeden bir organizasyonun `id` değeri, sonraki adımlarda kullanılmak üzere kaydedilmelidir.

## 3. Abone Grubu Listeleme

Seçilen dağıtım organizasyonu için mevcut abone gruplarını listeleyen servis. Her abone grubu, farklı tüketim profiline sahip aboneleri temsil eder.

```python
# Örnek: Kayseri ve Civarı Elektrik için abone grupları
dist_id = orgs[10]['id']  # KAYSERİ VE CİVARI ELEKTRİK T.A.Ş.(ED)
profile_groups = ep.seffaflik.multiple_factor_profile_group(
    period='2026-01-01', 
    distId=dist_id
)
print(profile_groups)
```

**Parametreler:**
- `period` (string, zorunlu): Sorgulanacak dönem (format: 'YYYY-MM-DD')
- `distId` (integer, zorunlu): Dağıtım organizasyonu ID'si (önceki adımdan alınır)

**Dönen Değerler:**

|   id | name                  |
|-----:|:----------------------|
|    0 | Alternatif            |
|   35 | Sanayi-AG             |
|   36 | Sanayi-OG             |
|   73 | Ticarethane - AG      |
|   86 | Tarımsal Sulama - OG  |
|   87 | Ticarethane - OG      |
|   88 | Tarımsal Sulama - AG  |
|   89 | Mesken - AG           |
|   90 | Mesken - OG           |
|  155 | Aydınlatma - KIRŞEHİR |
|  157 | Aydınlatma - KONYA    |
|  165 | Aydınlatma - NEVŞEHİR |
|  166 | Aydınlatma - NİĞDE    |
|  183 | Aydınlatma - AKSARAY  |
|  185 | Aydınlatma - KARAMAN  |

**Açıklama:**
- **AG**: Alçak Gerilim
- **OG**: Orta Gerilim
- Her organizasyon için farklı abone grupları bulunabilir

## 4. Profil Katsayıları Sorgulama

Belirtilen dönem, organizasyon, abone grubu ve okuma tipi için saatlik profil katsayılarını döndüren servis.

```python
import pandas as pd

# Örnek: Kayseri ve Civarı Elektrik, Ticarethane - OG grubu, Üç Zamanlı okuma tipi için
profiles = ep.seffaflik.multiple_factor_data(
    period='2026-01-01',
    distId=orgs[10]['id'],
    subscriberProfileGroup=profile_groups[6]['id'],  # Ticarethane - OG
    meterReadingType=1  # Üç Zamanlı
)

# Sonuçları DataFrame'e dönüştürüp ilk 10 satırı göster
df = pd.DataFrame(profiles.get('items'))
print(df[:10])
```

**Parametreler:**
- `period` (string, zorunlu): Sorgulanacak dönem (format: 'YYYY-MM-DD')
- `distId` (integer, zorunlu): Dağıtım organizasyonu ID'si
- `subscriberProfileGroup` (integer, zorunlu): Abone grubu ID'si
- `meterReadingType` (integer, zorunlu): Okuma tipi ID'si (1: Üç Zamanlı, 3: Tek Zamanlı)

**Dönen Değerler:**

| period                    | time                      |   multiplier |
|:--------------------------|:--------------------------|-------------:|
| 2026-01-01 00:00:00+03:00 | 2026-01-01 00:00:00+03:00 |   0.00393844 |
| 2026-01-01 01:00:00+03:00 | 2026-01-01 01:00:00+03:00 |   0.00388684 |
| 2026-01-01 02:00:00+03:00 | 2026-01-01 02:00:00+03:00 |   0.00363215 |
| 2026-01-01 03:00:00+03:00 | 2026-01-01 03:00:00+03:00 |   0.00368697 |
| 2026-01-01 04:00:00+03:00 | 2026-01-01 04:00:00+03:00 |   0.00383668 |
| 2026-01-01 05:00:00+03:00 | 2026-01-01 05:00:00+03:00 |   0.00440733 |
| 2026-01-01 06:00:00+03:00 | 2026-01-01 06:00:00+03:00 |   0.00273154 |
| 2026-01-01 07:00:00+03:00 | 2026-01-01 07:00:00+03:00 |   0.00274974 |
| 2026-01-01 08:00:00+03:00 | 2026-01-01 08:00:00+03:00 |   0.00290296 |
| 2026-01-01 09:00:00+03:00 | 2026-01-01 09:00:00+03:00 |   0.00289851 |

**Açıklama:**
- `period`: Sorgulanan dönem
- `time`: Saatlik zaman damgası (24 saatlik veri döner)
- `multiplier`: O saat için profil katsayısı (çarpan değeri)

**Not:** Profil katsayıları, bir günlük toplam tüketimin saatlik dağılımını temsil eder. Okuma tipi tek zamanlı seçildiğinde, tüm saatlerin katsayıları toplandığında toplam değerin yaklaşık 1.0 olması beklenir. Okuma tipi üç zamanlı seçildiğinde ise, bu toplam yaklaşık 3.0 değerine yakın olur.
