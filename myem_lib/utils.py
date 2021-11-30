"""Utils."""
import os
from typing import Any, Dict

import jwt
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from myem_lib.exceptions import HttpError, Unauthenticated, Unauthorized


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)
session = sessionmaker(bind=engine)

app = FastAPI()

router = InferringRouter()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Http Exception handler."""
    if isinstance(exc, HttpError):
        return JSONResponse(
            content={
                "errors": exc.args[0],
            },
            status_code=exc.status_code,
        )
    return JSONResponse(content={"errors": "Internal server error"}, status_code=500)


def get_public_key(token: str = Depends(oauth2_scheme)) -> Any:
    """Returns a public key from a url contains a decoded header and a token."""
    # env var will be loaded from the specific micro service.
    url = os.getenv("PUBLIC_KEY_URL", "INVALID URL")
    try:
        jwk_client = jwt.PyJWKClient(url)
        return jwk_client.get_signing_key_from_jwt(token).key
    except Exception:
        raise Unauthenticated("Invalid token") from Exception


def get_active_user(
    token: str = Depends(oauth2_scheme), public_key: str = Depends(get_public_key)
) -> Dict["str", Any]:
    """Decode a jwt token."""
    try:
        decoded_token = jwt.decode(token, public_key, algorithms=["RS256"])
    except Exception:
        raise Unauthorized("unauthorized !") from Exception

    return decoded_token


def get_db() -> Any:
    """Get database instance."""
    db = session()
    try:
        yield db
    finally:
        db.close()
