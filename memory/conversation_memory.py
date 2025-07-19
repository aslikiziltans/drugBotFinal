"""
Gelişmiş Sohbet Bellek Yönetimi
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import hashlib
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from config.settings import settings

@dataclass
class ConversationContext:
    """Sohbet bağlamı için veri sınıfı"""
    topic_keywords: List[str]
    grant_types_mentioned: List[str]
    query_complexity: str  # simple, medium, complex
    semantic_theme: str
    response_quality: float
    processing_time: float
    sources_count: int

@dataclass 
class MemoryEntry:
    """Bellek girişi için veri sınıfı"""
    id: str
    role: str
    content: str
    timestamp: datetime
    context: ConversationContext
    metadata: Dict[str, Any]
    session_id: str
    query_hash: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary'ye dönüştür"""
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "context": asdict(self.context),
            "metadata": self.metadata,
            "session_id": self.session_id,
            "query_hash": self.query_hash
        }

class EnhancedConversationMemory:
    """Gelişmiş sohbet bellek yönetimi sınıfı"""
    
    def __init__(self, max_history: int = None, persist_path: str = None):
        self.max_history = max_history or settings.MAX_CHAT_HISTORY
        self.persist_path = persist_path or "interfaces/data/memory"
        self.conversation_history: deque = deque(maxlen=self.max_history)
        self.session_id: Optional[str] = None
        self.semantic_clusters: Dict[str, List[str]] = defaultdict(list)
        self.query_cache: Dict[str, Dict[str, Any]] = {}
        self.topic_trends: Dict[str, int] = defaultdict(int)
        
        # Persistent storage dizinini oluştur
        Path(self.persist_path).mkdir(parents=True, exist_ok=True)
        
        # Mevcut memory'yi yükle
        self._load_persistent_memory()
    
    def _generate_query_hash(self, query: str) -> str:
        """Sorgu için benzersiz hash oluştur"""
        return hashlib.md5(query.lower().encode()).hexdigest()[:16]
    
    def _extract_context(self, message: str, metadata: Dict[str, Any] = None) -> ConversationContext:
        """Mesajdan bağlam bilgilerini çıkar"""
        metadata = metadata or {}
        
        # Topic keywords çıkar
        topic_keywords = []
        grant_keywords = ['amif', 'grant', 'hibe', 'funding', 'application', 'başvuru']
        for keyword in grant_keywords:
            if keyword.lower() in message.lower():
                topic_keywords.append(keyword)
        
        # Grant tiplerini tespit et
        grant_types = []
        grant_patterns = {
            'women': ['women', 'woman', 'kadın', 'kadınlar'],
            'children': ['children', 'child', 'çocuk', 'çocuklar'],
            'health': ['health', 'sağlık', 'healthcare'],
            'digital': ['digital', 'dijital', 'technology'],
            'pathways': ['pathways', 'education', 'eğitim']
        }
        
        for grant_type, patterns in grant_patterns.items():
            if any(pattern in message.lower() for pattern in patterns):
                grant_types.append(grant_type)
        
        # Query complexity
        word_count = len(message.split())
        if word_count < 5:
            complexity = "simple"
        elif word_count < 15:
            complexity = "medium"
        else:
            complexity = "complex"
        
        # Semantic theme
        if any(word in message.lower() for word in ['compare', 'karşılaştır', 'difference', 'fark']):
            theme = "comparison"
        elif any(word in message.lower() for word in ['eligibility', 'uygunluk', 'criteria']):
            theme = "eligibility"
        elif any(word in message.lower() for word in ['budget', 'cost', 'maliyet', 'bütçe']):
            theme = "financial"
        else:
            theme = "general"
        
        return ConversationContext(
            topic_keywords=topic_keywords,
            grant_types_mentioned=grant_types,
            query_complexity=complexity,
            semantic_theme=theme,
            response_quality=metadata.get('response_quality', 0.0),
            processing_time=metadata.get('processing_time', 0.0),
            sources_count=metadata.get('sources_count', 0)
        )
    
    def add_user_message(self, message: str, metadata: Dict[str, Any] = None):
        """
        Gelişmiş kullanıcı mesajı ekleme
        
        Args:
            message: Kullanıcı mesajı
            metadata: Ek bilgiler
        """
        context = self._extract_context(message, metadata)
        query_hash = self._generate_query_hash(message)
        
        # Benzer sorgu daha önce sorulmuş mu kontrol et
        if query_hash in self.query_cache:
            context.response_quality = self.query_cache[query_hash].get('avg_quality', 0.0)
        
        entry = MemoryEntry(
            id=f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{query_hash[:8]}",
            role="user",
            content=message,
            timestamp=datetime.now(),
            context=context,
            metadata=metadata or {},
            session_id=self.session_id or "default",
            query_hash=query_hash
        )
        
        self.conversation_history.append(entry)
        self._update_semantic_clusters(entry)
        self._update_topic_trends(entry)
    
    def add_assistant_message(self, message: str, metadata: Dict[str, Any] = None):
        """
        Gelişmiş asistan mesajı ekleme
        
        Args:
            message: Asistan mesajı
            metadata: Ek bilgiler
        """
        context = self._extract_context(message, metadata)
        
        entry = MemoryEntry(
            id=f"assistant_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            role="assistant",
            content=message,
            timestamp=datetime.now(),
            context=context,
            metadata=metadata or {},
            session_id=self.session_id or "default",
            query_hash=""
        )
        
        self.conversation_history.append(entry)
        
        # Cache'i güncelle
        if hasattr(self, '_last_user_query_hash'):
            if self._last_user_query_hash not in self.query_cache:
                self.query_cache[self._last_user_query_hash] = {
                    'queries': [],
                    'responses': [],
                    'avg_quality': 0.0,
                    'total_responses': 0
                }
            
            cache_entry = self.query_cache[self._last_user_query_hash]
            cache_entry['responses'].append(message)
            cache_entry['total_responses'] += 1
            
            # Kalite puanını güncelle
            if metadata and 'response_quality' in metadata:
                current_avg = cache_entry['avg_quality']
                new_quality = metadata['response_quality']
                cache_entry['avg_quality'] = (current_avg + new_quality) / 2
    
    def _update_semantic_clusters(self, entry: MemoryEntry):
        """Semantic cluster'ları güncelle"""
        theme = entry.context.semantic_theme
        self.semantic_clusters[theme].append(entry.id)
        
        # Cluster boyutunu sınırla
        if len(self.semantic_clusters[theme]) > 50:
            self.semantic_clusters[theme] = self.semantic_clusters[theme][-50:]
    
    def _update_topic_trends(self, entry: MemoryEntry):
        """Topic trend'lerini güncelle"""
        for keyword in entry.context.topic_keywords:
            self.topic_trends[keyword] += 1
        
        for grant_type in entry.context.grant_types_mentioned:
            self.topic_trends[f"grant_{grant_type}"] += 1
    
    def get_similar_queries(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        """
        Benzer sorguları bul
        
        Args:
            query: Referans sorgu
            limit: Döndürülecek maksimum sonuç sayısı
            
        Returns:
            Benzer sorguların listesi
        """
        query_context = self._extract_context(query)
        similar_entries = []
        
        for entry in self.conversation_history:
            if entry.role == "user":
                # Semantic theme benzerliği
                theme_match = entry.context.semantic_theme == query_context.semantic_theme
                
                # Grant type overlap
                grant_overlap = len(set(entry.context.grant_types_mentioned) & 
                                  set(query_context.grant_types_mentioned))
                
                # Keyword overlap
                keyword_overlap = len(set(entry.context.topic_keywords) & 
                                    set(query_context.topic_keywords))
                
                # Similarity score
                similarity_score = 0
                if theme_match:
                    similarity_score += 3
                similarity_score += grant_overlap * 2
                similarity_score += keyword_overlap
                
                if similarity_score > 0:
                    similar_entries.append((entry, similarity_score))
        
        # Score'a göre sırala ve limit uygula
        similar_entries.sort(key=lambda x: x[1], reverse=True)
        return [entry for entry, score in similar_entries[:limit]]
    
    def get_context_aware_history(self, current_query: str, max_entries: int = 10) -> List[MemoryEntry]:
        """
        Bağlam farkında geçmiş döndür
        
        Args:
            current_query: Mevcut sorgu
            max_entries: Maksimum entry sayısı
            
        Returns:
            Bağlama uygun geçmiş
        """
        query_context = self._extract_context(current_query)
        relevant_entries = []
        
        # Son geçmişten başla
        recent_history = list(self.conversation_history)[-20:]
        
        for entry in recent_history:
            relevance_score = 0
            
            # Zaman yakınlığı
            time_diff = datetime.now() - entry.timestamp
            if time_diff < timedelta(minutes=30):
                relevance_score += 3
            elif time_diff < timedelta(hours=2):
                relevance_score += 2
            elif time_diff < timedelta(hours=24):
                relevance_score += 1
            
            # Semantic theme benzerliği
            if entry.context.semantic_theme == query_context.semantic_theme:
                relevance_score += 4
            
            # Grant type benzerliği
            grant_overlap = len(set(entry.context.grant_types_mentioned) & 
                              set(query_context.grant_types_mentioned))
            relevance_score += grant_overlap * 2
            
            if relevance_score > 0:
                relevant_entries.append((entry, relevance_score))
        
        # Relevance score'a göre sırala
        relevant_entries.sort(key=lambda x: x[1], reverse=True)
        return [entry for entry, score in relevant_entries[:max_entries]]
    
    def get_topic_trends(self) -> Dict[str, int]:
        """
        Topic trend'lerini döndür
        
        Returns:
            Topic trend'leri
        """
        return dict(self.topic_trends)
    
    def get_conversation_context(self) -> Dict[str, Any]:
        """
        Genel sohbet bağlamını döndür
        
        Returns:
            Sohbet bağlam bilgileri
        """
        if not self.conversation_history:
            return {
                "total_entries": 0,
                "semantic_themes": [],
                "top_topics": [],
                "grant_types": [],
                "avg_response_quality": 0.0
            }
        
        semantic_themes = set()
        grant_types = set()
        all_topics = []
        quality_scores = []
        
        for entry in self.conversation_history:
            semantic_themes.add(entry.context.semantic_theme)
            grant_types.update(entry.context.grant_types_mentioned)
            all_topics.extend(entry.context.topic_keywords)
            if hasattr(entry.context, 'response_quality'):
                quality_scores.append(entry.context.response_quality)
        
        # Topic frekanslarını hesapla
        from collections import Counter
        topic_counter = Counter(all_topics)
        
        return {
            "total_entries": len(self.conversation_history),
            "semantic_themes": list(semantic_themes),
            "top_topics": dict(topic_counter.most_common(5)),
            "grant_types": list(grant_types),
            "avg_response_quality": sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        }
    
    def cluster_conversations(self):
        """
        Sohbetleri cluster'lara ayır
        """
        # Semantic cluster'ları güncelle
        self.semantic_clusters.clear()
        
        for entry in self.conversation_history:
            theme = entry.context.semantic_theme
            self.semantic_clusters[theme].append(entry.id)
    
    def get_memory_clusters(self) -> Dict[str, List[str]]:
        """
        Memory cluster'larını döndür
        
        Returns:
            Cluster bilgileri
        """
        return dict(self.semantic_clusters)
    
    def get_semantic_summary(self) -> Dict[str, Any]:
        """
        Semantic analiz özeti
        
        Returns:
            Semantic analiz sonuçları
        """
        return {
            "total_conversations": len(self.conversation_history),
            "semantic_clusters": {k: len(v) for k, v in self.semantic_clusters.items()},
            "top_topics": dict(sorted(self.topic_trends.items(), 
                                    key=lambda x: x[1], reverse=True)[:10]),
            "query_cache_size": len(self.query_cache),
            "session_id": self.session_id
        }
    
    def _save_persistent_memory(self):
        """Memory'yi kalıcı olarak kaydet"""
        try:
            memory_data = {
                "conversation_history": [entry.to_dict() for entry in self.conversation_history],
                "semantic_clusters": dict(self.semantic_clusters),
                "query_cache": self.query_cache,
                "topic_trends": dict(self.topic_trends),
                "session_id": self.session_id,
                "last_updated": datetime.now().isoformat()
            }
            
            filepath = Path(self.persist_path) / f"memory_{self.session_id or 'default'}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            print(f"⚠️ Memory kaydetme hatası: {e}")
    
    def _load_persistent_memory(self):
        """Kalıcı memory'yi yükle"""
        try:
            filepath = Path(self.persist_path) / f"memory_{self.session_id or 'default'}.json"
            
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    memory_data = json.load(f)
                
                # Conversation history'yi yükle
                for entry_dict in memory_data.get("conversation_history", []):
                    # MemoryEntry'yi yeniden oluştur
                    context = ConversationContext(**entry_dict["context"])
                    entry = MemoryEntry(
                        id=entry_dict["id"],
                        role=entry_dict["role"],
                        content=entry_dict["content"],
                        timestamp=datetime.fromisoformat(entry_dict["timestamp"]),
                        context=context,
                        metadata=entry_dict["metadata"],
                        session_id=entry_dict["session_id"],
                        query_hash=entry_dict["query_hash"]
                    )
                    self.conversation_history.append(entry)
                
                # Diğer verileri yükle
                self.semantic_clusters = defaultdict(list, memory_data.get("semantic_clusters", {}))
                self.query_cache = memory_data.get("query_cache", {})
                self.topic_trends = defaultdict(int, memory_data.get("topic_trends", {}))
                
                print(f"✅ Memory yüklendi: {len(self.conversation_history)} entry")
                
        except Exception as e:
            print(f"⚠️ Memory yükleme hatası: {e}")
    
    def clear_history(self):
        """Tüm geçmişi temizle"""
        self.conversation_history.clear()
        self.semantic_clusters.clear()
        self.query_cache.clear()
        self.topic_trends.clear()
        self._save_persistent_memory()
    
    def set_session_id(self, session_id: str):
        """
        Session ID belirle ve persistent memory'yi kaydet
        
        Args:
            session_id: Session kimliği
        """
        # Mevcut session'ı kaydet
        if self.session_id:
            self._save_persistent_memory()
        
        # Yeni session'ı başlat
        self.session_id = session_id
        self.conversation_history.clear()
        self.semantic_clusters.clear()
        self.query_cache.clear()
        self.topic_trends.clear()
        
        # Yeni session'ın memory'sini yükle
        self._load_persistent_memory()
    
    def get_session_id(self) -> Optional[str]:
        """Session ID döndür"""
        return self.session_id
    
    def __del__(self):
        """Destructor - memory'yi kaydet"""
        try:
            if hasattr(self, 'conversation_history') and self.conversation_history:
                self._save_persistent_memory()
        except:
            pass 