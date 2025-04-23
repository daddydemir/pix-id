from fastapi import FastAPI
#from app.api import faces, users
from app.config.logging import configure_logging, setup_logger
import uvicorn

configure_logging()
logger = setup_logger(__name__)

app = FastAPI()

#app.include_router(faces.router)
#app.include_router(users.router)

@app.on_event("startup")
async def startup_event():
    logger.info("Application started")

if __name__ == "__main__":
    uvicorn_config = uvicorn.Config(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        log_config=None 
    )
    server = uvicorn.Server(uvicorn_config)
    server.run()