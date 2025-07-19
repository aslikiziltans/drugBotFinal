"""
DrugBot için ilaç bilgi tabanı yükleyici
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain.schema import Document

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DrugKnowledgeLoader:
    """İlaç bilgi tabanını yükleyen sınıf"""
    
    def __init__(self, knowledge_base_path: str = "data/processed/drug_knowledge_base.json"):
        """
        Drug knowledge loader'ı başlatır
        
        Args:
            knowledge_base_path: İlaç bilgi tabanı JSON dosyasının yolu
        """
        self.knowledge_base_path = Path(knowledge_base_path)
        self.documents = []
        
    def load_drug_knowledge(self) -> List[Document]:
        """
        İlaç bilgi tabanını yükler ve Document formatına dönüştürür
        
        Returns:
            List[Document]: LangChain Document formatında ilaç bilgileri
        """
        try:
            logger.info("💊 İlaç bilgi tabanı yükleniyor...")
            
            if not self.knowledge_base_path.exists():
                logger.error(f"❌ Bilgi tabanı bulunamadı: {self.knowledge_base_path}")
                return []
            
            # JSON dosyasını yükle
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                drug_data = json.load(f)
            
            documents = []
            
            for drug_info in drug_data:
                content = drug_info.get("content", "")
                metadata = drug_info.get("metadata", {})
                
                # LangChain Document formatına dönüştür
                doc = Document(
                    page_content=content,
                    metadata=metadata
                )
                
                documents.append(doc)
            
            logger.info(f"✅ {len(documents)} ilaç belgesi yüklendi")
            self.documents = documents
            return documents
            
        except Exception as e:
            logger.error(f"❌ İlaç bilgi tabanı yüklenirken hata: {e}")
            return []
    
    def get_drug_names(self) -> List[str]:
        """
        Yüklenen ilaç isimlerini döndürür
        
        Returns:
            List[str]: İlaç isimleri
        """
        if not self.documents:
            self.load_drug_knowledge()
        
        drug_names = []
        for doc in self.documents:
            drug_name = doc.metadata.get("drug_name", "")
            if drug_name:
                drug_names.append(drug_name)
        
        return drug_names
    
    def search_drug_by_name(self, drug_name: str) -> Optional[Document]:
        """
        İsme göre ilaç arar
        
        Args:
            drug_name: Aranacak ilaç ismi
            
        Returns:
            Optional[Document]: Bulunan ilaç belgesi
        """
        if not self.documents:
            self.load_drug_knowledge()
        
        drug_name_lower = drug_name.lower()
        
        for doc in self.documents:
            doc_drug_name = doc.metadata.get("drug_name", "").lower()
            if drug_name_lower in doc_drug_name or doc_drug_name in drug_name_lower:
                return doc
        
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        İlaç bilgi tabanı istatistiklerini döndürür
        
        Returns:
            Dict[str, Any]: İstatistikler
        """
        if not self.documents:
            self.load_drug_knowledge()
        
        stats = {
            "total_drugs": len(self.documents),
            "average_content_length": 0,
            "source_distribution": {}
        }
        
        if self.documents:
            total_length = sum(len(doc.page_content) for doc in self.documents)
            stats["average_content_length"] = total_length / len(self.documents)
            
            # Kaynak dağılımı
            for doc in self.documents:
                source = doc.metadata.get("source", "Unknown")
                stats["source_distribution"][source] = stats["source_distribution"].get(source, 0) + 1
        
        return stats


def load_drug_documents() -> List[Document]:
    """
    İlaç belgelerini yükler - mevcut PDF loader ile uyumlu
    
    Returns:
        List[Document]: İlaç belgeleri
    """
    loader = DrugKnowledgeLoader()
    return loader.load_drug_knowledge()


def main():
    """Test fonksiyonu"""
    loader = DrugKnowledgeLoader()
    documents = loader.load_drug_knowledge()
    
    print(f"📊 Yüklenen ilaç sayısı: {len(documents)}")
    
    # İstatistikler
    stats = loader.get_statistics()
    print(f"📈 İstatistikler: {stats}")
    
    # Örnek ilaç arama
    drug_names = loader.get_drug_names()
    if drug_names:
        print(f"🔍 Örnek ilaç isimleri: {drug_names[:5]}")
        
        # İlk ilacı arama
        first_drug = loader.search_drug_by_name(drug_names[0])
        if first_drug:
            print(f"🎯 Bulunan ilaç: {first_drug.metadata.get('drug_name', 'Bilinmeyen')}")


if __name__ == "__main__":
    main() 