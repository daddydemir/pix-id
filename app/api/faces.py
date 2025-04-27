from fastapi import APIRouter, File, UploadFile, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from app.database import get_db
from app.services import face_service
from app.repository import user_service 
from app.config.logging import setup_logger


logger = setup_logger(__name__)
router = APIRouter(
    prefix="/faces",
    tags=["faces"]
)

templates = Jinja2Templates(directory="app/templates")

@router.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@router.post("/upload/")
async def upload_files(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Birden fazla resim yükler ve yüz tespiti yapar."""
    try:
        processed_count = 0
        for file in files:
            # Dosya uzantısı kontrolü
            if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                logger.warning(f"Desteklenmeyen dosya formatı: {file.filename}")
                continue
                
            try:
                await face_service.process_uploaded_image(file, db)
                processed_count += 1
            except Exception as file_error:
                logger.error(f"Dosya işleme hatası - {file.filename}: {str(file_error)}")
                continue

        if processed_count == 0:
            raise HTTPException(
                status_code=400,
                detail="Hiçbir resim işlenemedi"
            )

        return RedirectResponse(
            url="/faces/unknown",
            status_code=303
        )

    except Exception as e:
        logger.error(f"Toplu yükleme hatası: {str(e)}")
        raise HTTPException(status_code=500, detail="Yükleme başarısız")

@router.get("/known_users", response_class=HTMLResponse)
async def known_users(request: Request, db: Session = Depends(get_db)):
    """Bilinen yüzleri listeler."""
    try:
        known_faces = face_service.get_known_faces(db)
        return templates.TemplateResponse(
            "known_users.html", 
            {
                "request": request, 
                "faces": known_faces
            }
        )
    except Exception as e:
        logger.error(f"Bilinen yüzler endpoint hatası: {str(e)}")
        raise HTTPException(status_code=500, detail="İşlem başarısız")

@router.get("/unknown", response_class=HTMLResponse)
async def unknown_faces(request: Request, db: Session = Depends(get_db)):
    """Tanınmayan yüzleri listeler."""
    try:
        unknown_faces = face_service.get_unknown_faces(db)
        logger.info(f"Tanınmayan yüzler: {unknown_faces}")
        return templates.TemplateResponse(
            "unknown_faces.html", 
            {
                "request": request, 
                "faces": unknown_faces
            }
        )
    except Exception as e:
        logger.error(f"Tanınmayan yüzler endpoint hatası: {str(e)}")
        raise HTTPException(status_code=500, detail="İşlem başarısız")
    
@router.get("/person/{person_id}", response_class=HTMLResponse)
async def person_details(
    person_id: str, 
    request: Request, 
    db: Session = Depends(get_db)
):
    """Kişinin tüm eşleşmelerini gösterir."""
    try:
        person = user_service.get_user_by_uuid(db, person_id)
        if not person:
            raise HTTPException(status_code=404, detail="Kişi bulunamadı")
            
        matches = face_service.get_person_matches(db, person_id)
        
        return templates.TemplateResponse(
            "person_details.html",
            {
                "request": request,
                "person": person,
                "matches": matches
            }
        )
    except Exception as e:
        logger.error(f"Kişi detayları endpoint hatası: {str(e)}")
        raise HTTPException(status_code=500, detail="İşlem başarısız")