"""
Kaynak takip ajanı
"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent

class SourceTrackerAgent(BaseAgent):
    """Kaynak atıflarını takip eden ajan"""
    
    def __init__(self):
        super().__init__(
            name="source_tracker",
            description="Yanıtlarda kullanılan kaynakları takip eder ve atıfları yönetir"
        )
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kaynak takibi yapar
        
        Args:
            state: Mevcut durum
            
        Returns:
            Kaynak bilgileri ve güncellenmiş durum
        """
        retrieved_documents = state.get("retrieved_documents", [])
        qa_response = state.get("qa_response", "")
        
        # Her durumda source_tracking_performed = True ayarla
        state["source_tracking_performed"] = True
        
        if not retrieved_documents:
            # Boş belgeler listesi durumunda default değerler
            state["sources"] = []
            state["cited_response"] = qa_response
            return state
        
        # Kaynak bilgilerini çıkar
        sources = self._extract_sources(retrieved_documents)
        
        # Kaynak atıflı yanıt oluştur
        cited_response = self._add_citations(qa_response, sources)
        
        # Durumu güncelle
        state["sources"] = sources
        state["cited_response"] = cited_response
        
        return state
    
    def _extract_sources(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Belgelerden kaynak bilgilerini çıkarır
        
        Args:
            documents: Belgeler listesi
            
        Returns:
            Kaynak bilgileri listesi
        """
        sources = []
        seen_sources = set()
        
        for doc in documents:
            metadata = doc.get("metadata", {})
            source_path = metadata.get("source", "")
            
            # Clean source name - path'den dosya adını çıkar
            clean_source = source_path.replace('data/raw/', '').replace('.pdf', '')
            if not clean_source:
                clean_source = metadata.get("filename", "Bilinmeyen")
            
            # Sayfa bilgisini al
            page_number = metadata.get("page_number", metadata.get("page", ""))
            page_display = f"Sayfa {page_number}" if page_number else "Sayfa bilinmiyor"
            
            # Aynı kaynağı tekrar ekleme
            source_key = (clean_source, page_number)
            if source_key in seen_sources:
                continue
            
            seen_sources.add(source_key)
            
            sources.append({
                "clean_source": clean_source,
                "page": page_display,
                "source_path": source_path,
                "chunk_index": metadata.get("chunk_index", 0),
                "similarity_score": doc.get("similarity_score", 0.0),
                "content": doc.get("content", "")[:100] + "..."
            })
        
        return sources
    
    def _add_citations(self, response: str, sources: List[Dict[str, Any]]) -> str:
        """
        Orijinal yanıtı döndürür - Kaynaklar ayrı listede gösteriliyor
        
        Args:
            response: Orijinal yanıt
            sources: Kaynak listesi
            
        Returns:
            Orijinal yanıt (kaynaklar artık yanıtın sonuna eklenmiyor)
        """
        # Kaynaklar artık yanıtın sonuna eklenmiyor, sadece ayrı listede gösteriliyor
        return response
    
    def get_source_summary(self, sources: List[Dict[str, Any]]) -> str:
        """
        Kaynak özetini döndürür
        
        Args:
            sources: Kaynak listesi
            
        Returns:
            Kaynak özeti
        """
        if not sources:
            return "Hiç kaynak bulunamadı."
        
        unique_files = set(source.get("clean_source", "") for source in sources)
        return f"Toplam {len(sources)} chunk, {len(unique_files)} farklı belgeden kullanıldı." 