from fastapi import Request
from time import time
from app.config.logging import setup_logger
import json

logger = setup_logger(__name__)

async def log_request_middleware(request: Request, call_next):
    start_time = time()
    
    request_details = {
        "client_ip": request.client.host,
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "path_params": dict(request.path_params),
        "query_params": dict(request.query_params)
    }
    
    logger.info(
        f"İstek alındı - IP: {request_details['client_ip']} "
        f"Method: {request_details['method']} URL: {request_details['url']}"
    )

    response = await call_next(request)
    
    process_time = time() - start_time
    
    logger.info(
        f"Yanıt gönderildi - Durum Kodu: {response.status_code} "
        f"İşlem Süresi: {process_time:.2f}s"
    )

    logger.debug(
        "Detaylı istek bilgileri: \n" + 
        json.dumps(request_details, indent=2, ensure_ascii=False)
    )

    return response