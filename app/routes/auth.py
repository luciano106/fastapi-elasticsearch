from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import jwt
import datetime
import os

router = APIRouter(tags=["Auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretjwtkey")
ALGORITHM = "HS256"
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")  # Default to local

# Dummy user for testing
fake_user_db = {"user": {"username": "user", "password": "password"}}

if ENVIRONMENT == "local":
    @router.post("/token", summary="Generate JWT Token")
    def login(form_data: OAuth2PasswordRequestForm = Depends()):
        """
        This endpoint generates a **JWT access token** for authentication.

        How it works:
        1. In Swagger UI (`/docs`):
        - Click "Authorize" (🔒).
        - Enter your `username` = user and `password` = password.
        - Swagger will automatically retrieve the token and use it for secured endpoints.

        2. Public Endpoint:
        - This endpoint does **not** require authentication.
        - It is **publicly accessible** for users to obtain an authentication token to test.

        3. Using the Token in REST Clients (Postman, cURL, etc.):
        - Make a `POST /token` request to retrieve a token, same credentials point 1 above.
        - Use the token in the `Authorization` header for protected requests:
            ```bash
            curl -X GET "http://localhost:8000/movies/search?title=Sun" \
            -H "Authorization: Bearer eyJhbGciOiJIUzI..."
            ```

        Once authenticated, you can access all protected endpoints without manually passing the token in Swagger UI.
        """
        user = fake_user_db.get(form_data.username)
        if not user or form_data.password != user["password"]:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Create JWT token
        expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        token = jwt.encode({"sub": user["username"], "exp": expiration}, SECRET_KEY, algorithm=ALGORITHM)

        return {"access_token": token, "token_type": "bearer"}