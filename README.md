# 💊 DrugBot - Proje Geliştirme Raporu

Bu doküman, DrugBot projesinin geliştirme süreçlerini ve sprint çıktılarını detaylandırmak amacıyla oluşturulmuştur.

---

## 🚀 Sprint 1: Temel Fonksiyonların Geliştirilmesi

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
![Ana Sayfa](https://i.imgur.com/rD4g5dM.png)

**Sorgu İşlenirken:**
*Kullanıcı bir soru sorduğunda sistemin yanıtı hazırlama süreci.*
![Sorgu İşleniyor](https://i.imgur.com/5zS3sL3.png)

**Yanıt Ekranı:**
*Sistemin ürettiği anlaşılır ve formatlanmış ilaç bilgisi yanıtı.*
![Yanıt Ekranı](https://i.imgur.com/BvY9E9O.png)

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

---

## ⚠️ Yasal Uyarı

Bu proje **sadece bilgilendirme amaçlıdır** ve kesinlikle **tıbbi tavsiye niteliği taşımaz**. Herhangi bir ilacı kullanmadan önce mutlaka bir doktora veya eczacıya danışın. Bu yazılımın kullanımından kaynaklanabilecek herhangi bir sorun kullanıcının kendi sorumluluğundadır.