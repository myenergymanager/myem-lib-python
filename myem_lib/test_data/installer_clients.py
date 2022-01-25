"""Installer clients data."""

from uuid import UUID


clients = [
    {
        "id": 1,
        "user_id": 1,
        "installer_id": UUID("3b4408da-f0d6-446d-9b5c-fbe4735ff5e4"),
    },
    {
        "id": 2,
        "user_id": 2,
    },
]

comments = [
    {
        "id": 1,
        "client_id": 1,
        "message": "message 1",
    },
    {
        "id": 2,
        "client_id": 1,
        "message": "message 2",
    },
    {
        "id": 3,
        "client_id": 2,
        "message": "message 3",
    },
    {
        "id": 4,
        "client_id": 2,
        "message": "message 4",
    },
]
