"""
Data ingestion module

This module performs PDF file loading, text processing and vector database
storage operations.

Usage example:
    from ingestion import PDFLoader, TextProcessor
    from ingestion.vector_store import get_vector_store, add_documents_to_vector_store
    
    # Load PDFs
    loader = PDFLoader()
    documents = loader.load_all_pdfs("data/raw")
    
    # Process and chunk texts
    processor = TextProcessor()
    chunks = processor.process_documents(documents)
    
    # Save to vector database
    add_documents_to_vector_store(chunks)
"""

from .pdf_loader import PDFLoader
from .text_processor import TextProcessor

__all__ = ["PDFLoader", "TextProcessor"]

def create_ingestion_pipeline(data_dir: str = "data/raw"):
    """
    Creates a complete data processing pipeline
    
    Args:
        data_dir: Directory containing PDF files
        
    Returns:
        (loader, processor) tuple
    """
    loader = PDFLoader(data_dir=data_dir)
    processor = TextProcessor()
    
    return loader, processor

def run_full_ingestion(data_dir: str = "data/raw", reset_db: bool = False):
    """
    Runs the complete data processing workflow
    
    Args:
        data_dir: Directory containing PDF files
        reset_db: Reset database
        
    Returns:
        True if successful
    """
    try:
        from .vector_store import reset_vector_store, add_documents_to_vector_store
        
        print("🚀 Veri işleme pipeline'ı başlatılıyor...")
        
        # Pipeline bileşenlerini oluştur
        loader, processor = create_ingestion_pipeline(data_dir)
        
        # Veritabanını sıfırla (istenirse)
        if reset_db:
            reset_vector_store()
        
        # PDF'leri yükle
        print("\n📂 1. PDF dosyaları yükleniyor...")
        documents = loader.load_all_pdfs()
        
        if not documents:
            print("❌ Yüklenecek PDF dosyası bulunamadı")
            return False
        
        print(f"📊 {len(documents)} belge yüklendi")
        
        # Metinleri işle ve vektör veritabanına kaydet
        print("\n✂️  2. Metinler işleniyor ve vektör veritabanına kaydediliyor...")
        success = processor.process_and_store_documents(documents)
        
        if not success:
            print("❌ Belge işleme ve kaydetme başarısız")
            return False
        
        print("\n🎉 Veri işleme pipeline'ı başarıyla tamamlandı!")
        return True
        
    except Exception as e:
        print(f"❌ Veri işleme hatası: {e}")
        return False 