"""Plant Care API - Сервис для ухода за комнатными растениями"""

import logging
from fastapi import FastAPI
from pydantic_settings import BaseSettings
from pydantic import BaseModel

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
logger.setLevel(settings.LOG_LEVEL)

# Создание приложения
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

# In-memory "база данных"
plants_db = {}
next_plant_id = 1

# Pydantic модели для валидации данных
class PlantCreate(BaseModel):
    name: str
    species: str
    care_instructions: str = "Поливать раз в неделю"

class PlantResponse(BaseModel):
    id: int
    name: str
    species: str
    care_instructions: str
    last_watered_ml: int = 0

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

@app.get("/plants", response_model=list[PlantResponse])
async def get_all_plants():
    logger.info("Запрос списка всех растений")
    return list(plants_db.values())

@app.post("/plants", response_model=PlantResponse, status_code=201)
async def add_plant(plant: PlantCreate):
    global next_plant_id
    new_plant = PlantResponse(
        id=next_plant_id,
        name=plant.name,
        species=plant.species,
        care_instructions=plant.care_instructions,
        last_watered_ml=0
    )
    plants_db[next_plant_id] = new_plant
    logger.info(f"Добавлено новое растение: '{plant.name}' (ID: {next_plant_id})")
    next_plant_id += 1
    return new_plant

@app.get("/plants/{plant_id}/care")
async def get_plant_care(plant_id: int):
    logger.info(f"Запрос инструкций по уходу для растения ID: {plant_id}")
    if plant_id not in plants_db:
        logger.warning(f"Растение с ID {plant_id} не найдено")
        raise HTTPException(status_code=404, detail="Растение не найдено")
    
    plant = plants_db[plant_id]
    return {
        "plant_id": plant.id,
        "name": plant.name,
        "care_instructions": plant.care_instructions,
        "recommended_water_ml": settings.DEFAULT_WATER_AMOUNT_ML
    }

@app.post("/plants/{plant_id}/water")
async def water_plant(plant_id: int):
    logger.info(f"Полив растения ID: {plant_id} объемом {settings.DEFAULT_WATER_AMOUNT_ML} мл")
    if plant_id not in plants_db:
        logger.warning(f"Попытка полить несуществующее растение ID: {plant_id}")
        raise HTTPException(status_code=404, detail="Растение не найдено")
    
    plant = plants_db[plant_id]
    plant.last_watered_ml += settings.DEFAULT_WATER_AMOUNT_ML
    logger.info(f"Растение '{plant.name}' успешно полито. Всего вылито: {plant.last_watered_ml} мл")
    
    return {
        "message": f"Растение '{plant.name}' полито!",
        "water_added_ml": settings.DEFAULT_WATER_AMOUNT_ML,
        "total_water_ml": plant.last_watered_ml
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
