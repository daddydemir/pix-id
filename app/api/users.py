from fastapi import APIRouter, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Person
from app.repository import user_service
from app.config.logging import setup_logger
import uuid

logger = setup_logger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/update/{user_uuid}")
async def update_person(
    user_uuid: str,
    name: str = Form(...),
    surname: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Tanınmayan kullanıcıyı günceller.
    
    Args:
        user_uuid: Kullanıcının UUID'si
        name: Kullanıcının adı
        surname: Kullanıcının soyadı
        db: Veritabanı oturumu
    """

    logger.info(f"Kullanıcı güncelleme isteği: {user_uuid} - {name} {surname}")
    try:
        # UUID kontrolü
        try:
            user_id = uuid.UUID(user_uuid)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Geçersiz UUID formatı"
            )

        # İsim ve soyisim kontrolü
        if len(name.strip()) < 2 or len(surname.strip()) < 2:
            raise HTTPException(
                status_code=400,
                detail="İsim ve soyisim en az 2 karakter olmalıdır"
            )

        # Kullanıcıyı güncelle
        updated_user = user_service.update_user(
            db=db,
            user_id=user_id,
            name=name.strip(),
            surname=surname.strip()
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=404,
                detail="Kullanıcı bulunamadı"
            )
        
        logger.info(f"Kullanıcı güncellendi: {user_uuid} - {name} {surname}")
        
        return RedirectResponse(
            url="/faces/known_users",
            status_code=303  # See Other - POST'tan sonra GET için
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Kullanıcı güncelleme hatası: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Kullanıcı güncellenirken bir hata oluştu"
        )