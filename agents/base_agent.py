"""
Temel ajan sınıfı
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from langchain_core.messages import BaseMessage

class BaseAgent(ABC):
    """Tüm ajanlar için temel sınıf"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ajanın ana çalışma mantığı
        
        Args:
            state: Mevcut durum
            
        Returns:
            Güncellenmiş durum
        """
        pass
    
    def format_response(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Yanıt formatlar
        
        Args:
            content: Yanıt içeriği
            metadata: Ek bilgiler
            
        Returns:
            Formatlanmış yanıt
        """
        return {
            "content": content,
            "agent": self.name,
            "metadata": metadata or {}
        } 