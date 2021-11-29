"""Utils."""
import json
import os
from typing import Any, Dict

import jwt
from jwt import PyJWKClient
from nameko.web.handlers import HttpRequestHandler
from werkzeug import Response
from myem_lib.exceptions import BadRequest, HttpError, Unauthenticated, Unauthorized
from functools import partial
from nameko.extensions import register_entrypoint


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

    def __init__(self, method, url, expected_exceptions=(), **kwargs):
        super().__init__(method, url, expected_exceptions=expected_exceptions)
        self.allowed_origin = kwargs.get('origin', ['*'])
        self.allowed_methods = kwargs.get('methods', ['*'])
        self.allow_credentials = kwargs.get('credentials', True)

    def handle_request(self, request):
        self.request = request
        if request.method == 'OPTIONS':
            return self.response_from_result(result='')
        return super().handle_request(request)

    def response_from_result(self, *args, **kwargs):
        response = super(HttpEntrypoint, self).response_from_result(*args, **kwargs)
        response.headers.add("Access-Control-Allow-Headers",
                             self.request.headers.get("Access-Control-Request-Headers"))
        response.headers.add("Access-Control-Allow-Credentials", str(self.allow_credentials).lower())
        response.headers.add("Access-Control-Allow-Methods", ",".join(self.allowed_methods))
        response.headers.add("Access-Control-Allow-Origin", ",".join(self.allowed_origin))
        return response

    @classmethod
    def decorator(cls, *args, **kwargs):
        """
        We're overriding the decorator classmethod to allow it to register an options
        route for each standard REST call. This saves us from manually defining OPTIONS
        routes for each CORs enabled endpoint
        """
        def registering_decorator(fn, args, kwargs):
            instance = cls(*args, **kwargs)
            register_entrypoint(fn, instance)
            if instance.method in ('GET', 'POST', 'DELETE', 'PUT', 'PATCH') and \
                    ('*' in instance.allowed_methods or instance.method in instance.allowed_methods):
                options_args = ['OPTIONS'] + list(args[1:])
                options_instance = cls(*options_args, **kwargs)
                register_entrypoint(fn, options_instance)
            return fn

        if len(args) == 1 and isinstance(args[0], types.FunctionType):
            return registering_decorator(args[0], args=(), kwargs={})
        else:
            return partial(registering_decorator, args=args, kwargs=kwargs)
        # more https://github.com/nameko/nameko/issues/309
        # https://github.com/harel/nameko-cors/edit/master/__init__.py


http = HttpEntrypoint.decorator


def get_public_key(token: str) -> Any:
    """Returns a public key from a url contains a decoded header and a token."""
    # env var will be loaded from the specific micro service.
    url = os.getenv("PUBLIC_KEY_URL", "INVALID")
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
