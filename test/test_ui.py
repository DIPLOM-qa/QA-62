import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import allure


@pytest.fixture(scope="function")
def driver():
    """Фикстура для инициализации и закрытия браузера"""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument(
        "--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    yield driver
    driver.quit()


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
                assert "кинопоиск" in footer.text
                "Текст 'кинопоиск' не найден в футере"
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
