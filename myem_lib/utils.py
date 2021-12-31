"""Utils."""
import json
import os
from typing import Any, Dict
from urllib.request import urlopen

import jwt
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi_pagination import add_pagination
from jwcrypto.jwk import JWK
from pydantic import ValidationError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def init_app(app: FastAPI) -> None:
    """Init fast api app."""
    add_middleware(app)
    add_validation_exception_handler(app)
    add_pagination(app)


def add_validation_exception_handler(app: FastAPI) -> None:
    """Override validation exception_handler."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Override validation_exception_handler."""
        if len(exc.args[0][0].exc.args) > 0:
            return JSONResponse(
                {
                    "errors": [
                        {
                            element._loc: str(element.exc)  # pylint: disable=W0212
                            if not isinstance(element.exc, ValidationError)
                            else [
                                f"{nested_element._loc} {nested_element.exc.msg_template}"  # pylint: disable=W0212
                                for nested_element in element.exc.args[0]
                            ]
                        }  # pylint: disable=W0212
                        for element in exc.args[0][0].exc.args[0]
                    ]
                },
                status_code=422,
            )
        # Specific case with user micro service.
        else:
            return JSONResponse(
                {
                    "errors": [
                        {element._loc[1]: element.exc.msg_template}  # pylint: disable=W0212
                        for element in exc.args[0]
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


def get_public_key(index: int = 0) -> str:
    """Returns a public key from a url contains a decoded header and a token."""
    # we used urllib rather than requests because it's has an incompabilities with
    # fast api or other you can check the same error in this link
    # https://stackoverflow.com/questions/49820173/requests-recursionerror-maximum-recursion-depth-exceeded
    try:
        with urlopen(os.environ["PUBLIC_KEY_URL"]) as f:
            header_key = json.loads(f.read())["keys"][index]
            return JWK(**header_key).export_to_pem()
    except Exception:
        raise HTTPException(detail="Invalid Key", status_code=400) from Exception


def get_private_key(index: int = 0) -> str:
    """Returns a private key from a url contains a decoded header and a token."""
    try:
        with urlopen(os.environ["PUBLIC_KEY_URL"]) as f:
            header_key = json.loads(f.read())["keys"][index]
            return JWK(**header_key).export_to_pem(private_key=True, password=None)
    except Exception:
        raise HTTPException(detail="unauthorized", status_code=401) from Exception


def get_active_user(token: str = Depends(oauth2_scheme), index: int = 0) -> Dict["str", Any]:
    """Decode a jwt token."""
    try:
        decoded_token = jwt.decode(token, get_public_key(index), algorithms=["RS256"])
    except jwt.exceptions.InvalidAudienceError:
        # fast-api users specify the audience for some reason and that break our decode function
        # to solve this we will try to decode our token for simple users if it raise an
        # jwt.exceptions.InvalidAudienceError we decode the token with a specified audience
        try:
            decoded_token = jwt.decode(
                token, get_public_key(index), audience="fastapi-users:auth", algorithms=["RS256"]
            )
        except Exception:
            raise HTTPException(detail="unauthorized", status_code=401) from Exception
    except Exception:
        raise HTTPException(detail="unauthorized", status_code=401) from Exception

    return decoded_token
