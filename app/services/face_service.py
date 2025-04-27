import shutil
import face_recognition
import os
import uuid
from app.models import Person, Encoding, Match, Image
import numpy as np
import cv2
from app.repository import user_service, image_service, encoding_service, match_service
from app.config.logging import setup_logger
from app.config.settings import settings
from app.services.image_service import compress_jpeg
from sqlalchemy.orm import Session
import aiofiles

logger = setup_logger(__name__)

IMAGE_FOLDER = settings.IMAGE_FOLDER
FACE_FOLDER = settings.FACE_FOLDER

os.makedirs(FACE_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

async def process_uploaded_image(file, db):
    """Yüklenen resmi işler ve yüz tespiti yapar."""
    filename = uuid.uuid4()
    file_location = f"{IMAGE_FOLDER}/{filename}.jpg"
    
    # Resmi asenkron olarak kaydet
    async with aiofiles.open(file_location, "wb") as buffer:
        content = await file.read()
        await buffer.write(content)

    compress_jpeg(file_location, file_location)
    image_id = image_service.create_image(db, file_location).uuid 
    detect_faces(file_location, image_id, db)
    
    return "Success"

# fotodaki yuzleri tesbit edip taniyip tanimadigini kontrol eder / performans problemi olabilir.
def label_faces_in_image(image_path, filename, db):
    # Görüntüyü yükle
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)

    # Veritabanındaki kişileri karşılaştır
    known_persons = db.query(Person).all()
    known_encodings = [np.frombuffer(person.encoding, dtype=np.float64) for person in known_persons]

    # Etiketli resim oluşturma
    for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_encodings, encoding)
        label = "Bilinmeyen" if True not in matches else known_persons[matches.index(True)].name

        # Yüzü çerçeveye al ve etiketle
        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(image, label, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)

    result_image_path = f"{FACE_FOLDER}/{filename}_labeled.jpg"
    cv2.imwrite(result_image_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

    return result_image_path

def detect_faces(image_path: str, filename: str, db) -> list[dict]:
    """
    1. Yüzleri tespit eder
    2. Her yüzü locale kaydeder
    3. Her yüz için:
       - DB'de encoding kontrolü yapar
       - Varsa: matching tablosuna kayıt atar
       - Yoksa: person -> encoding -> matching kayıtlarını oluşturur
    """
    try:
        logger.info(f"Yüz tespiti başlatıldı: {image_path}")
        
        # Görüntüyü yükle ve yüzleri tespit et
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)
        
        detected_faces = []
        
        # Her yüz için işlem yap
        for idx, (encoding, face_location) in enumerate(zip(face_encodings, face_locations)):
            try:
                # 1. Yüz görüntüsünü locale kaydet
                top, right, bottom, left = face_location
                face_image = image[top:bottom, left:right]
                face_filename = f"face_{filename}_{idx}.jpg"
                face_path = os.path.join(FACE_FOLDER, face_filename)
                cv2.imwrite(face_path, cv2.cvtColor(face_image, cv2.COLOR_RGB2BGR))
                logger.info(f"Yüz görüntüsü kaydedildi: {face_path}")
                
                # 2. Encoding'i bytes'a çevir
                encoding_bytes = encoding.tobytes()
                
                # 3. DB'deki encodinglerle karşılaştır
                known_encodings = db.query(Encoding).all()
                found_match = False
                
                for known_encoding in known_encodings:
                    known_face = np.frombuffer(known_encoding.encoding, dtype=np.float64)
                    # Karşılaştırma yap
                    if face_recognition.compare_faces([known_face], encoding)[0]:
                        # Eşleşme bulundu
                        confidence_score = int((1 - face_recognition.face_distance([known_face], encoding)[0]) * 100)
                        
                        # Matching tablosuna kaydet
                        match_service.create_match(
                            db=db,
                            person_id=known_encoding.person_id,
                            matched_image_id=filename,
                            confidence_score=confidence_score
                        )
                        found_match = True
                        logger.info(f"Eşleşme bulundu - Confidence: {confidence_score}%")
                        break
                
                # 4. Eşleşme bulunamadıysa yeni kayıtlar oluştur
                if not found_match:
                    # Önce person kaydı oluştur
                    new_person = Person(uuid=uuid.uuid4(), is_active=True)
                    db.add(new_person)
                    db.flush()  # ID'yi al
                    
                    # Sonra encoding kaydı oluştur
                    new_encoding = Encoding(
                        uuid=uuid.uuid4(),
                        person_id=new_person.uuid,
                        face_path=face_path,
                        encoding=encoding_bytes
                    )
                    db.add(new_encoding)
                    
                    # Son olarak matching kaydı oluştur
                    match_service.create_match(
                        db=db,
                        person_id=new_person.uuid,
                        matched_image_id=filename,
                        confidence_score=100  # İlk kayıt olduğu için 100
                    )
                    
                    logger.info("Yeni yüz kaydedildi ve ilişkiler oluşturuldu")
                
                detected_faces.append({
                    'face_path': face_path,
                    'location': {'top': top, 'right': right, 'bottom': bottom, 'left': left},
                    'is_new': not found_match
                })
                
            except Exception as face_error:
                logger.error(f"Yüz işleme hatası - idx {idx}: {str(face_error)}")
                continue
        
        db.commit()
        logger.info(f"Toplam {len(detected_faces)} yüz işlendi")
        return detected_faces
        
    except Exception as e:
        db.rollback()
        logger.error(f"Yüz tespiti genel hatası: {str(e)}")
        raise


def get_unknown_faces(db) -> list[dict]:
    """Tanınmayan kişileri ve yüz resimlerini getirir."""
    try:
        # İsmi olmayan aktif kişileri ve encoding'lerini getir
        unknown_faces = (
            db.query(Person, Encoding, Match)
            .join(Encoding, Person.uuid == Encoding.person_id)
            .join(Match, Person.uuid == Match.person_id)
            .filter(Person.name == None)
            .filter(Person.is_active == True)
            .order_by(Person.uuid, Match.created_at.desc())  # Önce uuid sonra tarih
            .distinct(Person.uuid)  # Her kişi için en son eşleşme
            .all()
        )

        logger.info(f"Tanınmayan yüzler: {len(unknown_faces)} kişi bulundu")

        result = []
        for person, encoding, match in unknown_faces:
            try:
                # Dosyanın varlığını kontrol et
                if os.path.exists(encoding.face_path):
                    result.append({
                        'person_id': str(person.uuid),
                        'face_path': encoding.face_path[4:],
                        'detected_at': match.created_at,
                        'confidence_score': match.confidence_score
                    })
                else:
                    logger.warning(f"Dosya bulunamadı: {encoding.face_path} - Kişi: {person.uuid}")

            except Exception as person_error:
                logger.error(f"Kişi işleme hatası - {person.uuid}: {str(person_error)}")
                continue

        logger.info(f"Toplam {len(result)} tanınmayan yüz bulundu")
        return result

    except Exception as e:
        logger.error(f"Tanınmayan yüzleri getirme hatası: {str(e)}")
        raise


def get_known_faces(db) -> list[dict]:
    """İsim ve soyismi bilinen kişileri ve son yüz resimlerini getirir."""
    try:
        # İsmi, soyismi olan aktif kişileri, encoding ve son eşleşmeleriyle getir
        known_faces = (
            db.query(Person, Encoding, Match)
            .join(Encoding, Person.uuid == Encoding.person_id)
            .join(Match, Person.uuid == Match.person_id)
            .filter(Person.name != None)
            .filter(Person.surname != None)
            .filter(Person.is_active == True)
            .order_by(Person.uuid, Match.created_at.desc())  # Önce uuid sonra tarih
            .distinct(Person.uuid)  # Her kişi için en son eşleşme
            .all()
        )

        result = []
        for person, encoding, match in known_faces:
            try:
                # Dosyanın varlığını kontrol et
                if os.path.exists(encoding.face_path):
                    result.append({
                        'person_id': str(person.uuid),
                        'name': person.name,
                        'surname': person.surname,
                        'face_path': encoding.face_path[4:],
                        'last_seen': match.created_at,
                        'confidence_score': match.confidence_score
                    })
                else:
                    logger.warning(f"Dosya bulunamadı: {encoding.face_path} - Kişi: {person.uuid}")

            except Exception as person_error:
                logger.error(f"Kişi işleme hatası - {person.uuid}: {str(person_error)}")
                continue

        logger.info(f"Toplam {len(result)} bilinen yüz bulundu")
        return result

    except Exception as e:
        logger.error(f"Bilinen yüzleri getirme hatası: {str(e)}")
        raise


def get_person_matches(db: Session, person_id: str) -> list[dict]:
    """Kişinin tüm eşleşmelerini ve orijinal fotoğrafları getirir."""
    try:
        # Kişinin tüm eşleşmelerini, encoding ve resim bilgileriyle birlikte getir
        matches = (
            db.query(Match, Image, Encoding)
            .join(Image, Match.matched_image_id == Image.uuid)
            .join(Encoding, Match.person_id == Encoding.person_id)
            .filter(Match.person_id == person_id)
            .order_by(Match.created_at.desc())
            .all()
        )

        person_matches = []
        for match, image, encoding in matches:
            # Dosya varlığını kontrol et
            if os.path.exists( encoding.face_path):
                person_matches.append({
                    'face_path': encoding.face_path[4:],
                    'original_image_path': f"{image.file_path[4:]}",
                    'detected_at': match.created_at,
                    'confidence_score': match.confidence_score
                })
            else:
                logger.warning(f"Dosya bulunamadı: {encoding.face_path} - Eşleşme ID: {match.uuid}")

        logger.info(f"Kişi {person_id} için {len(person_matches)} eşleşme bulundu")
        return person_matches

    except Exception as e:
        logger.error(f"Kişi eşleşmelerini getirme hatası: {str(e)}")
        raise
