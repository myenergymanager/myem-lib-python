"""FastApiSettingsMixin."""
import json
import os
from typing import Any
from urllib.request import urlopen

import jwt
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi_pagination import add_pagination
from jwcrypto.jwk import JWK
from nameko.exceptions import RemoteError


class RPCValidationException(Exception):
    """RPC Validation Exception."""


class FastApiSettingsMixin:
    """FastApi settings mixin."""

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    @classmethod
    def init_app(cls, app: FastAPI) -> None:
        """Init fast api app."""
        cls.add_middleware(app)
        cls.add_validation_exception_handler(app)
        cls.add_rpc_remote_validation_exception_handler(app)
        add_pagination(app)

    @classmethod
    def add_rpc_remote_validation_exception_handler(
        cls, app: FastAPI, remote_rpc_exc: type[Exception] = RemoteError
    ) -> None:
        """Add rpc remote validation exception_handler."""

        @app.exception_handler(remote_rpc_exc)
        async def http_exception_handler(request: Any, exc: Any) -> JSONResponse:
            if exc.exc_type == "RPCValidationException":
                return JSONResponse({"detail": exc.value}, status_code=status.HTTP_400_BAD_REQUEST)
            return JSONResponse(
                {"detail": "Erreur interne du serveur"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @classmethod
    def add_validation_exception_handler(cls, app: FastAPI) -> None:
        """Override validation exception_handler."""

        @app.exception_handler(RequestValidationError)
        async def validation_exception_handler(
            request: Request, exc: RequestValidationError
        ) -> JSONResponse:
            """Override validation_exception_handler."""
            errors: Any = []
            for e in exc.errors():
                new_dict = current = {}
                existed = False
                for item in errors:
                    if str(e["loc"][1]) == list(item.keys())[0]:
                        new_dict = current = item
                        existed = True
                        break
                for i in range(1, len(e["loc"])):
                    if i == len(e["loc"]) - 1:
                        current[str(e["loc"][i])] = e["msg"]
                    elif current.get(str(e["loc"][i])):
                        current = current[str(e["loc"][i])]
                    else:
                        current[str(e["loc"][i])] = {}
                        current = current[str(e["loc"][i])]
                if not existed:
                    errors.append(new_dict)
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=jsonable_encoder({"errors": errors}),
            )

    @classmethod
    def add_middleware(cls, app: FastAPI) -> None:
        """Added middleware to a fast api application."""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @classmethod
    def get_public_key(cls, index: int = 0) -> str:
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

    @classmethod
    def get_private_key(cls, index: int = 0) -> str:
        """Returns a private key from a url contains a decoded header and a token."""
        try:
            with urlopen(os.environ["PUBLIC_KEY_URL"]) as f:
                header_key = json.loads(f.read())["keys"][index]
                return JWK(**header_key).export_to_pem(private_key=True, password=None)
        except Exception:
            raise HTTPException(detail="unauthorized", status_code=401) from Exception

    @classmethod
    def get_active_user(
        cls,
        token: str = Depends(oauth2_scheme),
        audience: str = "fastapi-users:auth",
        index: int = 0,
    ) -> dict["str", Any]:
        """Decode a jwt token."""
        try:
            decoded_token = jwt.decode(token, cls.get_public_key(index), algorithms=["RS256"])
        except jwt.exceptions.InvalidAudienceError:
            # fast-api users specify the audience for some reason and that break our decode function
            # to solve this we will try to decode our token for simple users if it raise an
            # jwt.exceptions.InvalidAudienceError we decode the token with a specified audience
            try:
                decoded_token = jwt.decode(
                    token, cls.get_public_key(index), audience=audience, algorithms=["RS256"]
                )
            except Exception:
                raise HTTPException(detail="unauthorized", status_code=401) from Exception
        except Exception:
            raise HTTPException(detail="unauthorized", status_code=401) from Exception

        return decoded_token
