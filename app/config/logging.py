import logging
import logging.handlers
import os
from datetime import datetime
import sys

# Log dizini oluşturma
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def get_log_file():
    current_date = datetime.now().strftime('%Y-%m-%d')
    return f"{LOG_DIR}/{current_date}.log"

def configure_logging():
    # Temel log formatı
    log_format = '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
    
    # Kök logger'ı yapılandır
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Tüm handler'ları temizle
    root_logger.handlers.clear()
    
    # Dosya handler'ı
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=get_log_file(),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(file_handler)
    
    # Konsol handler'ı
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(console_handler)
    
    # FastAPI ve uvicorn loggerlarını yapılandır
    for logger_name in ['fastapi', 'uvicorn', 'uvicorn.access', 'uvicorn.error']:
        logger = logging.getLogger(logger_name)
        logger.handlers = root_logger.handlers
        logger.propagate = False

def setup_logger(name):
    return logging.getLogger(name)