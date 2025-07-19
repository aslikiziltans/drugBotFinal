"""
Text processing and chunking operations
"""

from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from config.settings import settings
from ingestion.vector_store import add_documents_to_vector_store

class TextProcessor:
    """Text processing and chunking class"""
    
    def __init__(self):
        """Initialize text splitter"""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def process_documents(self, documents: List[Document]) -> List[Document]:
        """
        Process documents and split into chunks
        
        Args:
            documents: Documents to process
            
        Returns:
            Processed and chunked documents
        """
        if not documents:
            return []
        
        print(f"📝 {len(documents)} belge işleniyor...")
        
        all_chunks = []
        
        for doc in documents:
            # Belgeyi chunk'lara böl
            chunks = self.text_splitter.split_documents([doc])
            
            # Her chunk için metadata güncelle
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'chunk_size': len(chunk.page_content)
                })
            
            all_chunks.extend(chunks)
            
            print(f"📄 İşleniyor: {doc.metadata.get('source', 'unknown')}")
            print(f"✂️  {len(chunks)} parçaya bölündü")
        
        print(f"🎉 Toplam {len(all_chunks)} metin parçası oluşturuldu")
        return all_chunks
    
    def process_and_store_documents(self, documents: List[Document]) -> bool:
        """
        Belgeleri işle ve vector store'a ekle
        
        Args:
            documents: İşlenecek belgeler
            
        Returns:
            bool: Başarılı ise True
        """
        try:
            # Belgeleri işle
            processed_docs = self.process_documents(documents)
            
            if not processed_docs:
                print("⚠️  İşlenecek belge bulunamadı")
                return False
            
            # Vector store'a ekle
            success = add_documents_to_vector_store(processed_docs)
            
            return success
            
        except Exception as e:
            print(f"❌ Belge işleme ve saklama hatası: {e}")
            return False
    
    def _clean_text(self, text: str) -> str:
        """
        Metni temizler
        
        Args:
            text: Temizlenecek metin
            
        Returns:
            Temizlenmiş metin
        """
        if not text:
            return ""
        
        # Fazla boşlukları ve gereksiz karakterleri temizle
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Satır başı ve sonundaki boşlukları temizle
            line = line.strip()
            
            # Boş satırları ve çok kısa satırları atla
            if len(line) > 2:
                # Fazla boşlukları tek boşluğa çevir
                line = ' '.join(line.split())
                cleaned_lines.append(line)
        
        # Satırları birleştir
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Fazla satır sonlarını temizle
        while '\n\n\n' in cleaned_text:
            cleaned_text = cleaned_text.replace('\n\n\n', '\n\n')
        
        return cleaned_text.strip()
    
    def get_chunk_statistics(self, chunks: List[Document]) -> dict:
        """
        Chunk istatistiklerini döndürür
        
        Args:
            chunks: Document chunk'ları
            
        Returns:
            İstatistik bilgileri
        """
        if not chunks:
            return {"total_chunks": 0}
        
        chunk_sizes = [len(chunk.page_content) for chunk in chunks]
        
        return {
            "total_chunks": len(chunks),
            "average_chunk_size": sum(chunk_sizes) / len(chunks),
            "min_chunk_size": min(chunk_sizes),
            "max_chunk_size": max(chunk_sizes),
            "total_characters": sum(chunk_sizes),
            "documents_processed": len(set(chunk.metadata.get("filename", "") for chunk in chunks))
        } 