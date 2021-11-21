"""Utils."""
import json
from typing import Any, Dict

import jwt
from jwt import PyJWKClient
from nameko.web.handlers import HttpRequestHandler
from werkzeug import Response
from myem_lib.exceptions import BadRequest, HttpError, Unauthenticated


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


class TokenDecoder:
    """Token Decoder Class."""

    @staticmethod
    def get_public_key(url: str, token: str) -> Any:
        """Returns a public key from a url contains a decoded header and a token."""
        try:
            jwk_client = PyJWKClient(url)
            return jwk_client.get_signing_key_from_jwt(token).key
        except Exception:
            raise Unauthenticated("Token not valid !") from Exception

    @staticmethod
    def decode_jwt_token(token: str, url: str) -> Dict[str, Any]:
        """Decode a jwt token."""

        parts = token.split()

        if len(parts) != 2:
            raise BadRequest("Authorization header missed")

        token = parts[1]

        public_key = TokenDecoder.get_public_key(url=url, token=token)

        return jwt.decode(token, public_key, algorithms=["RS256"])
