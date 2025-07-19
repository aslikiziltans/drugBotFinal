"""
Durum yönetimi - LangGraph state'i yönetir
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from langchain_core.messages import BaseMessage

@dataclass
class MultiAgentState:
    """LangGraph için çoklu ajan durumu"""
    
    # Kullanıcı sorgusu
    query: str = ""
    
    # Algılanan dil
    detected_language: str = "tr"
    
    # Sohbet geçmişi
    messages: List[BaseMessage] = field(default_factory=list)
    
    # Belge arama sonuçları
    retrieved_documents: List[Dict[str, Any]] = field(default_factory=list)
    
    # QA yanıtı
    qa_response: str = ""
    
    # Kaynak bilgileri
    sources: List[Dict[str, Any]] = field(default_factory=list)
    
    # Kaynak atıflı final yanıt
    cited_response: str = ""
    
    # İşlem durumları
    retrieval_performed: bool = False
    qa_performed: bool = False
    source_tracking_performed: bool = False
    cross_document_performed: bool = False
    
    # Cross-document analysis sonuçları
    cross_document_analysis: Dict[str, Any] = field(default_factory=dict)
    
    # Session bilgileri
    session_id: Optional[str] = None
    
    # Ek metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

class StateManager:
    """Durum yönetimi sınıfı"""
    
    def __init__(self):
        self.current_state = MultiAgentState()
    
    def initialize_state(self, query: str, session_id: Optional[str] = None) -> MultiAgentState:
        """
        Yeni bir durum başlatır
        
        Args:
            query: Kullanıcı sorgusu
            session_id: Session kimliği
            
        Returns:
            Başlatılmış durum
        """
        self.current_state = MultiAgentState(
            query=query,
            session_id=session_id
        )
        return self.current_state
    
    def update_state(self, updates: Dict[str, Any]) -> MultiAgentState:
        """
        Durumu günceller
        
        Args:
            updates: Güncellenecek alanlar
            
        Returns:
            Güncellenmiş durum
        """
        for key, value in updates.items():
            if hasattr(self.current_state, key):
                setattr(self.current_state, key, value)
        
        return self.current_state
    
    def get_state(self) -> MultiAgentState:
        """
        Mevcut durumu döndürür
        
        Returns:
            Mevcut durum
        """
        return self.current_state
    
    def reset_state(self):
        """Durumu sıfırlar"""
        self.current_state = MultiAgentState()
    
    def is_workflow_complete(self) -> bool:
        """
        Workflow'un tamamlanıp tamamlanmadığını kontrol eder
        
        Returns:
            Workflow tamamlandı mı
        """
        return (
            self.current_state.retrieval_performed and
            self.current_state.qa_performed and
            self.current_state.source_tracking_performed and
            self.current_state.cross_document_performed
        )
    
    def get_progress_summary(self) -> Dict[str, bool]:
        """
        İlerleme özeti döndürür
        
        Returns:
            İlerleme durumu
        """
        return {
            "retrieval_performed": self.current_state.retrieval_performed,
            "qa_performed": self.current_state.qa_performed,
            "source_tracking_performed": self.current_state.source_tracking_performed,
            "cross_document_performed": self.current_state.cross_document_performed,
            "workflow_complete": self.is_workflow_complete()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Durumu dictionary'ye dönüştürür
        
        Returns:
            Dictionary formatında durum
        """
        return {
            "query": self.current_state.query,
            "detected_language": self.current_state.detected_language,
            "messages": [msg.dict() if hasattr(msg, 'dict') else str(msg) for msg in self.current_state.messages],
            "retrieved_documents": self.current_state.retrieved_documents,
            "qa_response": self.current_state.qa_response,
            "sources": self.current_state.sources,
            "cited_response": self.current_state.cited_response,
            "retrieval_performed": self.current_state.retrieval_performed,
            "qa_performed": self.current_state.qa_performed,
            "source_tracking_performed": self.current_state.source_tracking_performed,
            "cross_document_performed": self.current_state.cross_document_performed,
            "cross_document_analysis": self.current_state.cross_document_analysis,
            "session_id": self.current_state.session_id,
            "metadata": self.current_state.metadata
        } 