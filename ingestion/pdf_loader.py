"""
PDF dosyalarını yükleme ve ayrıştırma
"""

import os
import re
from typing import List
import fitz  # PyMuPDF
from pathlib import Path
from langchain_core.documents import Document

class PDFLoader:
    """PDF dosyalarını yükler ve LangChain Document nesneleri olarak döndürür"""
    
    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = Path(data_dir)
        self.supported_extensions = ['.pdf']
    
    def load_pdf(self, file_path: str) -> List[Document]:
        """
        Tek bir PDF dosyasını yükler ve her sayfa için ayrı Document olarak döndürür
        
        Args:
            file_path: PDF dosyasının yolu
            
        Returns:
            LangChain Document nesnelerinin listesi (her sayfa için bir tane)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF dosyası bulunamadı: {file_path}")
        
        documents = []
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        try:
            # PyMuPDF ile PDF'i aç
            pdf_document = fitz.open(file_path)
            total_pages = len(pdf_document)
            
            print(f"📄 {filename} işleniyor... ({total_pages} sayfa)")
            
            # Her sayfayı ayrı document olarak işle
            for page_num in range(total_pages):
                page = pdf_document[page_num]
                text = page.get_text()
                
                # Boş sayfaları atla
                if not text.strip():
                    continue
                
                # Metadata oluştur
                metadata = {
                    "source": file_path,
                    "filename": filename,
                    "page_number": str(page_num + 1),  # 1-indexed
                    "total_pages": str(total_pages),
                    "file_size": str(file_size),
                    "source_type": "pdf",
                    "page_display": f"Sayfa {page_num + 1}",
                    "source_display": filename,
                    # Grant ve belge tipi metadata'sı ekle
                    "grant_group": self._extract_grant_group(filename),
                    "document_type": self._extract_document_type(filename)
                }
                
                # Document nesnesi oluştur
                doc = Document(
                    page_content=text,
                    metadata=metadata
                )
                
                documents.append(doc)
            
            pdf_document.close()
            print(f"✅ {filename}: {len(documents)} sayfa yüklendi")
            
        except Exception as e:
            print(f"❌ {filename} yüklenirken hata: {e}")
            raise
        
        return documents
    
    def load_all_pdfs(self, directory: str = None) -> List[Document]:
        """
        Belirtilen dizindeki tüm PDF dosyalarını yükler
        
        Args:
            directory: PDF dosyalarının bulunduğu dizin
            
        Returns:
            Tüm PDF'lerden oluşan Document listesi
        """
        if directory is None:
            directory = self.data_dir
        
        directory = Path(directory)
        
        if not directory.exists():
            raise FileNotFoundError(f"Dizin bulunamadı: {directory}")
        
        all_documents = []
        
        # PDF dosyalarını bul
        pdf_files = []
        for ext in self.supported_extensions:
            pdf_files.extend(directory.glob(f"*{ext}"))
        
        if not pdf_files:
            print(f"⚠️  {directory} dizininde PDF dosyası bulunamadı")
            return all_documents
        
        print(f"📂 {len(pdf_files)} PDF dosyası bulundu")
        
        # Her PDF dosyasını yükle
        for pdf_file in pdf_files:
            try:
                documents = self.load_pdf(str(pdf_file))
                all_documents.extend(documents)
            except Exception as e:
                print(f"❌ {pdf_file.name} atlandı: {e}")
                continue
        
        print(f"📚 Toplam {len(all_documents)} sayfa yüklendi")
        return all_documents
    
    def get_pdf_info(self, file_path: str) -> dict:
        """
        PDF dosyası hakkında bilgi döndürür
        
        Args:
            file_path: PDF dosyasının yolu
            
        Returns:
            PDF bilgileri içeren dictionary
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF dosyası bulunamadı: {file_path}")
        
        try:
            pdf_document = fitz.open(file_path)
            info = {
                "filename": os.path.basename(file_path),
                "page_count": len(pdf_document),
                "file_size": os.path.getsize(file_path),
                "metadata": pdf_document.metadata
            }
            pdf_document.close()
            return info
            
        except Exception as e:
            raise Exception(f"PDF bilgisi alınamadı: {e}") 
    
    def _extract_grant_group(self, filename: str) -> str:
        """
        Dosya adından grant grubunu çıkarır
        
        Args:
            filename: Dosya adı
            
        Returns:
            Grant grup ID'si
        """
        # AMIF-2025-TF2-AG-INTE-01-WOMEN formatından grant grubunu çıkar
        grant_pattern = r'(AMIF-\d{4}-[^_]+)'
        match = re.search(grant_pattern, filename)
        
        if match:
            return match.group(1)
        else:
            return "unknown_grant"
    
    def _extract_document_type(self, filename: str) -> str:
        """
        Dosya adından belge tipini çıkarır
        
        Args:
            filename: Dosya adı
            
        Returns:
            Belge tipi
        """
        filename_lower = filename.lower()
        
        if 'call-fiche' in filename_lower or 'call_fiche' in filename_lower:
            return 'call_document'
        elif 'separator_faq' in filename_lower:
            return 'faq'
        elif 'template' in filename_lower:
            return 'template'
        elif 'guide' in filename_lower or 'guideline' in filename_lower:
            return 'guide'
        elif 'separator_aga' in filename_lower:
            return 'administrative_guide'
        elif 'separator_af' in filename_lower:
            return 'application_form'
        elif 'separator_om' in filename_lower:
            return 'operational_manual'
        elif 'separator_tc' in filename_lower:
            return 'terms_conditions'
        elif 'separator_rules' in filename_lower:
            return 'rules_document'
        elif 'separator_general-mga' in filename_lower:
            return 'general_agreement'
        elif 'evaluation' in filename_lower:
            return 'evaluation_guide'
        else:
            return 'other' 