"""
Document retrieval agent
"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from ingestion.vector_store import search_documents, get_collection_info

class DocumentRetrieverAgent(BaseAgent):
    """Agent that performs document search operations"""
    
    def __init__(self, vector_store=None):
        super().__init__(
            name="document_retriever",
            description="Searches for relevant documents from vector database based on query"
        )
        # vector_store parametresi compatibility için, ama kullanmıyoruz
    
    def _detect_language(self, text: str) -> str:
        """
        Simple language detection
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code ('tr', 'en', 'it')
        """
        text_lower = text.lower()
        
        # Turkish indicators
        turkish_indicators = [
            'nedir', 'nelerdir', 'nasıl', 'ne', 'hangi', 'için', 'ile', 'bir', 'bu', 'şu',
            'mı', 'mi', 'mu', 'mü', 'da', 'de', 'ta', 'te', 'la', 'le', 'ın', 'in', 'un', 'ün',
            'hibe', 'başvuru', 'proje', 'belgeler', 'kriterler', 'süreç'
        ]
        
        # English indicators  
        english_indicators = [
            'what', 'how', 'which', 'where', 'when', 'why', 'is', 'are', 'the', 'and', 'or',
            'in', 'on', 'at', 'for', 'with', 'by', 'from', 'to', 'of', 'grant', 'application',
            'project', 'documents', 'criteria', 'process', 'requirements', 'eligibility', 
            'personnel', 'costs', 'budget', 'funding', 'can', 'should', 'must', 'will',
            'this', 'that', 'these', 'those', 'do', 'does', 'did', 'have', 'has', 'had'
        ]
        
        # Italian indicators
        italian_indicators = [
            'che', 'cosa', 'come', 'quale', 'dove', 'quando', 'perché', 'è', 'sono', 'il', 'la',
            'di', 'a', 'da', 'in', 'con', 'su', 'per', 'tra', 'fra', 'sovvenzioni', 'domanda',
            'progetto', 'documenti', 'criteri', 'processo'
        ]
        
        # Split words
        words = text_lower.split()
        
        # Counter for each language - use exact match
        tr_score = sum(1 for word in words if word in turkish_indicators)
        en_score = sum(1 for word in words if word in english_indicators)
        it_score = sum(1 for word in words if word in italian_indicators)
        
        print(f"🔍 Language scores - TR: {tr_score}, EN: {en_score}, IT: {it_score}")
        print(f"📝 Words: {words}")
        
        # Return language with highest score
        if tr_score >= en_score and tr_score >= it_score:
            return 'turkish'
        elif en_score >= it_score:
            return 'english' 
        else:
            return 'italian'
    
    def _is_query_relevant(self, query: str, language: str) -> bool:
        """
        Sorgunun grant belgeleri ile ilgili olup olmadığını kontrol eder
        
        Args:
            query: Soru metni
            language: Dil kodu ('tr' veya 'en')
            
        Returns:
            True eğer belge araması yapılması gerekiyorsa, False aksi halde
        """
        # Kişisel selamlaşma ve genel sohbet ifadeleri
        irrelevant_patterns_tr = [
            'merhaba', 'hey', 'selam', 'nasılsın', 'nasıl gidiyor', 
            'günaydın', 'iyi akşamlar', 'teşekkürler', 'sağol',
            'hoşça kal', 'görüşürüz', 'naber', 'ne var ne yok'
        ]
        
        irrelevant_patterns_en = [
            'hello', 'hi', 'hey', 'how are you', 'how is it going',
            'good morning', 'good evening', 'thank you', 'thanks',
            'goodbye', 'see you', 'what\'s up', 'how\'s life'
        ]
        
        query_lower = query.lower().strip()
        
        # Dile göre pattern kontrolü
        if language == 'tr':
            patterns = irrelevant_patterns_tr
        else:
            patterns = irrelevant_patterns_en
        
        # Kısa ve genel sorular (5 kelimeden az)
        words = query_lower.split()
        if len(words) < 3:
            for pattern in patterns:
                if pattern in query_lower:
                    return False
        
        # Grant ile ilgili anahtar kelimeler
        grant_keywords_tr = [
            'grant', 'hibe', 'amif', 'proje', 'başvuru', 'finansman',
            'bütçe', 'maliyet', 'personel', 'eligibility', 'uygunluk',
            'criteria', 'kriter', 'application', 'document', 'belge'
        ]
        
        grant_keywords_en = [
            'grant', 'amif', 'project', 'application', 'funding',
            'budget', 'cost', 'personnel', 'eligibility', 'criteria',
            'documentation', 'requirement', 'guideline', 'procedure'
        ]
        
        all_keywords = grant_keywords_tr + grant_keywords_en
        
        # Grant ile ilgili kelime varlığı kontrolü
        has_grant_keyword = any(keyword in query_lower for keyword in all_keywords)
        
        # Eğer grant kelimesi varsa, kesinlikle ilgili
        if has_grant_keyword:
            return True
        
        # Eğer hiç grant kelimesi yoksa ve kısa ise, büyük ihtimalle ilgisiz
        if len(words) < 5 and not has_grant_keyword:
            return False
        
        # Uzun sorular için varsayılan olarak ilgili kabul et
        return len(words) >= 5

    def _extract_grant_types_from_query(self, query: str) -> List[str]:
        """
        Sorgudan hangi grant tiplerinin bahsedildiğini çıkarır
        
        Args:
            query: Kullanıcı sorgusu
            
        Returns:
            Tespit edilen grant tipleri
        """
        query_lower = query.lower()
        grant_types = []
        
        # Grant tip keyword mapping
        grant_mappings = {
            'women': ['women', 'woman', 'kadın', 'kadınlar', 'female', 'gender'],
            'children': ['children', 'child', 'çocuk', 'çocuklar', 'youth', 'minors'],
            'health': ['health', 'sağlık', 'healthcare', 'medical', 'tıbbi'],
            'digital': ['digital', 'dijital', 'technology', 'teknoloji', 'online'],
            'pathways': ['pathways', 'education', 'eğitim', 'training', 'öğretim']
        }
        
        for grant_type, keywords in grant_mappings.items():
            if any(keyword in query_lower for keyword in keywords):
                grant_types.append(grant_type)
        
        return grant_types
    
    def _perform_multi_search(self, query: str, grant_types: List[str]) -> List[Dict[str, Any]]:
        """
        Çoklu arama stratejisi - farklı grant tipleri için ayrı aramalar yapar
        
        Args:
            query: Ana sorgu
            grant_types: Tespit edilen grant tipleri
            
        Returns:
            Birleştirilmiş arama sonuçları
        """
        all_documents = []
        unique_sources = set()
        
        # 1. Ana sorgu ile arama
        main_results = search_documents(query, k=6)
        for doc in main_results:
            source = doc.metadata.get('source', '')
            if source not in unique_sources:
                unique_sources.add(source)
                all_documents.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
        
        # 2. Her grant tipi için spesifik arama
        if grant_types:
            for grant_type in grant_types:
                # Grant-specific search terms
                search_terms = {
                    'women': 'AMIF-2025 WOMEN grant eligibility criteria budget',
                    'children': 'AMIF-2025 CHILDREN grant eligibility criteria budget',
                    'health': 'AMIF-2025 HEALTH grant eligibility criteria budget',
                    'digital': 'AMIF-2025 DIGITAL grant eligibility criteria budget',
                    'pathways': 'AMIF-2025 PATHWAYS grant eligibility criteria budget'
                }
                
                search_query = search_terms.get(grant_type, f'AMIF-2025 {grant_type.upper()}')
                grant_results = search_documents(search_query, k=4)
                
                for doc in grant_results:
                    source = doc.metadata.get('source', '')
                    if source not in unique_sources:
                        unique_sources.add(source)
                        all_documents.append({
                            "content": doc.page_content,
                            "metadata": doc.metadata
                        })
        
        print(f"📊 Çoklu arama: {len(main_results)} ana + {len(all_documents) - len(main_results)} ek = {len(all_documents)} toplam sonuç")
        return all_documents

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Belge arama işlemini gerçekleştirir
        
        Args:
            state: Mevcut durum (query içermeli)
            
        Returns:
            Bulunan belgeler ve güncellenmiş durum
        """
        query = state.get("query", "")
        
        if not query:
            state["retrieved_documents"] = []
            state["retrieval_performed"] = True
            state["detected_language"] = "tr"
            return state
        
        # Basit dil algılama
        detected_language = self._detect_language(query)
        state["detected_language"] = detected_language
        
        # Sorgunun relevansını kontrol et
        if not self._is_query_relevant(query, detected_language):
            print(f"🚫 '{query}' sorgusu grant belgeleri ile ilgili değil, retrieval atlanıyor")
            state["retrieved_documents"] = []
            state["retrieval_performed"] = True
            return state
        
        try:
            # Grant tiplerini tespit et
            grant_types = self._extract_grant_types_from_query(query)
            print(f"🎯 Tespit edilen grant tipleri: {grant_types}")
            
            # Çoklu arama stratejisi kullan
            if len(grant_types) >= 2:
                # Karşılaştırma sorusu - çoklu arama yap
                print(f"🔄 Çoklu grant arama stratejisi kullanılıyor")
                doc_dicts = self._perform_multi_search(query, grant_types)
            else:
                # Tekli arama yap
                documents = search_documents(query, k=8)
                
                # Belgeleri dict formatına çevir
                doc_dicts = []
                for doc in documents:
                    doc_dict = {
                        "content": doc.page_content,
                        "metadata": doc.metadata
                    }
                    doc_dicts.append(doc_dict)
            
            # Durumu güncelle
            state["retrieved_documents"] = doc_dicts
            state["retrieval_performed"] = True
            state["detected_language"] = detected_language
            state["grant_types_detected"] = grant_types
            
            print(f"🔍 '{query}' için {len(doc_dicts)} sonuç bulundu")
            print(f"🌐 Algılanan dil: {detected_language}")
            
        except Exception as e:
            print(f"❌ Belge arama hatası: {e}")
            state["retrieved_documents"] = []
            state["retrieval_performed"] = True
            state["detected_language"] = detected_language
        
        return state 