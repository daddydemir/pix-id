from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings

# PostgreSQL bağlantı bilgileri
database_url = settings.DATABASE_URL

# Veritabanı bağlantısını oluştur
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# class Person(Base):
#     __tablename__ = "persons"

#     id = Column(Integer, primary_key=True, index=True)
#     uuid = Column(String, unique=True, index=True)
#     name = Column(String, unique=True, index=True)
#     encoding = Column(LargeBinary)

# Tabloları oluştur
Base.metadata.create_all(bind=engine)

# Veritabanı bağlantı fonksiyonu
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
