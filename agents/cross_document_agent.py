"""
Cross-Document Reasoning Agent
Çoklu belge analizi, grant karşılaştırması ve belgeler arası çıkarım yapan ajan
"""

from typing import Dict, Any, List, Tuple, Set
from collections import defaultdict
import re
from agents.base_agent import BaseAgent
from config.models import get_llm_model
from langchain_core.prompts import PromptTemplate

class CrossDocumentAgent(BaseAgent):
    """
    Belgeler arası mantık yürütme ve karşılaştırma yapan ajan
    """
    
    def __init__(self):
        super().__init__(
            name="cross_document_agent",
            description="Çoklu belge analizi, grant karşılaştırması ve belgeler arası çıkarım yapar"
        )
        self.llm = get_llm_model()
        
    def _extract_grant_groups(self, documents: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Belgeleri grant gruplarına ayırır - geliştirilmiş algoritma
        
        Args:
            documents: Belge listesi
            
        Returns:
            Grant gruplarına ayrılmış belgeler
        """
        grant_groups = defaultdict(list)
        
        for doc in documents:
            metadata = doc.get('metadata', {})
            
            # 1. Önce metadata'dan grant_group'u al
            grant_group = metadata.get('grant_group')
            
            if grant_group and grant_group != 'unknown_grant':
                grant_groups[grant_group].append(doc)
                continue
            
            # 2. Metadata'da yoksa dosya adından çıkar
            filename = metadata.get('filename', '') or metadata.get('source', '')
            
            if filename:
                # AMIF-2025-TF2-AG-INTE-01-WOMEN formatında grant ID'si ara
                grant_patterns = [
                    r'(AMIF-\d{4}-TF\d+-AG-[^_]+)',  # Full pattern
                    r'(AMIF-\d{4}-[^_]+)',           # Shorter pattern
                ]
                
                grant_found = False
                for pattern in grant_patterns:
                    matches = re.findall(pattern, filename, re.IGNORECASE)
                    if matches:
                        grant_id = matches[0].upper()
                        grant_groups[grant_id].append(doc)
                        grant_found = True
                        break
                
                if not grant_found:
                    # 3. Son çare olarak içerikten grant keyword'lerini ara
                    content = doc.get('content', '').upper()
                    
                    # Bilinen grant tiplerini ara
                    grant_keywords = {
                        'AMIF-2025-TF2-AG-INTE-01-WOMEN': ['WOMEN', 'GENDER', 'FEMALE'],
                        'AMIF-2025-TF2-AG-INTE-05-CHILDREN': ['CHILDREN', 'CHILD', 'MINORS', 'YOUTH'],
                        'AMIF-2025-TF2-AG-INTE-02-HEALTH': ['HEALTH', 'MEDICAL', 'HEALTHCARE'],
                        'AMIF-2025-TF2-AG-INTE-03-DIGITAL': ['DIGITAL', 'TECHNOLOGY', 'ONLINE'],
                        'AMIF-2025-TF2-AG-INTE-04-PATHWAYS': ['PATHWAYS', 'EDUCATION', 'TRAINING']
                    }
                    
                    best_match = None
                    max_score = 0
                    
                    for grant_id, keywords in grant_keywords.items():
                        score = sum(1 for keyword in keywords if keyword in content)
                        if score > max_score:
                            max_score = score
                            best_match = grant_id
                    
                    if best_match and max_score > 0:
                        grant_groups[best_match].append(doc)
                    else:
                        grant_groups['UNKNOWN'].append(doc)
            else:
                grant_groups['UNKNOWN'].append(doc)
        
        print(f"📊 {len(grant_groups)} grant grubu tanımlandı: {list(grant_groups.keys())}")
        return dict(grant_groups)
    
    def _identify_document_types(self, filename: str) -> str:
        """
        Dosya tipini belirler (call text, FAQ, template, etc.)
        
        Args:
            filename: Dosya adı
            
        Returns:
            Belge tipi
        """
        filename_lower = filename.lower()
        
        if 'call-fiche' in filename_lower or 'call_fiche' in filename_lower:
            return 'call_document'
        elif 'faq' in filename_lower:
            return 'faq'
        elif 'template' in filename_lower:
            return 'template'
        elif 'guide' in filename_lower or 'guideline' in filename_lower:
            return 'guide'
        elif 'aga' in filename_lower:
            return 'administrative_guide'
        elif 'evaluation' in filename_lower:
            return 'evaluation_guide'
        else:
            return 'other'
    
    def _perform_cross_grant_comparison(self, grant_groups: Dict[str, List[Dict[str, Any]]], query: str) -> Dict[str, Any]:
        """
        Grant'lar arası karşılaştırma yapar
        
        Args:
            grant_groups: Grant grupları
            query: Kullanıcı sorgusu
            
        Returns:
            Karşılaştırma sonucu
        """
        if len(grant_groups) < 2:
            return {"comparison_type": "single_grant", "analysis": "Tek grant analizi"}
        
        # Karşılaştırma prompt'u
        comparison_prompt = PromptTemplate(
            template="""You are analyzing multiple AMIF grant programs for comparison.
            
Grant Groups Available:
{grant_summaries}

User Query: {query}

Please provide a detailed comparison focusing on:
1. Key differences between grants
2. Eligibility criteria variations
3. Budget allocation differences
4. Target group distinctions
5. Implementation requirements

Respond in the same language as the query.

Comparison Analysis:""",
            input_variables=["grant_summaries", "query"]
        )
        
        # Grant özetlerini hazırla
        grant_summaries = []
        for grant_id, docs in grant_groups.items():
            doc_types = [self._identify_document_types(doc.get('metadata', {}).get('filename', '')) for doc in docs]
            content_preview = docs[0].get('content', '')[:300] + "..." if docs else ""
            
            grant_summaries.append(f"""
Grant ID: {grant_id}
Document Types: {', '.join(set(doc_types))}
Document Count: {len(docs)}
Content Preview: {content_preview}
""")
        
        # LLM ile karşılaştırma yap
        try:
            response = self.llm.invoke(
                comparison_prompt.format(
                    grant_summaries="\n".join(grant_summaries),
                    query=query
                )
            )
            
            return {
                "comparison_type": "cross_grant",
                "analysis": response.content if hasattr(response, 'content') else str(response),
                "grants_compared": list(grant_groups.keys()),
                "total_documents": sum(len(docs) for docs in grant_groups.values())
            }
        except Exception as e:
            return {
                "comparison_type": "error",
                "analysis": f"Karşılaştırma hatası: {str(e)}",
                "grants_compared": list(grant_groups.keys())
            }
    
    def _analyze_document_relationships(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Belgeler arası ilişkileri analiz eder
        
        Args:
            documents: Belge listesi
            
        Returns:
            İlişki analizi
        """
        relationships = {
            "document_types": defaultdict(int),
            "common_themes": [],
            "reference_patterns": [],
            "coverage_gaps": []
        }
        
        # Belge tiplerini say
        for doc in documents:
            filename = doc.get('metadata', {}).get('filename', '')
            doc_type = self._identify_document_types(filename)
            relationships["document_types"][doc_type] += 1
        
        # Ortak temaları bul
        all_content = " ".join([doc.get('content', '') for doc in documents])
        
        # Anahtar kelime analizi
        key_themes = [
            'eligibility', 'budget', 'personnel', 'cost', 'application', 
            'deadline', 'criteria', 'evaluation', 'implementation',
            'uygunluk', 'bütçe', 'personel', 'maliyet', 'başvuru',
            'kriterler', 'değerlendirme', 'uygulama'
        ]
        
        for theme in key_themes:
            count = len(re.findall(rf'\b{theme}\b', all_content, re.IGNORECASE))
            if count > 0:
                relationships["common_themes"].append({
                    "theme": theme,
                    "frequency": count
                })
        
        return relationships
    
    def _synthesize_cross_document_answer(self, documents: List[Dict[str, Any]], query: str, grant_groups: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Çoklu belgeden sentezlenmiş yanıt oluşturur
        
        Args:
            documents: Belge listesi
            query: Kullanıcı sorgusu
            grant_groups: Grant grupları
            
        Returns:
            Sentezlenmiş yanıt
        """
        synthesis_prompt = PromptTemplate(
            template="""You are analyzing information from multiple AMIF grant documents to provide a comprehensive answer.

Document Groups:
{document_groups}

User Question: {query}

Please synthesize information from across all documents to provide:
1. A comprehensive answer based on ALL relevant documents
2. Identification of any conflicting information between documents
3. Gaps where information might be missing
4. Cross-references between related information in different documents

Important:
- Respond in the same language as the question
- Clearly indicate which documents support each piece of information
- Highlight any discrepancies or complementary information
- Provide a holistic view that combines insights from multiple sources

Synthesized Answer:""",
            input_variables=["document_groups", "query"]
        )
        
        # Belge gruplarını formatla
        document_groups = []
        for grant_id, docs in grant_groups.items():
            group_content = f"\n--- Grant Group: {grant_id} ---\n"
            for i, doc in enumerate(docs):
                filename = doc.get('metadata', {}).get('filename', f'Document {i+1}')
                content = doc.get('content', '')[:500] + "..." if len(doc.get('content', '')) > 500 else doc.get('content', '')
                group_content += f"\nFile: {filename}\nContent: {content}\n"
            document_groups.append(group_content)
        
        try:
            response = self.llm.invoke(
                synthesis_prompt.format(
                    document_groups="\n".join(document_groups),
                    query=query
                )
            )
            
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            return f"Belge sentezi hatası: {str(e)}"
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cross-document reasoning işlemini gerçekleştirir
        
        Args:
            state: Mevcut durum
            
        Returns:
            Güncellenmiş durum
        """
        documents = state.get("retrieved_documents", [])
        query = state.get("query", "")
        
        if not documents or not query:
            state["cross_document_analysis"] = {"analysis": "Yeterli belge bulunamadı"}
            state["cross_document_performed"] = True
            return state
        
        try:
            print(f"🔗 Cross-document analizi başlatılıyor: {len(documents)} belge")
            
            # Grant gruplarına ayır
            grant_groups = self._extract_grant_groups(documents)
            
            # Belge ilişkilerini analiz et
            relationships = self._analyze_document_relationships(documents)
            
            # Grant karşılaştırması (eğer birden fazla grant varsa)
            comparison_result = self._perform_cross_grant_comparison(grant_groups, query)
            
            # Sentezlenmiş yanıt oluştur
            synthesized_answer = self._synthesize_cross_document_answer(documents, query, grant_groups)
            
            # Durumu güncelle
            state["cross_document_analysis"] = {
                "grant_groups": {k: len(v) for k, v in grant_groups.items()},
                "relationships": relationships,
                "comparison": comparison_result,
                "synthesized_answer": synthesized_answer,
                "total_grants_analyzed": len(grant_groups),
                "cross_document_insights": len(relationships["common_themes"])
            }
            state["cross_document_performed"] = True
            
            print(f"✅ Cross-document analizi tamamlandı")
            print(f"🎯 {len(grant_groups)} grant grubu, {len(relationships['common_themes'])} ortak tema")
            
        except Exception as e:
            print(f"❌ Cross-document analizi hatası: {e}")
            state["cross_document_analysis"] = {"analysis": f"Analiz hatası: {str(e)}"}
            state["cross_document_performed"] = True
        
        return state 