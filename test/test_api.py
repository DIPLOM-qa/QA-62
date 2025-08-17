from config import Config


def test_get_film_by_id(api_client):
    """Тест получения данных о фильме по ID"""
    response = api_client.get(f"/films/{Config.TEST_FILM_ID}")
    assert response.status_code == 200
    data = response.json()
    assert data["kinopoiskId"] == Config.TEST_FILM_ID
    assert data["nameRu"] == "Триггер"


def test_get_series_seasons(api_client):
    """Тест получения данных о сезонах сериала"""
    response = api_client.get(f"/films/{Config.TEST_SERIES_ID}/seasons")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) > 0


def test_get_film_awards(api_client):
    """Тест получения данных о наградах фильма"""
    response = api_client.get(
        f"/films/{Config.TEST_FILM_WITH_AWARDS_ID}/awards")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) > 0


def test_get_similar_films(api_client):
    """Тест получения списка похожих фильмов"""
    response = api_client.get(
        f"/films/{Config.TEST_FILM_WITH_SIMILARS_ID}/similars")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) > 0

    def test_empty_film_request(api_client):
        """Тест поиска фильма с пустым запросом"""
    response = api_client.get("/films/")
    assert response.status_code == 400
    assert "message" in response.json()


def test_empty_seasons_request(api_client):
    """Тест поиска сезонов с пустым ID"""
    response = api_client.get("/films/{}/seasons")
    assert response.status_code == 400
    assert "message" in response.json()


def test_unsupported_post_method(api_client):
    """Тест не поддерживаемого метода POST"""
    response = api_client.post(f"/films/{Config.TEST_FILM_ID}")
    assert response.status_code in [500, 405]  # 500 или 405 Method Not Allowed


def test_empty_distributions_request(api_client):
    """Тест получения данных о прокате с пустым ID"""
    response = api_client.get("/films/{}/distributions")
    assert response.status_code == 400
    assert "message" in response.json()


def test_future_premieres(api_client):
    """Тест поиска кинопремьер в будущем"""
    response = api_client.get(
        "/films/premieres", params={"year": 2030, "month": "JANUARY"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []
