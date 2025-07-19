"""
Supervisor ajanı - Diğer ajanları koordine eder
"""

from typing import Dict, Any, Literal
from langgraph.types import Command
from agents.base_agent import BaseAgent

class SupervisorAgent(BaseAgent):
    """Diğer ajanları koordine eden supervisor ajan"""
    
    def __init__(self):
        super().__init__(
            name="supervisor",
            description="Diğer ajanları koordine eder ve workflow'u yönetir"
        )
    
    def execute(self, state: Dict[str, Any]) -> Command[Literal["document_retriever", "qa_agent", "cross_document", "source_tracker", "__end__"]]:
        """
        Workflow koordinasyonunu gerçekleştirir
        
        Args:
            state: Mevcut durum
            
        Returns:
            Sonraki ajan için Command
        """
        # Durum kontrolü
        retrieval_performed = state.get("retrieval_performed", False)
        qa_performed = state.get("qa_performed", False)
        cross_document_performed = state.get("cross_document_performed", False)
        source_tracking_performed = state.get("source_tracking_performed", False)
        
        # Workflow adımları
        if not retrieval_performed:
            print("🎯 Supervisor: Belge arama ajanına yönlendiriliyor...")
            return Command(goto="document_retriever")
        
        elif not cross_document_performed:
            print("🎯 Supervisor: Cross-document analiz ajanına yönlendiriliyor...")
            return Command(goto="cross_document")
        
        elif not qa_performed:
            print("🎯 Supervisor: QA ajanına yönlendiriliyor...")
            return Command(goto="qa_agent")
        
        elif not source_tracking_performed:
            print("🎯 Supervisor: Kaynak takip ajanına yönlendiriliyor...")
            return Command(goto="source_tracker")
        
        else:
            print("🎯 Supervisor: Workflow tamamlandı!")
            return Command(goto="__end__") 