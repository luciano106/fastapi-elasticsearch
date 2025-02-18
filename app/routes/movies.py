from fastapi import APIRouter, HTTPException, Query, Depends
from app.security import validate_jwt_token 
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache
from app.elastic_utils import search_movies as search_movies_util, index_movies as index_movies_util
from app.models import ErrorResponseDetail, IndexMovieResponse, MovieSearchResponse

router = APIRouter()

@router.post("/index", dependencies=[Depends(validate_jwt_token)], responses={
                 200: {"model": IndexMovieResponse, "description": "Successful response."},
                 400: {"model": ErrorResponseDetail, "description": "Invalid request parameters."},
                 401: {"model": ErrorResponseDetail, "description": "Unauthorized. Invalid or missing token."},
                 502: {"model": ErrorResponseDetail, "description": "External API error while fetching movies."},
                 504: {"model": ErrorResponseDetail, "description": "External API timeout."},
             })
def index_movies_endpoint(title: str = Query("", description="Optional title substring"),
                          page: int = Query(1, description="Optional starting page")):
    """
    Endpoint to index movies in Elasticsearch.

    - `title` (optional): Substring to filter movies by title. If empty, it fetches all available movies.
    - `page` (optional, default `1`): The starting page to fetch movies from the external API.
    - If the client sends the `Idempotency-Key` header, duplicate requests within 10 minutes will be rejected

    This endpoint retrieves movies from an external API and stores them in Elasticsearch.
    If a title is provided, only movies containing that substring will be indexed.
    If no title is given, all movies will be indexed.
    """
    result = index_movies_util(title, page)
    
    FastAPICache.clear()
    
    return IndexMovieResponse(**result)


@router.get("/search", dependencies=[Depends(validate_jwt_token)], responses={
                 200: {"model": MovieSearchResponse, "description": "Successful response."},
                 401: {"model": ErrorResponseDetail, "description": "Unauthorized. Invalid or missing token."}})
@cache(expire=300)
def search_movies_endpoint(title: str = Query(..., description="Substring to search in movie titles"),
                           year: int = Query(None, description="Exact year of the movie"),
                           page: int = Query(1, ge=1, description="Page number (default: 1)"),
                           size: int = Query(10, ge=1, le=100, description="Number of results per page (default: 10, max: 100)")):
    """
    Endpoint to search for movies in Elasticsearch with pagination.

    - `title` (required): Substring to search for in movie titles.
    - `year` (optional): Filter by exact release year.
    - `page` (optional, default `1`): The page number to retrieve.
    - `size` (optional, default `10`, max `100`): The number of results per page.
    
    This endpoint queries Elasticsearch for movies matching the given criteria.
    It supports pagination and returns a paginated list of movies that match the search conditions.
    """
    
    movies_data = search_movies_util(title=title, year=year, page=page, size=size)
    
    return MovieSearchResponse(**movies_data)