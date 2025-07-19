"""
Basit OpenAI QA Agent - Doğrudan OpenAI API kullanır
"""

import os
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from config.settings import settings

class SimpleQAAgent:
    """Basit QA Agent - OpenAI o4-mini kullanır"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="o4-mini",
            api_key=settings.OPENAI_API_KEY,
            base_url="https://api.openai.com/v1",
            temperature=0.1
        )
        print(f"🤖 SimpleQA Agent başlatıldı - Model: o4-mini")
    
    def generate_response(self, query: str, documents: List[Dict]) -> str:
        """
        Verilen belgeler ve sorgu ile OpenAI yanıtı oluştur
        
        Args:
            query: Kullanıcı sorusu
            documents: Bulunan belgeler [{'content': str, 'source': str, 'page': str}]
            
        Returns:
            OpenAI'dan gelen yanıt
        """
        try:
            print(f"🧠 OpenAI QA sistemi çalışıyor - Sorgu: '{query[:50]}...'")
            print(f"📄 {len(documents)} belge işleniyor...")
            
            # Sorunun dilini algıla
            query_language = self._detect_language(query)
            print(f"🌍 Algılanan dil: {query_language}")
            
            # Belgeleri formatla
            formatted_docs = self._format_documents(documents)
            
            # Dile göre prompt oluştur
            prompt = self._create_multilingual_prompt(query, formatted_docs, query_language)
            
            print(f"📝 Prompt uzunluğu: {len(prompt)} karakter")
            
            # OpenAI API çağrısı
            response = self.llm.invoke(prompt)
            
            print(f"✅ OpenAI yanıtı alındı - {len(response.content)} karakter")
            
            return response.content
            
        except Exception as e:
            print(f"❌ OpenAI QA hatası: {e}")
            return f"Özür dilerim, yanıt oluştururken bir hata oluştu: {str(e)}"
    
    def _detect_language(self, text: str) -> str:
        """Metnin dilini algıla"""
        # Basit anahtar kelime bazlı dil algılama
        text_lower = text.lower()
        
        # Türkçe karakterler ve kelimeler
        turkish_indicators = ['ı', 'ğ', 'ş', 'ç', 'ö', 'ü', 'nedir', 'nasıl', 'neden', 'hangi', 'ne', 'kim', 'nerede', 'başvuru', 'süreç', 'gider', 'maliyet']
        
        # İtalyanca karakterler ve kelimeler  
        italian_indicators = ['è', 'ò', 'à', 'ù', 'ì', 'che', 'come', 'quando', 'dove', 'perché', 'cosa', 'chi', 'quale', 'processo', 'costi', 'spese']
        
        # İngilizce kelimeler
        english_indicators = ['what', 'how', 'when', 'where', 'why', 'who', 'which', 'process', 'requirements', 'costs', 'application', 'specific']
        
        # Skorlama
        turkish_score = sum(1 for indicator in turkish_indicators if indicator in text_lower)
        italian_score = sum(1 for indicator in italian_indicators if indicator in text_lower)
        english_score = sum(1 for indicator in english_indicators if indicator in text_lower)
        
        # En yüksek skoru alan dili döndür
        if turkish_score >= italian_score and turkish_score >= english_score:
            return 'turkish'
        elif italian_score >= english_score:
            return 'italian'
        else:
            return 'english'
    
    def _create_multilingual_prompt(self, query: str, formatted_docs: str, language: str) -> str:
        """Dile göre uygun prompt oluştur"""
        
        if language == 'turkish':
            return f"""Sen AMIF (Asylum, Migration and Integration Fund) hibe belgelerindeki bilgileri kullanarak soruları yanıtlayan bir uzman asistansın.

Aşağıdaki belgelerden elde edilen bilgileri kullanarak soruyu yanıtla:

{formatted_docs}

Soru: {query}

Yanıtlarken:
1. Sadece verilen belgelerden elde edilen bilgileri kullan
2. Yanıtını TÜRKÇE ver
3. Hangi belgeden hangi bilgiyi aldığını belirt
4. Detaylı ve anlaşılır bir açıklama yap
5. Eğer bilgi belgelerdeYoksa, bunu belirt

Yanıt:"""
        
        elif language == 'italian':
            return f"""Sei un assistente esperto che risponde alle domande utilizzando le informazioni contenute nei documenti dei fondi AMIF (Asylum, Migration and Integration Fund).

Utilizza le informazioni ottenute dai seguenti documenti per rispondere alla domanda:

{formatted_docs}

Domanda: {query}

Quando rispondi:
1. Utilizza solo le informazioni ottenute dai documenti forniti
2. Rispondi in ITALIANO
3. Indica da quale documento hai ottenuto quali informazioni
4. Fornisci una spiegazione dettagliata e comprensibile
5. Se le informazioni non sono presenti nei documenti, indicalo

Risposta:"""
        
        else:  # English
            return f"""You are an expert assistant that answers questions using information from AMIF (Asylum, Migration and Integration Fund) documents.

Use the information obtained from the following documents to answer the question:

{formatted_docs}

Question: {query}

When answering:
1. Only use information obtained from the provided documents
2. Answer in ENGLISH
3. Indicate which document you obtained which information from
4. Provide a detailed and understandable explanation
5. If information is not available in the documents, indicate this

Answer:"""
    
    def _format_documents(self, documents: List[Dict]) -> str:
        """Belgeleri prompt için formatla"""
        formatted = ""
        
        for i, doc in enumerate(documents, 1):
            source = doc.get('clean_source', 'Bilinmeyen kaynak')
            page = doc.get('page', 'Sayfa bilgisi yok')
            content = doc.get('content', '')[:800]  # İlk 800 karakter
            
            formatted += f"\n--- Belge {i} ---\n"
            formatted += f"Kaynak: {source}\n"
            formatted += f"Sayfa: {page}\n"
            formatted += f"İçerik: {content}\n\n"
        
        return formatted 