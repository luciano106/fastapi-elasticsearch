import jwt
import os

from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from app.models import ErrorResponse

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretjwtkey")
ALGORITHM = "HS256"

   
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

def validate_jwt_token(token: str = Security(oauth2_scheme)):
    """
    Validate JWT token and return user payload or error.
    """
    if not token:
        error = ErrorResponse(code="MISSING_TOKEN", message="Authentication token is required.")
        raise HTTPException(status_code=401, detail=error.model_dump())
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        error = ErrorResponse(code="TOKEN_EXPIRED", message="Token has expired.")
        raise HTTPException(status_code=401, detail=error.model_dump())
    except jwt.InvalidTokenError:
        error = ErrorResponse(code="INVALID_TOKEN", message="Invalid authentication token.")
        raise HTTPException(status_code=401, detail=error.model_dump())