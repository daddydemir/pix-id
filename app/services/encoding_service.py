from sqlalchemy.orm import Session
from app.models import Encoding
from app.config.logging import setup_logger
from datetime import datetime
from typing import Optional, List
import uuid
import numpy as np

logger = setup_logger(__name__)

def create_encoding(
    db: Session, 
    person_id: uuid.UUID, 
    encoding_data: bytes
) -> Encoding:
    """Yeni yüz encoding kaydı oluşturur."""
    try:
        new_encoding = Encoding(
            uuid=uuid.uuid4(),
            person_id=person_id,
            encoding=encoding_data
        )
        db.add(new_encoding)
        db.commit()
        db.refresh(new_encoding)
        logger.info(f"Yeni encoding kaydı oluşturuldu: Kişi={person_id}")
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
    """Kişiye ait tüm encoding'leri getirir."""
    try:
        encodings = db.query(Encoding).filter(Encoding.person_id == person_id).all()
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
    new_encoding_data: bytes
) -> Optional[Encoding]:
    """Encoding verisini günceller."""
    try:
        encoding = get_encoding_by_id(db, encoding_id)
        if encoding:
            encoding.encoding = new_encoding_data
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