Ürün İsmi

DrugBot – Akıllı İlaç Bilgi Asistanı

Ürün Açıklaması

İlaçBot, vatandaşların ilaç kullanımıyla ilgili temel sorularına kolay anlaşılır, güvenilir ve güncel cevaplar sunan bir yapay zeka destekli sohbet asistanıdır. Kullanıcılar, ilaç adını ya da barkodunu girerek ya da doğal dilde soru sorarak hızlıca bilgiye ulaşabilir.

Ürün Özellikleri

•	İlaç Bilgi Veritabanı: Tüm ilaçların prospektüs verileri (doz, kullanım şekli, yan etkiler, kontrendikasyonlar) güncel olarak saklanır.
•	Doğal Dil ile Soru-Cevap: Kullanıcı, örn. “Bu ilaç aç mı tok mu alınmalı?” gibi serbestçe soru yazar; chatbot kısa, sade yanıt üretir.
•	Kritik Durumlarda Yönlendirme: Riskli ya da acil sorularda kullanıcıyı hekime veya eczacıya yönlendirir.
•	Arama ve Doğrulama: Yanlış/eksik ilaç adı girildiğinde doğrulama ister.
•	Kullanıcı Arayüzü: Basit web/mobil ekranı, soru geçmişi ve favori ilaçlar.
•	Güvenli Bilgi: Medikal danışman onaylı, sadece bilimsel kaynaklara dayalı cevaplar.

Hedef Kitle

•	Her yaş ve eğitim düzeyinden vatandaşlar
•	Özellikle yaşlılar, kronik hastalar ve yakınları
•	Düşük sağlık okuryazarlığı olan bireyler

Product Backlog (Kısa Liste)

1.	İlaç veritabanı oluşturulması ve güncelleme sistemi
2.	Prospektüs bilgilerini otomatik çekme ve işleme
3.	Kullanıcıdan doğal dilde soru alma modülü
4.	LLM ile özet ve sade yanıt üretme
5.	Kritik uyarı ve hekime yönlendirme sistemi
6.	Web ve mobil arayüz tasarımı
7.	Kullanıcı geçmişi ve favori ilaçlar özelliği
8.	Medikal doğruluk kontrolleri ve testler

Sprint Planı (3 Sprint)

•	Sprint 1: Temel ilaç veritabanı kurulumu, prospektüs veri çekme & arama/doğrulama
•	Sprint 2: LLM entegrasyonu, soru-cevap motoru ve uyarı sistemi
•	Sprint 3: Web arayüz, kullanım geçmişi, test ve kullanıcı geri bildirimi
<img width="470" height="645" alt="image" src="https://github.com/user-attachments/assets/8ae1d98f-bad7-4114-ba59-afd6167a2bc6" />
# 💊 DrugBot - Proje Geliştirme Raporu

Bu doküman, DrugBot projesinin geliştirme süreçlerini ve sprint çıktılarını detaylandırmak amacıyla oluşturulmuştur.

---

## 🚀 Sprint 2: Temel Fonksiyonların Geliştirilmesi

### Sprint Notları
- **Proje Yönetimi**: Proje takibi için Trello kullanılmasına karar verildi.
- **UI/UX Tasarım**: Arayüz tasarımları için Figma üzerinde çalışıldı.
- **Backend Mimarisi**: Projenin temelini Flask ve LangChain oluşturmaktadır.
- **Veritabanı**: Vektör veritabanı olarak ChromaDB seçildi.
- **Dil Modeli**: Yanıtların üretilmesi için OpenAI GPT-4 modeli entegre edildi.
- **Veri Seti**: OnSIDES v3.1.0 veri seti, ilaç bilgilerinin kaynağı olarak kullanıldı.

### Puan Tamamlama Mantığı
- **Tahmini Puan**: 100 Puan
- **Tamamlanan Puan**: 120 Puan
- **Açıklama**: İlk sprint için temel kurulum, veri işleme ve arayüzün iskeleti hedeflenmişti. Vektör veritabanının beklenenden hızlı entegre edilmesiyle fazladan puan kazanıldı.

### Daily Scrum
- Günlük toplantılar, geliştirme sürecindeki engelleri ve ilerlemeyi takip etmek amacıyla düzenli olarak yapıldı. Kritik bir sorunla karşılaşılmadı.

### Sprint Board Güncellemesi
- Trello panosu üzerinde görevler "To Do", "In Progress" ve "Done" sütunlarında takip edildi. Sprint sonunda tüm temel görevler "Done" sütununa taşındı.

### Ürün Durumu: Ekran Görüntüleri

**Ana Sayfa ve Örnek Sorular:**
*Kullanıcıları karşılayan ve örnek sorgular sunan başlangıç ekranı.*
'https://github.com/aslikiziltans/drugBotFinal/tree/main/ekranfoto' bu sayfayi ziyaret edebilirsiniz. 

**Sorgu İşlenirken:**
*Kullanıcı bir soru sorduğunda sistemin yanıtı hazırlama süreci.*
'https://github.com/aslikiziltans/drugBotFinal/tree/main/ekranfoto' bu sayfayi ziyaret edebilirsiniz. 

**Yanıt Ekranı:**
*Sistemin ürettiği anlaşılır ve formatlanmış ilaç bilgisi yanıtı.*
'https://github.com/aslikiziltans/drugBotFinal/tree/main/ekranfoto' bu sayfayi ziyaret edebilirsiniz. 


### Sprint Review: Alınan Kararlar
- Vektör veritabanı oluşturma script'i (`create_drug_vectordb.py`) başarıyla tamamlandı ve test edildi.
- Web arayüzü (`drugbot_web.py`) temel işlevselliğe kavuştu: kullanıcı sorgusu alma, backend'e iletme ve yanıtı gösterme.
- Yanıt formatının kullanıcı dostu olması için özel bir prompt yapısı geliştirildi.

### Sprint Retrospective
- **Olumlu Yönler**: Ekip içi iletişim ve koordinasyon yüksekti. Teknik hedeflere ulaşıldı.
- **Geliştirilecek Yönler**: Gelecek sprintlerde daha detaylı birim (unit) testleri yazılması kararlaştırıldı.

---

## 🛠️ Proje Mimarisi ve Çalışma Prensibi

DrugBot, kullanıcı sorgularını işlemek ve doğru yanıtlar üretmek için modüler bir mimari kullanır.

### Mermaid Diagramı
Aşağıdaki diagram, bir kullanıcı sorgusunun sistem içinde nasıl işlendiğini göstermektedir:

```mermaid
graph TD
    subgraph Kullanıcı Arayüzü
        A[Kullanıcı Sorusu] --> B{Flask Web Sunucusu};
    end

    subgraph Backend Servisleri
        B --> C[DrugBotWeb Sınıfı];
        C --> D{Vektör Veritabanı (ChromaDB)};
        C --> E{LLM (OpenAI GPT-4)};
    end

    subgraph Veri Katmanı
        F[OnSIDES Dataset] --> G[create_drug_vectordb.py];
        G --> D;
    end

    B -- Sorguyu Alır --> C;
    C -- Anlamsal Arama Yapar --> D;
    D -- İlgili İlaç Bilgilerini Döndürür --> C;
    C -- Bilgilerle Prompt Oluşturur --> E;
    E -- Anlaşılır Yanıt Üretir --> C;
    C -- Yanıtı Arayüze Gönderir --> B;
    B -- Yanıtı Gösterir --> A;

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#ccf,stroke:#333,stroke-width:2px
    style F fill:#fcf,stroke:#333,stroke-width:2px
```

### Teknoloji Yığını
- **Backend**: Flask, LangChain
- **Dil Modeli**: OpenAI GPT-4
- **Vektör Veritabanı**: ChromaDB
- **Frontend**: HTML, CSS, JavaScript
- **Veri Seti**: OnSIDES v3.1.0

---

## 🚀 Hızlı Başlangıç

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin.

### Gereksinimler
- Python 3.8 veya üstü
- OpenAI API Anahtarı

### 1. Projeyi Klonlama
```bash
git clone https://github.com/aslikiziltan/GrantSpider_Chatbot_asliFeatures.git
cd GrantSpider_Chatbot_asliFeatures
```

### 2. Bağımlılıkları Yükleme
```bash
pip install -r requirements.txt
```

### 3. Ortam Değişkenlerini Ayarlama
Proje ana dizininde `.env` adında bir dosya oluşturun ve içine OpenAI API anahtarınızı ekleyin:
```
OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### 4. Vektör Veritabanını Oluşturma
İlaç verilerini işleyip vektör veritabanını oluşturmak için aşağıdaki komutu çalıştırın. Bu işlem biraz zaman alabilir.
```bash
python create_drug_vectordb.py
```

### 5. Web Uygulamasını Başlatma
```bash
python interfaces/drugbot_web.py
```
Uygulama başlatıldıktan sonra tarayıcınızda `http://localhost:5001` adresini ziyaret edebilirsiniz.

### 6. Ekran Fotograflari

'https://github.com/aslikiziltans/drugBotFinal/tree/main/ekranfoto' bu sayfayi ziyaret edebilirsiniz. 
---




