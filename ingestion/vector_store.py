"""
Vektör veritabanı yönetimi - OpenAI Embeddings ile
"""

import os
import shutil
from typing import List, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document

from config.settings import settings

# Global vector store instance
_vector_store = None

def reset_global_vector_store():
    """Global vector store instance'ını sıfırla"""
    global _vector_store
    _vector_store = None
    print("🔄 Global vector store instance sıfırlandı")

def get_embeddings():
    """OpenAI embeddings modelini döndür"""
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    print(f"🔧 OpenAI Embeddings başlatılıyor - Model: {settings.EMBEDDING_MODEL}")
    print(f"🔑 API Key: {settings.OPENAI_API_KEY[:20]}...")
    
    return OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        openai_api_key=settings.OPENAI_API_KEY,
        openai_api_base="https://api.openai.com/v1/"
    )

def get_vector_store():
    """
    Global vector store instance'ını döndür
    """
    global _vector_store
    
    if _vector_store is None:
        print("🔧 Vector store başlatılıyor...")
        
        # Veritabanı dizinini oluştur
        db_path = Path(settings.VECTOR_DB_PATH)
        db_path.mkdir(parents=True, exist_ok=True)
        
        # Embeddings modelini al
        embeddings = get_embeddings()
        
        # ChromaDB ayarları
        chroma_settings = ChromaSettings(
            persist_directory=str(db_path),
            anonymized_telemetry=False
        )
        
        # Chroma vector store'u oluştur
        _vector_store = Chroma(
            collection_name="amif_documents",
            embedding_function=embeddings,
            persist_directory=str(db_path),
            client_settings=chroma_settings
        )
        
        print("✅ Vector store hazır")
    
    return _vector_store

def reset_vector_store():
    """
    Vector store'u sıfırla - mevcut collection'ı sil
    """
    global _vector_store
    
    print("🗑️  Mevcut vector store sıfırlanıyor...")
    
    # Global instance'ı temizle
    _vector_store = None
    
    # Veritabanı dizinini sil
    db_path = Path(settings.VECTOR_DB_PATH)
    if db_path.exists():
        shutil.rmtree(db_path)
        print("✅ Veritabanı dizini silindi")
    
    # Yeni dizini oluştur
    db_path.mkdir(parents=True, exist_ok=True)
    print("✅ Yeni veritabanı dizini oluşturuldu")

def add_documents_to_vector_store(documents: List[Document]) -> bool:
    """
    Belgeleri vector store'a ekle - büyük batch'leri böler
    
    Args:
        documents: Eklenecek belgeler
        
    Returns:
        bool: Başarılı ise True
    """
    try:
        if not documents:
            print("⚠️  Eklenecek belge bulunamadı")
            return False
        
        vector_store = get_vector_store()
        
        print(f"📝 {len(documents)} belge vector store'a ekleniyor...")
        
        # ChromaDB maksimum batch boyutu
        MAX_BATCH_SIZE = 5000
        
        # Eğer belge sayısı maksimum batch boyutundan büyükse, böl
        if len(documents) > MAX_BATCH_SIZE:
            print(f"📦 Büyük batch tespit edildi. {MAX_BATCH_SIZE}'lik parçalara bölünüyor...")
            
            total_added = 0
            for i in range(0, len(documents), MAX_BATCH_SIZE):
                batch = documents[i:i + MAX_BATCH_SIZE]
                batch_num = (i // MAX_BATCH_SIZE) + 1
                total_batches = (len(documents) + MAX_BATCH_SIZE - 1) // MAX_BATCH_SIZE
                
                print(f"📦 Batch {batch_num}/{total_batches}: {len(batch)} belge ekleniyor...")
                
                # Bu batch'i ekle
                vector_store.add_documents(batch)
                total_added += len(batch)
                
                print(f"✅ Batch {batch_num} tamamlandı. Toplam eklenen: {total_added}")
        else:
            # Küçük batch, direkt ekle
            vector_store.add_documents(documents)
            total_added = len(documents)
        
        print(f"✅ Toplam {total_added} belge başarıyla eklendi")
        return True
        
    except Exception as e:
        print(f"❌ Belge ekleme hatası: {e}")
        return False

def search_documents(query: str, k: int = 5) -> List[Document]:
    """
    Vector store'da arama yap
    
    Args:
        query: Arama sorgusu
        k: Döndürülecek sonuç sayısı
        
    Returns:
        List[Document]: Bulunan belgeler
    """
    try:
        vector_store = get_vector_store()
        
        print(f"🔍 Arama yapılıyor: '{query}' (k={k})")
        
        # Collection bilgisini kontrol et
        collection = vector_store._collection
        count = collection.count()
        print(f"📊 Collection'da {count} doküman var")
        
        # Similarity search yap
        results = vector_store.similarity_search(query, k=k)
        
        print(f"✅ Arama tamamlandı: {len(results)} sonuç bulundu")
        
        return results
        
    except Exception as e:
        print(f"❌ Arama hatası: {e}")
        return []

def get_collection_info():
    """
    Collection bilgilerini döndür
    """
    try:
        vector_store = get_vector_store()
        
        # Collection'daki belge sayısını al
        collection = vector_store._collection
        count = collection.count()
        
        print(f"🔍 Collection info - Count: {count}, Name: {collection.name}")
        
        return {
            "document_count": count,
            "collection_name": "amif_documents",
            "embedding_model": settings.EMBEDDING_MODEL
        }
        
    except Exception as e:
        print(f"❌ Collection bilgisi alınamadı: {e}")
        return {
            "document_count": 0,
            "collection_name": "amif_documents",
            "embedding_model": settings.EMBEDDING_MODEL,
            "error": str(e)
        } 