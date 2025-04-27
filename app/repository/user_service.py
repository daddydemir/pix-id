from sqlalchemy.orm import Session
from app.models import Person
from app.config.logging import setup_logger
import uuid
from datetime import datetime

logger = setup_logger(__name__)

def get_all_users(db: Session):
    """Tüm aktif kullanıcıları getirir."""
    try:
        users = db.query(Person).filter(Person.is_active == True).all()
        logger.info(f"Toplam {len(users)} aktif kullanıcı getirildi")
        return users
    except Exception as e:
        logger.error(f"Kullanıcılar getirilirken hata oluştu: {str(e)}")
        raise

def get_user_by_id(db: Session, user_id: int):
    """ID'ye göre kullanıcı getirir."""
    try:
        user = db.query(Person).filter(Person.id == user_id, Person.is_active == True).first()
        if user:
            logger.info(f"ID: {user_id} olan kullanıcı getirildi")
        else:
            logger.warning(f"ID: {user_id} olan kullanıcı bulunamadı")
        return user
    except Exception as e:
        logger.error(f"Kullanıcı getirme hatası - ID {user_id}: {str(e)}")
        raise

def get_user_by_uuid(db: Session, uuid_str: str):
    """UUID'ye göre kullanıcı getirir."""
    try:
        user = db.query(Person).filter(Person.uuid == uuid_str, Person.is_active == True).first()
        if user:
            logger.info(f"UUID: {uuid_str} olan kullanıcı getirildi")
        return user
    except Exception as e:
        logger.error(f"UUID ile kullanıcı getirme hatası: {str(e)}")
        raise

def create_user(db: Session, name: str, surname: str):
    """Yeni kullanıcı oluşturur."""
    try:
        new_user = Person(
            uuid=uuid.uuid4(),
            name=name,
            surname=surname,
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"Yeni kullanıcı oluşturuldu: {name} {surname}")
        return new_user
    except Exception as e:
        db.rollback()
        logger.error(f"Kullanıcı oluşturma hatası: {str(e)}")
        raise

def update_user(db: Session, user_id: int, name: str = None, surname: str = None):
    """Kullanıcı bilgilerini günceller."""
    try:
        user = get_user_by_uuid(db, user_id)
        if user:
            if name:
                user.name = name
            if surname:
                user.surname = surname
            db.commit()
            logger.info(f"Kullanıcı güncellendi - ID: {user_id}")
            return user
        logger.warning(f"Güncellenecek kullanıcı bulunamadı - ID: {user_id}")
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"Kullanıcı güncelleme hatası - ID {user_id}: {str(e)}")
        raise

def delete_user(db: Session, user_id: int):
    """Kullanıcıyı soft delete yapar."""
    try:
        user = get_user_by_id(db, user_id)
        if user:
            user.is_active = False
            db.commit()
            logger.info(f"Kullanıcı silindi - ID: {user_id}")
            return True
        logger.warning(f"Silinecek kullanıcı bulunamadı - ID: {user_id}")
        return False
    except Exception as e:
        db.rollback()
        logger.error(f"Kullanıcı silme hatası - ID {user_id}: {str(e)}")
        raise

def search_users(db: Session, search_term: str):
    """İsim veya soyisme göre kullanıcı arar."""
    try:
        users = db.query(Person).filter(
            Person.is_active == True,
            (Person.name.ilike(f"%{search_term}%") | Person.surname.ilike(f"%{search_term}%"))
        ).all()
        logger.info(f"'{search_term}' için {len(users)} kullanıcı bulundu")
        return users
    except Exception as e:
        logger.error(f"Kullanıcı arama hatası: {str(e)}")
        raise