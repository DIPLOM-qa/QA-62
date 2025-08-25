import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import allure


def pytest_addoption(parser):
    """Добавляем опции для выбора браузера"""
    parser.addoption("--browser", action="store", default="chrome")
    parser.addoption("--headless", action="store_true")
    parser.addoption(
        "--url", action="store", default="https://www.kinopoisk.ru/")


@pytest.fixture(scope="function")
def driver(request):
    """Универсальная фикстура для инициализации браузера"""
    browser_name = request.config.getoption("--browser").lower()
    headless = request.config.getoption("--headless")
    base_url = request.config.getoption("--url")

    driver = None

    try:
        if browser_name == "chrome":
            driver = _init_chrome_driver(headless)
        elif browser_name == "firefox":
            driver = _init_firefox_driver(headless)
        elif browser_name == "edge":
            driver = _init_edge_driver(headless)
        else:
            pytest.skip(f"Неподдерживаемый браузер: {browser_name}")

    except Exception as e:
        print(f"Ошибка при инициализации {browser_name}: {e}")
        # Пробуем системный драйвер как запасной вариант
        try:
            if browser_name == "chrome":
                options = Options()
                _add_common_options(options, headless)
                service = Service()
                driver = webdriver.Chrome(service=service, options=options)
            else:
                pytest.skip(f"Не удалось инициализировать {browser_name}: {e}")
        except Exception as fallback_error:
            pytest.skip(
                f"Не удалось инициализировать {browser_name}:{fallback_error}")

    if driver is None:
        pytest.skip(f"Не удалось инициализировать браузер {browser_name}")

    # Устанавливаем таймауты
    driver.implicitly_wait(15)
    driver.set_page_load_timeout(30)
    driver.base_url = base_url

    yield driver

    # Закрываем браузер

    driver.quit()


def _init_chrome_driver(headless):
    """Инициализация Chrome драйвера"""
    options = Options()
    _add_common_options(options, headless)

    # Специфичные для Chrome опции
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def _init_firefox_driver(headless):
    """Инициализация Firefox драйвера"""
    options = FirefoxOptions()
    _add_common_options(options, headless)

    service = Service(GeckoDriverManager().install())
    return webdriver.Firefox(service=service, options=options)


def _init_edge_driver(headless):
    """Инициализация Edge драйвера"""
    options = EdgeOptions()
    _add_common_options(options, headless)

    service = Service(EdgeChromiumDriverManager().install())
    return webdriver.Edge(service=service, options=options)


def _add_common_options(options, headless):
    """Добавление общих опций для всех браузеров"""
    if not headless:
        options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    if headless:
        if hasattr(options, 'add_argument'):
            options.add_argument("--headless=new")
        else:
            options.headless = True


@pytest.fixture
def base_url(driver):
    """Фикстура для базового URL"""
    return driver.base_url


class TestKinopoisk:
    @allure.feature("Главная страница")
    @allure.story("Загрузка главной страницы")
    def test_01_main_page_loaded(self, driver):
        """Проверка загрузки главной страницы"""
        with allure.step("Открытие главной страницы"):
            driver.get("https://www.kinopoisk.ru/")

        with allure.step("Проверка заголовка страницы"):
            try:
                WebDriverWait(driver, 30).until(
                    lambda d: "кинопоиск" in d.title.lower()
                )
            except TimeoutException:
                allure.attach(
                    driver.get_screenshot_as_png(), name="main_page_failed",
                    attachment_type=allure.attachment_type.PNG)
                pytest.fail(
                    "Главная страница не загрузилась или "
                    "заголовок не соответствует ожидаемому")

    @allure.feature("Поиск")
    @allure.story("Поиск фильма")
    def test_02_search_movie(self, driver):
        """Тест поиска фильма"""
        with allure.step("Открытие главной страницы"):
            driver.get("https://www.kinopoisk.ru/")

        with allure.step("Ввод поискового запроса"):
            search_input = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((
                    By.CSS_SELECTOR, "input[name='kp_query']"))
            )
            ActionChains(driver).send_keys_to_element(
                search_input, "Крестный отец").perform()
            search_input.submit()

        with allure.step("Проверка результатов поиска"):
            try:
                WebDriverWait(driver, 30).until(
                    EC.visibility_of_element_located((
                        By.XPATH, "//*[contains(text(), 'Крестный отец')]"))
                )
            except TimeoutException:
                allure.attach(
                    driver.get_screenshot_as_png(), name="search_failed",
                    attachment_type=allure.attachment_type.PNG)
                pytest.fail("Результаты поиска не содержат искомый фильм")

    @allure.feature("Страница фильма")
    @allure.story("Элементы страницы фильма")
    def test_03_movie_page_elements(self, driver):
        """Проверка страницы фильма"""
        with allure.step("Открытие страницы фильма"):
            driver.get("https://www.kinopoisk.ru/film/325/")

        with allure.step("Проверка заголовка страницы"):
            try:
                WebDriverWait(driver, 30).until(
                    lambda d: "Крестный отец" in d.title
                )
            except TimeoutException:
                allure.attach(
                    driver.get_screenshot_as_png(), name="movie_title_failed",
                    attachment_type=allure.attachment_type.PNG)
                pytest.fail(
                    "Заголовок страницы фильма не соответствует ожидаемому")

        with allure.step("Проверка наличия рейтинга"):
            try:
                WebDriverWait(driver, 30).until(
                    EC.visibility_of_element_located((
                        By.CSS_SELECTOR, "span.styles_ratingKpTop__8p7mM"))
                )
            except TimeoutException:
                allure.attach(
                    driver.get_screenshot_as_png(), name="rating_missing",
                    attachment_type=allure.attachment_type.PNG)
                pytest.fail("Рейтинг фильма не отображается")

    @allure.feature("Футер")
    @allure.story("Проверка футера")
    def test_04_check_footer(self, driver):
        """Проверка футера"""
        with allure.step("Открытие главной страницы"):
            driver.get("https://www.kinopoisk.ru/")

        with allure.step("Проверка футера"):
            try:
                footer = WebDriverWait(driver, 30).until(
                    EC.visibility_of_element_located((
                        By.CSS_SELECTOR, "footer"))
                )
                assert "Яндекс" in footer.text
                "Текст 'Яндекс' не найден в футере"
            except TimeoutException:
                allure.attach(
                    driver.get_screenshot_as_png(), name="footer_missing",
                    attachment_type=allure.attachment_type.PNG)
                pytest.fail("Футер не отображается")

    @allure.feature("Авторизация")
    @allure.story("Проверка формы входа")
    def test_05_login_form(self, driver):
        """Проверка формы авторизации"""
        with allure.step("Открытие главной страницы"):
            driver.get("https://www.kinopoisk.ru/")

        with allure.step("Клик по кнопке входа"):
            try:
                login_button = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((
                        By.XPATH, "//button[contains(text(), 'Войти')]"))
                )
                login_button.click()
            except TimeoutException:
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="login_button_missing",
                    attachment_type=allure.attachment_type.PNG)
                pytest.fail("Кнопка входа не найдена или не кликабельна")


if __name__ == "__main__":
    pytest.main(["-v", "--tb=short", "--alluredir=allure-results"])
