import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import allure
import requests


class Config:
    """Конфигурационные параметры."""
    API_URL = "https://kinopoiskapiunofficial.tech/api/v2.2/"
    HEADERS = {
        "X-API-KEY": "50884c19-4a50-4f26-86ca-8d3bf8b256ea",
        "Content-Type": "application/json"
    }
    KINO_URL = "https://www.kinopoisk.ru"


@pytest.fixture
def api_client():
    """Фикстура для работы с API Kinopoisk."""

    class APIClient:
        def __init__(self):
            self.base_url = Config.API_URL
            self.headers = Config.HEADERS

        def get(self, endpoint, params=None):
            """GET запрос к API."""
            url = f"{self.base_url}{endpoint}"
            return requests.get(url, headers=self.headers, params=params)

        def post(self, endpoint, data=None):
            """POST запрос к API."""
            url = f"{self.base_url}{endpoint}"
            return requests.post(url, headers=self.headers, json=data)

    return APIClient()


def pytest_addoption(parser):
    """Добавляем опции для выбора браузера."""
    parser.addoption(
        "--browser", action="store", default="chrome",
        help="Браузер для тестов: chrome, firefox, edge"
    )
    parser.addoption(
        "--headless", action="store_true", help="Запуск в headless режиме"
    )
    parser.addoption(
        "--url", action="store", default="https://www.kinopoisk.ru/",
        help="URL для тестирования"
    )


@pytest.fixture(scope="function")
def driver(request):
    """Универсальная фикстура для инициализации браузера."""
    browser_name = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")
    base_url = request.config.getoption("--url")

    driver = None

    try:
        if browser_name.lower() == "chrome":
            driver = _init_chrome_driver(headless)
        elif browser_name.lower() == "firefox":
            driver = _init_firefox_driver(headless)
        elif browser_name.lower() == "edge":
            driver = _init_edge_driver(headless)
        else:
            raise ValueError(f"Неподдерживаемый браузер: {browser_name}")

    except Exception:
        # Если автоматическая установка не сработала, пробуем системный драйвер
        try:
            if browser_name.lower() == "chrome":
                options = Options()
                if headless:
                    options.add_argument("--headless")
                service = Service()
                driver = webdriver.Chrome(service=service, options=options)
        except Exception as fallback_error:
            pytest.skip(
                f"Не удалось инициализировать {browser_name}: {fallback_error}"
                )

    if driver is None:
        pytest.skip(f"Не удалось инициализировать браузер {browser_name}")

    # Устанавливаем таймауты
    driver.implicitly_wait(15)
    driver.set_page_load_timeout(45)

    # Сохраняем URL для использования в тестах
    driver.base_url = base_url

    yield driver

    # Закрываем браузер
    try:
        driver.quit()
    except Exception:
        pass


def _init_chrome_driver(headless):
    """Инициализация Chrome драйвера."""
    options = Options()

    # Базовые опции
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Опции для стабильности
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--ignore-certificate-errors")

    # Улучшенные настройки для производительности
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-renderer-backgrounding")

    if headless:
        options.add_argument("--headless=new")

    # Автоматическая установка драйвера
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Дополнительные настройки драйвера
    driver.set_script_timeout(30)

    return driver


def _init_firefox_driver(headless):
    """Инициализация Firefox драйвера."""
    options = FirefoxOptions()

    if headless:
        options.add_argument("--headless")

    service = Service(GeckoDriverManager().install())
    return webdriver.Firefox(service=service, options=options)


def _init_edge_driver(headless):
    """Инициализация Edge драйвера."""
    options = EdgeOptions()

    if headless:
        options.add_argument("--headless")

    service = Service(EdgeChromiumDriverManager().install())
    return webdriver.Edge(service=service, options=options)


@pytest.fixture
def base_url(driver):
    """Фикстура для базового URL."""
    return driver.base_url


# Хуки для обработки ошибок
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Создание скриншотов при падении тестов."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        try:
            driver = item.funcargs['driver']
            allure.attach(
                driver.get_screenshot_as_png(),
                name="screenshot_on_failure",
                attachment_type=allure.attachment_type.PNG
            )
        except Exception as e:
            print(f"Не удалось сделать скриншот: {e}")
