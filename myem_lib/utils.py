"""Utils."""
import os
from typing import Any, Dict

import jwt
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def init_app(app: FastAPI) -> None:
    """Init fast api app."""
    add_middleware(app)
    add_validation_exception_handler(app)


def add_validation_exception_handler(app: FastAPI) -> None:
    """Override validation exception_handler."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Override validation_exception_handler."""
        return JSONResponse(
            {
                "errors": [
                    {element._loc: element.exc.msg_template}  # pylint: disable=W0212
                    for element in exc.args[0][0].exc.args[0]
                ]
            },
            status_code=422,
        )


def add_middleware(app: FastAPI) -> None:
    """Added middleware to a fast api application."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def get_public_key(token: str = Depends(oauth2_scheme)) -> Any:
    """Returns a public key from a url contains a decoded header and a token."""
    # env var will be loaded from the specific micro service.
    url = os.environ["PUBLIC_KEY_URL"]
    try:
        jwk_client = jwt.PyJWKClient(url)
        return jwk_client.get_signing_key_from_jwt(token).key
    except Exception:
        raise HTTPException(detail="Invalid token", status_code=400) from Exception


def get_active_user(
    token: str = Depends(oauth2_scheme), public_key: str = Depends(get_public_key)
) -> Dict["str", Any]:
    """Decode a jwt token."""
    try:
        decoded_token = jwt.decode(token, public_key, algorithms=["RS256"])
    except Exception:
        raise HTTPException(detail="unauthorized", status_code=401) from Exception

    return decoded_token
