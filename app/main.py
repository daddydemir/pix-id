from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.api import faces, users
from app.config.logging import configure_logging, setup_logger
import uvicorn
from app.database import init_db
from app.middleware.logging import log_request_middleware
from fastapi.staticfiles import StaticFiles

configure_logging()
logger = setup_logger(__name__)

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.middleware("http")(log_request_middleware)
app.include_router(faces.router)

@app.get("/")
async def root():
    return RedirectResponse(url="/faces/upload")

app.include_router(faces.router)
app.include_router(users.router)

@app.on_event("startup")
async def startup_event():
    init_db()
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