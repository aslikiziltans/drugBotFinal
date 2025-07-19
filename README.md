# 💊 DrugBot - İlaç Bilgi Asistanı

> **OnSIDES Dataset ile güçlendirilmiş akıllı ilaç danışmanı**

DrugBot, 2,562 ilaç bileşeni hakkında güvenilir bilgi sunan yapay zeka destekli web uygulamasıdır. FDA, EMA ve KEGG kaynaklarından derlenen OnSIDES v3.1.0 dataset'ini kullanarak ilaç yan etkileri, kullanım talimatları ve yemek etkileşimleri hakkında anlaşılır bilgiler verir.

## 🌟 Özellikler

### 🔍 **Akıllı İlaç Arama**
- 2,562 ilaç bileşeni veritabanı
- Semantik arama ile doğru sonuçlar
- Türkçe sorgu desteği

### 💬 **Anlaşılır Yanıtlar**
- Tıbbi terimler yerine günlük dil
- Emoji destekli düzenli format
- Korkutmayan, bilgilendirici ton

### 🎨 **Modern Web Arayüzü**
- Koyu tema ile göz dostu tasarım
- Responsive mobil uyumlu
- Gerçek zamanlı sohbet deneyimi

### 🔒 **Güvenlik Öncelikli**
- Sürekli tıbbi uyarılar
- Kaynak şeffaflığı
- Doktor tavsiyesi hatırlatmaları

## 🚀 Hızlı Başlangıç

### Gereksinimler
```bash
Python 3.8+
OpenAI API Key
```

### 1. Kurulum
```bash
# Depoyu klonlayın
git clone <repo-url>
cd GrantSpider
git checkout asliFeatures

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

### 2. Çevre Değişkenlerini Ayarlayın
```bash
# .env dosyası oluşturun
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

### 3. Vektör Veritabanını Oluşturun
```bash
python3 create_drug_vectordb.py
```

### 4. Web Uygulamasını Başlatın
```bash
python3 interfaces/drugbot_web.py
```

### 5. Tarayıcıda Açın
```
http://localhost:5001
```

## 📱 Kullanım

### Örnek Sorular
- "aspirin yan etkileri nelerdir?"
- "paracetamol aç karınla mı alınır?"
- "ibuprofen ne için kullanılır?"
- "antibiyotik nasıl kullanılır?"

### Yanıt Formatı
```
💊 İlaç Hakkında: [Ne için kullanılır]
⚠️ Olası Yan Etkiler: [Yaygın yan etkiler]
🍽️ Nasıl Alınır: [Yemek ile ilişkisi]
⏰ Ne Zaman Alınır: [Dozaj zamanlaması]
💡 Dikkat Edilecekler: [Önemli uyarılar]
🏥 Hatırlatma: [Doktor tavsiyesi]
```

## 🏗️ Mimari

### Klasör Yapısı
```
DrugBot/
├── agents/                 # LangGraph ajanları
│   ├── drug_advisor_agent.py
│   └── document_retriever.py
├── ingestion/             # Veri işleme
│   ├── drug_data_processor.py
│   ├── drug_pdf_loader.py
│   └── vector_store.py
├── interfaces/            # Web arayüzü
│   ├── drugbot_web.py
│   ├── templates/
│   └── static/
├── data/                  # Veritabanları
│   ├── db/               # Vektör veritabanı
│   └── processed/        # İşlenmiş veriler
└── create_drug_vectordb.py # Veritabanı oluşturucu
```

### Teknoloji Yığını
- **Backend**: Flask, LangChain, OpenAI GPT-4
- **Vector DB**: ChromaDB
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Dataset**: OnSIDES v3.1.0 (FDA/EMA/KEGG)

## 🔧 API Endpointleri

### Chat Endpoint
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "aspirin yan etkileri nelerdir?"
}
```

### Sistem İstatistikleri
```bash
GET /api/stats
```

### Son Sorgular
```bash
GET /api/recent
```

## 📊 Dataset Bilgileri

### OnSIDES v3.1.0
- **Kaynak**: FDA, EMA, EMC, KEGG
- **İlaç Sayısı**: 2,562 bileşen
- **Yan Etki**: 7,177 farklı yan etki
- **Toplam Kayıt**: 7.1+ milyon ilişki

### Veri İşleme
1. CSV dosyalarından ilaç bilgileri çıkarma
2. Metin parçalama ve temizleme
3. OpenAI embeddings ile vektörizasyon
4. ChromaDB'de saklama

## ⚠️ Güvenlik ve Sorumluluk

### Önemli Uyarılar
- Bu sistem **sadece bilgilendirme amaçlıdır**
- Kesinlikle **tıbbi tavsiye vermez**
- Her zaman **doktorunuza danışın**
- Acil durumlarda **112'yi arayın**

### Veri Güvenliği
- API anahtarları `.env` dosyasında
- Kullanıcı verileri loglanmaz
- HTTPS kullanımı önerilir

## 🧪 Test

### Unit Testler
```bash
python -m pytest tests/
```

### Manuel Test
```bash
# Basit sorgu testi
curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "aspirin"}'
```

## 📈 Performans

### Yanıt Süreleri
- **Vektör Arama**: ~200ms
- **LLM İşleme**: ~2-5 saniye
- **Toplam**: ~3-6 saniye

### Kaynak Kullanımı
- **RAM**: ~500MB (vektör DB dahil)
- **Disk**: ~35MB (veritabanı)
- **CPU**: Orta düzey

## 🤝 Katkıda Bulunma

### Geliştirme Süreci
1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişiklikleri commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'i push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request açın

### Kod Standartları
- Python PEP 8 uyumluluğu
- Türkçe docstring'ler
- Type hints kullanımı
- Error handling zorunlu

## 📝 Sürüm Notları

### v1.0.0 (Mevcut)
- ✅ OnSIDES dataset entegrasyonu
- ✅ Web arayüzü
- ✅ GPT-4 destekli yanıtlar
- ✅ Türkçe dil desteği
- ✅ Anlaşılır çıktı formatı

### Planlanan Özellikler
- 🔄 İlaç etkileşim kontrolü
- 🔄 Çoklu dil desteği
- 🔄 Mobil uygulama
- 🔄 Sesli asistan

## 📞 Destek

### Yaygın Sorunlar
1. **"Vektör veritabanı boş"** → `create_drug_vectordb.py` çalıştırın
2. **"API hatası"** → `.env` dosyasında OpenAI anahtarını kontrol edin
3. **"Port kullanımda"** → `drugbot_web.py`'de farklı port kullanın

### İletişim
- 🐛 Bug raporları için Issues açın
- 💡 Özellik istekleri için Discussions kullanın
- 📧 Acil durumlar için repository sahibine ulaşın

## 📜 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 🙏 Teşekkürler

- **OnSIDES Dataset** geliştiricilerine
- **OpenAI** GPT-4 modeli için
- **LangChain** ekosistemi için
- **ChromaDB** vektör veritabanı için

---

**⚠️ Yasal Uyarı**: DrugBot bir eğitim ve araştırma projesidir. Gerçek tıbbi durumlar için mutlaka sağlık profesyonellerine danışın. Bu yazılımın kullanımından doğabilecek her türlü zarar kullanıcının sorumluluğundadır.

**💊 Sağlıklı günler dileriz!**