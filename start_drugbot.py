"""
DrugBot Başlatma Script'i - Tam Kapasiteli Sürüm
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI

# .env dosyasını yükle
load_dotenv()

# Proje root dizinini PYTHONPATH'a ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DrugBotChat:
    """DrugBot Chat Sistemi"""
    
    def __init__(self):
        """DrugBot'u başlatır"""
        self.setup_vector_store()
        self.setup_llm()
        
    def setup_vector_store(self):
        """Vektör veritabanını yükler"""
        try:
            embeddings = OpenAIEmbeddings(
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                model="text-embedding-3-small"
            )
            
            self.vectorstore = Chroma(
                persist_directory="data/db",
                embedding_function=embeddings,
                collection_name="drug_knowledge"
            )
            
            logger.info("✅ Vektör veritabanı yüklendi")
            
        except Exception as e:
            logger.error(f"❌ Vektör veritabanı yüklenemedi: {e}")
            raise
    
    def setup_llm(self):
        """LLM modelini ayarlar"""
        try:
            self.llm = ChatOpenAI(
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                model_name="gpt-4",
                temperature=0.1
            )
            
            logger.info("✅ LLM modeli hazır")
            
        except Exception as e:
            logger.error(f"❌ LLM modeli ayarlanamadı: {e}")
            raise
    
    def search_drugs(self, query: str, k: int = 3):
        """İlaç arama"""
        try:
            results = self.vectorstore.similarity_search(query, k=k)
            return results
        except Exception as e:
            logger.error(f"❌ Arama hatası: {e}")
            return []
    
    def get_drug_response(self, query: str):
        """İlaç hakkında yanıt oluştur"""
        try:
            # İlaç bilgilerini ara
            drug_docs = self.search_drugs(query, k=3)
            
            if not drug_docs:
                return self.get_no_info_response()
            
            # Context hazırla
            context = "\n\n".join([doc.page_content for doc in drug_docs])
            
            # Prompt oluştur
            prompt = f"""
Sen uzman bir ilaç danışmanı yapay zekasın. İlaçların yan etkileri, yemek etkileşimleri ve kullanım tavsiyeleri konusunda bilgi sağlarsın.

ÖNEMLI GÜVENLİK KURALLARI:
1. Bu bilgiler yalnızca genel bilgilendirme amaçlıdır
2. Kesinlikle teşhis koymak veya tedavi önermek yok
3. Her zaman doktora danışmayı tavsiye et
4. Acil durumlarda hemen doktora gitmeyi söyle

Kullanıcının Sorusu: {query}

İlaç Bilgileri:
{context}

Yanıtlarken:
1. Sorulan ilaç hakkında temel bilgiyi ver
2. Yan etkileri açıkla
3. Yemek etkileşimlerini belirt (aç karın mı tok karın mı)
4. Kullanım zamanlaması hakkında bilgi ver
5. Önemli uyarıları ekle
6. Güvenlik uyarısı ile bitir

Örnek Yanıt Formatı:
🔍 **İlaç Bilgisi:** [İlaç adı ve temel bilgi]
⚠️ **Yan Etkileri:** [Başlıca yan etkiler]
🍽️ **Yemek Etkileşimi:** [Aç karın/tok karın tavsiyeleri]
⏰ **Kullanım Zamanı:** [Ne zaman alınmalı]
🚨 **Önemli Uyarılar:** [Özel durumlar]

💡 **Hatırlatma:** Bu bilgiler genel bilgilendirme amaçlıdır. Kesinlikle doktorunuza danışın.

Yanıt:
"""
            
            # LLM'den yanıt al
            response = self.llm.invoke(prompt)
            
            # Güvenlik uyarısı ekle
            safety_warning = """

🚨 **ÖNEMLİ GÜVENLİK UYARISI**

Bu bilgiler yalnızca genel bilgilendirme amaçlıdır:
- Kesinlikle tıbbi tavsiye değildir
- Doktorunuzun reçetesini değiştirmeyin
- Yan etki yaşarsanız hemen doktora gidin
- Acil durumlarda 112'yi arayın

💊 **Doktorunuza danışmadan ilaç kullanmayın!**
"""
            
            return response.content + safety_warning
            
        except Exception as e:
            logger.error(f"❌ Yanıt oluşturma hatası: {e}")
            return self.get_error_response()
    
    def get_no_info_response(self):
        """Bilgi bulunamadığında yanıt"""
        return """
🔍 **Bilgi Bulunamadı**

Aradığınız ilaç hakkında veritabanımda bilgi bulunmadı.

💡 **Öneriler:**
- İlaç adını doğru yazdığınızdan emin olun
- Farklı kelimeler kullanarak tekrar deneyin
- Doktorunuza veya eczacınıza danışın

⚠️ **Güvenlik Uyarısı:** Bu sistem yalnızca genel bilgilendirme amaçlıdır.
"""
    
    def get_error_response(self):
        """Hata durumunda yanıt"""
        return """
❌ **Sistem Hatası**

Üzgünüm, sorgunuzu işlerken bir hata oluştu.

💡 **Öneriler:**
- Lütfen tekrar deneyin
- Sorunuzu farklı şekilde sorun
- Doktorunuza danışın

⚠️ **Güvenlik:** Bu sistem tıbbi tavsiye vermez.
"""

def main():
    """DrugBot'u başlatır"""
    
    print("🚀 DrugBot Başlatılıyor...")
    print("💊 OnSIDES Dataset ile güçlendirilmiş İlaç Danışmanı")
    print("📊 2,562 ilaç bileşeni ile tam kapasiteli çalışıyor")
    print("⚠️  Bu sistem yalnızca genel bilgilendirme amaçlıdır!")
    print("-" * 60)
    
    try:
        # DrugBot'u başlat
        drugbot = DrugBotChat()
        
        print("✅ DrugBot hazır! İlaç hakkında soru sorabilirsiniz.")
        print("Çıkmak için 'quit' yazın.")
        print("-" * 60)
        
        while True:
            user_input = input("\n💬 Soru: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'çıkış']:
                print("👋 DrugBot kapatılıyor...")
                break
            
            if not user_input:
                continue
            
            print("\n🤖 DrugBot düşünüyor...")
            
            # Yanıt al
            response = drugbot.get_drug_response(user_input)
            
            print(f"\n🤖 **DrugBot:**")
            print(response)
            
    except KeyboardInterrupt:
        print("\n👋 DrugBot kapatılıyor...")
    except Exception as e:
        logger.error(f"❌ Hata: {e}")
        print(f"❌ Bir hata oluştu: {e}")

if __name__ == "__main__":
    main() 