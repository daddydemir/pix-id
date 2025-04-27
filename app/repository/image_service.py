from sqlalchemy.orm import Session
from app.models import Image
from app.config.logging import setup_logger
import uuid
from datetime import datetime
from typing import Optional, List

logger = setup_logger(__name__)

def get_all_images(db: Session) -> List[Image]:
    """Tüm görüntüleri getirir."""
    try:
        images = db.query(Image).all()
        logger.info(f"Toplam {len(images)} görüntü getirildi")
        return images
    except Exception as e:
        logger.error(f"Görüntüler getirilirken hata oluştu: {str(e)}")
        raise

def get_image_by_id(db: Session, image_id: int) -> Optional[Image]:
    """ID'ye göre görüntü getirir."""
    try:
        image = db.query(Image).filter(Image.id == image_id).first()
        if image:
            logger.info(f"ID: {image_id} olan görüntü getirildi")
        else:
            logger.warning(f"ID: {image_id} olan görüntü bulunamadı")
        return image
    except Exception as e:
        logger.error(f"Görüntü getirme hatası - ID {image_id}: {str(e)}")
        raise

def get_image_by_uuid(db: Session, uuid_str: str) -> Optional[Image]:
    """UUID'ye göre görüntü getirir."""
    try:
        image = db.query(Image).filter(Image.uuid == uuid_str).first()
        if image:
            logger.info(f"UUID: {uuid_str} olan görüntü getirildi")
        return image
    except Exception as e:
        logger.error(f"UUID ile görüntü getirme hatası: {str(e)}")
        raise

def create_image(db: Session, file_path: str) -> Image:
    """Yeni görüntü kaydı oluşturur."""
    try:
        new_image = Image(
            uuid=uuid.uuid4(),
            file_path=file_path,
            created_at=datetime.utcnow()
        )
        db.add(new_image)
        db.commit()
        db.refresh(new_image)
        logger.info(f"Yeni görüntü kaydı oluşturuldu: {file_path}")
        return new_image
    except Exception as e:
        db.rollback()
        logger.error(f"Görüntü oluşturma hatası: {str(e)}")
        raise

def update_image_path(db: Session, image_id: int, new_file_path: str) -> Optional[Image]:
    """Görüntü dosya yolunu günceller."""
    try:
        image = get_image_by_id(db, image_id)
        if image:
            image.file_path = new_file_path
            db.commit()
            logger.info(f"Görüntü yolu güncellendi - ID: {image_id}")
            return image
        logger.warning(f"Güncellenecek görüntü bulunamadı - ID: {image_id}")
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"Görüntü güncelleme hatası - ID {image_id}: {str(e)}")
        raise

def delete_image(db: Session, image_id: int) -> bool:
    """Görüntü kaydını siler."""
    try:
        image = get_image_by_id(db, image_id)
        if image:
            db.delete(image)
            db.commit()
            logger.info(f"Görüntü silindi - ID: {image_id}")
            return True
        logger.warning(f"Silinecek görüntü bulunamadı - ID: {image_id}")
        return False
    except Exception as e:
        db.rollback()
        logger.error(f"Görüntü silme hatası - ID {image_id}: {str(e)}")
        raise

def get_images_by_date_range(db: Session, start_date: datetime, end_date: datetime) -> List[Image]:
    """Belirli tarih aralığındaki görüntüleri getirir."""
    try:
        images = db.query(Image).filter(
            Image.created_at >= start_date,
            Image.created_at <= end_date
        ).all()
        logger.info(f"Tarih aralığında {len(images)} görüntü bulundu")
        return images
    except Exception as e:
        logger.error(f"Tarih aralığı ile görüntü getirme hatası: {str(e)}")
        raise