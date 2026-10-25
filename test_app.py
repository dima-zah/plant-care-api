from fastapi.testclient import TestClient
from app_final import app

client = TestClient(app)

def test_health_check():
    """Тест 1: Проверка работоспособности /health"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_version():
    """Тест 2: Проверка /version"""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "name" in data


def test_add_plant():
    """Тест 3: Добавление нового растения (основной маршрут)"""
    plant_data = {
        "name": "Тестовый кактус",
        "species": "Cactus testensis",
        "care_instructions": "Поливать раз в месяц"
    }
    response = client.post("/plants", json=plant_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == "Тестовый кактус"
    assert data["species"] == "Cactus testensis"
    assert "id" in data


def test_get_plants_list():
    """Тест 4: Получение списка всех растений"""
    response = client.get("/plants")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_plant_care_with_valid_id():
    """Тест 5: Получение инструкций по уходу (маршрут с параметром)"""
    # Сначала добавляем растение
    plant_data = {"name": "Фикус", "species": "Ficus benjamina"}
    response = client.post("/plants", json=plant_data)
    plant_id = response.json()["id"]
    
    # Теперь получаем инструкции по уходу для этого растения
    response = client.get(f"/plants/{plant_id}/care")
    assert response.status_code == 200
    
    data = response.json()
    assert data["plant_id"] == plant_id
    assert "care_instructions" in data
    assert "recommended_water_ml" in data


def test_get_plant_care_with_invalid_id():
    """Тест 6: Ошибка 404 при запросе несуществующего растения (случай с ошибкой)"""
    # Пробуем получить инструкции для несуществующего ID
    response = client.get("/plants/99999/care")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_water_plant():
    """Тест 7: Полив растения (использует переменную окружения)"""
    # Добавляем растение
    plant_data = {"name": "Монстера", "species": "Monstera deliciosa"}
    response = client.post("/plants", json=plant_data)
    plant_id = response.json()["id"]
    
    # Поливаем растение
    response = client.post(f"/plants/{plant_id}/water")
    assert response.status_code == 200
    
    data = response.json()
    assert "water_added_ml" in data
    assert "total_water_ml" in data
    assert data["water_added_ml"] > 0
