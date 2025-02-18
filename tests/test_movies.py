import os
import pytest

from fastapi import HTTPException
from fastapi_cache import FastAPICache
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.database import es
from app.config import INDEX_NAME
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

os.environ["INDEX_NAME"] = "movies_test"
from app.main import app

@pytest.fixture
def setup_test_index():
    """
    Creates a temporary Elasticsearch index for testing.
    Ensures the index exists before each test and deletes it afterward.
    """
    test_index = os.getenv("INDEX_NAME", "movies_test")
    
    if es.indices.exists(index=test_index):
        es.indices.delete(index=test_index)

    es.indices.create(index=test_index)
    yield test_index

    es.indices.delete(index=test_index, ignore=[400, 404])


@pytest.fixture
def client():
    """
    Creates a synchronous test client for FastAPI.
    """
    return TestClient(app)


@pytest.fixture
def auth_token(client):
    """
    Generates a valid JWT token for authentication.
    """
    response = client.post("/token", data={"username": "user", "password": "password"})
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def headers(auth_token):
    """
    Returns headers with an authentication token for protected endpoints.
    """
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def mock_external_api():
    """
    Mock response from the external movie API.
    """
    return {
        "page": 1,
        "per_page": 10,
        "total": 3,
        "total_pages": 1,
        "data": [
            {"Title": "The Matrix", "Year": 1999, "imdbID": "tt0133093"},
            {"Title": "The Matrix Reloaded", "Year": 2003, "imdbID": "tt0234215"},
            {"Title": "The Matrix Revolutions", "Year": 2003, "imdbID": "tt0242653"}
        ]
    }

@pytest.fixture(scope="session", autouse=True)
def init_test_cache():
    """Inicializa la caché en memoria antes de correr los tests."""
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")

@pytest.fixture(scope="session", autouse=True)
def init_test_cache():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")

@pytest.fixture(autouse=True)
def clear_cache():
    FastAPICache.clear()

@patch("app.elastic_utils.fetch_movies_from_api")
def test_index_movies(mock_fetch_movies, client, headers, setup_test_index, mock_external_api):
    """
    Tests the `/index` endpoint by mocking the external API but using real Elasticsearch.
    """
    mock_fetch_movies.return_value = mock_external_api  # Mock API response

    response = client.post("/api/v1/movies/index?title=Matrix&page=1", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Movies indexed"
    assert data["total_indexed"] == 3  # The mocked API returns 3 movies


def test_index_movies_invalid_token(client):
    """
    Tests unauthorized access to `/index` endpoint (missing token).
    """
    response = client.post("/api/v1/movies/index?title=Matrix&page=1")

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "MISSING_TOKEN"


@patch("app.elastic_utils.fetch_movies_from_api")
def test_external_api_timeout(mock_fetch_movies, client, headers):
    """
    Simulates an external API timeout.
    """
    mock_fetch_movies.side_effect = HTTPException(
        status_code=504,
        detail={"code": "EXTERNAL_API_TIMEOUT", "message": "The external API request timed out."}
    )

    response = client.post("/api/v1/movies/index?title=Matrix&page=1", headers=headers)

    assert response.status_code == 504
    assert response.json()["detail"]["code"] == "EXTERNAL_API_TIMEOUT"


def test_search_movies(client, headers, setup_test_index):
    """
    Tests the `/search` endpoint by inserting real data into Elasticsearch.
    """
    test_index = setup_test_index

    es.index(index=test_index, id="test123", document={"Title": "The Matrix", "Year": 1999, "imdbID": "tt0133093"})
    es.index(index=test_index, id="test124", document={"Title": "The Matrix Reloaded", "Year": 2003, "imdbID": "tt0234215"})
    es.index(index=test_index, id="test125", document={"Title": "The Matrix Revolutions", "Year": 2003, "imdbID": "tt0242653"})
    es.indices.refresh(index=test_index)

    response = client.get("/api/v1/movies/search?title=Matrix&page=1&size=10", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total_results"] == 3
    assert len(data["movies"]) == 3
    
@patch("app.elastic_utils.fetch_movies_from_api")
def test_search_movies_no_results(mock_fetch_movies, client, headers, setup_test_index, mock_external_api):
    """
    Tests `/search` when no movies match the criteria.
    """    

    mock_fetch_movies.return_value = {
        "page": 1,
        "per_page": 10,
        "total": 0,
        "total_pages": 0,
        "data": []
    }

    response = client.get("/api/v1/movies/search?title=NonExistent&page=1&size=10", headers=headers)

    print("🔍 Debugging response JSON:", response.json())
    print("🔍 Debugging response status code:", response.status_code)

    assert response.status_code == 200
    data = response.json()

    assert data["total_results"] == 0
    assert data["movies"] == []
    
@patch("app.elastic_utils.fetch_movies_from_api")
def test_index_movies_no_results(mock_fetch_movies, client, headers, setup_test_index):
    """
    Tests `/index` when the external API returns no movies.
    """
    mock_fetch_movies.return_value = {
        "page": 1,
        "per_page": 10,
        "total": 0,
        "total_pages": 0,
        "data": []
    }

    response = client.post("/api/v1/movies/index?title=NonExistent&page=1", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Movies indexed"
    assert data["total_indexed"] == 0

@patch("app.elastic_utils.fetch_movies_from_api")
def test_index_movies_multiple_pages(mock_fetch_movies, client, headers, setup_test_index):
    """
    Tests `/index` when the external API returns multiple pages.
    """
    mock_fetch_movies.side_effect = [
        {
            "page": 1,
            "per_page": 10,
            "total": 20,
            "total_pages": 2,
            "data": [{"Title": f"Movie {i}", "Year": 2000, "imdbID": f"tt000{i}"} for i in range(10)]
        },
        {
            "page": 2,
            "per_page": 10,
            "total": 20,
            "total_pages": 2,
            "data": [{"Title": f"Movie {i}", "Year": 2000, "imdbID": f"tt000{i}"} for i in range(10, 20)]
        }
    ]

    response = client.post("/api/v1/movies/index?title=Movies&page=1", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total_indexed"] == 20

@patch("app.elastic_utils.fetch_movies_from_api")
def test_index_movies_invalid_data(mock_fetch_movies, client, headers, setup_test_index):
    """
    Tests `/index` when the external API returns malformed data.
    """
    mock_fetch_movies.return_value = {
        "page": 1,
        "per_page": 10,
        "total": 3,
        "total_pages": 1,
        "data": [
            {"Title": "The Matrix", "Year": "1999"},  # Falta imdbID
            {"Title": "Inception"},  # Falta Year e imdbID
            {}  # Objeto vacío
        ]
    }

    response = client.post("/api/v1/movies/index?title=Matrix&page=1", headers=headers)

    assert response.status_code == 500
    
@patch("app.elastic_utils.fetch_movies_from_api")
@patch("app.database.es.index")
def test_index_movies_elasticsearch_failure(mock_es_index, mock_fetch_movies, client, headers, setup_test_index):
    """
    Tests `/index` when Elasticsearch fails.
    """
    mock_fetch_movies.return_value = {
        "page": 1,
        "per_page": 10,
        "total": 3,
        "total_pages": 1,
        "data": [
            {"Title": "The Matrix", "Year": 1999, "imdbID": "tt0133093"},
            {"Title": "Inception", "Year": 2010, "imdbID": "tt1375666"},
            {"Title": "Interstellar", "Year": 2014, "imdbID": "tt0816692"}
        ]
    }

    mock_es_index.side_effect = Exception("Elasticsearch down")

    response = client.post("/api/v1/movies/index?title=Matrix&page=1", headers=headers)

    assert response.status_code == 500
    assert response.json()["code"] == "SERVER_ERROR"

def test_index_movies_invalid_token(client):
    """
    Tests unauthorized access to `/index` endpoint.
    """
    response = client.post("/api/v1/movies/index?title=Matrix&page=1")

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "MISSING_TOKEN"