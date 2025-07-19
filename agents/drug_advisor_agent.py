"""
DrugBot - İlaç Danışmanı Agent
"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from config.models import get_llm_model
from langchain_core.prompts import PromptTemplate

class DrugAdvisorAgent(BaseAgent):
    """İlaç danışmanlığı yapan agent"""
    
    def __init__(self, client=None, vectorstore=None):
        super().__init__(
            name="drug_advisor_agent",
            description="İlaç yan etkileri, yemek etkileşimleri ve kullanım tavsiyeleri hakkında bilgi sağlar"
        )
        self.client = client or get_llm_model()
        self.vectorstore = vectorstore
        self.drug_prompt_template = self._create_drug_prompt_template()
    
    def _create_drug_prompt_template(self) -> PromptTemplate:
        """DrugBot için özel prompt template'i oluşturur"""
        template = """
Sen uzman bir ilaç danışmanı yapay zekasın. İlaçların yan etkileri, yemek etkileşimleri ve kullanım tavsiyeleri konusunda bilgi sağlarsın.

ÖNEMLI GÜVENLİK KURALLARI:
1. Bu bilgiler yalnızca genel bilgilendirme amaçlıdır
2. Kesinlikle teşhis koymak veya tedavi önermek yok
3. Her zaman doktora danışmayı tavsiye et
4. Acil durumlarda hemen doktora gitmeyi söyle

Kullanıcının Sorusu: {question}

İlaç Bilgileri:
{documents}

Dil Tercihi: {language}

Yanıtlarken:
1. Sorulan ilaç hakkında temel bilgiyi ver
2. Yan etkileri açıkla
3. Yemek etkileşimlerini belirt (aç karın mı tok karın mı)
4. Kullanım zamanlaması hakkında bilgi ver
5. Önemli uyarıları ekle
6. Soruya uygun dilde yanıt ver (Türkçe/İngilizce)
7. Güvenlik uyarısı ile bitir

Örnek Yanıt Formatı:
🔍 **İlaç Bilgisi:** [İlaç adı ve temel bilgi]
⚠️ **Yan Etkileri:** [Başlıca yan etkiler]
🍽️ **Yemek Etkileşimi:** [Aç karın/tok karın tavsiyeleri]
⏰ **Kullanım Zamanı:** [Ne zaman alınmalı]
🚨 **Önemli Uyarılar:** [Özel durumlar]

💡 **Hatırlatma:** Bu bilgiler genel bilgilendirme amaçlıdır. Kesinlikle doktorunuza danışın.

Yanıt:
"""
        return PromptTemplate(
            template=template,
            input_variables=["question", "documents", "language"]
        )
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        İlaç danışmanlığı işlemini gerçekleştirir
        
        Args:
            state: Mevcut durum (query, retrieved_documents ve detected_language içermeli)
            
        Returns:
            Yanıt ve güncellenmiş durum
        """
        query = state.get("query", "")
        retrieved_documents = state.get("retrieved_documents", [])
        detected_language = state.get("detected_language", "tr")
        
        print(f"💊 DrugBot - Dil: {detected_language}, Sorgu: '{query[:50]}...'")
        
        # Basit güvenlik kontrolü
        if len(query.strip().split()) < 2:
            safety_message = self._get_safety_message(detected_language)
            state["drug_response"] = safety_message
            state["drug_consultation_performed"] = True
            return state
        
        if not query or not retrieved_documents:
            no_info_message = self._get_no_info_message(detected_language)
            state["drug_response"] = no_info_message
            state["drug_consultation_performed"] = True
            return state
        
        # İlaç belgelerini formatla
        formatted_docs = self._format_drug_documents(retrieved_documents)
        
        # Dil tespiti
        language_text = "Türkçe" if detected_language == "tr" else "English"
        
        # Prompt oluştur ve LLM'e gönder
        prompt = self.drug_prompt_template.format(
            question=query,
            documents=formatted_docs,
            language=language_text
        )
        
        print(f"📝 DrugBot prompt uzunluğu: {len(prompt)} karakter")
        
        try:
            if hasattr(self.client, 'chat'):
                # OpenAI client
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Sen uzman bir ilaç danışmanı yapay zekasın."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=2000
                )
                drug_response = response.choices[0].message.content
            else:
                # LangChain client
                response = self.client.invoke(prompt)
                drug_response = response.content if hasattr(response, 'content') else str(response)
            
            # Güvenlik uyarısı ekle
            safety_warning = self._get_safety_warning(detected_language)
            drug_response = f"{drug_response}\n\n{safety_warning}"
            
            print(f"✅ DrugBot yanıtı alındı - Uzunluk: {len(drug_response)} karakter")
            
            # Yanıtı duruma ekle
            state["drug_response"] = drug_response
            state["drug_consultation_performed"] = True
            
            return state
            
        except Exception as e:
            print(f"❌ DrugBot hatası: {e}")
            error_message = self._get_error_message(detected_language)
            state["drug_response"] = error_message
            state["drug_consultation_performed"] = True
            return state
    
    def _format_drug_documents(self, documents: List[Dict[str, Any]]) -> str:
        """
        İlaç belgelerini prompt için formatlar
        
        Args:
            documents: Formatlanacak ilaç belgeleri
            
        Returns:
            Formatlanmış belge metni
        """
        formatted = []
        
        for i, doc in enumerate(documents, 1):
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            drug_name = metadata.get("drug_name", "Bilinmeyen İlaç")
            source = metadata.get("source", "OnSIDES")
            
            header = f"İlaç Bilgisi {i} - {drug_name} (Kaynak: {source}):"
            
            formatted.append(f"""
{header}
{content}
---
""")
        
        return "\n".join(formatted)
    
    def _get_safety_message(self, language: str) -> str:
        """Güvenlik mesajı döndürür"""
        if language == "tr":
            return """
🏥 **DrugBot Güvenlik Mesajı**

Bu sistem ilaç bilgileri hakkında genel bilgilendirme sağlar.

⚠️ **Önemli Uyarılar:**
- Kesinlikle teşhis koymam veya tedavi önermem
- Acil durumlarda hemen doktora gidin
- İlaç kullanımı konusunda mutlaka doktorunuza danışın

Lütfen sorunuzu daha detaylı olarak belirtin.
"""
        else:
            return """
🏥 **DrugBot Safety Message**

This system provides general information about medications.

⚠️ **Important Warnings:**
- I never diagnose or recommend treatment
- In emergencies, consult a doctor immediately
- Always consult your doctor about medication use

Please specify your question in more detail.
"""
    
    def _get_no_info_message(self, language: str) -> str:
        """Bilgi bulunmadığında mesaj döndürür"""
        if language == "tr":
            return """
🔍 **Bilgi Bulunamadı**

Aradığınız ilaç hakkında veritabanımda bilgi bulunmadı.

💡 **Öneriler:**
- İlaç adını doğru yazdığınızdan emin olun
- Farklı kelimeler kullanarak tekrar deneyin
- Doktorunuza veya eczacınıza danışın

⚠️ **Güvenlik Uyarısı:** Bu sistem yalnızca genel bilgilendirme amaçlıdır.
"""
        else:
            return """
🔍 **No Information Found**

No information about the requested medication was found in our database.

💡 **Suggestions:**
- Make sure you spelled the medication name correctly
- Try different keywords
- Consult your doctor or pharmacist

⚠️ **Safety Warning:** This system is for general information only.
"""
    
    def _get_safety_warning(self, language: str) -> str:
        """Güvenlik uyarısı döndürür"""
        if language == "tr":
            return """
🚨 **ÖNEMLİ GÜVENLİK UYARISI**

Bu bilgiler yalnızca genel bilgilendirme amaçlıdır:
- Kesinlikle tıbbi tavsiye değildir
- Doktorunuzun reçetesini değiştirmeyin
- Yan etki yaşarsanız hemen doktora gidin
- Acil durumlarda 112'yi arayın

💊 **Doktorunuza danışmadan ilaç kullanmayın!**
"""
        else:
            return """
🚨 **IMPORTANT SAFETY WARNING**

This information is for general educational purposes only:
- This is not medical advice
- Do not change your doctor's prescription
- If you experience side effects, see a doctor immediately
- Call emergency services in urgent situations

💊 **Do not use medication without consulting your doctor!**
"""
    
    def _get_error_message(self, language: str) -> str:
        """Hata mesajı döndürür"""
        if language == "tr":
            return """
❌ **Sistem Hatası**

Üzgünüm, sorgunuzu işlerken bir hata oluştu.

💡 **Öneriler:**
- Lütfen tekrar deneyin
- Sorunuzu farklı şekilde sorun
- Doktorunuza danışın

⚠️ **Güvenlik:** Bu sistem tıbbi tavsiye vermez.
"""
        else:
            return """
❌ **System Error**

Sorry, an error occurred while processing your question.

💡 **Suggestions:**
- Please try again
- Rephrase your question
- Consult your doctor

⚠️ **Safety:** This system does not provide medical advice.
""" 

    def get_drug_advice(self, query: str, context: str = "") -> str:
        """
        Basit ilaç danışmanlığı
        
        Args:
            query: Kullanıcı sorusu
            context: İlaç bilgileri context'i
            
        Returns:
            İlaç danışmanlığı yanıtı
        """
        # Prompt oluştur
        prompt = f"""
Sen uzman bir ilaç danışmanı yapay zekasın. İlaçların yan etkileri, yemek etkileşimleri ve kullanım tavsiyeleri konusunda bilgi sağlarsın.

ÖNEMLI GÜVENLİK KURALLARI:
1. Bu bilgiler yalnızca genel bilgilendirme amaçlıdır
2. Kesinlikle teşhis koymak veya tedavi önermek yok
3. Her zaman doktora danışmayı tavsiye et
4. Acil durumlarda hemen doktora gitmeyi söyle

Kullanıcının Sorusu: {query}

İlaç Bilgileri:
{context}

Yanıtlarken:
1. Sorulan ilaç hakkında temel bilgiyi ver
2. Yan etkileri açıkla
3. Yemek etkileşimlerini belirt (aç karın mı tok karın mı)
4. Kullanım zamanlaması hakkında bilgi ver
5. Önemli uyarıları ekle
6. Güvenlik uyarısı ile bitir

Örnek Yanıt Formatı:
🔍 **İlaç Bilgisi:** [İlaç adı ve temel bilgi]
⚠️ **Yan Etkileri:** [Başlıca yan etkiler]
🍽️ **Yemek Etkileşimi:** [Aç karın mı tok karın mı]
⏰ **Kullanım Zamanlaması:** [Ne zaman alınmalı]
❗ **Uyarılar:** [Önemli uyarılar]
🏥 **Güvenlik Uyarısı:** Kesinlikle doktorunuza danışın!
"""
        
        try:
            if hasattr(self.client, 'chat'):
                # OpenAI client
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Sen uzman bir ilaç danışmanı yapay zekasın."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=2000
                )
                return response.choices[0].message.content
            else:
                # LangChain client
                response = self.client.invoke(prompt)
                return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            return f"Üzgünüm, bir hata oluştu: {str(e)}\n\n🏥 **Güvenlik Uyarısı:** Kesinlikle doktorunuza danışın!"

    def get_drug_consultation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orijinal get_drug_advice methodu (LangGraph için)
        """
        # ... existing code ... 