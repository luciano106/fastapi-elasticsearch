import uuid

from pydantic import BaseModel
from typing import List

class Movie(BaseModel):
    Title: str
    Year: int
    imdbID: str

class MovieSearchResponse(BaseModel):
    movies: List[Movie]
    total_results: int
    page: int
    size: int
    
class IndexMovieResponse(BaseModel):
    status: str
    total_indexed: int

class ErrorResponse(BaseModel):
    id: str
    code: str
    message: str

    def __init__(self, code: str, message: str):
        super().__init__(id=str(uuid.uuid4()), code=code, message=message)

class ErrorResponseDetail(BaseModel):
    detail: ErrorResponse