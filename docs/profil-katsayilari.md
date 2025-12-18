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




### Ek Kod: Tüm Organizasyonlar İçin Profil Katsayıları Toplama
```python
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

def tum_organizasyon_katsayilari(ep, period: str, max_workers: int = 10, max_retries: int = 3, retry_delay: float = 1.0) -> pd.DataFrame:
    """
    Tüm organizasyonlar, profil grupları ve okuma tipleri için katsayı verilerini çeker.

    Args:
        ep: epint örneği
        period (str): Hangi dönem için veri çekilecek (örn: '2026-01-01')
        max_workers (int): Paralel çalışacak worker sayısı
        max_retries (int): Maksimum tekrar denemesi (hata halinde)
        retry_delay (float): Hatalı denemede sonraki deneme aralığı (saniye)

    Returns:
        pd.DataFrame: datetime, org_name, org_id, profile_name, profile_id, reading_type_name, reading_type_id, coef alanları ile tablo
    """

    print(f"[*] Organizasyonlar listeleniyor...")
    orgs = ep.seffaflik.multiple_factor_distribution(period=period)
    reading_types = ep.seffaflik.data_multiple_factor_reading()
    print(f"[*] {len(orgs)} organizasyon bulundu")
    print(f"[*] {len(reading_types)} okuma tipi bulundu")

    # Her organizasyonun gruplarını çek
    for org in orgs:
        print(f"[+] {org.get('name')} (Id: {org.get('id')})")
        org["groups"] = ep.seffaflik.multiple_factor_profile_group(
            period=period, distributionId=org.get("id")
        )
        print(f"    → {len(org['groups'])} profil grubu çekildi")

    # Görevleri oluştur
    gorevler = []
    for org in orgs:
        for grup in org["groups"]:
            for read_type in reading_types:
                gorevler.append({
                    "org_id": org["id"],
                    "org_name": org["name"],
                    "profile_id": grup["id"],
                    "profile_name": grup["name"],
                    "reading_type_id": read_type["id"],
                    "reading_type_name": read_type["name"],
                })

    toplam_gorev = len(gorevler)
    print(f"\n[*] Toplam {toplam_gorev} çekim görevi hazırlandı. Paralel çalışıyor (max_workers={max_workers})...")

    # Tek görev çekme, retry'lı
    def tek_gorevi_cek(task: Dict[str, Any]) -> Dict[str, Any]:
        for attempt in range(max_retries):
            try:
                result = ep.seffaflik.multiple_factor_data(
                    period=period,
                    distid=task["org_id"],
                    meterreadtype=task["reading_type_id"],
                    profileGroup=task["profile_id"]
                )
                return {
                    "success": True,
                    "task": task,
                    "data": result.get("items", []),
                    "attempt": attempt + 1
                }
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"[!] Hata ({attempt+1}/{max_retries}): {task['org_name']} | {task['profile_name']} | {task['reading_type_name']} : {e}")
                    time.sleep(retry_delay)
                else:
                    print(f"[✗] BAŞARISIZ: {task['org_name']} | {task['profile_name']} | {task['reading_type_name']} : {e}")
                    return {
                        "success": False,
                        "task": task,
                        "error": str(e),
                        "attempt": max_retries
                    }
        return None

    results = []
    tamamlanan = 0
    hatali = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(tek_gorevi_cek, t): t for t in gorevler}
        for future in as_completed(futures):
            sonuc = future.result()
            results.append(sonuc)
            tamamlanan += 1
            if sonuc["success"]:
                task = sonuc["task"]
                kayit_sayisi = len(sonuc["data"])
                print(f"[✓] ({tamamlanan}/{toplam_gorev}) {task['org_name']} | {task['profile_name']} | {task['reading_type_name']} ({kayit_sayisi} kayıt deneme={sonuc['attempt']})")
            else:
                hatali += 1

    # DataFrame'e aktar
    print(f"\n[*] DataFrame oluşturuluyor...")
    rows = []
    for sonuc in results:
        if sonuc and sonuc["success"]:
            task = sonuc["task"]
            for item in sonuc["data"]:
                rows.append({
                    "datetime": item.get("time") or item.get("period"),
                    "org_name": task["org_name"],
                    "org_id": task["org_id"],
                    "profile_name": task["profile_name"],
                    "profile_id": task["profile_id"],
                    "reading_type_name": task["reading_type_name"],
                    "reading_type_id": task["reading_type_id"],
                    "coef": item.get("multiplier")
                })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(by=["datetime", "org_id", "profile_id", "reading_type_id"]).reset_index(drop=True)

    print(f"\n{'='*70}")
    print(f"[*] Özet")
    print(f"    Toplam görev: {toplam_gorev}")
    print(f"    Başarı: {tamamlanan - hatali}")
    print(f"    Başarısız: {hatali}")
    print(f"    Başarı oranı: {(100*(tamamlanan-hatali)/toplam_gorev):.2f}%")
    print(f"    Satır Sayısı: {len(df)}")
    print(f"{'='*70}\n")

    if hatali > 0:
        print("[!] Başarısız çekimler:")
        for sonuc in results:
            if sonuc and not sonuc["success"]:
                task = sonuc["task"]
                print(f"    - {task['org_name']} / {task['profile_name']} / {task['reading_type_name']}")
        print()
    return df

# Kısa kullanım
if __name__ == "__main__":
    period = '2026-01-01'
    df = tum_organizasyon_katsayilari(
        ep=ep,
        period=period,
        max_workers=10,
        max_retries=3,
        retry_delay=1.0
    )
    print("DataFrame İlk 10 Satır:")
    print(df.head(10))
    print(f"\nDataFrame Shape: {df.shape}")
    print(f"\nKolon Listesi: {df.columns.tolist()}")
```