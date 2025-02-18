import logging

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.models import ErrorResponse

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            error = ErrorResponse(code=str(e.status_code), message=e.detail)
            logger.error(f"Error {e.status_code}: {e.detail}")
            return JSONResponse(status_code=e.status_code, content=error.model_dump())
        except Exception as e:
            error = ErrorResponse(code="SERVER_ERROR", message="An unexpected error occurred.")
            logger.exception("Unexpected server error")
            return JSONResponse(status_code=500, content=error.model_dump())
