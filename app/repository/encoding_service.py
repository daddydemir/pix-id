from sqlalchemy.orm import Session
from app.models import Encoding, Match, Image
from app.config.logging import setup_logger
from datetime import datetime
from typing import Optional, List
import uuid
import numpy as np

logger = setup_logger(__name__)

def create_encoding(
    db: Session, 
    person_id: uuid.UUID, 
    encoding_data: bytes,
    face_path: str  # Yeni parametre
) -> Encoding:
    """
    Yeni yüz encoding kaydı oluşturur.
    
    Args:
        db: Veritabanı oturumu
        person_id: Kişi UUID'si
        encoding_data: Yüz encoding verisi
        face_path: Tespit edilen yüz görüntüsünün yolu
    """
    try:
        new_encoding = Encoding(
            uuid=uuid.uuid4(),
            person_id=person_id,
            encoding=encoding_data,
            face_path=face_path 
        )
        db.add(new_encoding)
        db.commit()
        db.refresh(new_encoding)
        logger.info(f"Yeni encoding kaydı oluşturuldu: Kişi={person_id}, Face Path={face_path}")
        return new_encoding
    except Exception as e:
        db.rollback()
        logger.error(f"Encoding oluşturma hatası: {str(e)}")
        raise

def get_encoding_by_id(db: Session, encoding_id: int) -> Optional[Encoding]:
    """ID'ye göre encoding getirir."""
    try:
        encoding = db.query(Encoding).filter(Encoding.id == encoding_id).first()
        if encoding:
            logger.info(f"ID: {encoding_id} olan encoding getirildi")
        else:
            logger.warning(f"ID: {encoding_id} olan encoding bulunamadı")
        return encoding
    except Exception as e:
        logger.error(f"Encoding getirme hatası - ID {encoding_id}: {str(e)}")
        raise

def get_encoding_by_uuid(db: Session, uuid_str: str) -> Optional[Encoding]:
    """UUID'ye göre encoding getirir."""
    try:
        encoding = db.query(Encoding).filter(Encoding.uuid == uuid_str).first()
        if encoding:
            logger.info(f"UUID: {uuid_str} olan encoding getirildi")
        return encoding
    except Exception as e:
        logger.error(f"UUID ile encoding getirme hatası: {str(e)}")
        raise

def get_encodings_by_person(db: Session, person_id: uuid.UUID) -> List[Encoding]:
    """
    Kişiye ait tüm encoding'leri getirir.
    
    Returns:
        List[Encoding]: Her bir encoding kaydı face_path ile birlikte
    """
    try:
        encodings = (
            db.query(Encoding)
            .filter(Encoding.person_id == person_id)
            .order_by(Encoding.created_at.desc())  # En son eklenenler önce
            .all()
        )
        
        logger.info(f"Kişi ID: {person_id} için {len(encodings)} encoding bulundu")
        return encodings
    except Exception as e:
        logger.error(f"Kişi encoding'leri getirme hatası - Kişi ID {person_id}: {str(e)}")
        raise

def delete_encoding(db: Session, encoding_id: int) -> bool:
    """Encoding kaydını siler."""
    try:
        encoding = get_encoding_by_id(db, encoding_id)
        if encoding:
            db.delete(encoding)
            db.commit()
            logger.info(f"Encoding silindi - ID: {encoding_id}")
            return True
        logger.warning(f"Silinecek encoding bulunamadı - ID: {encoding_id}")
        return False
    except Exception as e:
        db.rollback()
        logger.error(f"Encoding silme hatası - ID {encoding_id}: {str(e)}")
        raise

def update_encoding(
    db: Session, 
    encoding_id: int, 
    new_encoding_data: bytes,
    new_face_path: str = None  # Opsiyonel parametre
) -> Optional[Encoding]:
    """
    Encoding verisini günceller.
    
    Args:
        db: Veritabanı oturumu
        encoding_id: Güncellenecek encoding ID'si
        new_encoding_data: Yeni encoding verisi
        new_face_path: Yeni yüz görüntüsü yolu (opsiyonel)
    """
    try:
        encoding = get_encoding_by_id(db, encoding_id)
        if encoding:
            encoding.encoding = new_encoding_data
            if new_face_path:  # Eğer yeni yüz yolu verildiyse
                encoding.face_path = new_face_path
            db.commit()
            logger.info(f"Encoding güncellendi - ID: {encoding_id}")
            return encoding
        logger.warning(f"Güncellenecek encoding bulunamadı - ID: {encoding_id}")
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"Encoding güncelleme hatası - ID {encoding_id}: {str(e)}")
        raise

def compare_encodings(encoding1: bytes, encoding2: bytes) -> float:
    """İki encoding arasındaki benzerliği hesaplar."""
    try:
        # NumPy array'lerine dönüştür
        enc1_array = np.frombuffer(encoding1, dtype=np.float64)
        enc2_array = np.frombuffer(encoding2, dtype=np.float64)
        
        # Cosine similarity hesapla
        similarity = np.dot(enc1_array, enc2_array)
        logger.debug(f"Encoding karşılaştırma sonucu: {similarity}")
        return similarity
    except Exception as e:
        logger.error(f"Encoding karşılaştırma hatası: {str(e)}")
        raise

def get_person_images(db: Session, person_id: uuid.UUID) -> List[dict]:
    """
    Bir kişinin eşleştiği tüm resimleri getirir.
    Returns:
        List[dict]: Her bir eşleşme için resim bilgisi ve güven skorunu içeren liste
    """
    try:
        # Kişinin tüm eşleşmelerini ve ilgili resim bilgilerini al
        matches = (
            db.query(Match, Image)
            .join(Image, Match.matched_image_id == Image.uuid)
            .filter(Match.person_id == person_id)
            .order_by(Match.confidence_score.desc())
            .all()
        )

        results = []
        for match, image in matches:
            results.append({
                "image_path": image.file_path,
                "confidence_score": match.confidence_score,
                "match_date": match.created_at,
                "image_uuid": str(image.uuid)
            })

        logger.info(f"Kişi {person_id} için {len(results)} resim bulundu")
        return results

    except Exception as e:
        logger.error(f"Kişi resimleri getirme hatası - Kişi ID {person_id}: {str(e)}")
        raise