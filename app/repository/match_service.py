from sqlalchemy.orm import Session
from app.models import Match
from app.config.logging import setup_logger
from datetime import datetime
from typing import Optional, List
import uuid

logger = setup_logger(__name__)

def create_match(
    db: Session, 
    person_id: uuid.UUID, 
    matched_image_id: uuid.UUID, 
    confidence_score: int
) -> Match:
    """Yeni eşleşme kaydı oluşturur."""
    try:
        new_match = Match(
            person_id=person_id,
            matched_image_id=matched_image_id,
            confidence_score=confidence_score,
            created_at=datetime.utcnow()
        )
        db.add(new_match)
        db.commit()
        db.refresh(new_match)
        logger.info(f"Yeni eşleşme kaydı oluşturuldu: Kişi={person_id}, Görüntü={matched_image_id}")
        return new_match
    except Exception as e:
        db.rollback()
        logger.error(f"Eşleşme oluşturma hatası: {str(e)}")
        raise

def get_match_by_id(db: Session, match_id: int) -> Optional[Match]:
    """ID'ye göre eşleşme getirir."""
    try:
        match = db.query(Match).filter(Match.id == match_id).first()
        if match:
            logger.info(f"ID: {match_id} olan eşleşme getirildi")
        else:
            logger.warning(f"ID: {match_id} olan eşleşme bulunamadı")
        return match
    except Exception as e:
        logger.error(f"Eşleşme getirme hatası - ID {match_id}: {str(e)}")
        raise

def get_matches_by_person(db: Session, person_id: uuid.UUID) -> List[Match]:
    """Kişiye ait tüm eşleşmeleri getirir."""
    try:
        matches = db.query(Match).filter(Match.person_id == person_id).all()
        logger.info(f"Kişi ID: {person_id} için {len(matches)} eşleşme bulundu")
        return matches
    except Exception as e:
        logger.error(f"Kişi eşleşmeleri getirme hatası - Kişi ID {person_id}: {str(e)}")
        raise

def get_matches_by_image(db: Session, image_id: uuid.UUID) -> List[Match]:
    """Görüntüye ait tüm eşleşmeleri getirir."""
    try:
        matches = db.query(Match).filter(Match.matched_image_id == image_id).all()
        logger.info(f"Görüntü ID: {image_id} için {len(matches)} eşleşme bulundu")
        return matches
    except Exception as e:
        logger.error(f"Görüntü eşleşmeleri getirme hatası - Görüntü ID {image_id}: {str(e)}")
        raise

def get_matches_by_confidence_threshold(
    db: Session, 
    threshold: int
) -> List[Match]:
    """Belirli güven skorunun üstündeki eşleşmeleri getirir."""
    try:
        matches = db.query(Match).filter(Match.confidence_score >= threshold).all()
        logger.info(f"Güven skoru {threshold} üzerinde {len(matches)} eşleşme bulundu")
        return matches
    except Exception as e:
        logger.error(f"Güven skoru filtreleme hatası: {str(e)}")
        raise

def get_recent_matches(
    db: Session, 
    limit: int = 10
) -> List[Match]:
    """En son eşleşmeleri getirir."""
    try:
        matches = db.query(Match).order_by(Match.created_at.desc()).limit(limit).all()
        logger.info(f"Son {limit} eşleşme getirildi")
        return matches
    except Exception as e:
        logger.error(f"Son eşleşmeleri getirme hatası: {str(e)}")
        raise

def delete_match(db: Session, match_id: int) -> bool:
    """Eşleşme kaydını siler."""
    try:
        match = get_match_by_id(db, match_id)
        if match:
            db.delete(match)
            db.commit()
            logger.info(f"Eşleşme silindi - ID: {match_id}")
            return True
        logger.warning(f"Silinecek eşleşme bulunamadı - ID: {match_id}")
        return False
    except Exception as e:
        db.rollback()
        logger.error(f"Eşleşme silme hatası - ID {match_id}: {str(e)}")
        raise