"""Utils."""
import json
import os
from typing import Any, Dict

import jwt
from jwt import PyJWKClient
from nameko.web.handlers import HttpRequestHandler
from werkzeug import Response
from myem_lib.exceptions import BadRequest, HttpError, Unauthenticated, Unauthorized


class HttpEntrypoint(HttpRequestHandler):
    """Control formatting of errors returned from the service by overriding response_from_exception.

    more https://nameko.readthedocs.io/en/stable/built_in_extensions.html#http.
    """

    def response_from_exception(self, exc: Exception) -> Response:
        """Response_from_exception."""

        if isinstance(exc, HttpError):
            response = Response(
                json.dumps(
                    {
                        "errors": exc.args[0],
                    }
                ),
                status=exc.status_code,
                mimetype="application/json",
            )
            return response
        return HttpRequestHandler.response_from_exception(self, exc)


http = HttpEntrypoint.decorator


def get_public_key(token: str) -> Any:
    """Returns a public key from a url contains a decoded header and a token."""
    # env var will be loaded from the specific micro service.
    url = os.getenv("PUBLIC_KEY_URL")
    try:
        jwk_client = PyJWKClient(url)
        return jwk_client.get_signing_key_from_jwt(token).key
    except Exception:
        raise Unauthenticated("Invalid token") from Exception


def decode_jwt_token(token: str) -> Dict[str, Any]:
    """Decode a jwt token."""

    # the token is split into two parts based on a space character
    # to separate authorization type from token
    parts = token.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise BadRequest("Authorization header missed")

    token = parts[1]

    public_key = get_public_key(token=token)

    try:
        decoded_token = jwt.decode(token, public_key, algorithms=["RS256"])
    except Exception:
        raise Unauthorized("unauthorized !") from Exception

    return decoded_token


def get_user_from_request_header(request: Any) -> Dict[str, Any]:
    """Get user data from a request header."""
    token = request.headers.get("Authorization", None)

    if not token:
        raise Unauthenticated("not authenticated !")

    return decode_jwt_token(token=token)
