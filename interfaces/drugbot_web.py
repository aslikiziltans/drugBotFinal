"""
DrugBot Web Interface - Flask App
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI

# .env dosyasını yükle
load_dotenv()

# Proje root dizinini ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "drugbot-secret-key-2024")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DrugBotWeb:
    """DrugBot Web Sistemi"""
    
    def __init__(self):
        """DrugBot web sistemini başlatır"""
        self.setup_vector_store()
        self.setup_llm()
        self.query_history = []
        
    def setup_vector_store(self):
        """Vektör veritabanını yükler"""
        try:
            embeddings = OpenAIEmbeddings(
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                model="text-embedding-3-small"
            )
            
            self.vectorstore = Chroma(
                persist_directory=str(project_root / "data" / "db"),
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
        """İlaç hakkında anlaşılır yanıt oluştur"""
        try:
            # İlaç bilgilerini ara
            drug_docs = self.search_drugs(query, k=3)
            
            if not drug_docs:
                return {
                    "response": self.get_no_info_response(),
                    "sources": [],
                    "found_drugs": []
                }
            
            # Context hazırla
            context = "\n\n".join([doc.page_content for doc in drug_docs])
            
            # Bulunan ilaçları al
            found_drugs = []
            sources = []
            
            for i, doc in enumerate(drug_docs):
                drug_name = doc.metadata.get("drug_name", "Bilinmeyen İlaç")
                found_drugs.append(drug_name)
                sources.append({
                    "title": drug_name,
                    "source": doc.metadata.get("source", "OnSIDES"),
                    "type": "İlaç Bilgisi"
                })
            
            # Prompt oluştur - DAHA ANLAŞILIR
            prompt = f"""
Sen bir ilaç danışmanı yapay zekasın. Sıradan insanların anlayabileceği basit ve anlaşılır bir dilde yanıt vermelisin.

ÖNEMLI KURALLAR:
1. Tıbbi terimler yerine günlük dilde karşılıklarını kullan
2. Kısa ve net cümleler kur
3. Madde madde açıkla
4. Korku yaratma, sakinleştirici bir dil kullan
5. Güvenlik uyarısı ile bitir

Kullanıcının Sorusu: {query}

İlaç Bilgileri:
{context}

YANIT FORMATINI AYNEN KULLAN:

💊 **İlaç Hakkında:**
[İlaç adı ve ne için kullanıldığı - basit dilde]

⚠️ **Olası Yan Etkiler:**
[En yaygın yan etkileri - günlük dilde, korkutmadan]

🍽️ **Nasıl Alınır:**
[Yemekle mi, aç karınla mı - basit açıklama]

⏰ **Ne Zaman Alınır:**
[Günün hangi saati, ne sıklıkla - basit]

💡 **Dikkat Edilecekler:**
[Önemli uyarılar - anlaşılır dilde]

🏥 **Hatırlatma:**
Bu bilgiler sadece genel bilgi amaçlıdır. İlaç kullanımı konusunda mutlaka doktorunuza danışın.

Yanıt (Türkçe ve anlaşılır dilde):
"""
            
            # LLM'den yanıt al
            response = self.llm.invoke(prompt)
            
            # Sorgu geçmişine ekle
            self.query_history.append({
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "found_drugs": found_drugs
            })
            
            # Sadece son 10 sorguyu sakla
            if len(self.query_history) > 10:
                self.query_history = self.query_history[-10:]
            
            return {
                "response": response.content,
                "sources": sources,
                "found_drugs": found_drugs
            }
            
        except Exception as e:
            logger.error(f"❌ Yanıt oluşturma hatası: {e}")
            return {
                "response": self.get_error_response(),
                "sources": [],
                "found_drugs": []
            }
    
    def get_no_info_response(self):
        """Bilgi bulunamadığında yanıt"""
        return """
🔍 **Bilgi Bulunamadı**

Üzgünüm, aradığınız ilaç hakkında bilgi bulunamadı.

💡 **Deneyebilirsiniz:**
• İlaç adını farklı şekilde yazın
• Etken madde adını deneyin
• Doktorunuza veya eczacınıza danışın

🏥 **Unutmayın:** Bu sistem sadece genel bilgi verir, tıbbi tavsiye değildir.
"""
    
    def get_error_response(self):
        """Hata durumunda yanıt"""
        return """
❌ **Bir Sorun Oluştu**

Üzgünüm, sorgunuzu işlerken bir hata oluştu.

💡 **Yapabilecekleriniz:**
• Sayfayı yenileyin
• Sorunuzu tekrar deneyin
• Daha basit kelimeler kullanın

🏥 **Önemli:** Acil durumlarda doktora başvurun!
"""
    
    def get_stats(self):
        """Sistem istatistikleri"""
        try:
            collection = self.vectorstore._collection
            total_docs = collection.count()
            
            return {
                "total_drugs": "2,562",
                "total_documents": f"{total_docs:,}",
                "query_count": len(self.query_history),
                "status": "Aktif"
            }
        except:
            return {
                "total_drugs": "2,562",
                "total_documents": "N/A",
                "query_count": len(self.query_history),
                "status": "Aktif"
            }
    
    def get_recent_queries(self):
        """Son sorguları döndür"""
        return self.query_history[-5:]  # Son 5 sorgu

# Global DrugBot instance
drugbot = DrugBotWeb()

@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('drugbot_index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint"""
    try:
        data = request.json
        query = data.get('message', '').strip()
        
        if not query:
            return jsonify({
                "success": False,
                "error": "Lütfen bir soru yazın"
            })
        
        # DrugBot'dan yanıt al
        result = drugbot.get_drug_response(query)
        
        return jsonify({
            "success": True,
            "response": result["response"],
            "sources": result["sources"],
            "found_drugs": result["found_drugs"]
        })
        
    except Exception as e:
        logger.error(f"Chat hatası: {e}")
        return jsonify({
            "success": False,
            "error": "Bir hata oluştu, lütfen tekrar deneyin"
        })

@app.route('/api/stats')
def stats():
    """Sistem istatistikleri"""
    return jsonify(drugbot.get_stats())

@app.route('/api/recent')
def recent_queries():
    """Son sorgular"""
    return jsonify(drugbot.get_recent_queries())

if __name__ == '__main__':
    print("🚀 DrugBot Web Interface başlatılıyor...")
    print("💊 http://localhost:5001 adresinden erişebilirsiniz")
    print("⚠️  Bu sistem sadece genel bilgilendirme amaçlıdır!")
    
    app.run(debug=True, host='0.0.0.0', port=5001) 