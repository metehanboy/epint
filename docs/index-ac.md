## Genel Bakış

### Versiyon bilgisi

_Versiyon_ : 1.0.0

### URI şeması

_Sunucu_ : epys-prp.epias.com.tr  
_Kök Dizin_ : /index-ac  
_Şemalar_ : HTTPS

### Etiketler

-   additionalConsumption
    
-   index
    
-   indexAcLookup
    
-   readObligation
    
-   summaryReport
    

## Doküman Hakkında

Bu dokümanda Endeks/Ek Tüketim servislerinin tanımları ve bu servislerin nasıl çağrılacağı anlatılmaktadır.

## 1\. EPYS Endeks/Ek Tüketim Servisleri Hakkında

EPYS Endeks/Ek Tüketim uygulaması REST servisler üzerine kuruludur. JSON ve XML isteklerini kabul eder ve gelen isteğe göre JSON yada XML cevap döner.

Uygulamanın kullanıcı arayüzünde görmüş olduğunuz bilgilerin tamamı dışarıya açık olan bu servislerden alınmaktadır. Bu arayüzü kullanmadan da sahip olduğunuz uygulamalar ile sistemi kullanmanız mümkündür.

Uygulamayı çağırabilmek için EKYS de kayıtlı bir kullanıcınız olmalı ve bu kullanıcının ilgili servisleri çağırabilmek için yeterli yetkisi olmalıdır. Uygulamaya gelen tüm istekler Merkezi Yetkilendirme Sunucusu’ndan ([https://cas.epias.com.tr](https://cas.epias.com.tr/)) TGT alınarak gönderilmelidir.

## 2\. İstemci Oluşturmak

## 3\. EPYS Endeks/Ek Tüketim Uygulaması Servis Çağrımı

TGT (Ticket Granting Ticket) kullanıcının oturumunu kontrol eder. TGT Servisinden alacağınız değer 45 dakika boyunca kullanmasanız bile aktiftir. TGT değerini her kullanışınızda 45 dakikalık süre tekrar başlar.

TGT tekrar kullanılabilen bir değerdir. Her istek için TGT almanıza gerek yoktur. Her istek için TGT almanız halinde CAS (Merkezi Yetkilendirme Sunucusu) tarafından bloke edilebilirsiniz.

### 3.1. Ticket Granting Ticket (TGT) Oluşturma

Gönderilen **HTTP** isteğinin header kısmında **Content-Type** karşılığında ise **application/x-www-form-urlencoded** yazmalıdır.

 
| parametre | değer |
| --- | --- |
| 
username

 | 

EKYS Kullanıcı Adı

 |
| 

password

 | 

EKYS Şifresi

 |

örnek http isteği

```ruby
POST /cas/v1/tickets HTTP/1.1
Host: cas.epias.com.tr
Cache-Control: no-cache
Content-Type: application/x-www-form-urlencoded

username=DGPYSUSER&password=DGPYSSIFRE
```

Servisten **HTTP 200** cevabını beklemelisiniz. Sonuç olarak aşağıdaki gibi bir örnek dönecektir.

örnek cevap

```ruby
TGT-237-U0TU0jUHLyOEIrdoDBEEf3AdRFAXGLifK2ITn4LoY3HfhstGtx-cas02.epias.com.tr
```

### 3.2. Service Ticket (ST) Oluşturma

ST oluşturabilmeniz için öncelikle geçerli TGT bilgisi almış olmanız gerekmektedir. Alınan TGT bilgisi ile **[https://cas.epias.com.tr/cas/v1/tickets/TGT-237-U0TU0jUHLyOEIrdoDBEEf3AdRFAXGLifK2ITn4LoY3HfhstGtx-cas02.epias.com.tr](https://cas.epias.com.tr/cas/v1/tickets/TGT-237-U0TU0jUHLyOEIrdoDBEEf3AdRFAXGLifK2ITn4LoY3HfhstGtx-cas02.epias.com.tr) adresine aşağıdaki değerleri \*POST** metodu ile göndermeniz gerekmektedir. ST oluşturabilmeniz için kullanıcak **service** bilgisi aşağıdaki gibidir. Service ticket bilgisi **tek kullanımlık olup 15 saniye içinde kullanılmaz ise geçerliliğini kaybetmektedir**.

 
| ortam | service |
| --- | --- |
| 
PROD

 | 

[https://epys.epias.com.tr](https://epys.epias.com.tr/)

 |
| 

TEST

 | 

[https://epys-prp.epias.com.tr](https://epys-prp.epias.com.tr/)

 |

Gönderilen **HTTP** isteğinin header kısmında **Content-Type** karşılığında ise **application/x-www-form-urlencoded** yazmalıdır.

 
| parametre | değer |
| --- | --- |
| 
service

 | 

[https://epys.epias.com.tr](https://epys.epias.com.tr/)

 |

örnek http isteği

```ruby
POST /cas/v1/tickets/TGT-237-U0TU0jUHLyOEIrdoDBEEf3AdRFAXGLifK2ITn4LoY3HfhstGtx-cas02.epias.com.tr HTTP/1.1
Host: cas.epias.com.tr
Content-Type: application/x-www-form-urlencoded
Content-Length: 39

service=https%3A%2F%2Fepys.epias.com.tr
```

Servisten **HTTP 200** cevabını beklemelisiniz. Sonuç olarak aşağıdaki gibi bir örnek dönecektir.

örnek cevap

```ruby
ST-30853663-c3OsaqpG16IDVGIA3cbs-cashazel-n201
```

### 3.3. EPYS Endeks/Ek Tüketim Uygulaması Örnek Mesaj Yapısı

EPYS servislerinin standart bir mesaj yapısı bulunmaktadır. Gönderdiğiniz tüm isteklerde bu formata uygun veri göndermelisiniz.

Öncelikle her isteğin **HTTP header** alanına aşağıdaki değerleri eklemelisiniz.

 
| parametre | değer |
| --- | --- |
| 
TGT

 | 

(Ticket Granting Ticket) (TGT) Örneğin : TGT-237-U0TU0jUHLyOEIrdoDBEEf3AdRFAXGLifK2ITn4LoY3HfhstGtx-cas02.epias.com.tr

 |
| 

ST

 | 

(Service Ticket) (ST) Örneğin : ST-30853663-c3OsaqpG16IDVGIA3cbs-cashazel-n201

 |
| 

Accept

 | 

application/json veya application/xml

 |
| 

Content-Type

 | 

application/json veya application/xml

 |

servise has parametreleri içeren **body** alanıdır. Tüm servisler için farklılık gösterebilir.

Aşağıdaki örnekte teslim gününün doğru olup olmadığını kontrol eden bir mesaj bulunmaktadır.

<table><tbody><tr><td class="icon"><i class="fa icon-warning" title="Warning"></i></td><td class="content">Servise gelen ve giden tüm mesajlardaki tarih alanları ISO-8601 formatındadır. Format <strong>yyyy-MM-dd’T’HH:mm:ssXXX</strong> şeklinde olmalıdır. Timezone değeri Yaz Saati Uygulamasında için +03:00 Kış Saatin Uygulamasında +02:00 olarak değişmektedir. Örnek bir zaman değeri şu şekildedir. 2016-03-25T00:00:00+03:00</td></tr></tbody></table>

Örnek ISO8601 Parser Java 8

```java
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;

public class DateUtil
{

    public static Date fromISO8601Date(String v)
    {
        if (null == v) return null;
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssXXX");
        try
        {
            return sdf.parse(v);
        } catch (ParseException e)
        {
            throw new RuntimeException(e);
        }
    }

    public static String toISO8601Date(Date v)
    {
        if (null == v) return null;
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssXXX");
        return sdf.format(v);
    }
}
```

Örnek HTTP Mesajı

```ruby
POST /reconciliation-res/servis/v1/luy-invoice/invoice/list HTTP/1.1
Host: epys.epias.com.tr
Accept: application/json
Content-Type: application/json
TGT: TGT-237-U0TU0jUHLyOEIrdoDBEEf3AdRFAXGLifK2ITn4LoY3HfhstGtx-cas02.epias.com.tr
Cache-Control: no-cache
{
  "effectiveDate": "2019-04-01T00:00:00+03:00"
}
```

Örnek JSON Mesajı

```json
{
   "status":"200 OK",
   "correlationId":"(NotUsingGateway)b09d8806-46b9-4703-b185-2167bf74e55e",
   "spanIds":"14826",
   "hostName":"10.199.199.67",
   "clientIp":"127.0.0.1",
   "userName":"NA",
   "successMessage":null,
   "errors":null,
   "body":{
      "content":{
          "completed": true
      }
   }
}
```

Gönderilen tüm isteklere dönen cevaplar da iki bölümden oluşur. Birinci bölüm isteğin başarılı olup olmadığını dönen **status** değeri. İkinci bölüm ise **body** alanında sonucu dönen kısım.

Her sonuç mesajında aşağıdaki alanlar sabit olarak bulunur.

   
| parametre | tip | değer | açıklama |
| --- | --- | --- | --- |
| 
status

 | 

string

 | 

"200 OK" başarılı diğer hallerde hata kodu içerir

 | 

Aldığınız hatanın HTTP status kodunu dönmektedir.

 |
| 

error

 | 

list

 | 

başarılı durumda liste **null** dönmektedir

 | 

Hata almanız durumunda liste içinde aldığınız hatanın hata kodu ve hata mesajlarını dönmektedir. Hatalar ile ilgili detaylı bilgi almak isterseniz bu değerleri göndermeniz gerekmektedir.

 |
| 

correlationId

 | 

string

 | 

yapmış olduğunuz isteği tekilleştirmeye yarar **spanIds** ile birlikte

 | 

hata almanız durumunad bu bilgi ile birlikte **spanIds** göndermeniz zorunludur.

 |
| 

spanIds

 | 

string

 | 

yapmış olduğunuz isteği tekilleştirmeye yarar **correlationId** ile birlikte

 | 

hata almanız durumunad bu bilgi ile birlikte **correlationId** göndermeniz zorunludur.

 |

<table><tbody><tr><td class="icon"><i class="fa icon-important" title="Important"></i></td><td class="content"><strong>VAL-</strong> hata kodu ile başlayan hata mesajlarının olduğunuz istek ile ilgili bir sorun olduğunu belirtir. İsteğinizi gözden geçirmelisiniz veya iş kurallarını kontrol etmelisiniz. <strong>APP-</strong> hata kodu ile başlayan hata mesajları sistemde bir hata olduğunu belirtir. EPİAŞ irtibata geçmelisiniz.</td></tr></tbody></table>

Örnek Başarılı JSON Cevap Mesajı

```json
{
   "status":"200 OK",
   "correlationId":"b09d8806-46b9-4703-b185-2167bf74e55e",
   "spanIds":"14826",
   "hostName":"1.1.1.1",
   "clientIp":"127.0.0.1",
   "userName":"TESTUSER",
   "successMessage":null,
   "errors":null,
   "body":{
      "content":{
          "completed": true
      }
   }
}
```

Örnek Hatalı JSON Cevap Mesajı

```json
{
  "status": "400 BAD_REQUEST",
  "correlationId": "b09d8806-46b9-4703-b185-2167bf74e55e!",
  "spanIds": "38048",
  "hostName":"1.1.1.1",
  "clientIp":"127.0.0.1",
  "userName": "TESTUSER",
  "successMessage": null,
  "errors": [
    {
      "errorCode": "VAL-PER-1002",
      "errorMessage": "2020-01-01T00:00:00+03:00[GMT+03:00] tarihi için faturalama dönemi bulunamamıştır. "
    }
  ],
  "body": {}
}
```

## 4\. Servis Detayları

Bu bölümden kategorilerine göre Servis çağırım detayları ile ilgili bilgilere ulaşabilirsiniz.

### 4.1. Ek Tüketim Pasife Alma Servisi

<table><tbody><tr><td class="icon"><i class="fa icon-warning" title="Warning"></i></td><td class="content">Servis parametre detaylarına <a href="#_additional-consumption-passivate">buradan</a> erişebilirsiniz.</td></tr></tbody></table>

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Katılımcılar:</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">Sayaç Okuyan Kurum</p></td></tr></tbody></table>

**Not:** Bu servisi çağırabilmek için aşağıdaki yetkiye sahip olmak gerekmektedir.

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Yetkiler</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">ST - Ek Tüketim İşlemleri - Ek Tüketim Kaydı Pasife Al</p></td></tr></tbody></table>

Request

```json
{
    "id": 42,
    "explanation": "Ek Tuketim Pasife Alma Aciklamasi"
}
```

Response

```json
{
    "status": "200 OK",
    "correlationId": "c6db6fcc-80d3-403f-9983-c10949ec7f2c",
    "spanIds": "(index-ac)8***7",
    "hostName": "*.*.*.*",
    "clientIp": "*.*.*.*",
    "userName": "USER_NAME",
    "successMessage": null,
    "errors": null,
    "body": {
        "content": {
            "id": 42,
            "consumptionPointId": 200000**0,
            "eic": "40Z000200000**0I",
            "readingOrganizationId": 1010,
            "meterOwnerOrganizationId": 5780,
            "firstReadDate": "2023-07-21T00:00:00+03:00",
            "lastReadDate": "2023-08-08T00:00:00+03:00",
            "energyType": {
                "id": 1,
                "value": "ACTIVE",
                "localizations": [
                    {
                        "language": "tr-TR",
                        "text": "Aktif"
                    }
                ]
            },
            "additionalConsumptionStatus": {
                "id": 2,
                "value": "PASSIVE",
                "localizations": [
                    {
                        "language": "tr-TR",
                        "text": "Pasif"
                    }
                ]
            }
        }
    }
}
```

### 4.2. Ek Tüketim Sorgulama Servisi

<table><tbody><tr><td class="icon"><i class="fa icon-warning" title="Warning"></i></td><td class="content">Servis parametre detaylarına <a href="#_additional-consumption-query">buradan</a> erişebilirsiniz.</td></tr></tbody></table>

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Katılımcılar:</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">Piyasa Katılımcısı</p><p class="tableblock">Sayaç Okuyan Kurum</p></td></tr></tbody></table>

**Not:** Bu servisi çağırabilmek için aşağıdaki yetkiye sahip olmak gerekmektedir.

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Yetkiler</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">ST - Endeks İşlemleri - Ek Tüketim Listesi Görüntüle</p></td></tr></tbody></table>

Request

```json
{
    "eic": "40Z0002000000**I",
    "consumptionPointId": 2000000**,
    "firstReadDateAsPeriod": "2023-07-01T00:00:00+03:00",
    "lastReadDateAsPeriod": "2023-08-01T00:00:00+03:00",
    "energyTypes": [
        1
    ],
    "id": 42,
    "additionalConsumptionStatuses": [
        1
    ],
    "additionalConsumptionReasons": [
        1
    ],
    "createDateStartAsPeriod": "2023-08-01T00:00:00+03:00",
    "createDateEndAsPeriod": "2023-09-01T00:00:00+03:00",
    "page": {
        "number": 1,
        "size": 10,
        "sort": {
            "field": "createDate",
            "direction": "DESC"
        },
        "total": 1
    },
    "readingOrganizationId": "1010",
    "portfolioType": 1,
    "meterOwnerOrganizationId": "5780"
}
```

Response

```json
{
    "status": "200 OK",
    "correlationId": "c6db6fcc-80d3-403f-9983-c10949ec7f2c",
    "spanIds": "(index-ac)8***7",
    "hostName": "*.*.*.*",
    "clientIp": "*.*.*.*",
    "userName": "USER_NAME",
    "successMessage": null,
    "errors": null,
    "body": {
        "content": {
            "items": [
                {
                    "id": 42,
                    "consumptionPointId": 200000000,
                    "eic": "40Z000200000000I",
                    "readingOrganizationId": 1010,
                    "readingOrganizationName": "SAYAC OKUYAN KURUM ADI",
                    "meterOwnerOrganizationId": 5780,
                    "meterOwnerOrganizationName": "ORGANIZASYON ADI",
                    "firstReadDate": "2023-07-21T00:00:00+03:00",
                    "lastReadDate": "2023-08-08T00:00:00+03:00",
                    "createDate": "2023-08-22T14:13:27.795978+03:00",
                    "modifyDate": "2023-08-22T14:13:27.795978+03:00",
                    "createUser": "USER_NAME",
                    "modifyUser": "USER_NAME",
                    "energyType": {
                        "id": 1,
                        "value": "ACTIVE",
                        "localizations": [
                            {
                                "language": "tr-TR",
                                "text": "Aktif"
                            }
                        ]
                    },
                    "t1": "10",
                    "t2": "10",
                    "t3": "10",
                    "reactiveOrDemand": null,
                    "inductive": null,
                    "capacitive": null,
                    "demand": null,
                    "explanation": "test",
                    "period": 18,
                    "additionalConsumptionStatus": {
                        "id": 1,
                        "value": "ACTIVE",
                        "localizations": [
                            {
                                "language": "tr-TR",
                                "text": "Aktif"
                            }
                        ]
                    },
                    "additionalConsumptionReason": {
                        "id": 1,
                        "value": "MEASURING_CIRCUIT_FAILURE",
                        "localizations": [
                            {
                                "language": "tr-TR",
                                "text": "Ölçü Devresi Sorunu"
                            }
                        ]
                    },
                    "uploadPeriod": 14,
                    "portfolioType": {
                        "id": 1,
                        "value": "PORTFOLIO",
                        "localizations": [
                            {
                                "language": "tr-TR",
                                "text": "Portföy"
                            }
                        ]
                    }
                }
            ],
            "page": {
                "number": 1,
                "size": 10,
                "total": 1,
                "sort": {
                    "field": "createDate",
                    "direction": "DESC"
                }
            },
            "sortableFields": [
                "createDate"
            ]
        }
    }
}
```

### 4.3. Ek Tüketim Kayıt Servisi

<table><tbody><tr><td class="icon"><i class="fa icon-warning" title="Warning"></i></td><td class="content">Servis parametre detaylarına <a href="#_additional-consumption-save">buradan</a> erişebilirsiniz.</td></tr></tbody></table>

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Katılımcılar:</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">Sayaç Okuyan Kurum</p></td></tr></tbody></table>

**Not:** Bu servisi çağırabilmek için aşağıdaki yetkiye sahip olmak gerekmektedir.

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Yetkiler</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">ST - Ek Tüketim İşlemleri - Ek Tüketim Kaydet</p></td></tr></tbody></table>

Request

```json
{
    "capacitive": null,
    "demand": null,
    "energyType": 1,
    "explanation": "Ek Tuketim Kaydetme Aciklamasi",
    "inductive": null,
    "firstReadDate": "2023-08-30T00:00:00+03:00",
    "lastReadDate": "2023-08-31T00:00:00+03:00",
    "t1": 10,
    "t2": 20,
    "t3": 30,
    "additionalConsumptionReason": 1,
    "readingOrganizationId": 1010,
    "eic": "40Z000200000**6H",
    "consumptionPointId": 200000**6
}
```

Response

```json
{
    "status": "200 OK",
    "correlationId": "c6db6fcc-80d3-403f-9983-c10949ec7f2c",
    "spanIds": "(index-ac)8***7",
    "hostName": "*.*.*.*",
    "clientIp": "*.*.*.*",
    "userName": "USER_NAME",
    "successMessage": null,
    "errors": null,
    "body": {
        "content": {
            "id": 61,
            "consumptionPointId": 200000**6,
            "eic": "40Z000200000**6H",
            "readingOrganizationId": 1010,
            "meterOwnerOrganizationId": 5780,
            "firstReadDate": "2023-08-30T00:00:00+03:00",
            "lastReadDate": "2023-08-31T00:00:00+03:00",
            "energyType": {
                "id": 1,
                "value": "ACTIVE",
                "localizations": [
                    {
                        "language": "tr-TR",
                        "text": "Aktif"
                    }
                ]
            },
            "additionalConsumptionStatus": {
                "id": 1,
                "value": "ACTIVE",
                "localizations": [
                    {
                        "language": "tr-TR",
                        "text": "Aktif"
                    }
                ]
            }
        }
    }
}
```

### 4.4. Endeks Kayıt Sayısı Sorgulama Servisi

<table><tbody><tr><td class="icon"><i class="fa icon-warning" title="Warning"></i></td><td class="content">Servis parametre detaylarına <a href="#_index-count">buradan</a> erişebilirsiniz.</td></tr></tbody></table>

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Katılımcılar:</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">Piyasa Katılımcısı</p><p class="tableblock">Sayaç Okuyan Kurum</p></td></tr></tbody></table>

**Not:** Bu servisi çağırabilmek için aşağıdaki yetkiye sahip olmak gerekmektedir.

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Yetkiler</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">ST - Endeks İşlemleri - Endeks Listesi Görüntüle</p></td></tr></tbody></table>

Request

```json
{
    "eic": "40Z000200000**6H",
    "consumptionPointId": 200000**6,
    "firstReadDateAsPeriod": "2023-08-01T00:00:00+03:00",
    "lastReadDateAsPeriod": "2023-08-01T00:00:00+03:00",
    "energyTypes": [
        1
    ],
    "firstReadTypes": [
        1
    ],
    "lastReadTypes": [
        1
    ],
    "indexId": "10000005216",
    "indexStatuses": [
        1
    ],
    "createDateStartAsPeriod": "2023-08-01T00:00:00+03:00",
    "createDateEndAsPeriod": "2023-09-01T00:00:00+03:00",
    "periodSwitch": false,
    "readingOrganizationId": "1010",
    "portfolioType": 1,
    "meterOwnerOrganizationId": "5780"
}
```

Response

```json
{
    "status": "200 OK",
    "correlationId": "c6db6fcc-80d3-403f-9983-c10949ec7f2c",
    "spanIds": "(index-ac)8***7",
    "hostName": "*.*.*.*",
    "clientIp": "*.*.*.*",
    "userName": "USER_NAME",
    "successMessage": null,
    "errors": null,
    "body": {
        "content": {
            "count": 1
        }
    }
}
```

### 4.5. Endeks Dışa Aktarma Yardımcı Servisi

<table><tbody><tr><td class="icon"><i class="fa icon-warning" title="Warning"></i></td><td class="content">Servis parametre detaylarına <a href="#_index-export">buradan</a> erişebilirsiniz.</td></tr></tbody></table>

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Katılımcılar:</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">Piyasa Katılımcısı</p><p class="tableblock">Sayaç Okuyan Kurum</p></td></tr></tbody></table>

**Not:** Bu servisi ilk kez çağırırken page objesindeki offsetId alanı boş bırakılmalıdır. Ardından gelecek sorgularda, offsetId bilgisi önceki sorgu yanıtındaki offsetId bilgisi ile doldurulmalıdır.

**Not:** Bu servisi çağırabilmek için aşağıdaki yetkiye sahip olmak gerekmektedir.

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Yetkiler</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">ST - Endeks İşlemleri - Endeks Listesi Görüntüle</p></td></tr></tbody></table>

Request

```json
{
    "eic": "40Z000200000**6H",
    "consumptionPointId": 200000**6,
    "firstReadDateAsPeriod": "2023-08-01T00:00:00+03:00",
    "lastReadDateAsPeriod": "2023-08-01T00:00:00+03:00",
    "energyTypes": [
        1
    ],
    "firstReadTypes": [
        1
    ],
    "lastReadTypes": [
        1
    ],
    "indexId": "10000005216",
    "indexStatuses": [
        1
    ],
    "createDateStartAsPeriod": "2023-08-01T00:00:00+03:00",
    "createDateEndAsPeriod": "2023-09-01T00:00:00+03:00",
    "page": {
        "limit": "100",
        "offsetId": "1",
        "size": null
    },
    "periodSwitch": false,
    "readingOrganizationId": "1010",
    "portfolioType": 1,
    "meterOwnerOrganizationId": "5780"
}
```

Response

```json
{
    "status": "200 OK",
    "correlationId": "c6db6fcc-80d3-403f-9983-c10949ec7f2c",
    "spanIds": "(index-ac)8***7",
    "hostName": "*.*.*.*",
    "clientIp": "*.*.*.*",
    "userName": "USER_NAME",
    "successMessage": null,
    "errors": null,
    "body": {
        "content": {
            "items": [
                {
                    "indexId": 10000005216,
                    "version": 1,
                    "consumptionPointId": 200000**6,
                    "eic": "40Z000200000**6H",
                    "readingOrganizationId": 1010,
                    "readingOrganizationName": "SAYAC OKUYAN KURUM ADI",
                    "meterOwnerOrganizationId": 5780,
                    "meterOwnerOrganizationName": "ORGANIZASYON ADI",
                    "firstReadDate": "2023-08-04T00:00:00+03:00",
                    "lastReadDate": "2023-08-05T00:00:00+03:00",
                    "createDate": "2023-08-23T22:04:52.588897+03:00",
                    "energyType": {
                        "id": 1,
                        "value": "ACTIVE",
                        "localizations": [
                            {
                                "language": "tr-TR",
                                "text": "Aktif"
                            }
                        ]
                    },
                    "firstT1": "10",
                    "firstT2": "20",
                    "firstT3": "30",
                    "lastT1": "40",
                    "lastT2": "50",
                    "lastT3": "60",
                    "firstReactiveOrDemand": null,
                    "lastReactive": null,
                    "firstInductive": null,
                    "lastInductive": null,
                    "firstCapacitive": null,
                    "lastCapacitive": null,
                    "demand": null,
                    "factor": 1,
                    "meterBrand": "TEST 1",
                    "meterSerialNumber": "12345T",
                    "digitCount": 2,
                    "firstReadType": {
                        "id": 1,
                        "value": "PERIODIC",
                        "localizations": [
                            {
                                "language": "tr-TR",
                                "text": "Periyodik Okuma"
                            }
                        ]
                    },
                    "lastReadType": {
                        "id": 1,
                        "value": "PERIODIC",
                        "localizations": [
                            {
                                "language": "tr-TR",
                                "text": "Periyodik Okuma"
                            }
                        ]
                    },
                    "firstLoadType": {
                        "id": 1,
                        "value": "OSOS",
                        "localizations": [
                            {
                                "language": "tr-TR",
                                "text": "OSOS"
                            }
                        ]
                    },
                    "lastLoadType": {
                        "id": 1,
                        "value": "OSOS",
                        "localizations": [
                            {
                                "language": "tr-TR",
                                "text": "OSOS"
                            }
                        ]
                    },
                    "explanation": "aciklama",
                    "period": 1,
                    "periodExplanation": null,
                    "indexStatus": {
                        "id": 1,
                        "value": "ACTIVE",
                        "localizations": [
                            {
                                "language": "tr-TR",
                                "text": "Aktif"
                            }
                        ]
                    },
                    "uploadPeriod": 18,
                    "createUser": "SYSTEM",
                    "portfolioType": {
                        "id": 1,
                        "value": "PORTFOLIO",
                        "localizations": [
                            {
                                "language": "tr-TR",
                                "text": "Portföy"
                            }
                        ]
                    }
                }
            ],
            "page": {
                "limit": 100,
                "offsetId": 5998,
                "size": 1
            }
        }
    }
}
```

### 4.6. Endeks Pasife Alma Servisi

<table><tbody><tr><td class="icon"><i class="fa icon-warning" title="Warning"></i></td><td class="content">Servis parametre detaylarına <a href="#_index-passivate">buradan</a> erişebilirsiniz.</td></tr></tbody></table>

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Katılımcılar:</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">Sayaç Okuyan Kurum</p></td></tr></tbody></table>

**Not:** Bu servisi çağırabilmek için aşağıdaki yetkiye sahip olmak gerekmektedir.

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Yetkiler</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">ST - Endeks İşlemleri - Endeks Kaydı Pasife Al</p></td></tr></tbody></table>

Request

```json
{
  "explanation": "Endeks Pasife Alma Aciklamasidir",
  "indexId": 10000005212
}
```

Response

```json
{
    "status": "200 OK",
    "correlationId": "9a1c2817-e995-42eb-bed3-ada51f0b56f4",
    "spanIds": "(index-ac)8***7",
    "hostName": "*.*.*.*",
    "clientIp": "*.*.*.*",
    "userName": "USER_NAME",
    "successMessage": null,
    "errors": null,
    "body": {
        "content": {
            "indexId": 10000005212,
            "version": 2,
            "consumptionPointId": 200000**4,
            "eic": "40Z000200000**4C",
            "readingOrganizationId": 1010,
            "meterOwnerOrganizationId": 5780,
            "firstReadDate": "2023-08-15T00:00:00+03:00",
            "lastReadDate": "2023-08-16T00:00:00+03:00",
            "energyType": {
                "id": 1,
                "value": "ACTIVE",
                "localizations": [
                    {
                        "language": "tr-TR",
                        "text": "Aktif"
                    }
                ]
            },
            "indexStatus": {
                "id": 2,
                "value": "PASSIVE",
                "localizations": [
                    {
                        "language": "tr-TR",
                        "text": "Pasif"
                    }
                ]
            },
            "fullOverrideExist": null
        }
    }
}
```

### 4.7. Endeks Sorgulama Servisi

<table><tbody><tr><td class="icon"><i class="fa icon-warning" title="Warning"></i></td><td class="content">Servis parametre detaylarına <a href="#_index-query">buradan</a> erişebilirsiniz.</td></tr></tbody></table>

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Katılımcılar:</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">Piyasa Katılımcısı</p><p class="tableblock">Sayaç Okuyan Kurum</p></td></tr></tbody></table>

**Not:** "id" parametresi DGPYS migrasyonu ile gelen kayıtları eşleştirmek için kullanılır.

**Not:** Bu servisi çağırabilmek için aşağıdaki yetkiye sahip olmak gerekmektedir.

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Yetkiler</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">ST - Endeks İşlemleri - Endeks Listesi Görüntüle</p></td></tr></tbody></table>

Request

```json
{
    "eic": "40Z000200000**54",
    "consumptionPointId": 200000**5,
    "firstReadDateAsPeriod": null,
    "lastReadDateAsPeriod": "2023-08-01T00:00:00+03:00",
    "energyTypes": [
        1
    ],
    "firstReadTypes": [
        1
    ],
    "lastReadTypes": [
        1
    ],
    "indexId": 10000005213,
    "id": 1234,
    "indexStatuses": [
        1
    ],
    "createDateStartAsPeriod": "2023-08-01T00:00:00+03:00",
    "createDateEndAsPeriod": "2023-08-30T00:00:00+03:00",
    "page": {
        "number": 1,
        "size": 10,
        "sort": {
            "field": "createDate",
            "direction": "DESC"
        },
        "total": 10
    },
    "excludedIndexStatuses": [
        3
    ],
    "periodSwitch": false,
    "readingOrganizationId": "1010",
    "portfolioType": 1,
    "meterOwnerOrganizationId": "9082"
}
```

Response

```json
{
    "status": "200 OK",
    "correlationId": "292ac7ed-bb68-4f93-8703-3ebee303b4b7",
    "spanIds": "(index-ac)8***7",
    "hostName": "*.*.*.*",
    "clientIp": "*.*.*.*",
    "userName": "USER_NAME",
    "successMessage": null,
    "errors": null,
    "body": {
        "content": {
            "items": [
                {
                    "id": 1234,
                    "indexId": 10000005213,
                    "version": 1,
                    "consumptionPointId": 200000**5,
                    "eic": "40Z000200000**54",
                    "readingOrganizationId": 1010,
                    "readingOrganizationName": "SAYAC OKUYAN KURUM ADI",
                    "meterOwnerOrganizationId": 9082,
                    "meterOwnerOrganizationName": "TEDARIKCI ORGANIZASYON ADI",
                    "firstReadDate": "2023-08-04T00:00:00+03:00",
                    "lastReadDate": "2023-08-05T00:00:00+03:00",
                    "createDate": "2023-08-23T22:04:52.579896+03:00",
                    "energyType": {
                        "id": 1,
                        "value": "ACTIVE",
                        "localizations": [
                            {
                                "language": "tr-TR",
                                "text": "Aktif"
                            }
                        ]
                    },
                    "firstT1": 10,
                    "firstT2": 20,
                    "firstT3": 30,
                    "lastT1": 40,
                    "lastT2": 50,
                    "lastT3": 60,
                    "firstReactiveOrDemand": null,
                    "lastReactive": null,
                    "firstInductive": null,
                    "lastInductive": null,
                    "firstCapacitive": null,
                    "lastCapacitive": null,
                    "demand": null,
                    "factor": 1,
                    "meterBrand": "SAYAC MARKA",
                    "meterSerialNumber": "SAYAC SERI NO",
                    "digitCount": 2,
                    "firstReadType": {
                        "id": 1,
                        "value": "PERIODIC",
                        "localizations": [
                            {
                                "language": "tr-TR",
                                "text": "Periyodik Okuma"
                            }
                        ]
                    },
                    "lastReadType": {
                        "id": 1,
                        "value": "PERIODIC",
                        "localizations": [
                            {
                                "language": "tr-TR",
                                "text": "Periyodik Okuma"
                            }
                        ]
                    },
                    "firstLoadType": {
                        "id": 1,
                        "value": "OSOS",
                        "localizations": [
                            {
                                "language": "tr-TR",
                                "text": "OSOS"
                            }
                        ]
                    },
                    "lastLoadType": {
                        "id": 1,
                        "value": "OSOS",
                        "localizations": [
                            {
                                "language": "tr-TR",
                                "text": "OSOS"
                            }
                        ]
                    },
                    "explanation": "aciklama",
                    "period": 1,
                    "periodExplanation": null,
                    "indexStatus": {
                        "id": 1,
                        "value": "ACTIVE",
                        "localizations": [
                            {
                                "language": "tr-TR",
                                "text": "Aktif"
                            }
                        ]
                    },
                    "uploadPeriod": 18,
                    "createUser": "SYSTEM",
                    "portfolioType": {
                        "id": 1,
                        "value": "PORTFOLIO",
                        "localizations": [
                            {
                                "language": "tr-TR",
                                "text": "Portföy"
                            }
                        ]
                    }
                }
            ],
            "page": {
                "number": 1,
                "size": 10,
                "total": 1,
                "sort": {
                    "field": "createDate",
                    "direction": "DESC"
                }
            },
            "sortableFields": [
                "createDate"
            ]
        }
    }
}
```

### 4.8. Endeks Kayıt Servisi

<table><tbody><tr><td class="icon"><i class="fa icon-warning" title="Warning"></i></td><td class="content">Servis parametre detaylarına <a href="#_index-save">buradan</a> erişebilirsiniz.</td></tr></tbody></table>

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Katılımcılar:</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">Sayaç Okuyan Kurum</p></td></tr></tbody></table>

**Not:** Bu servisi çağırabilmek için aşağıdaki yetkiye sahip olmak gerekmektedir.

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Yetkiler</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">ST - Endeks İşlemleri - Endeks Kaydet</p></td></tr></tbody></table>

Request

```json
{
    "energyType": 1,
    "factor": "1.0",
    "digitCount": 2,
    "meterSerialNumber": "3",
    "meterBrand": "4",
    "firstT1": "10.0",
    "firstT2": "30.0",
    "firstT3": "50.0",
    "lastT1": "20.0",
    "lastT2": "40.0",
    "lastT3": "60.0",
    "firstInductive": null,
    "lastInductive": null,
    "firstCapacitive": null,
    "lastCapacitive": null,
    "demand": null,
    "firstReadType": 1,
    "lastReadType": 1,
    "firstLoadType": 1,
    "lastLoadType": 1,
    "explanation": "Endeks Kaydetme Aciklamasidir",
    "periodExplanation": null,
    "firstReadDate": "2023-08-30T00:00:00+03:00",
    "lastReadDate": "2023-08-31T00:00:00+03:00",
    "readingOrganizationId": 1010,
    "eic": "40Z000200000266H",
    "consumptionPointId": 200000266,
    "overrideFullOverlap": true
}
```

Response

```json
{
    "status": "200 OK",
    "correlationId": "c6db6fcc-80d3-403f-9983-c10949ec7f2c",
    "spanIds": "(index-ac)8***7",
    "hostName": "*.*.*.*",
    "clientIp": "*.*.*.*",
    "userName": "USER_NAME",
    "successMessage": null,
    "errors": null,
    "body": {
        "content": {
            "indexId": 10000006260,
            "version": 1,
            "consumptionPointId": 200000**6,
            "eic": "40Z000200000**6H",
            "readingOrganizationId": 1010,
            "meterOwnerOrganizationId": 5780,
            "firstReadDate": "2023-08-30T00:00:00+03:00",
            "lastReadDate": "2023-08-31T00:00:00+03:00",
            "energyType": {
                "id": 1,
                "value": "ACTIVE",
                "localizations": [
                    {
                        "language": "tr-TR",
                        "text": "Aktif"
                    }
                ]
            },
            "indexStatus": {
                "id": 1,
                "value": "ACTIVE",
                "localizations": [
                    {
                        "language": "tr-TR",
                        "text": "Aktif"
                    }
                ]
            },
            "fullOverrideExist": null
        }
    }
}
```

### 4.9. Endeks Toplu Kayıt Servisi

<table><tbody><tr><td class="icon"><i class="fa icon-warning" title="Warning"></i></td><td class="content">Servis parametre detaylarına <a href="#_index-save-batch">buradan</a> erişebilirsiniz.</td></tr></tbody></table>

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Katılımcılar:</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">Sayaç Okuyan Kurum</p></td></tr></tbody></table>

**Not:** Tek seferde en fazla 1000 kayıt desteklenmektedir.

**Not:** Bu servisi çağırabilmek için aşağıdaki yetkiye sahip olmak gerekmektedir.

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Yetkiler</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">ST - Endeks İşlemleri - Endeks Kaydet</p></td></tr></tbody></table>

Request

```json
[
    {
        "consumptionPointId": 200000**4,
        "digitCount": 2,
        "energyType": 1,
        "explanation": "aciklama",
        "factor": 1,
        "firstLoadType": 1,
        "firstReadDate": "2023-08-01T00:00:00+03:00",
        "firstReadType": 1,
        "firstT1": 10,
        "firstT2": 20,
        "firstT3": 30,
        "lastLoadType": 1,
        "lastReadDate": "2023-08-02T00:00:00+03:00",
        "lastReadType": 1,
        "lastT1": 40,
        "lastT2": 50,
        "lastT3": 60,
        "meterBrand": "TEST 1",
        "meterSerialNumber": "12345T",
        "overrideFullOverlap": true,
        "readingOrganizationId": 1010
    },
    {
        "consumptionPointId": 200000**4,
        "digitCount": 2,
        "energyType": 1,
        "explanation": "aciklama",
        "factor": 1,
        "firstLoadType": 1,
        "firstReadDate": "2023-08-02T00:00:00+03:00",
        "firstReadType": 1,
        "firstT1": 10,
        "firstT2": 20,
        "firstT3": 30,
        "lastLoadType": 1,
        "lastReadDate": "2023-08-03T00:00:00+03:00",
        "lastReadType": 1,
        "lastT1": 40,
        "lastT2": 50,
        "lastT3": 60,
        "meterBrand": "TEST 1",
        "meterSerialNumber": "12345T",
        "overrideFullOverlap": true,
        "readingOrganizationId": 1010
    }
]
```

Response

```json
{
    "status": "200 OK",
    "correlationId": "c6db6fcc-80d3-403f-9983-c10949ec7f2c",
    "spanIds": "(index-ac)8***7",
    "hostName": "*.*.*.*",
    "clientIp": "*.*.*.*",
    "userName": "USER_NAME",
    "successMessage": null,
    "errors": null,
    "body": {
        "content": [
            {
                "indexId": 10000005766,
                "consumptionPointId": 200000**4,
                "firstReadDate": "2023-08-01T00:00:00+03:00",
                "lastReadDate": "2023-08-02T00:00:00+03:00",
                "energyType": 1,
                "isSuccessful": true,
                "errorMessage": null
            },
            {
                "indexId": 10000005749,
                "consumptionPointId": 200000**4,
                "firstReadDate": "2023-08-02T00:00:00+03:00",
                "lastReadDate": "2023-08-03T00:00:00+03:00",
                "energyType": 1,
                "isSuccessful": true,
                "errorMessage": null
            }
        ]
    }
}
```

Request (XML)

```xml
<IndexSaveRequestWrapperDto>
    <IndexSaveRequestDto>
                <consumptionPointId>200000**4</consumptionPointId>
                <demand />
                <digitCount>2</digitCount>
                <eic>40Z000200000**4H</eic>
                <energyType>1</energyType>
                <explanation>aciklama</explanation>
                <factor>1</factor>
                <firstCapacitive />
                <firstInductive />
                <firstLoadType>0</firstLoadType>
                <firstReadDate>2023-08-30T00:00:00+03:00</firstReadDate>
                <firstReadType>0</firstReadType>
                <firstT1>10</firstT1>
                <firstT2>20</firstT2>
                <firstT3>30</firstT3>
                <lastCapacitive />
                <lastInductive />
                <lastLoadType>0</lastLoadType>
                <lastReadDate>2023-08-31T00:00:00+03:00</lastReadDate>
                <lastReadType>0</lastReadType>
                <lastT1>40</lastT1>
                <lastT2>50</lastT2>
                <lastT3>60</lastT3>
                <meterBrand>TEST 1</meterBrand>
                <meterSerialNumber>12345T</meterSerialNumber>
                <overrideFullOverlap>true</overrideFullOverlap>
                <periodExplanation />
                <readingOrganizationId>1010</readingOrganizationId>
        </IndexSaveRequestDto>
        <IndexSaveRequestDto>
            <consumptionPointId>200000**4</consumptionPointId>
                <demand />
                <digitCount>2</digitCount>
                <eic>40Z000200000**4H</eic>
                <energyType>1</energyType>
                <explanation>aciklama</explanation>
                <factor>1</factor>
                <firstCapacitive />
                <firstInductive />
                <firstLoadType>0</firstLoadType>
                <firstReadDate>2023-08-29T00:00:00+03:00</firstReadDate>
                <firstReadType>0</firstReadType>
                <firstT1>10</firstT1>
                <firstT2>20</firstT2>
                <firstT3>30</firstT3>
                <lastCapacitive />
                <lastInductive />
                <lastLoadType>0</lastLoadType>
                <lastReadDate>2023-08-30T00:00:00+03:00</lastReadDate>
                <lastReadType>0</lastReadType>
                <lastT1>40</lastT1>
                <lastT2>50</lastT2>
                <lastT3>60</lastT3>
                <meterBrand>TEST 1</meterBrand>
                <meterSerialNumber>12345T</meterSerialNumber>
                <overrideFullOverlap>true</overrideFullOverlap>
                <periodExplanation />
                <readingOrganizationId>1010</readingOrganizationId>
        </IndexSaveRequestDto>
</IndexSaveRequestWrapperDto>
```

### 4.10. Endeks Güncelleme Servisi

<table><tbody><tr><td class="icon"><i class="fa icon-warning" title="Warning"></i></td><td class="content">Servis parametre detaylarına <a href="#_index-update">buradan</a> erişebilirsiniz.</td></tr></tbody></table>

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Katılımcılar:</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">Sayaç Okuyan Kurum</p></td></tr></tbody></table>

**Not:** Bu servisi çağırabilmek için aşağıdaki yetkiye sahip olmak gerekmektedir.

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Yetkiler</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">ST - Endeks İşlemleri - Endeks Güncelle</p></td></tr></tbody></table>

Request

```json
{
    "factor": "2.0",
    "digitCount": 3,
    "meterSerialNumber": "12345C",
    "meterBrand": "SAYAC MARKA",
    "firstT1": "11.0",
    "firstT2": 21,
    "firstT3": 31,
    "lastT1": 41,
    "lastT2": 51,
    "lastT3": 61,
    "firstInductive": null,
    "lastInductive": null,
    "firstCapacitive": null,
    "lastCapacitive": null,
    "demand": null,
    "firstReadType": 2,
    "lastReadType": 3,
    "firstLoadType": 2,
    "lastLoadType": 2,
    "explanation": "Endeks Guncelleme Aciklama",
    "indexId": 10000005213,
    "periodExplanation": null
}
```

Response

```json
{
    "status": "200 OK",
    "correlationId": "c6db6fcc-80d3-403f-9983-c10949ec7f2c",
    "spanIds": "(index-ac)8***7",
    "hostName": "*.*.*.*",
    "clientIp": "*.*.*.*",
    "userName": "USER_NAME",
    "successMessage": null,
    "errors": null,
    "body": {
        "content": {
            "indexId": 10000005213,
            "version": 3,
            "consumptionPointId": 200000**5,
            "eic": "40Z000200000**54",
            "readingOrganizationId": 1010,
            "meterOwnerOrganizationId": 9082,
            "firstReadDate": "2023-08-04T00:00:00+03:00",
            "lastReadDate": "2023-08-05T00:00:00+03:00",
            "energyType": {
                "id": 1,
                "value": "ACTIVE",
                "localizations": [
                    {
                        "language": "tr-TR",
                        "text": "Aktif"
                    }
                ]
            },
            "indexStatus": {
                "id": 1,
                "value": "ACTIVE",
                "localizations": [
                    {
                        "language": "tr-TR",
                        "text": "Aktif"
                    }
                ]
            },
            "fullOverrideExist": null
        }
    }
}
```

### 4.11. Mevcut Çoklu Seçim Anahtar Sorgulama Servisi

<table><tbody><tr><td class="icon"><i class="fa icon-warning" title="Warning"></i></td><td class="content">Mevcut çoklu seçim anahtar verilerini sorgular. Servis parametre detaylarına <a href="#_available-lookups">buradan</a> erişebilirsiniz.</td></tr></tbody></table>

**Not:** Bu servisi çağırabilmek için herhangi bir yetkiye sahip olmak gerekmemektedir.

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Yetkiler</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">N/A</p></td></tr></tbody></table>

### 4.12. Çoklu Seçim Detay Sorgulama Servisi

<table><tbody><tr><td class="icon"><i class="fa icon-warning" title="Warning"></i></td><td class="content">Çoklu seçim detay verilerini sorgular. Servis parametre detaylarına <a href="#_lookup-query">buradan</a> erişebilirsiniz.</td></tr></tbody></table>

**Not:** Bu servisi çağırabilmek için herhangi bir yetkiye sahip olmak gerekmemektedir.

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Yetkiler</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">N/A</p></td></tr></tbody></table>

### 4.13. Okuma Yükümlülük Raporu Sorgulama Servisi

<table><tbody><tr><td class="icon"><i class="fa icon-warning" title="Warning"></i></td><td class="content">Servis parametre detaylarına <a href="#_read-obligation-query">buradan</a> erişebilirsiniz.</td></tr></tbody></table>

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Katılımcılar:</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">Piyasa Katılımcısı</p><p class="tableblock">Sayaç Okuyan Kurum</p></td></tr></tbody></table>

**Not:** Bu servisi çağırabilmek için aşağıdaki yetkiye sahip olmak gerekmektedir.

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Yetkiler</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">ST - Okuma Yükümlülük Raporu</p></td></tr></tbody></table>

### 4.14. Endeks ve Ek Tüketim Özet Raporu Sorgulama Servisi

<table><tbody><tr><td class="icon"><i class="fa icon-warning" title="Warning"></i></td><td class="content">Servis parametre detaylarına <a href="#_summary-report-query">buradan</a> erişebilirsiniz.</td></tr></tbody></table>

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Katılımcılar:</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">Piyasa Katılımcısı</p><p class="tableblock">Sayaç Okuyan Kurum</p></td></tr></tbody></table>

**Not:** Bu servisi çağırabilmek için aşağıdaki yetkiye sahip olmak gerekmektedir.

<table class="tableblock frame-all grid-all stretch"><colgroup><col></colgroup><tbody><tr><td class="tableblock halign-left valign-top"><p class="tableblock"><strong>Yetkiler</strong></p></td></tr><tr><td class="tableblock halign-left valign-top"><p class="tableblock">ST - Endeks ve Ek Tüketim Özet Raporu</p></td></tr></tbody></table>

## 5\. Dizinler

### 5.1. Ek Tüketim Pasife Alma Servisi

```
POST /v1/additional-consumption/passivate
```

#### 5.1.1. Açıklama

Ek Tüketim verilerini pasife alır.

#### 5.1.2. Parametreler

  
| Tip | İsim | Şema |
| --- | --- | --- |
| 
**Body**



 | 

**body**  
_opsiyonel_



 | 

[AdditionalConsumptionPassivateRequestDto](#_additionalconsumptionpassivaterequestdto)



 |

#### 5.1.3. Cevaplar

  
| HTTP Kodu | Açıklama | Şema |
| --- | --- | --- |
| 
**200**



 | 

successful operation



 | 

[RestResponseAdditionalConsumptionSummaryDto](#_restresponseadditionalconsumptionsummarydto)



 |

#### 5.1.4. Kullanılanlar

-   `application/json`
    
-   `application/xml`
    

#### 5.1.5. Üretilenler

-   `application/json`
    
-   `application/xml`
    

#### 5.1.6. Etiketler

-   additionalConsumption
    

### 5.2. Ek Tüketim Sorgulama Servisi

```
POST /v1/additional-consumption/query
```

#### 5.2.1. Açıklama

Ek Tüketim verilerini sorgular.

#### 5.2.2. Parametreler

  
| Tip | İsim | Şema |
| --- | --- | --- |
| 
**Body**



 | 

**body**  
_opsiyonel_



 | 

[AdditionalConsumptionQueryRequestDto](#_additionalconsumptionqueryrequestdto)



 |

#### 5.2.3. Cevaplar

  
| HTTP Kodu | Açıklama | Şema |
| --- | --- | --- |
| 
**200**



 | 

successful operation



 | 

[RestResponseSortablePageResponseAdditionalConsumptionQueryResponseDto](#_restresponsesortablepageresponseadditionalconsumptionqueryresponsedto)



 |

#### 5.2.4. Kullanılanlar

-   `application/json`
    
-   `application/xml`
    

#### 5.2.5. Üretilenler

-   `application/json`
    
-   `application/xml`
    

#### 5.2.6. Etiketler

-   additionalConsumption
    

### 5.3. Ek Tüketim Kayıt Servisi

```
POST /v1/additional-consumption/save
```

#### 5.3.1. Açıklama

Ek Tüketim verilerini sisteme kaydeder.

#### 5.3.2. Parametreler

  
| Tip | İsim | Şema |
| --- | --- | --- |
| 
**Body**



 | 

**body**  
_opsiyonel_



 | 

[AdditionalConsumptionSaveRequestDto](#_additionalconsumptionsaverequestdto)



 |

#### 5.3.3. Cevaplar

  
| HTTP Kodu | Açıklama | Şema |
| --- | --- | --- |
| 
**200**



 | 

successful operation



 | 

[RestResponseAdditionalConsumptionSummaryDto](#_restresponseadditionalconsumptionsummarydto)



 |

#### 5.3.4. Kullanılanlar

-   `application/json`
    
-   `application/xml`
    

#### 5.3.5. Üretilenler

-   `application/json`
    
-   `application/xml`
    

#### 5.3.6. Etiketler

-   additionalConsumption
    

### 5.4. Endeks Kayıt Sayısı Sorgulama Servisi

#### 5.4.1. Açıklama

Endeks kayıt sayısı sorgular.

#### 5.4.2. Parametreler

  
| Tip | İsim | Şema |
| --- | --- | --- |
| 
**Body**



 | 

**body**  
_opsiyonel_



 | 

[IndexCountRequestDto](#_indexcountrequestdto)



 |

#### 5.4.3. Cevaplar

  
| HTTP Kodu | Açıklama | Şema |
| --- | --- | --- |
| 
**200**



 | 

successful operation



 | 

[RestResponseCountResponseDto](#_restresponsecountresponsedto)



 |

#### 5.4.4. Kullanılanlar

-   `application/json`
    
-   `application/xml`
    

#### 5.4.5. Üretilenler

-   `application/json`
    
-   `application/xml`
    

### 5.5. Endeks Dışa Aktarma Yardımcı Servisi

#### 5.5.1. Açıklama

Endeks verilerini dışarı aktarma icin yardımcı servis sunar.

#### 5.5.2. Parametreler

  
| Tip | İsim | Şema |
| --- | --- | --- |
| 
**Body**



 | 

**body**  
_opsiyonel_



 | 

[IndexExportRequestDto](#_indexexportrequestdto)



 |

#### 5.5.3. Cevaplar

  
| HTTP Kodu | Açıklama | Şema |
| --- | --- | --- |
| 
**200**



 | 

successful operation



 | 

[RestResponseExportPageResponseIndexQueryResponseDto](#_restresponseexportpageresponseindexqueryresponsedto)



 |

#### 5.5.4. Kullanılanlar

-   `application/json`
    
-   `application/xml`
    

#### 5.5.5. Üretilenler

-   `application/json`
    
-   `application/xml`
    

### 5.6. Endeks Pasife Alma Servisi

#### 5.6.1. Açıklama

Endeks verilerini pasife alır.

#### 5.6.2. Parametreler

  
| Tip | İsim | Şema |
| --- | --- | --- |
| 
**Body**



 | 

**body**  
_opsiyonel_



 | 

[IndexPassivateRequestDto](#_indexpassivaterequestdto)



 |

#### 5.6.3. Cevaplar

  
| HTTP Kodu | Açıklama | Şema |
| --- | --- | --- |
| 
**200**



 | 

successful operation



 | 

[RestResponseIndexSummaryDto](#_restresponseindexsummarydto)



 |

#### 5.6.4. Kullanılanlar

-   `application/json`
    
-   `application/xml`
    

#### 5.6.5. Üretilenler

-   `application/json`
    
-   `application/xml`
    

### 5.7. Endeks Sorgulama Servisi

#### 5.7.1. Açıklama

Endeks verilerini sorgular.

#### 5.7.2. Parametreler

  
| Tip | İsim | Şema |
| --- | --- | --- |
| 
**Body**



 | 

**body**  
_opsiyonel_



 | 

[IndexQueryRequestDto](#_indexqueryrequestdto)



 |

#### 5.7.3. Cevaplar

  
| HTTP Kodu | Açıklama | Şema |
| --- | --- | --- |
| 
**200**



 | 

successful operation



 | 

[RestResponseSortablePageResponseIndexQueryResponseDto](#_restresponsesortablepageresponseindexqueryresponsedto)



 |

#### 5.7.4. Kullanılanlar

-   `application/json`
    
-   `application/xml`
    

#### 5.7.5. Üretilenler

-   `application/json`
    
-   `application/xml`
    

### 5.8. Endeks Kayıt Servisi

#### 5.8.1. Açıklama

Endeks verilerini sisteme kaydeder.

#### 5.8.2. Parametreler

  
| Tip | İsim | Şema |
| --- | --- | --- |
| 
**Body**



 | 

**body**  
_opsiyonel_



 | 

[IndexSaveRequestDto](#_indexsaverequestdto)



 |

#### 5.8.3. Cevaplar

  
| HTTP Kodu | Açıklama | Şema |
| --- | --- | --- |
| 
**200**



 | 

successful operation



 | 

[RestResponseIndexSummaryDto](#_restresponseindexsummarydto)



 |

#### 5.8.4. Kullanılanlar

-   `application/json`
    
-   `application/xml`
    

#### 5.8.5. Üretilenler

-   `application/json`
    
-   `application/xml`
    

### 5.9. Endeks Toplu Kayıt Servisi

```
POST /v1/index/save-batch
```

#### 5.9.1. Açıklama

Endeks verilerini toplu olarak sisteme kaydeder.

#### 5.9.2. Parametreler

  
| Tip | İsim | Şema |
| --- | --- | --- |
| 
**Body**



 | 

**body**  
_opsiyonel_



 | 

< [IndexSaveRequestDto](#_indexsaverequestdto) > array



 |

#### 5.9.3. Cevaplar

  
| HTTP Kodu | Açıklama | Şema |
| --- | --- | --- |
| 
**200**



 | 

successful operation



 | 

[RestResponseIndexBatchSummaryDto](#_restresponseindexbatchsummarydto)



 |

#### 5.9.4. Kullanılanlar

-   `application/json`
    
-   `application/xml`
    

#### 5.9.5. Üretilenler

-   `application/json`
    
-   `application/xml`
    

### 5.10. Endeks Güncelleme Servisi

#### 5.10.1. Açıklama

Endeks verilerini günceller.

#### 5.10.2. Parametreler

  
| Tip | İsim | Şema |
| --- | --- | --- |
| 
**Body**



 | 

**body**  
_opsiyonel_



 | 

[IndexUpdateRequestDto](#_indexupdaterequestdto)



 |

#### 5.10.3. Cevaplar

  
| HTTP Kodu | Açıklama | Şema |
| --- | --- | --- |
| 
**200**



 | 

successful operation



 | 

[RestResponseIndexSummaryDto](#_restresponseindexsummarydto)



 |

#### 5.10.4. Kullanılanlar

-   `application/json`
    
-   `application/xml`
    

#### 5.10.5. Üretilenler

-   `application/json`
    
-   `application/xml`
    

### 5.11. Mevcut Çoklu Seçim Anahtar Sorgulama Servisi

#### 5.11.1. Açıklama

Mevcut çoklu seçim anahtar verilerini sorgular.

#### 5.11.2. Cevaplar

  
| HTTP Kodu | Açıklama | Şema |
| --- | --- | --- |
| 
**200**



 | 

successful operation



 | 

[RestResponseLookupTypeResponse](#_restresponselookuptyperesponse)



 |

#### 5.11.3. Üretilenler

-   `application/json`
    
-   `application/xml`
    

### 5.12. Çoklu Seçim Detay Sorgulama Servisi

#### 5.12.1. Açıklama

Çoklu seçim detay verilerini sorgular.

#### 5.12.2. Parametreler

  
| Tip | İsim | Şema |
| --- | --- | --- |
| 
**Header**



 | 

**accept-language**  
_opsiyonel_



 | 

string



 |
| 

**Body**



 | 

**body**  
_opsiyonel_



 | 

[LookupRequest](#_lookuprequest)



 |

#### 5.12.3. Cevaplar

  
| HTTP Kodu | Açıklama | Şema |
| --- | --- | --- |
| 
**200**



 | 

successful operation



 | 

[RestResponseLookupResponse](#_restresponselookupresponse)



 |

#### 5.12.4. Kullanılanlar

-   `application/json`
    
-   `application/xml`
    

#### 5.12.5. Üretilenler

-   `application/json`
    
-   `application/xml`
    

### 5.13. Okuma Yükümlülük Raporu Sorgulama Servisi

```
POST /v1/read-obligation/query
```

#### 5.13.1. Açıklama

Okuma Yükümlülük Raporu verilerini sorgular.

#### 5.13.2. Parametreler

  
| Tip | İsim | Şema |
| --- | --- | --- |
| 
**Body**



 | 

**body**  
_opsiyonel_



 | 

[ReadObligationQueryRequestDto](#_readobligationqueryrequestdto)



 |

#### 5.13.3. Cevaplar

  
| HTTP Kodu | Açıklama | Şema |
| --- | --- | --- |
| 
**200**



 | 

successful operation



 | 

[RestResponseSortablePageResponseReadObligationDto](#_restresponsesortablepageresponsereadobligationdto)



 |

#### 5.13.4. Kullanılanlar

-   `application/json`
    
-   `application/xml`
    

#### 5.13.5. Üretilenler

-   `application/json`
    
-   `application/xml`
    

#### 5.13.6. Etiketler

-   readObligation
    

### 5.14. Endeks ve Ek Tüketim Özet Raporu Sorgulama Servisi

```
POST /v1/summary-report/query
```

#### 5.14.1. Açıklama

Endeks ve Ek Tüketim Özet Raporu verilerini sorgular.

#### 5.14.2. Parametreler

  
| Tip | İsim | Şema |
| --- | --- | --- |
| 
**Body**



 | 

**body**  
_opsiyonel_



 | 

[SummaryReportQueryRequestDto](#_summaryreportqueryrequestdto)



 |

#### 5.14.3. Cevaplar

  
| HTTP Kodu | Açıklama | Şema |
| --- | --- | --- |
| 
**200**



 | 

successful operation



 | 

[RestResponseSummaryReportQueryResponseDto](#_restresponsesummaryreportqueryresponsedto)



 |

#### 5.14.4. Kullanılanlar

-   `application/json`
    
-   `application/xml`
    

#### 5.14.5. Üretilenler

-   `application/json`
    
-   `application/xml`
    

#### 5.14.6. Etiketler

-   summaryReport
    

## 6\. Tanımlar

### 6.1. AdditionalConsumptionPassivateRequestDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**explanation**  
_gerekli_



 | 

Açıklama



 | 

string



 |
| 

**id**  
_gerekli_



 | 

Ek Tüketim ID



 | 

integer (int64)



 |

### 6.2. AdditionalConsumptionQueryRequestDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**additionalConsumptionReasons**  
_opsiyonel_



 | 

Ek Tüketim Nedeni



 | 

< integer (int64) > array



 |
| 

**additionalConsumptionStatuses**  
_opsiyonel_



 | 

Ek Tüketim Durumu



 | 

< integer (int64) > array



 |
| 

**consumptionPointId**  
_opsiyonel_



 | 

Ölçüm Noktası ID



 | 

integer (int64)



 |
| 

**createDateEndAsPeriod**  
_opsiyonel_



 | 

İşlem Tarihi - Bitiş



 | 

string (date-time)



 |
| 

**createDateStartAsPeriod**  
_opsiyonel_



 | 

İşlem Tarihi - Başlangıç



 | 

string (date-time)



 |
| 

**eic**  
_opsiyonel_



 | 

EIC Kod



 | 

string



 |
| 

**energyTypes**  
_opsiyonel_



 | 

Enerji Türü



 | 

< integer (int64) > array



 |
| 

**firstReadDateAsPeriod**  
_opsiyonel_



 | 

Dönem - Başlangıç



 | 

string (date-time)



 |
| 

**id**  
_opsiyonel_



 | 

Ek Tüketim ID



 | 

integer (int64)



 |
| 

**lastReadDateAsPeriod**  
_opsiyonel_



 | 

Dönem - Bitiş



 | 

string (date-time)



 |
| 

**meterOwnerOrganizationId**  
_opsiyonel_



 | 

Organizasyon ID



 | 

integer (int64)



 |
| 

**page**  
_opsiyonel_



 |  | 

[Page](#_page)



 |
| 

**portfolioType**  
_opsiyonel_



 | 

Portföy Tipi



 | 

integer (int64)



 |
| 

**readingOrganizationId**  
_opsiyonel_



 | 

Sayaç Okuyan Kurum ID



 | 

integer (int64)



 |

### 6.3. AdditionalConsumptionQueryResponseDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**additionalConsumptionReason**  
_opsiyonel_



 | 

Ek Tüketim Nedeni



 | 

[LookupDTO](#_lookupdto)



 |
| 

**additionalConsumptionStatus**  
_opsiyonel_



 | 

Ek Tüketim Durumu



 | 

[LookupDTO](#_lookupdto)



 |
| 

**capacitive**  
_opsiyonel_



 | 

RC (kVarh)



 | 

string



 |
| 

**consumptionPointId**  
_opsiyonel_



 | 

Ölçüm Noktası ID



 | 

integer (int64)



 |
| 

**createDate**  
_opsiyonel_



 | 

İşlem Tarihi



 | 

string (date-time)



 |
| 

**createUser**  
_opsiyonel_



 | 

İşlem Yapan Kullanıcı



 | 

string



 |
| 

**demand**  
_opsiyonel_



 | 

Demand



 | 

string



 |
| 

**eic**  
_opsiyonel_



 | 

EIC Kod



 | 

string



 |
| 

**energyType**  
_opsiyonel_



 | 

Enerji Türü



 | 

[LookupDTO](#_lookupdto)



 |
| 

**explanation**  
_opsiyonel_



 | 

Açıklama



 | 

string



 |
| 

**firstReadDate**  
_opsiyonel_



 | 

Ek Tüketim Başlangıç Tarihi



 | 

string (date-time)



 |
| 

**id**  
_opsiyonel_



 | 

Ek Tüketim ID



 | 

integer (int64)



 |
| 

**inductive**  
_opsiyonel_



 | 

RI (kVarh)



 | 

string



 |
| 

**lastReadDate**  
_opsiyonel_



 | 

Ek Tüketim Bitiş Tarihi



 | 

string (date-time)



 |
| 

**meterOwnerOrganizationId**  
_opsiyonel_



 | 

Organizasyon ID



 | 

integer (int64)



 |
| 

**meterOwnerOrganizationName**  
_opsiyonel_



 | 

Organizasyon Adı



 | 

string



 |
| 

**modifyDate**  
_opsiyonel_



 | 

Güncelleme Tarihi



 | 

string (date-time)



 |
| 

**modifyUser**  
_opsiyonel_



 | 

Güncelleme Yapan Kullanıcı



 | 

string



 |
| 

**period**  
_opsiyonel_



 | 

Periyot



 | 

integer (int64)



 |
| 

**portfolioType**  
_opsiyonel_



 | 

Portföy Tipi



 | 

[LookupDTO](#_lookupdto)



 |
| 

**reactiveOrDemand**  
_opsiyonel_



 | 

Reaktif (kVarh) / Demand (kW)



 | 

string



 |
| 

**readingOrganizationId**  
_opsiyonel_



 | 

Sayaç Okuyan Kurum ID



 | 

integer (int64)



 |
| 

**readingOrganizationName**  
_opsiyonel_



 | 

Sayaç Okuyan Kurum Adı



 | 

string



 |
| 

**t1**  
_opsiyonel_



 | 

T1 (kWh)



 | 

string



 |
| 

**t2**  
_opsiyonel_



 | 

T2 (kWh)



 | 

string



 |
| 

**t3**  
_opsiyonel_



 | 

T3 (kWh)



 | 

string



 |
| 

**uploadPeriod**  
_opsiyonel_



 | 

Yükleme Süresi



 | 

integer (int64)



 |

### 6.4. AdditionalConsumptionSaveRequestDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**additionalConsumptionReason**  
_gerekli_



 | 

Ek Tüketim Nedeni



 | 

integer (int64)



 |
| 

**capacitive**  
_opsiyonel_



 | 

RC (kVarh)



 | 

number



 |
| 

**consumptionPointId**  
_opsiyonel_



 | 

Ölçüm Noktası ID



 | 

integer (int64)



 |
| 

**demand**  
_opsiyonel_



 | 

Demand



 | 

number



 |
| 

**eic**  
_opsiyonel_



 | 

EIC Kod



 | 

string



 |
| 

**energyType**  
_gerekli_



 | 

Enerji Türü



 | 

integer (int64)



 |
| 

**explanation**  
_opsiyonel_



 | 

Açıklama



 | 

string



 |
| 

**firstReadDate**  
_gerekli_



 | 

Ek Tüketim Başlangıç Tarihi



 | 

string (date-time)



 |
| 

**inductive**  
_opsiyonel_



 | 

RI (kVarh)



 | 

number



 |
| 

**lastReadDate**  
_gerekli_



 | 

Ek Tüketim Bitiş Tarihi



 | 

string (date-time)



 |
| 

**readingOrganizationId**  
_opsiyonel_



 | 

Sayaç Okuyan Kurum ID



 | 

integer (int64)



 |
| 

**t1**  
_opsiyonel_



 | 

T1 (kWh)



 | 

number



 |
| 

**t2**  
_opsiyonel_



 | 

T2 (kWh)



 | 

number



 |
| 

**t3**  
_opsiyonel_



 | 

T3 (kWh)



 | 

number



 |

### 6.5. AdditionalConsumptionSummaryDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**additionalConsumptionStatus**  
_opsiyonel_



 | 

Ek Tüketim Durumu



 | 

[LookupDTO](#_lookupdto)



 |
| 

**consumptionPointId**  
_opsiyonel_



 | 

Ölçüm Noktası ID



 | 

integer (int64)



 |
| 

**eic**  
_opsiyonel_



 | 

EIC Kod



 | 

string



 |
| 

**energyType**  
_opsiyonel_



 | 

Enerji Türü



 | 

[LookupDTO](#_lookupdto)



 |
| 

**firstReadDate**  
_opsiyonel_



 | 

Ek Tüketim Başlangıç Tarihi



 | 

string (date-time)



 |
| 

**id**  
_opsiyonel_



 | 

Ek Tüketim ID



 | 

integer (int64)



 |
| 

**lastReadDate**  
_opsiyonel_



 | 

Ek Tüketim Bitiş Tarihi



 | 

string (date-time)



 |
| 

**meterOwnerOrganizationId**  
_opsiyonel_



 | 

Organizasyon ID



 | 

integer (int64)



 |
| 

**readingOrganizationId**  
_opsiyonel_



 | 

Sayaç Okuyan Kurum ID



 | 

integer (int64)



 |

### 6.6. BaseDTO

_Tip_ : object

### 6.7. CountResponseDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**count**  
_opsiyonel_



 | 

Kayıt Sayısı



 | 

integer (int64)



 |

 
| İsim | Şema |
| --- | --- |
| 
**items**  
_opsiyonel_



 | 

< object > array



 |
| 

**page**  
_opsiyonel_



 | 

[Page](#_page)



 |

 
| İsim | Şema |
| --- | --- |
| 
**items**  
_opsiyonel_



 | 

< [IndexQueryResponseDto](#_indexqueryresponsedto) > array



 |
| 

**page**  
_opsiyonel_



 | 

[Page](#_page)



 |

### 6.10. IndexBatchSummaryDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**consumptionPointId**  
_opsiyonel_



 | 

Ölçüm Noktası ID



 | 

integer (int64)



 |
| 

**energyType**  
_opsiyonel_



 | 

Enerji Türü



 | 

integer (int64)



 |
| 

**errorMessage**  
_opsiyonel_



 | 

Hata Mesajı



 | 

string



 |
| 

**explanation**  
_opsiyonel_



 | 

Açıklama



 | 

string



 |
| 

**firstReadDate**  
_opsiyonel_



 | 

İlk Okuma Tarihi



 | 

string (date-time)



 |
| 

**indexId**  
_opsiyonel_



 | 

Endeks ID



 | 

integer (int64)



 |
| 

**isSuccessful**  
_opsiyonel_



 | 

Kayıt Başarılı mı?



 | 

boolean



 |
| 

**lastReadDate**  
_opsiyonel_



 | 

Son Okuma Tarihi



 | 

string (date-time)



 |

### 6.11. IndexCountRequestDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**consumptionPointId**  
_opsiyonel_



 | 

Ölçüm Noktası ID



 | 

integer (int64)



 |
| 

**createDateEndAsPeriod**  
_opsiyonel_



 | 

İşlem Tarihi - Bitiş



 | 

string (date-time)



 |
| 

**createDateStartAsPeriod**  
_opsiyonel_



 | 

İşlem Tarihi - Başlangıç



 | 

string (date-time)



 |
| 

**eic**  
_opsiyonel_



 | 

EIC Kod



 | 

string



 |
| 

**energyTypes**  
_opsiyonel_



 | 

Enerji Türü



 | 

< integer (int64) > array



 |
| 

**firstReadDateAsPeriod**  
_opsiyonel_



 | 

Dönem - İlk Okuma



 | 

string (date-time)



 |
| 

**firstReadTypes**  
_opsiyonel_



 | 

İlk Okuma Türü



 | 

< integer (int64) > array



 |
| 

**id**  
_opsiyonel_



 | 

ID (Migrasyon öncesi eşleme)



 | 

integer (int64)



 |
| 

**indexId**  
_opsiyonel_



 | 

Endeks ID



 | 

integer (int64)



 |
| 

**indexStatuses**  
_opsiyonel_



 | 

Endeks Durum



 | 

< integer (int64) > array



 |
| 

**lastReadDateAsPeriod**  
_opsiyonel_



 | 

Dönem - Son Okuma



 | 

string (date-time)



 |
| 

**lastReadTypes**  
_opsiyonel_



 | 

Son Okuma Türü



 | 

< integer (int64) > array



 |
| 

**meterOwnerOrganizationId**  
_opsiyonel_



 | 

Organizasyon ID



 | 

integer (int64)



 |
| 

**periodSwitch**  
_opsiyonel_



 | 

Okuma Periyodu



 | 

boolean



 |
| 

**portfolioType**  
_opsiyonel_



 | 

Portföy Tipi



 | 

integer (int64)



 |
| 

**readingOrganizationId**  
_opsiyonel_



 | 

Sayaç Okuyan Kurum ID



 | 

integer (int64)



 |

### 6.12. IndexExportRequestDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**consumptionPointId**  
_opsiyonel_



 | 

Ölçüm Noktası ID



 | 

integer (int64)



 |
| 

**createDateEndAsPeriod**  
_opsiyonel_



 | 

İşlem Tarihi - Bitiş



 | 

string (date-time)



 |
| 

**createDateStartAsPeriod**  
_opsiyonel_



 | 

İşlem Tarihi - Başlangıç



 | 

string (date-time)



 |
| 

**eic**  
_opsiyonel_



 | 

EIC Kod



 | 

string



 |
| 

**energyTypes**  
_opsiyonel_



 | 

Enerji Türü



 | 

< integer (int64) > array



 |
| 

**firstReadDateAsPeriod**  
_opsiyonel_



 | 

Dönem - İlk Okuma



 | 

string (date-time)



 |
| 

**firstReadTypes**  
_opsiyonel_



 | 

İlk Okuma Türü



 | 

< integer (int64) > array



 |
| 

**id**  
_opsiyonel_



 | 

ID (Migrasyon öncesi eşleme)



 | 

integer (int64)



 |
| 

**indexId**  
_opsiyonel_



 | 

Endeks ID



 | 

integer (int64)



 |
| 

**indexStatuses**  
_opsiyonel_



 | 

Endeks Durum



 | 

< integer (int64) > array



 |
| 

**lastReadDateAsPeriod**  
_opsiyonel_



 | 

Dönem - Son Okuma



 | 

string (date-time)



 |
| 

**lastReadTypes**  
_opsiyonel_



 | 

Son Okuma Türü



 | 

< integer (int64) > array



 |
| 

**meterOwnerOrganizationId**  
_opsiyonel_



 | 

Organizasyon ID



 | 

integer (int64)



 |
| 

**page**  
_opsiyonel_



 | 

Sorgulama Sayfası



 | 

[Page](#_page)



 |
| 

**periodSwitch**  
_opsiyonel_



 | 

Okuma Periyodu



 | 

boolean



 |
| 

**portfolioType**  
_opsiyonel_



 | 

Portföy Tipi



 | 

integer (int64)



 |
| 

**readingOrganizationId**  
_opsiyonel_



 | 

Sayaç Okuyan Kurum ID



 | 

integer (int64)



 |

### 6.13. IndexPassivateRequestDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**explanation**  
_gerekli_



 | 

Açıklama



 | 

string



 |
| 

**indexId**  
_gerekli_



 | 

Endeks ID



 | 

integer (int64)



 |

### 6.14. IndexQueryRequestDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**consumptionPointId**  
_opsiyonel_



 | 

Ölçüm Noktası ID



 | 

integer (int64)



 |
| 

**createDateEndAsPeriod**  
_opsiyonel_



 | 

İşlem Tarihi - Bitiş



 | 

string (date-time)



 |
| 

**createDateStartAsPeriod**  
_opsiyonel_



 | 

İşlem Tarihi - Başlangıç



 | 

string (date-time)



 |
| 

**eic**  
_opsiyonel_



 | 

EIC Kod



 | 

string



 |
| 

**energyTypes**  
_opsiyonel_



 | 

Enerji Türü



 | 

< integer (int64) > array



 |
| 

**firstReadDateAsPeriod**  
_opsiyonel_



 | 

Dönem - İlk Okuma



 | 

string (date-time)



 |
| 

**firstReadTypes**  
_opsiyonel_



 | 

İlk Okuma Türü



 | 

< integer (int64) > array



 |
| 

**id**  
_opsiyonel_



 | 

ID (Migrasyon öncesi eşleme)



 | 

integer (int64)



 |
| 

**indexId**  
_opsiyonel_



 | 

Endeks ID



 | 

integer (int64)



 |
| 

**indexStatuses**  
_opsiyonel_



 | 

Endeks Durum



 | 

< integer (int64) > array



 |
| 

**lastReadDateAsPeriod**  
_opsiyonel_



 | 

Dönem - Son Okuma



 | 

string (date-time)



 |
| 

**lastReadTypes**  
_opsiyonel_



 | 

Son Okuma Türü



 | 

< integer (int64) > array



 |
| 

**meterOwnerOrganizationId**  
_opsiyonel_



 | 

Organizasyon ID



 | 

integer (int64)



 |
| 

**page**  
_opsiyonel_



 | 

Sorgulama Sayfası



 | 

[Page](#_page)



 |
| 

**periodSwitch**  
_opsiyonel_



 | 

Okuma Periyodu



 | 

boolean



 |
| 

**portfolioType**  
_opsiyonel_



 | 

Portföy Tipi



 | 

integer (int64)



 |
| 

**readingOrganizationId**  
_opsiyonel_



 | 

Sayaç Okuyan Kurum ID



 | 

integer (int64)



 |

### 6.15. IndexQueryResponseDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**consumptionPointId**  
_opsiyonel_



 | 

Ölçüm Noktası ID



 | 

integer (int64)



 |
| 

**createDate**  
_opsiyonel_



 | 

İşlem Tarihi



 | 

string (date-time)



 |
| 

**createUser**  
_opsiyonel_



 | 

Kullanıcı Adı



 | 

string



 |
| 

**demand**  
_opsiyonel_



 | 

Demand



 | 

string



 |
| 

**digitCount**  
_opsiyonel_



 | 

Hane Sayısı



 | 

integer (int64)



 |
| 

**eic**  
_opsiyonel_



 | 

EIC Kod



 | 

string



 |
| 

**energyType**  
_opsiyonel_



 | 

Enerji Türü



 | 

[LookupDTO](#_lookupdto)



 |
| 

**explanation**  
_opsiyonel_



 | 

Açıklama



 | 

string



 |
| 

**factor**  
_opsiyonel_



 | 

Çarpan Değeri



 | 

number



 |
| 

**firstCapacitive**  
_opsiyonel_



 | 

RC İlk



 | 

string



 |
| 

**firstInductive**  
_opsiyonel_



 | 

RI İlk



 | 

string



 |
| 

**firstLoadType**  
_opsiyonel_



 | 

İlk Yükleme Türü



 | 

[LookupDTO](#_lookupdto)



 |
| 

**firstReactiveOrDemand**  
_opsiyonel_



 | 

Reaktif İlk / Demand



 | 

string



 |
| 

**firstReadDate**  
_opsiyonel_



 | 

İlk Okuma Tarihi



 | 

string (date-time)



 |
| 

**firstReadType**  
_opsiyonel_



 | 

İlk Okuma Türü



 | 

[LookupDTO](#_lookupdto)



 |
| 

**firstT1**  
_opsiyonel_



 | 

T1 İlk



 | 

string



 |
| 

**firstT2**  
_opsiyonel_



 | 

T2 İlk



 | 

string



 |
| 

**firstT3**  
_opsiyonel_



 | 

T3 İlk



 | 

string



 |
| 

**id**  
_opsiyonel_



 | 

ID (Migrasyon öncesi eşleme)



 | 

integer (int64)



 |
| 

**indexId**  
_opsiyonel_



 | 

Endeks ID



 | 

integer (int64)



 |
| 

**indexStatus**  
_opsiyonel_



 | 

Endeks Durum



 | 

[LookupDTO](#_lookupdto)



 |
| 

**lastCapacitive**  
_opsiyonel_



 | 

RC Son



 | 

string



 |
| 

**lastInductive**  
_opsiyonel_



 | 

RI Son



 | 

string



 |
| 

**lastLoadType**  
_opsiyonel_



 | 

Son Yükleme Türü



 | 

[LookupDTO](#_lookupdto)



 |
| 

**lastReactive**  
_opsiyonel_



 | 

Reaktif Son



 | 

string



 |
| 

**lastReadDate**  
_opsiyonel_



 | 

Son Okuma Tarihi



 | 

string (date-time)



 |
| 

**lastReadType**  
_opsiyonel_



 | 

Son Okuma Türü



 | 

[LookupDTO](#_lookupdto)



 |
| 

**lastT1**  
_opsiyonel_



 | 

T1 Son



 | 

string



 |
| 

**lastT2**  
_opsiyonel_



 | 

T2 Son



 | 

string



 |
| 

**lastT3**  
_opsiyonel_



 | 

T3 Son



 | 

string



 |
| 

**meterBrand**  
_opsiyonel_



 | 

Sayaç Marka



 | 

string



 |
| 

**meterOwnerOrganizationId**  
_opsiyonel_



 | 

Organizasyon ID



 | 

integer (int64)



 |
| 

**meterOwnerOrganizationName**  
_opsiyonel_



 | 

Organizasyon Adı



 | 

string



 |
| 

**meterSerialNumber**  
_opsiyonel_



 | 

Sayaç Seri No



 | 

string



 |
| 

**period**  
_opsiyonel_



 | 

Okuma Periyodu



 | 

integer (int64)



 |
| 

**periodExplanation**  
_opsiyonel_



 | 

Periyot Açıklama



 | 

[LookupDTO](#_lookupdto)



 |
| 

**portfolioType**  
_opsiyonel_



 | 

Portföy Tipi



 | 

[LookupDTO](#_lookupdto)



 |
| 

**readingOrganizationId**  
_opsiyonel_



 | 

Sayaç Okuyan Kurum ID



 | 

integer (int64)



 |
| 

**readingOrganizationName**  
_opsiyonel_



 | 

Sayaç Okuyan Kurum Adı



 | 

string



 |
| 

**uploadPeriod**  
_opsiyonel_



 | 

Yükleme Süresi



 | 

integer (int64)



 |
| 

**version**  
_opsiyonel_



 | 

Versiyon



 | 

integer (int64)



 |

### 6.16. IndexSaveRequestDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**consumptionPointId**  
_opsiyonel_



 | 

Ölçüm Noktası ID



 | 

integer (int64)



 |
| 

**demand**  
_opsiyonel_



 | 

Demand



 | 

number



 |
| 

**digitCount**  
_opsiyonel_



 | 

Hane Sayısı



 | 

integer (int64)



 |
| 

**eic**  
_opsiyonel_



 | 

EIC Kod



 | 

string



 |
| 

**energyType**  
_opsiyonel_



 | 

Enerji Türü



 | 

integer (int64)



 |
| 

**explanation**  
_opsiyonel_



 | 

Açıklama



 | 

string



 |
| 

**factor**  
_opsiyonel_



 | 

Çarpan Değeri



 | 

number



 |
| 

**firstCapacitive**  
_opsiyonel_



 | 

RC İlk



 | 

number



 |
| 

**firstInductive**  
_opsiyonel_



 | 

RI İlk



 | 

number



 |
| 

**firstLoadType**  
_opsiyonel_



 | 

İlk Yükleme Türü



 | 

integer (int64)



 |
| 

**firstReadDate**  
_opsiyonel_



 | 

İlk Okuma Tarihi



 | 

string (date-time)



 |
| 

**firstReadType**  
_opsiyonel_



 | 

İlk Okuma Türü



 | 

integer (int64)



 |
| 

**firstT1**  
_opsiyonel_



 | 

T1 İlk



 | 

number



 |
| 

**firstT2**  
_opsiyonel_



 | 

T2 İlk



 | 

number



 |
| 

**firstT3**  
_opsiyonel_



 | 

T3 İlk



 | 

number



 |
| 

**lastCapacitive**  
_opsiyonel_



 | 

RC Son



 | 

number



 |
| 

**lastInductive**  
_opsiyonel_



 | 

RI Son



 | 

number



 |
| 

**lastLoadType**  
_opsiyonel_



 | 

Son Yükleme Türü



 | 

integer (int64)



 |
| 

**lastReadDate**  
_opsiyonel_



 | 

Son Okuma Tarihi



 | 

string (date-time)



 |
| 

**lastReadType**  
_opsiyonel_



 | 

Son Okuma Türü



 | 

integer (int64)



 |
| 

**lastT1**  
_opsiyonel_



 | 

T1 Son



 | 

number



 |
| 

**lastT2**  
_opsiyonel_



 | 

T2 Son



 | 

number



 |
| 

**lastT3**  
_opsiyonel_



 | 

T3 Son



 | 

number



 |
| 

**meterBrand**  
_opsiyonel_



 | 

Sayaç Marka



 | 

string



 |
| 

**meterSerialNumber**  
_opsiyonel_



 | 

Sayaç Seri No



 | 

string



 |
| 

**overrideFullOverlap**  
_opsiyonel_



 | 

Tam Çakışma Kaydetme



 | 

boolean



 |
| 

**periodExplanation**  
_opsiyonel_



 | 

Periyot Açıklama



 | 

integer (int64)



 |
| 

**readingOrganizationId**  
_opsiyonel_



 | 

Sayaç Okuyan Kurum ID



 | 

integer (int64)



 |

### 6.17. IndexSummaryDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**consumptionPointId**  
_opsiyonel_



 | 

Ölçüm Noktası ID



 | 

integer (int64)



 |
| 

**eic**  
_opsiyonel_



 | 

EIC Kod



 | 

string



 |
| 

**energyType**  
_opsiyonel_



 | 

Enerji Türü



 | 

[LookupDTO](#_lookupdto)



 |
| 

**explanation**  
_opsiyonel_



 | 

Açıklama



 | 

string



 |
| 

**firstReadDate**  
_opsiyonel_



 | 

İlk Okuma Tarihi



 | 

string (date-time)



 |
| 

**fullOverrideExist**  
_opsiyonel_



 | 

Tam Çakışma Mevcut



 | 

boolean



 |
| 

**indexId**  
_opsiyonel_



 | 

Endeks ID



 | 

integer (int64)



 |
| 

**indexStatus**  
_opsiyonel_



 | 

Endeks Durum



 | 

[LookupDTO](#_lookupdto)



 |
| 

**lastReadDate**  
_opsiyonel_



 | 

Son Okuma Tarihi



 | 

string (date-time)



 |
| 

**meterOwnerOrganizationId**  
_opsiyonel_



 | 

Organizasyon ID



 | 

integer (int64)



 |
| 

**readingOrganizationId**  
_opsiyonel_



 | 

Sayaç Okuyan Kurum ID



 | 

integer (int64)



 |
| 

**version**  
_opsiyonel_



 | 

Versiyon



 | 

integer (int64)



 |

### 6.18. IndexUpdateRequestDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**demand**  
_opsiyonel_



 | 

Demand



 | 

number



 |
| 

**digitCount**  
_opsiyonel_



 | 

Hane Sayısı



 | 

integer (int64)



 |
| 

**explanation**  
_opsiyonel_



 | 

Açıklama



 | 

string



 |
| 

**factor**  
_opsiyonel_



 | 

Çarpan Değeri



 | 

number



 |
| 

**firstCapacitive**  
_opsiyonel_



 | 

RC İlk



 | 

number



 |
| 

**firstInductive**  
_opsiyonel_



 | 

RI İlk



 | 

number



 |
| 

**firstLoadType**  
_opsiyonel_



 | 

İlk Yükleme Türü



 | 

integer (int64)



 |
| 

**firstReadType**  
_opsiyonel_



 | 

İlk Okuma Türü



 | 

integer (int64)



 |
| 

**firstT1**  
_opsiyonel_



 | 

T1 İlk



 | 

number



 |
| 

**firstT2**  
_opsiyonel_



 | 

T2 İlk



 | 

number



 |
| 

**firstT3**  
_opsiyonel_



 | 

T3 İlk



 | 

number



 |
| 

**indexId**  
_opsiyonel_



 | 

Endeks ID



 | 

integer (int64)



 |
| 

**lastCapacitive**  
_opsiyonel_



 | 

RC Son



 | 

number



 |
| 

**lastInductive**  
_opsiyonel_



 | 

RI Son



 | 

number



 |
| 

**lastLoadType**  
_opsiyonel_



 | 

Son Yükleme Türü



 | 

integer (int64)



 |
| 

**lastReadType**  
_opsiyonel_



 | 

Son Okuma Türü



 | 

integer (int64)



 |
| 

**lastT1**  
_opsiyonel_



 | 

T1 Son



 | 

number



 |
| 

**lastT2**  
_opsiyonel_



 | 

T2 Son



 | 

number



 |
| 

**lastT3**  
_opsiyonel_



 | 

T3 Son



 | 

number



 |
| 

**meterBrand**  
_opsiyonel_



 | 

Sayaç Marka



 | 

string



 |
| 

**meterSerialNumber**  
_opsiyonel_



 | 

Sayaç Seri No



 | 

string



 |
| 

**periodExplanation**  
_opsiyonel_



 | 

Periyot Açıklama



 | 

integer (int64)



 |

### 6.19. LocalizationDTO

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**language**  
_opsiyonel_



 | 

Çoklu Seçim Dili



 | 

string



 |
| 

**text**  
_opsiyonel_



 | 

Çoklu Seçim Açıklama (Dile Göre)



 | 

string



 |

### 6.20. LookupDTO

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**id**  
_opsiyonel_



 | 

Çoklu Seçim ID



 | 

integer (int64)



 |
| 

**localizations**  
_opsiyonel_



 | 

Çoklu Seçim Yerelleştirme Listesi



 | 

< [LocalizationDTO](#_localizationdto) > array



 |
| 

**value**  
_opsiyonel_



 | 

Çoklu Seçim Değer



 | 

string



 |

### 6.21. LookupRequest

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**lookupType**  
_gerekli_



 | 

Çoklu Seçim Anahtarı



 | 

string



 |

### 6.22. LookupResponse

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**values**  
_opsiyonel_



 | 

Çoklu Seçim Değer Listesi



 | 

< [LookupDTO](#_lookupdto) > array



 |

### 6.23. LookupTypeDTO

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**lookupDescription**  
_opsiyonel_



 | 

Çoklu Seçim Anahtar Açıklama



 | 

string



 |
| 

**lookupType**  
_opsiyonel_



 | 

Çoklu Seçim Anahtarı



 | 

string



 |

### 6.24. LookupTypeResponse

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**types**  
_opsiyonel_



 | 

Çoklu Seçim Anahtar Listesi



 | 

< [LookupTypeDTO](#_lookuptypedto) > array



 |

### 6.25. Page

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**number**  
_opsiyonel_



 | 

${VALUE\_PAGE\_NUMBER}  
**Örnek** : `"${EXAMPLE_PAGE_NUMBER}"`



 | 

integer (int64)



 |
| 

**size**  
_opsiyonel_



 | 

${VALUE\_PAGE\_SIZE}  
**Örnek** : `"${EXAMPLE_PAGE_SIZE}"`



 | 

integer (int64)



 |
| 

**sort**  
_opsiyonel_



 | 

${VALUE\_PAGE\_SORT}



 | 

[SortDTO](#_sortdto)



 |
| 

**total**  
_opsiyonel_



 | 

${VALUE\_PAGE\_TOTAL}  
**Örnek** : `"${EXAMPLE_PAGE_TOTAL}"`



 | 

integer (int64)



 |

### 6.26. ReadObligationDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**effectiveId**  
_opsiyonel_



 | 

Sayaç ID



 | 

integer (int64)



 |
| 

**eic**  
_opsiyonel_



 | 

EIC Kod



 | 

string



 |
| 

**indexAcData**  
_opsiyonel_



 | 

Endeks / Ek Tüketim Verisi



 | 

boolean



 |
| 

**meterId**  
_opsiyonel_



 | 

Sayaç ID



 | 

integer (int64)



 |
| 

**organizationId**  
_opsiyonel_



 | 

Tedarikçi Organizasyon ID



 | 

integer (int64)



 |
| 

**organizationName**  
_opsiyonel_



 | 

Tedarikçi Organizasyon Adı



 | 

string



 |
| 

**period**  
_opsiyonel_



 | 

Dönem



 | 

string (date-time)



 |
| 

**readingOrganizationId**  
_opsiyonel_



 | 

Sayaç Okuyan Kurum ID



 | 

integer (int64)



 |
| 

**readingOrganizationName**  
_opsiyonel_



 | 

Sayaç Okuyan Kurum Adı



 | 

string



 |
| 

**reconciliationData**  
_opsiyonel_



 | 

Uzlaştırma Verisi



 | 

boolean



 |
| 

**uniqueCode**  
_opsiyonel_



 | 

Tekil Kod



 | 

string



 |

### 6.27. ReadObligationQueryRequestDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**effectiveId**  
_opsiyonel_



 | 

Sayaç ID



 | 

integer (int64)



 |
| 

**eic**  
_opsiyonel_



 | 

EIC Kod



 | 

string



 |
| 

**excludeHighReadPeriod**  
_opsiyonel_



 | 

Yüksek Okuma Periyotlular Hariç



 | 

boolean



 |
| 

**organizationId**  
_opsiyonel_



 | 

Tedarikçi Organizasyon ID



 | 

integer (int64)



 |
| 

**page**  
_opsiyonel_



 |  | 

[Page](#_page)



 |
| 

**period**  
_opsiyonel_



 | 

Dönem



 | 

string (date-time)



 |
| 

**readingOrganizationId**  
_opsiyonel_



 | 

Sayaç Okuyan Kurum ID



 | 

integer (int64)



 |
| 

**uniqueCode**  
_opsiyonel_



 | 

Tekil Kod



 | 

string



 |

### 6.28. RestResponse

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**body**  
_opsiyonel_



 | 

Yapılan istek başarılı olması durumunda çağırılan servisin cevabıdır. İstekler başarısız ise bu alan boş gelecektir.



 | 

[RestResponseBodyObject](#_restresponsebodyobject)



 |
| 

**clientIp**  
_opsiyonel_



 | 

İsteği yapan istemcinin IP bilgisi



 | 

string



 |
| 

**correlationId**  
_opsiyonel_



 | 

Yapmış olduğunuz isteği tekilleştirmeye yarar. Hata almanız durumunda bu bilgiyi göndermeniz zorunludur.



 | 

string



 |
| 

**dispatch**  
_opsiyonel_



 |  | 

string



 |
| 

**errors**  
_opsiyonel_



 | 

Başarılı durumda liste _boş_ dönmektedir. Hata almanız durumunda liste içinde aldığınız hatanın hata kodu ve hata mesajlarını dönmektedir. Hatalar ile ilgili detaylı bilgi almak isterseniz bu değerleri göndermeniz gerekmektedir.



 | 

< [RestResponseError](#_restresponseerror) > array



 |
| 

**hostName**  
_opsiyonel_



 |  | 

string



 |
| 

**spanIds**  
_opsiyonel_



 |  | 

string



 |
| 

**status**  
_opsiyonel_



 | 

Yapılan isteğin HTTP durum kodunu dönmektedir.



 | 

string



 |
| 

**successMessage**  
_opsiyonel_



 |  | 

string



 |
| 

**unsuccessfulList**  
_opsiyonel_



 | 

Yapılan istekte hatalı olan ve sisteme kaydedilmeyen kayıtların listesini dönmektedir.



 | 

< [BaseDTO](#_basedto) > array



 |
| 

**userName**  
_opsiyonel_



 | 

İsteği yapan kullanıcı bilgisi



 | 

string



 |

### 6.29. RestResponseAdditionalConsumptionSummaryDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**body**  
_opsiyonel_



 | 

Yapılan istek başarılı olması durumunda çağırılan servisin cevabıdır. İstekler başarısız ise bu alan boş gelecektir.



 | 

[RestResponseBodyAdditionalConsumptionSummaryDto](#_restresponsebodyadditionalconsumptionsummarydto)



 |
| 

**clientIp**  
_opsiyonel_



 | 

İsteği yapan istemcinin IP bilgisi



 | 

string



 |
| 

**correlationId**  
_opsiyonel_



 | 

Yapmış olduğunuz isteği tekilleştirmeye yarar. Hata almanız durumunda bu bilgiyi göndermeniz zorunludur.



 | 

string



 |
| 

**dispatch**  
_opsiyonel_



 |  | 

string



 |
| 

**errors**  
_opsiyonel_



 | 

Başarılı durumda liste _boş_ dönmektedir. Hata almanız durumunda liste içinde aldığınız hatanın hata kodu ve hata mesajlarını dönmektedir. Hatalar ile ilgili detaylı bilgi almak isterseniz bu değerleri göndermeniz gerekmektedir.



 | 

< [RestResponseError](#_restresponseerror) > array



 |
| 

**hostName**  
_opsiyonel_



 |  | 

string



 |
| 

**spanIds**  
_opsiyonel_



 |  | 

string



 |
| 

**status**  
_opsiyonel_



 | 

Yapılan isteğin HTTP durum kodunu dönmektedir.



 | 

string



 |
| 

**successMessage**  
_opsiyonel_



 |  | 

string



 |
| 

**unsuccessfulList**  
_opsiyonel_



 | 

Yapılan istekte hatalı olan ve sisteme kaydedilmeyen kayıtların listesini dönmektedir.



 | 

< [BaseDTO](#_basedto) > array



 |
| 

**userName**  
_opsiyonel_



 | 

İsteği yapan kullanıcı bilgisi



 | 

string



 |

### 6.30. RestResponseBody

 
| İsim | Şema |
| --- | --- |
| 
**content**  
_opsiyonel_  
_sadece okuma_



 | 

object



 |

### 6.31. RestResponseBodyAdditionalConsumptionSummaryDto

 
| İsim | Şema |
| --- | --- |
| 
**content**  
_opsiyonel_  
_sadece okuma_



 | 

[AdditionalConsumptionSummaryDto](#_additionalconsumptionsummarydto)



 |

### 6.32. RestResponseBodyCountResponseDto

 
| İsim | Şema |
| --- | --- |
| 
**content**  
_opsiyonel_  
_sadece okuma_



 | 

[CountResponseDto](#_countresponsedto)



 |

### 6.33. RestResponseBodyExportPageResponseIndexQueryResponseDto

 
| İsim | Şema |
| --- | --- |
| 
**content**  
_opsiyonel_  
_sadece okuma_



 | 

[ExportPageResponseIndexQueryResponseDto](#_exportpageresponseindexqueryresponsedto)



 |

### 6.34. RestResponseBodyIndexBatchSummaryDto

 
| İsim | Şema |
| --- | --- |
| 
**content**  
_opsiyonel_  
_sadece okuma_



 | 

[IndexBatchSummaryDto](#_indexbatchsummarydto)



 |

### 6.35. RestResponseBodyIndexSummaryDto

 
| İsim | Şema |
| --- | --- |
| 
**content**  
_opsiyonel_  
_sadece okuma_



 | 

[IndexSummaryDto](#_indexsummarydto)



 |

### 6.36. RestResponseBodyLookupResponse

 
| İsim | Şema |
| --- | --- |
| 
**content**  
_opsiyonel_  
_sadece okuma_



 | 

[LookupResponse](#_lookupresponse)



 |

### 6.37. RestResponseBodyLookupTypeResponse

 
| İsim | Şema |
| --- | --- |
| 
**content**  
_opsiyonel_  
_sadece okuma_



 | 

[LookupTypeResponse](#_lookuptyperesponse)



 |

### 6.38. RestResponseBodyObject

 
| İsim | Şema |
| --- | --- |
| 
**content**  
_opsiyonel_  
_sadece okuma_



 | 

object



 |

### 6.39. RestResponseBodySortablePageResponseAdditionalConsumptionQueryResponseDto

 
| İsim | Şema |
| --- | --- |
| 
**content**  
_opsiyonel_  
_sadece okuma_



 | 

[SortablePageResponseAdditionalConsumptionQueryResponseDto](#_sortablepageresponseadditionalconsumptionqueryresponsedto)



 |

### 6.40. RestResponseBodySortablePageResponseIndexQueryResponseDto

 
| İsim | Şema |
| --- | --- |
| 
**content**  
_opsiyonel_  
_sadece okuma_



 | 

[SortablePageResponseIndexQueryResponseDto](#_sortablepageresponseindexqueryresponsedto)



 |

### 6.41. RestResponseBodySortablePageResponseReadObligationDto

 
| İsim | Şema |
| --- | --- |
| 
**content**  
_opsiyonel_  
_sadece okuma_



 | 

[SortablePageResponseReadObligationDto](#_sortablepageresponsereadobligationdto)



 |

### 6.42. RestResponseBodySummaryReportQueryResponseDto

 
| İsim | Şema |
| --- | --- |
| 
**content**  
_opsiyonel_  
_sadece okuma_



 | 

[SummaryReportQueryResponseDto](#_summaryreportqueryresponsedto)



 |

### 6.43. RestResponseCountResponseDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**body**  
_opsiyonel_



 | 

Yapılan istek başarılı olması durumunda çağırılan servisin cevabıdır. İstekler başarısız ise bu alan boş gelecektir.



 | 

[RestResponseBodyCountResponseDto](#_restresponsebodycountresponsedto)



 |
| 

**clientIp**  
_opsiyonel_



 | 

İsteği yapan istemcinin IP bilgisi



 | 

string



 |
| 

**correlationId**  
_opsiyonel_



 | 

Yapmış olduğunuz isteği tekilleştirmeye yarar. Hata almanız durumunda bu bilgiyi göndermeniz zorunludur.



 | 

string



 |
| 

**dispatch**  
_opsiyonel_



 |  | 

string



 |
| 

**errors**  
_opsiyonel_



 | 

Başarılı durumda liste _boş_ dönmektedir. Hata almanız durumunda liste içinde aldığınız hatanın hata kodu ve hata mesajlarını dönmektedir. Hatalar ile ilgili detaylı bilgi almak isterseniz bu değerleri göndermeniz gerekmektedir.



 | 

< [RestResponseError](#_restresponseerror) > array



 |
| 

**hostName**  
_opsiyonel_



 |  | 

string



 |
| 

**spanIds**  
_opsiyonel_



 |  | 

string



 |
| 

**status**  
_opsiyonel_



 | 

Yapılan isteğin HTTP durum kodunu dönmektedir.



 | 

string



 |
| 

**successMessage**  
_opsiyonel_



 |  | 

string



 |
| 

**unsuccessfulList**  
_opsiyonel_



 | 

Yapılan istekte hatalı olan ve sisteme kaydedilmeyen kayıtların listesini dönmektedir.



 | 

< [BaseDTO](#_basedto) > array



 |
| 

**userName**  
_opsiyonel_



 | 

İsteği yapan kullanıcı bilgisi



 | 

string



 |

### 6.44. RestResponseError

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**errorCode**  
_opsiyonel_



 | 

Alınan hatanın kod bilgisi



 | 

string



 |
| 

**errorMessage**  
_opsiyonel_



 | 

Alınan hatanın açıklaması



 | 

string



 |

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**body**  
_opsiyonel_



 | 

Yapılan istek başarılı olması durumunda çağırılan servisin cevabıdır. İstekler başarısız ise bu alan boş gelecektir.



 | 

[RestResponseBodyExportPageResponseIndexQueryResponseDto](#_restresponsebodyexportpageresponseindexqueryresponsedto)



 |
| 

**clientIp**  
_opsiyonel_



 | 

İsteği yapan istemcinin IP bilgisi



 | 

string



 |
| 

**correlationId**  
_opsiyonel_



 | 

Yapmış olduğunuz isteği tekilleştirmeye yarar. Hata almanız durumunda bu bilgiyi göndermeniz zorunludur.



 | 

string



 |
| 

**dispatch**  
_opsiyonel_



 |  | 

string



 |
| 

**errors**  
_opsiyonel_



 | 

Başarılı durumda liste _boş_ dönmektedir. Hata almanız durumunda liste içinde aldığınız hatanın hata kodu ve hata mesajlarını dönmektedir. Hatalar ile ilgili detaylı bilgi almak isterseniz bu değerleri göndermeniz gerekmektedir.



 | 

< [RestResponseError](#_restresponseerror) > array



 |
| 

**hostName**  
_opsiyonel_



 |  | 

string



 |
| 

**spanIds**  
_opsiyonel_



 |  | 

string



 |
| 

**status**  
_opsiyonel_



 | 

Yapılan isteğin HTTP durum kodunu dönmektedir.



 | 

string



 |
| 

**successMessage**  
_opsiyonel_



 |  | 

string



 |
| 

**unsuccessfulList**  
_opsiyonel_



 | 

Yapılan istekte hatalı olan ve sisteme kaydedilmeyen kayıtların listesini dönmektedir.



 | 

< [BaseDTO](#_basedto) > array



 |
| 

**userName**  
_opsiyonel_



 | 

İsteği yapan kullanıcı bilgisi



 | 

string



 |

### 6.46. RestResponseIndexBatchSummaryDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**body**  
_opsiyonel_



 | 

Yapılan istek başarılı olması durumunda çağırılan servisin cevabıdır. İstekler başarısız ise bu alan boş gelecektir.



 | 

[RestResponseBodyIndexBatchSummaryDto](#_restresponsebodyindexbatchsummarydto)



 |
| 

**clientIp**  
_opsiyonel_



 | 

İsteği yapan istemcinin IP bilgisi



 | 

string



 |
| 

**correlationId**  
_opsiyonel_



 | 

Yapmış olduğunuz isteği tekilleştirmeye yarar. Hata almanız durumunda bu bilgiyi göndermeniz zorunludur.



 | 

string



 |
| 

**dispatch**  
_opsiyonel_



 |  | 

string



 |
| 

**errors**  
_opsiyonel_



 | 

Başarılı durumda liste _boş_ dönmektedir. Hata almanız durumunda liste içinde aldığınız hatanın hata kodu ve hata mesajlarını dönmektedir. Hatalar ile ilgili detaylı bilgi almak isterseniz bu değerleri göndermeniz gerekmektedir.



 | 

< [RestResponseError](#_restresponseerror) > array



 |
| 

**hostName**  
_opsiyonel_



 |  | 

string



 |
| 

**spanIds**  
_opsiyonel_



 |  | 

string



 |
| 

**status**  
_opsiyonel_



 | 

Yapılan isteğin HTTP durum kodunu dönmektedir.



 | 

string



 |
| 

**successMessage**  
_opsiyonel_



 |  | 

string



 |
| 

**unsuccessfulList**  
_opsiyonel_



 | 

Yapılan istekte hatalı olan ve sisteme kaydedilmeyen kayıtların listesini dönmektedir.



 | 

< [BaseDTO](#_basedto) > array



 |
| 

**userName**  
_opsiyonel_



 | 

İsteği yapan kullanıcı bilgisi



 | 

string



 |

### 6.47. RestResponseIndexSummaryDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**body**  
_opsiyonel_



 | 

Yapılan istek başarılı olması durumunda çağırılan servisin cevabıdır. İstekler başarısız ise bu alan boş gelecektir.



 | 

[RestResponseBodyIndexSummaryDto](#_restresponsebodyindexsummarydto)



 |
| 

**clientIp**  
_opsiyonel_



 | 

İsteği yapan istemcinin IP bilgisi



 | 

string



 |
| 

**correlationId**  
_opsiyonel_



 | 

Yapmış olduğunuz isteği tekilleştirmeye yarar. Hata almanız durumunda bu bilgiyi göndermeniz zorunludur.



 | 

string



 |
| 

**dispatch**  
_opsiyonel_



 |  | 

string



 |
| 

**errors**  
_opsiyonel_



 | 

Başarılı durumda liste _boş_ dönmektedir. Hata almanız durumunda liste içinde aldığınız hatanın hata kodu ve hata mesajlarını dönmektedir. Hatalar ile ilgili detaylı bilgi almak isterseniz bu değerleri göndermeniz gerekmektedir.



 | 

< [RestResponseError](#_restresponseerror) > array



 |
| 

**hostName**  
_opsiyonel_



 |  | 

string



 |
| 

**spanIds**  
_opsiyonel_



 |  | 

string



 |
| 

**status**  
_opsiyonel_



 | 

Yapılan isteğin HTTP durum kodunu dönmektedir.



 | 

string



 |
| 

**successMessage**  
_opsiyonel_



 |  | 

string



 |
| 

**unsuccessfulList**  
_opsiyonel_



 | 

Yapılan istekte hatalı olan ve sisteme kaydedilmeyen kayıtların listesini dönmektedir.



 | 

< [BaseDTO](#_basedto) > array



 |
| 

**userName**  
_opsiyonel_



 | 

İsteği yapan kullanıcı bilgisi



 | 

string



 |

### 6.48. RestResponseLookupResponse

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**body**  
_opsiyonel_



 | 

Yapılan istek başarılı olması durumunda çağırılan servisin cevabıdır. İstekler başarısız ise bu alan boş gelecektir.



 | 

[RestResponseBodyLookupResponse](#_restresponsebodylookupresponse)



 |
| 

**clientIp**  
_opsiyonel_



 | 

İsteği yapan istemcinin IP bilgisi



 | 

string



 |
| 

**correlationId**  
_opsiyonel_



 | 

Yapmış olduğunuz isteği tekilleştirmeye yarar. Hata almanız durumunda bu bilgiyi göndermeniz zorunludur.



 | 

string



 |
| 

**dispatch**  
_opsiyonel_



 |  | 

string



 |
| 

**errors**  
_opsiyonel_



 | 

Başarılı durumda liste _boş_ dönmektedir. Hata almanız durumunda liste içinde aldığınız hatanın hata kodu ve hata mesajlarını dönmektedir. Hatalar ile ilgili detaylı bilgi almak isterseniz bu değerleri göndermeniz gerekmektedir.



 | 

< [RestResponseError](#_restresponseerror) > array



 |
| 

**hostName**  
_opsiyonel_



 |  | 

string



 |
| 

**spanIds**  
_opsiyonel_



 |  | 

string



 |
| 

**status**  
_opsiyonel_



 | 

Yapılan isteğin HTTP durum kodunu dönmektedir.



 | 

string



 |
| 

**successMessage**  
_opsiyonel_



 |  | 

string



 |
| 

**unsuccessfulList**  
_opsiyonel_



 | 

Yapılan istekte hatalı olan ve sisteme kaydedilmeyen kayıtların listesini dönmektedir.



 | 

< [BaseDTO](#_basedto) > array



 |
| 

**userName**  
_opsiyonel_



 | 

İsteği yapan kullanıcı bilgisi



 | 

string



 |

### 6.49. RestResponseLookupTypeResponse

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**body**  
_opsiyonel_



 | 

Yapılan istek başarılı olması durumunda çağırılan servisin cevabıdır. İstekler başarısız ise bu alan boş gelecektir.



 | 

[RestResponseBodyLookupTypeResponse](#_restresponsebodylookuptyperesponse)



 |
| 

**clientIp**  
_opsiyonel_



 | 

İsteği yapan istemcinin IP bilgisi



 | 

string



 |
| 

**correlationId**  
_opsiyonel_



 | 

Yapmış olduğunuz isteği tekilleştirmeye yarar. Hata almanız durumunda bu bilgiyi göndermeniz zorunludur.



 | 

string



 |
| 

**dispatch**  
_opsiyonel_



 |  | 

string



 |
| 

**errors**  
_opsiyonel_



 | 

Başarılı durumda liste _boş_ dönmektedir. Hata almanız durumunda liste içinde aldığınız hatanın hata kodu ve hata mesajlarını dönmektedir. Hatalar ile ilgili detaylı bilgi almak isterseniz bu değerleri göndermeniz gerekmektedir.



 | 

< [RestResponseError](#_restresponseerror) > array



 |
| 

**hostName**  
_opsiyonel_



 |  | 

string



 |
| 

**spanIds**  
_opsiyonel_



 |  | 

string



 |
| 

**status**  
_opsiyonel_



 | 

Yapılan isteğin HTTP durum kodunu dönmektedir.



 | 

string



 |
| 

**successMessage**  
_opsiyonel_



 |  | 

string



 |
| 

**unsuccessfulList**  
_opsiyonel_



 | 

Yapılan istekte hatalı olan ve sisteme kaydedilmeyen kayıtların listesini dönmektedir.



 | 

< [BaseDTO](#_basedto) > array



 |
| 

**userName**  
_opsiyonel_



 | 

İsteği yapan kullanıcı bilgisi



 | 

string



 |

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**body**  
_opsiyonel_



 | 

Yapılan istek başarılı olması durumunda çağırılan servisin cevabıdır. İstekler başarısız ise bu alan boş gelecektir.



 | 

[RestResponseBodySortablePageResponseAdditionalConsumptionQueryResponseDto](#_restresponsebodysortablepageresponseadditionalconsumptionqueryresponsedto)



 |
| 

**clientIp**  
_opsiyonel_



 | 

İsteği yapan istemcinin IP bilgisi



 | 

string



 |
| 

**correlationId**  
_opsiyonel_



 | 

Yapmış olduğunuz isteği tekilleştirmeye yarar. Hata almanız durumunda bu bilgiyi göndermeniz zorunludur.



 | 

string



 |
| 

**dispatch**  
_opsiyonel_



 |  | 

string



 |
| 

**errors**  
_opsiyonel_



 | 

Başarılı durumda liste _boş_ dönmektedir. Hata almanız durumunda liste içinde aldığınız hatanın hata kodu ve hata mesajlarını dönmektedir. Hatalar ile ilgili detaylı bilgi almak isterseniz bu değerleri göndermeniz gerekmektedir.



 | 

< [RestResponseError](#_restresponseerror) > array



 |
| 

**hostName**  
_opsiyonel_



 |  | 

string



 |
| 

**spanIds**  
_opsiyonel_



 |  | 

string



 |
| 

**status**  
_opsiyonel_



 | 

Yapılan isteğin HTTP durum kodunu dönmektedir.



 | 

string



 |
| 

**successMessage**  
_opsiyonel_



 |  | 

string



 |
| 

**unsuccessfulList**  
_opsiyonel_



 | 

Yapılan istekte hatalı olan ve sisteme kaydedilmeyen kayıtların listesini dönmektedir.



 | 

< [BaseDTO](#_basedto) > array



 |
| 

**userName**  
_opsiyonel_



 | 

İsteği yapan kullanıcı bilgisi



 | 

string



 |

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**body**  
_opsiyonel_



 | 

Yapılan istek başarılı olması durumunda çağırılan servisin cevabıdır. İstekler başarısız ise bu alan boş gelecektir.



 | 

[RestResponseBodySortablePageResponseIndexQueryResponseDto](#_restresponsebodysortablepageresponseindexqueryresponsedto)



 |
| 

**clientIp**  
_opsiyonel_



 | 

İsteği yapan istemcinin IP bilgisi



 | 

string



 |
| 

**correlationId**  
_opsiyonel_



 | 

Yapmış olduğunuz isteği tekilleştirmeye yarar. Hata almanız durumunda bu bilgiyi göndermeniz zorunludur.



 | 

string



 |
| 

**dispatch**  
_opsiyonel_



 |  | 

string



 |
| 

**errors**  
_opsiyonel_



 | 

Başarılı durumda liste _boş_ dönmektedir. Hata almanız durumunda liste içinde aldığınız hatanın hata kodu ve hata mesajlarını dönmektedir. Hatalar ile ilgili detaylı bilgi almak isterseniz bu değerleri göndermeniz gerekmektedir.



 | 

< [RestResponseError](#_restresponseerror) > array



 |
| 

**hostName**  
_opsiyonel_



 |  | 

string



 |
| 

**spanIds**  
_opsiyonel_



 |  | 

string



 |
| 

**status**  
_opsiyonel_



 | 

Yapılan isteğin HTTP durum kodunu dönmektedir.



 | 

string



 |
| 

**successMessage**  
_opsiyonel_



 |  | 

string



 |
| 

**unsuccessfulList**  
_opsiyonel_



 | 

Yapılan istekte hatalı olan ve sisteme kaydedilmeyen kayıtların listesini dönmektedir.



 | 

< [BaseDTO](#_basedto) > array



 |
| 

**userName**  
_opsiyonel_



 | 

İsteği yapan kullanıcı bilgisi



 | 

string



 |

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**body**  
_opsiyonel_



 | 

Yapılan istek başarılı olması durumunda çağırılan servisin cevabıdır. İstekler başarısız ise bu alan boş gelecektir.



 | 

[RestResponseBodySortablePageResponseReadObligationDto](#_restresponsebodysortablepageresponsereadobligationdto)



 |
| 

**clientIp**  
_opsiyonel_



 | 

İsteği yapan istemcinin IP bilgisi



 | 

string



 |
| 

**correlationId**  
_opsiyonel_



 | 

Yapmış olduğunuz isteği tekilleştirmeye yarar. Hata almanız durumunda bu bilgiyi göndermeniz zorunludur.



 | 

string



 |
| 

**dispatch**  
_opsiyonel_



 |  | 

string



 |
| 

**errors**  
_opsiyonel_



 | 

Başarılı durumda liste _boş_ dönmektedir. Hata almanız durumunda liste içinde aldığınız hatanın hata kodu ve hata mesajlarını dönmektedir. Hatalar ile ilgili detaylı bilgi almak isterseniz bu değerleri göndermeniz gerekmektedir.



 | 

< [RestResponseError](#_restresponseerror) > array



 |
| 

**hostName**  
_opsiyonel_



 |  | 

string



 |
| 

**spanIds**  
_opsiyonel_



 |  | 

string



 |
| 

**status**  
_opsiyonel_



 | 

Yapılan isteğin HTTP durum kodunu dönmektedir.



 | 

string



 |
| 

**successMessage**  
_opsiyonel_



 |  | 

string



 |
| 

**unsuccessfulList**  
_opsiyonel_



 | 

Yapılan istekte hatalı olan ve sisteme kaydedilmeyen kayıtların listesini dönmektedir.



 | 

< [BaseDTO](#_basedto) > array



 |
| 

**userName**  
_opsiyonel_



 | 

İsteği yapan kullanıcı bilgisi



 | 

string



 |

### 6.53. RestResponseSummaryReportQueryResponseDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**body**  
_opsiyonel_



 | 

Yapılan istek başarılı olması durumunda çağırılan servisin cevabıdır. İstekler başarısız ise bu alan boş gelecektir.



 | 

[RestResponseBodySummaryReportQueryResponseDto](#_restresponsebodysummaryreportqueryresponsedto)



 |
| 

**clientIp**  
_opsiyonel_



 | 

İsteği yapan istemcinin IP bilgisi



 | 

string



 |
| 

**correlationId**  
_opsiyonel_



 | 

Yapmış olduğunuz isteği tekilleştirmeye yarar. Hata almanız durumunda bu bilgiyi göndermeniz zorunludur.



 | 

string



 |
| 

**dispatch**  
_opsiyonel_



 |  | 

string



 |
| 

**errors**  
_opsiyonel_



 | 

Başarılı durumda liste _boş_ dönmektedir. Hata almanız durumunda liste içinde aldığınız hatanın hata kodu ve hata mesajlarını dönmektedir. Hatalar ile ilgili detaylı bilgi almak isterseniz bu değerleri göndermeniz gerekmektedir.



 | 

< [RestResponseError](#_restresponseerror) > array



 |
| 

**hostName**  
_opsiyonel_



 |  | 

string



 |
| 

**spanIds**  
_opsiyonel_



 |  | 

string



 |
| 

**status**  
_opsiyonel_



 | 

Yapılan isteğin HTTP durum kodunu dönmektedir.



 | 

string



 |
| 

**successMessage**  
_opsiyonel_



 |  | 

string



 |
| 

**unsuccessfulList**  
_opsiyonel_



 | 

Yapılan istekte hatalı olan ve sisteme kaydedilmeyen kayıtların listesini dönmektedir.



 | 

< [BaseDTO](#_basedto) > array



 |
| 

**userName**  
_opsiyonel_



 | 

İsteği yapan kullanıcı bilgisi



 | 

string



 |

### 6.54. SortDTO

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**direction**  
_opsiyonel_



 | 

${VALUE\_SORT\_DIRECTION}  
**Örnek** : `"ASC"`



 | 

enum (ASC, DESC)



 |
| 

**field**  
_opsiyonel_



 | 

${VALUE\_SORT\_FIELD}  
**Örnek** : `"${EXAMPLE_SORT_FIELD}"`



 | 

string



 |

 
| İsim | Şema |
| --- | --- |
| 
**items**  
_opsiyonel_



 | 

< object > array



 |
| 

**page**  
_opsiyonel_



 | 

[Page](#_page)



 |
| 

**sortableFields**  
_opsiyonel_



 | 

< string > array



 |

 
| İsim | Şema |
| --- | --- |
| 
**items**  
_opsiyonel_



 | 

< [AdditionalConsumptionQueryResponseDto](#_additionalconsumptionqueryresponsedto) > array



 |
| 

**page**  
_opsiyonel_



 | 

[Page](#_page)



 |
| 

**sortableFields**  
_opsiyonel_



 | 

< string > array



 |

 
| İsim | Şema |
| --- | --- |
| 
**items**  
_opsiyonel_



 | 

< [IndexQueryResponseDto](#_indexqueryresponsedto) > array



 |
| 

**page**  
_opsiyonel_



 | 

[Page](#_page)



 |
| 

**sortableFields**  
_opsiyonel_



 | 

< string > array



 |

 
| İsim | Şema |
| --- | --- |
| 
**items**  
_opsiyonel_



 | 

< [ReadObligationDto](#_readobligationdto) > array



 |
| 

**page**  
_opsiyonel_



 | 

[Page](#_page)



 |
| 

**sortableFields**  
_opsiyonel_



 | 

< string > array



 |

### 6.59. SummaryDurationReportDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**extremelyLate**  
_opsiyonel_



 | 

Çok Geç Yükleme



 | 

integer (int64)



 |
| 

**late**  
_opsiyonel_



 | 

Geç Yükleme



 | 

integer (int64)



 |
| 

**normal**  
_opsiyonel_



 | 

Zamanında Yükleme



 | 

integer (int64)



 |
| 

**total**  
_opsiyonel_



 | 

Toplam



 | 

integer (int64)



 |

### 6.60. SummaryReportQueryRequestDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**excludeHighReadPeriod**  
_opsiyonel_



 | 

Yüksek Okuma Periyotlular Hariç



 | 

boolean



 |
| 

**organizationId**  
_opsiyonel_



 | 

Organizasyon ID



 | 

integer (int64)



 |
| 

**period**  
_opsiyonel_



 | 

Dönem



 | 

string (date-time)



 |
| 

**readingOrganizationId**  
_opsiyonel_



 | 

Sayaç Okuyan Kurum ID



 | 

integer (int64)



 |

### 6.61. SummaryReportQueryResponseDto

 
| İsim | Şema |
| --- | --- |
| 
**durations**  
_opsiyonel_



 | 

[SummaryDurationReportDto](#_summarydurationreportdto)



 |
| 

**states**  
_opsiyonel_



 | 

[SummaryStateReportDto](#_summarystatereportdto)



 |

### 6.62. SummaryStateReportDto

  
| İsim | Açıklama | Şema |
| --- | --- | --- |
| 
**bothExisting**  
_opsiyonel_



 | 

Endeks ve Uzlaştırma Verisi Yüklenenler



 | 

integer (int64)



 |
| 

**bothNonExisting**  
_opsiyonel_



 | 

Endeks ve Uzlaştırma Verisi Yüklenmeyenler



 | 

integer (int64)



 |
| 

**onlyIndexAcExisting**  
_opsiyonel_



 | 

Sadece Endeks Verisi Yüklenenler



 | 

integer (int64)



 |
| 

**onlyReconciliationExisting**  
_opsiyonel_



 | 

Sadece Uzlaştırma Verisi Yüklenenler



 | 

integer (int64)



 |
| 

**total**  
_opsiyonel_



 | 

Toplam



 | 

integer (int64)



 |
| 

**totalIndexAcExisting**  
_opsiyonel_



 | 

Toplam Endeks Verisi Yüklenenler



 | 

integer (int64)



 |
| 

**totalIndexAcNonExisting**  
_opsiyonel_



 | 

Toplam Endeks Verisi Yüklenmeyenler



 | 

integer (int64)



 |
| 

**totalReconciliationExisting**  
_opsiyonel_



 | 

Toplam Uzlaştırma Verisi Yüklenenler



 | 

integer (int64)



 |
| 

**totalReconciliationNonExisting**  
_opsiyonel_



 | 

Toplam Uzlaştırma Verisi Yüklenmeyenler



 | 

integer (int64)



 |