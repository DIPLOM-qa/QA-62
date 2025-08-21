class Config:
    API_URL = "https://hd.kinopoisk.ru/"
    API_KEY = "50884c19-4a50-4f26-86ca-8d3bf8b256ea"

    HEADERS = {
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }

    # Тестовые данные
    TEST_FILM_ID = 1100777  # Триггер
    TEST_SERIES_ID = 5512084  # Сериал для теста сезонов
    TEST_FILM_WITH_AWARDS_ID = 258687  # Интерстеллар (есть награды)
    TEST_FILM_WITH_SIMILARS_ID = 258687  # Интерстеллар (есть похожие фильмы)
