"""
Question-answering agent
"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from config.models import get_llm_model
from langchain_core.prompts import PromptTemplate

class QAAgent(BaseAgent):
    """Agent that performs question-answering operations"""
    
    def __init__(self):
        super().__init__(
            name="qa_agent",
            description="Answers questions based on information retrieved from documents"
        )
        self.llm = get_llm_model()
        self.universal_prompt_template = self._create_universal_prompt_template()
    
    def _create_universal_prompt_template(self) -> PromptTemplate:
        """Universal QA prompt template - supports cross-document analysis"""
        template = """
You are given the following information from grant documents and a question.
Based on this information, answer the question accurately and in detail.

IMPORTANT: Respond in the same language as the question. If the question is in Turkish, respond in Turkish. If in English, respond in English. If in Italian, respond in Italian.

Given Documents:
{documents}

Cross-Document Analysis (if available):
{cross_document_analysis}

Question: {question}

When answering:
1. Use the information from the given documents AND cross-document analysis
2. If cross-document analysis provides grant comparisons or synthesis, incorporate that into your answer
3. Specify which document each piece of information comes from
4. If comparing multiple grants, highlight the differences and similarities clearly
5. If the answer involves multiple grants, use the cross-document insights
6. Respond in the SAME LANGUAGE as the question
7. Provide a detailed and clear explanation that leverages both document content and cross-document insights

Answer:
"""
        return PromptTemplate(
            template=template,
            input_variables=["documents", "question", "cross_document_analysis"]
        )
    


    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Soru-cevap işlemini gerçekleştirir
        
        Args:
            state: Mevcut durum (query, retrieved_documents ve detected_language içermeli)
            
        Returns:
            Yanıt ve güncellenmiş durum
        """
        query = state.get("query", "")
        retrieved_documents = state.get("retrieved_documents", [])
        detected_language = state.get("detected_language", "tr")
        cross_document_analysis = state.get("cross_document_analysis", {})
        
        print(f"🤖 QA Agent - Dil: {detected_language}, Sorgu: '{query[:50]}...'")
        
        # Basit relevans kontrolü - sadece çok kısa genel sorular için
        if len(query.strip().split()) < 3:
            simple_greetings = ['hello', 'hi', 'hey', 'merhaba', 'selam', 'ciao', 'salve']
            if any(greeting in query.lower() for greeting in simple_greetings):
                # o4-mini'nin doğal dil algılamasına güven - soru hangi dildeyse o dilde yanıt ver
                state["qa_response"] = "I'm designed to answer questions about AMIF grant documents. Please ask me about grant procedures, eligibility criteria, or application requirements."
                state["qa_performed"] = True
                return state
        
        if not query or not retrieved_documents:
            state["qa_response"] = "I couldn't find sufficient information to answer your question."
            state["qa_performed"] = True
            return state
        
        # Belgeleri formatla
        formatted_docs = self._format_documents(retrieved_documents)
        
        # Cross-document analysis'i formatla
        formatted_cross_analysis = self._format_cross_document_analysis(cross_document_analysis)
        
        # Evrensel prompt kullan - cross-document analysis ile
        prompt = self.universal_prompt_template
        print(f"🌍 Cross-document destekli prompt kullanılıyor")
        
        # Prompt oluştur ve LLM'e gönder
        prompt = prompt.format(
            documents=formatted_docs,
            question=query,
            cross_document_analysis=formatted_cross_analysis
        )
        
        print(f"📝 Prompt uzunluğu: {len(prompt)} karakter")
        
        response = self.llm.invoke(prompt)
        
        print(f"✅ LLM yanıtı alındı - Uzunluk: {len(response.content)} karakter")
        
        # Yanıtı duruma ekle
        state["qa_response"] = response.content
        state["qa_performed"] = True
        
        return state
    
    def _format_documents(self, documents: List[Dict[str, Any]]) -> str:
        """
        Belgeleri prompt için formatlar - dil algılamasız
        
        Args:
            documents: Formatlanacak belgeler
            
        Returns:
            Formatlanmış belge metni
        """
        formatted = []
        
        for i, doc in enumerate(documents, 1):
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            filename = metadata.get("filename", "Unknown Document")
            page_number = metadata.get("page_number", "Unknown page")
            
            header = f"Document {i} - {filename} (Page {page_number}):"
            
            formatted.append(f"""
{header}
{content}
---
""")
        
        return "\n".join(formatted)
    
    def _format_cross_document_analysis(self, cross_analysis: Dict[str, Any]) -> str:
        """
        Cross-document analysis sonuçlarını formatlar
        
        Args:
            cross_analysis: Cross-document analysis sonuçları
            
        Returns:
            Formatlanmış cross-document analizi
        """
        if not cross_analysis:
            return "No cross-document analysis available."
        
        formatted_parts = []
        
        # Grant grupları
        grant_groups = cross_analysis.get("grant_groups", {})
        if grant_groups:
            formatted_parts.append(f"Grant Groups Analyzed: {len(grant_groups)} groups")
            for grant_id, doc_count in grant_groups.items():
                formatted_parts.append(f"  - {grant_id}: {doc_count} documents")
        
        # Karşılaştırma sonuçları
        comparison = cross_analysis.get("comparison", {})
        if comparison and comparison.get("comparison_type") == "cross_grant":
            formatted_parts.append(f"\nGrant Comparison Analysis:")
            formatted_parts.append(comparison.get("analysis", "No comparison analysis available"))
            formatted_parts.append(f"Grants Compared: {', '.join(comparison.get('grants_compared', []))}")
        
        # Sentezlenmiş yanıt
        synthesized_answer = cross_analysis.get("synthesized_answer", "")
        if synthesized_answer and "hatası" not in synthesized_answer.lower():
            formatted_parts.append(f"\nSynthesized Cross-Document Insights:")
            formatted_parts.append(synthesized_answer)
        
        # İlişki analizi
        relationships = cross_analysis.get("relationships", {})
        common_themes = relationships.get("common_themes", [])
        if common_themes:
            formatted_parts.append(f"\nCommon Themes Across Documents:")
            for theme in common_themes[:5]:  # İlk 5 tema
                formatted_parts.append(f"  - {theme.get('theme', '')}: {theme.get('frequency', 0)} occurrences")
        
        return "\n".join(formatted_parts) if formatted_parts else "Cross-document analysis completed but no significant insights found." 