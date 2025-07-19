"""
DrugBot için vektör veritabanı oluşturma script'i
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

# .env dosyasını yükle
load_dotenv()

# Proje root dizinini ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_drug_knowledge():
    """İlaç bilgi tabanını yükle"""
    knowledge_path = Path("data/processed/drug_knowledge_base.json")
    
    if not knowledge_path.exists():
        logger.error(f"❌ Bilgi tabanı bulunamadı: {knowledge_path}")
        return []
    
    logger.info("📚 İlaç bilgi tabanı yükleniyor...")
    
    with open(knowledge_path, 'r', encoding='utf-8') as f:
        drug_data = json.load(f)
    
    documents = []
    for drug_info in drug_data:
        content = drug_info.get("content", "")
        metadata = drug_info.get("metadata", {})
        
        doc = Document(
            page_content=content,
            metadata=metadata
        )
        documents.append(doc)
    
    logger.info(f"✅ {len(documents)} ilaç belgesi yüklendi")
    return documents

def create_vector_database():
    """Vektör veritabanını oluştur"""
    try:
        logger.info("🚀 DrugBot vektör veritabanı oluşturuluyor...")
        
        # API Key kontrol
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.error("❌ OPENAI_API_KEY environment variable bulunamadı")
            return False
        
        # Embeddings setup
        embeddings = OpenAIEmbeddings(
            openai_api_key=openai_api_key,
            model="text-embedding-3-small"
        )
        
        # Metin bölen
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
        # İlaç belgelerini yükle
        documents = load_drug_knowledge()
        if not documents:
            logger.error("❌ İlaç belgeleri yüklenemedi")
            return False
        
        # Belgeleri böl
        logger.info("📝 Belgeler chunks'lara bölünüyor...")
        all_chunks = []
        
        for i, doc in enumerate(documents):
            if i % 500 == 0:
                logger.info(f"📈 İlerleme: {i}/{len(documents)} belge işlendi")
            
            chunks = text_splitter.split_text(doc.page_content)
            
            for chunk in chunks:
                chunk_doc = Document(
                    page_content=chunk,
                    metadata=doc.metadata
                )
                all_chunks.append(chunk_doc)
        
        logger.info(f"✅ {len(all_chunks)} metin parçası oluşturuldu")
        
        # Vektör veritabanı dizini
        persist_directory = "data/db"
        
        # Mevcut DB'yi sil
        if os.path.exists(persist_directory):
            import shutil
            shutil.rmtree(persist_directory)
            logger.info("🗑️ Eski vektör veritabanı silindi")
        
        # Yeni vektör veritabanı oluştur
        logger.info("🔧 Yeni vektör veritabanı oluşturuluyor...")
        
        vectorstore = Chroma.from_documents(
            documents=all_chunks,
            embedding=embeddings,
            persist_directory=persist_directory,
            collection_name="drug_knowledge"
        )
        
        # Veritabanını kaydet
        vectorstore.persist()
        
        logger.info("✅ DrugBot vektör veritabanı başarıyla oluşturuldu!")
        
        # Test arama
        logger.info("🔍 Test arama yapılıyor...")
        test_results = vectorstore.similarity_search("aspirin yan etkileri", k=3)
        
        logger.info(f"✅ Test başarılı: {len(test_results)} sonuç bulundu")
        
        for i, result in enumerate(test_results, 1):
            drug_name = result.metadata.get("drug_name", "Bilinmeyen")
            logger.info(f"  {i}. {drug_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Vektör veritabanı oluşturulurken hata: {e}")
        return False

def main():
    """Ana fonksiyon"""
    print("🚀 DrugBot Vektör Veritabanı Oluşturucu")
    print("💊 OnSIDES Dataset ile güçlendirilmiş")
    print("-" * 50)
    
    success = create_vector_database()
    
    if success:
        print("\n✅ Vektör veritabanı başarıyla oluşturuldu!")
        print("🎯 DrugBot artık tam kapasiteli çalışmaya hazır!")
    else:
        print("\n❌ Vektör veritabanı oluşturulamadı")
        print("⚠️  Lütfen hata loglarını kontrol edin")

if __name__ == "__main__":
    main() 