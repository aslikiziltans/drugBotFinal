"""
OnSIDES Dataset İşleyicisi - DrugBot için özel veri işleme
"""

import pandas as pd
import json
import os
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OnSIDESProcessor:
    """OnSIDES dataset'ini işleyen ve DrugBot için uygun formata dönüştüren sınıf"""
    
    def __init__(self, data_dir: str = "data/drug_data"):
        """
        OnSIDES processor'ı başlatır
        
        Args:
            data_dir: OnSIDES dataset'inin bulunduğu dizin
        """
        self.data_dir = Path(data_dir)
        self.csv_dir = self.data_dir / "csv"
        self.output_dir = Path("data/processed")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # CSV dosyalarını yükle
        self.load_data()
    
    def load_data(self):
        """OnSIDES CSV dosyalarını yükler"""
        try:
            logger.info("📚 OnSIDES dataset'i yükleniyor...")
            
            # Ana tablolar
            self.ingredients = pd.read_csv(self.csv_dir / "vocab_rxnorm_ingredient.csv")
            self.adverse_effects = pd.read_csv(self.csv_dir / "vocab_meddra_adverse_effect.csv")
            self.products = pd.read_csv(self.csv_dir / "vocab_rxnorm_product.csv")
            self.product_labels = pd.read_csv(self.csv_dir / "product_label.csv")
            
            # İlişki tabloları
            self.product_adverse_effects = pd.read_csv(self.csv_dir / "product_adverse_effect.csv")
            self.product_to_rxnorm = pd.read_csv(self.csv_dir / "product_to_rxnorm.csv")
            self.ingredient_to_product = pd.read_csv(self.csv_dir / "vocab_rxnorm_ingredient_to_product.csv")
            
            logger.info(f"✅ {len(self.ingredients)} ilaç bileşeni yüklendi")
            logger.info(f"✅ {len(self.adverse_effects)} yan etki terimi yüklendi")
            logger.info(f"✅ {len(self.product_adverse_effects)} ilaç-yan etki ilişkisi yüklendi")
            
        except Exception as e:
            logger.error(f"❌ Veri yükleme hatası: {e}")
            raise
    
    def create_drug_knowledge_base(self) -> List[Dict]:
        """
        DrugBot için ilaç bilgi tabanı oluşturur
        
        Returns:
            List[Dict]: İlaç bilgilerini içeren liste
        """
        logger.info("🔬 İlaç bilgi tabanı oluşturuluyor...")
        
        drug_knowledge = []
        
        # Tüm ilaç bileşenleri için işlem yap
        total_ingredients = len(self.ingredients)
        logger.info(f"📊 Toplam işlenecek ilaç: {total_ingredients}")
        
        # Her ilaç bileşeni için
        for idx, (_, ingredient) in enumerate(self.ingredients.iterrows(), 1):
            ingredient_id = ingredient['rxnorm_id']
            ingredient_name = ingredient['rxnorm_name']
            
            # İlerleme gösterici
            if idx % 100 == 0 or idx == total_ingredients:
                logger.info(f"📈 İlerleme: {idx}/{total_ingredients} ({idx/total_ingredients*100:.1f}%)")
            
            # Bu bileşenin yan etkilerini bul
            side_effects = self.get_side_effects_for_ingredient(ingredient_id)
            
            # Yemek etkileşimi bilgisi (şimdilik genel)
            food_interactions = self.get_food_interactions(ingredient_name)
            
            # İlaç bilgisi
            drug_info = {
                "drug_name": ingredient_name,
                "rxnorm_id": ingredient_id,
                "side_effects": side_effects,
                "food_interactions": food_interactions,
                "general_info": f"{ingredient_name} etken maddesini içeren ilaç"
            }
            
            drug_knowledge.append(drug_info)
        
        logger.info(f"✅ {len(drug_knowledge)} ilaç için bilgi tabanı oluşturuldu")
        return drug_knowledge
    
    def get_side_effects_for_ingredient(self, ingredient_id: int) -> List[Dict]:
        """
        Belirli bir ilaç bileşeni için yan etkileri alır
        
        Args:
            ingredient_id: RxNorm ilaç bileşen ID'si
            
        Returns:
            List[Dict]: Yan etki bilgileri
        """
        side_effects = []
        
        try:
            # Bileşenin ürünlerini bul
            ingredient_products = self.ingredient_to_product[
                self.ingredient_to_product['ingredient_id'] == ingredient_id
            ]
            
            for _, product_rel in ingredient_products.iterrows():
                product_id = product_rel['product_id']
                
                # Ürünün etiketlerini bul
                product_labels = self.product_to_rxnorm[
                    self.product_to_rxnorm['rxnorm_product_id'] == product_id
                ]
                
                for _, label_rel in product_labels.iterrows():
                    label_id = label_rel['label_id']
                    
                    # Etiketin yan etkilerini bul
                    label_effects = self.product_adverse_effects[
                        self.product_adverse_effects['product_label_id'] == label_id
                    ]
                    
                    for _, effect_rel in label_effects.iterrows():
                        effect_id = effect_rel['effect_meddra_id']
                        
                        # Yan etki adını bul
                        effect_info = self.adverse_effects[
                            self.adverse_effects['meddra_id'] == effect_id
                        ]
                        
                        if not effect_info.empty:
                            side_effects.append({
                                "effect_name": effect_info.iloc[0]['meddra_name'],
                                "effect_id": effect_id,
                                "effect_type": effect_info.iloc[0]['meddra_term_type']
                            })
        
        except Exception as e:
            logger.warning(f"⚠️ {ingredient_id} için yan etki bilgisi alınamadı: {e}")
        
        # Benzersiz yan etkileri döndür
        unique_effects = []
        seen_effects = set()
        
        for effect in side_effects:
            if effect['effect_name'] not in seen_effects:
                unique_effects.append(effect)
                seen_effects.add(effect['effect_name'])
        
        return unique_effects[:10]  # En fazla 10 yan etki
    
    def get_food_interactions(self, drug_name: str) -> Dict:
        """
        İlaç için yemek etkileşimi bilgilerini getirir
        
        Args:
            drug_name: İlaç adı
            
        Returns:
            Dict: Yemek etkileşimi bilgileri
        """
        # Temel yemek etkileşim şablonu
        # Gerçek projede daha kapsamlı bir veritabanından alınabilir
        
        common_food_interactions = {
            "empty_stomach": "Genellikle aç karınla alınması önerilir",
            "with_food": "Yemekle birlikte alınması önerilir",
            "avoid_dairy": "Süt ürünlerinden kaçının",
            "avoid_alcohol": "Alkol kullanmayın",
            "general_advice": "İlacı her zaman aynı şekilde (aç karın veya tok karın) alın"
        }
        
        # Basit kural tabanlı yaklaşım
        drug_lower = drug_name.lower()
        
        if any(term in drug_lower for term in ['tetracycline', 'doxycycline', 'ciprofloxacin']):
            return {
                "recommendation": "empty_stomach",
                "details": "Bu antibiyotik aç karınla alınmalıdır. Süt ürünlerinden kaçının.",
                "timing": "Yemekten 1 saat önce veya 2 saat sonra alın"
            }
        elif any(term in drug_lower for term in ['ibuprofen', 'naproxen', 'aspirin']):
            return {
                "recommendation": "with_food",
                "details": "Mide irritasyonunu önlemek için yemekle birlikte alın.",
                "timing": "Yemek sırasında veya hemen sonrasında alın"
            }
        else:
            return {
                "recommendation": "general_advice",
                "details": "İlacı her zaman aynı şekilde alın. Doktorunuzun tavsiyelerini takip edin.",
                "timing": "Düzenli zamanlarda alın"
            }
    
    def generate_drug_documents(self) -> List[Dict]:
        """
        DrugBot için belge formatında ilaç bilgileri oluşturur
        
        Returns:
            List[Dict]: Belge formatında ilaç bilgileri
        """
        logger.info("📄 DrugBot için belge formatı oluşturuluyor...")
        
        drug_knowledge = self.create_drug_knowledge_base()
        documents = []
        
        for drug in drug_knowledge:
            drug_name = drug['drug_name']
            side_effects = drug['side_effects']
            food_interactions = drug['food_interactions']
            
            # Yan etkileri metin olarak formatla
            side_effects_text = ""
            if side_effects:
                side_effects_text = "Yan Etkileri:\n"
                for effect in side_effects:
                    side_effects_text += f"- {effect['effect_name']}\n"
            else:
                side_effects_text = "Yan Etkileri: Bilgi bulunmamaktadır.\n"
            
            # Yemek etkileşimi metni
            food_text = f"""
Yemek Etkileşimi:
- Öneri: {food_interactions.get('recommendation', 'Genel tavsiye')}
- Detay: {food_interactions.get('details', 'Doktorunuza danışın')}
- Zamanlama: {food_interactions.get('timing', 'Düzenli zamanlarda alın')}
"""
            
            # Tam belge metni
            document_text = f"""
İlaç Adı: {drug_name}

{side_effects_text}

{food_text}

Genel Bilgi: {drug['general_info']}

Önemli Uyarı: Bu bilgiler yalnızca genel bilgilendirme amaçlıdır. 
İlaç kullanımı konusunda mutlaka doktorunuza danışın.
"""
            
            documents.append({
                "content": document_text.strip(),
                "metadata": {
                    "drug_name": drug_name,
                    "rxnorm_id": drug['rxnorm_id'],
                    "document_type": "drug_information",
                    "source": "OnSIDES_v3.1.0"
                }
            })
        
        logger.info(f"✅ {len(documents)} ilaç belgesi oluşturuldu")
        return documents
    
    def save_processed_data(self, documents: List[Dict]):
        """
        İşlenmiş verileri kaydet
        
        Args:
            documents: Belge formatında ilaç bilgileri
        """
        logger.info("💾 İşlenmiş veriler kaydediliyor...")
        
        # JSON formatında kaydet
        output_file = self.output_dir / "drug_knowledge_base.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(documents, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Veriler kaydedildi: {output_file}")
        
        # Özet istatistikleri
        total_drugs = len(documents)
        logger.info(f"📊 Toplam ilaç sayısı: {total_drugs}")


def main():
    """Ana işlem fonksiyonu"""
    try:
        logger.info("🚀 DrugBot için OnSIDES dataset işleme başlıyor...")
        
        # Processor'ı başlat
        processor = OnSIDESProcessor()
        
        # Belgeleri oluştur
        documents = processor.generate_drug_documents()
        
        # Verileri kaydet
        processor.save_processed_data(documents)
        
        logger.info("✅ OnSIDES dataset başarıyla işlendi!")
        
    except Exception as e:
        logger.error(f"❌ İşlem hatası: {e}")
        raise


if __name__ == "__main__":
    main() 