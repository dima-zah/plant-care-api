"""Plant Care API - Сервис для ухода за комнатными растениями"""

import logging
from fastapi import FastAPI
from pydantic_settings import BaseSettings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация из переменных окружения
class Settings(BaseSettings):
    APP_NAME: str = "Plant Care API"
    APP_VERSION: str = "1.0.0"
    DEFAULT_WATER_AMOUNT_ML: int = 250
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()

# Создание приложения
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

@app.on_event("startup")
async def startup_event():
    logger.info(f"Запуск {settings.APP_NAME} версии {settings.APP_VERSION}")

@app.get("/")
async def root():
    return {
        "message": "Добро пожаловать в Plant Care API!",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    logger.info("Health check запрос")
    return {"status": "healthy"}

@app.get("/version")
async def get_version():
    return {
        "version": settings.APP_VERSION,
        "name": settings.APP_NAME
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
