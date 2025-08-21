import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class Config:
    API_URL = "https://kinopoiskapiunofficial.tech/api/v2.2/"
    HEADERS = {
        "X-API-KEY": "50884c19-4a50-4f26-86ca-8d3bf8b256ea",
        "Content-Type": "application/json"
    }
    KINO_URL = "https://www.kinopoisk.ru"


@pytest.fixture
def api_client():
    """Фикстура для работы с API Kinopoisk"""
    class APIClient:
        def __init__(self):
            self.base_url = Config.API_URL
            self.headers = Config.HEADERS

        def get(self, endpoint, params=None):
            url = f"{self.base_url}{endpoint}"
            return requests.get(url, headers=self.headers, params=params)

        def post(self, endpoint, data=None):
            url = f"{self.base_url}{endpoint}"
            return requests.post(url, headers=self.headers, json=data)

    return APIClient()


@pytest.fixture(scope="function")
def browser():
    """Фикстура для работы с браузером"""
    options = webdriver.ChromeOptions()

    # Оптимальные настройки для тестов
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--remote-debugging-port=9222")

    try:
        # Основной вариант с обычным Chrome
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"Ошибка при инициализации ChromeDriver: {e}")
        try:
            # Альтернативный вариант с Chrome for Testing
            service = Service(
                ChromeDriverManager(chrome_type=ChromeDriverManager).install())
            driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"Ошибка при инициализации Chrome for Testing: {e}")
            raise

    # Настройка авторизации
    driver.get(Config.KINO_URL)
    driver.add_cookie({
        "name": "X-API-KEY",
        "value": Config.HEADERS["X-API-KEY"],
        "domain": "kinopoisk.ru",
        "path": "/",
        "secure": True
    })
    driver.refresh()

    yield driver

    driver.quit()
