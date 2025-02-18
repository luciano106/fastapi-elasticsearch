from fastapi import APIRouter
from app.routes.movies import router as movies_router

router = APIRouter()

router.include_router(movies_router, prefix="/api/v1/movies", tags=["Movies"])

