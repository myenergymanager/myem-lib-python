"""Exceptions."""


class HttpError(Exception):
    """HttpError."""

    error_code = "BAD_REQUEST"
    status_code = 400


class NotFound(HttpError):
    """NotFound Exception."""

    error_code = "NOT_FOUND"
    status_code = 404


class BadRequest(HttpError):
    """BadRequest Exception."""

    error_code = "BAD_REQUEST"
    status_code = 400


class Unauthenticated(HttpError):
    """Unauthenticated Exception."""

    error_code = "NOT_AUTHENTICATED"
    status_code = 403


class Unauthorized(HttpError):
    """Unauthorized Exception."""

    error_code = "NOT_AUTHORIZED"
    status_code = 401
