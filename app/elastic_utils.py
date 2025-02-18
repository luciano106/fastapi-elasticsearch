import requests

from fastapi import HTTPException
from app.database import es
from app.config import INDEX_NAME
from app.models import ErrorResponse

MOVIES_API_URL = "https://jsonmock.hackerrank.com/api/moviesdata/search/"

def create_index():
    """
    Create an index in Elasticsearch if it doesn't exist
    """
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(index=INDEX_NAME)


def fetch_movies_from_api(title: str, page: int):
    """
    Fetch movies from the Hackerrank external API.
    """
    url = f"{MOVIES_API_URL}?Title={title}&page={page}"

    try:
        response = requests.get(url, timeout=10)  # Set a timeout to avoid hanging requests
        response.raise_for_status()  # Raise an error for HTTP 4xx/5xx status codes

        return response.json()

    except requests.Timeout:
        raise HTTPException(
            status_code=504,
            detail={"code": "EXTERNAL_API_TIMEOUT", "message": "The external API request timed out."}
        ) from None

    except requests.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail={"code": "EXTERNAL_API_ERROR", "message": f"Error getting data from external API: {str(e)}"}
        ) from None


def index_movies(title: str = "", page: int = 1):
    """
    Gets movies from external API and indexes them in Elasticsearch.

    - `title`: (str) Title substring to search for movies (required).
    - `page`: (int) Home page (optional, defaults to `1`).
    If not provided, will loop through all available pages.
    """
    all_movies = []
    total_pages = None

    if not es.indices.exists(index=INDEX_NAME):
        create_index()

    while True:
        data = fetch_movies_from_api(title, page)

        if not data["data"]:  # If there are no more movies, we exit the loop
            break

        # We save `total_pages` in the first iteration
        if total_pages is None:
            total_pages = data["total_pages"]

        for movie in data["data"]:
            movie_doc = {
                "Title": movie["Title"],
                "Year": int(movie["Year"]),
                "imdbID": movie["imdbID"]
            }
            all_movies.append(movie_doc)

            # Index each document in Elasticsearch
            es.index(index=INDEX_NAME, id=movie["imdbID"], document=movie_doc)

        # If the user specified `page`, we only process that page and are done
        if total_pages and page >= total_pages:
            break

        page += 1  # next page

    return {"status": "Movies indexed", "total_indexed": len(all_movies)}

def search_movies(title: str = None, year: int = None, page: int = 1, size: int = 10):
    """
    Search movies in Elasticsearch with pagination.

- `title` (optional): Filter by substring in title.
- `year` (optional): Filter by exact year.
- `page` (optional, default 1): Page of results (1-indexed).
- `size` (optional, default 10): Number of results per page.
    """
    query = {"bool": {"must": []}}

    if title:
        query["bool"]["must"].append({
            "query_string": {
                "query": f"*{title}*",
                "default_field": "Title"
            }
        })

    if year:
        query["bool"]["must"].append({"term": {"Year": year}})

    from_value = (page - 1) * size

    response = es.search(index=INDEX_NAME, query=query, from_=from_value, size=size)

    return {
        "movies": [hit["_source"] for hit in response["hits"]["hits"]],
        "total_results": response["hits"]["total"]["value"],
        "page": page,
        "size": size
    }