"""Ui notifications data."""

from uuid import UUID


notifications = [
    {
        "id": 1,
        "user_id": UUID("3b4408da-f0d6-446d-9b5c-fbe4735ff5e4"),
        "title": "notification 1",
        "content": "notification content 1",
        "status": "NEW",
        "redirect_to": "https://www.google.com/",
    },
    {
        "id": 2,
        "user_id": UUID("3b4408da-f0d6-446d-9b5c-fbe4735ff5e4"),
        "title": "notification 2",
        "content": "notification content 2",
        "status": "NEW",
        "redirect_to": "https://www.google.com/",
    },
    {
        "id": 3,
        "user_id": UUID("3b4408da-f0d6-446d-9b5c-fbe4735ff5e4"),
        "title": "notification 3",
        "content": "notification content 3",
        "status": "NEW",
        "redirect_to": "https://www.google.com/",
    },
    {
        "id": 4,
        "user_id": UUID("3b4408da-f0d6-446d-9b5c-fbe4735ff5e4"),
        "title": "notification 4",
        "content": "notification content 4",
        "status": "READ",
        "redirect_to": "https://www.google.com/",
    },
    {
        "id": 5,
        "user_id": UUID("3b4408da-f0d6-446d-9b5c-fbe4735ff5e4"),
        "title": "notification 5",
        "content": "notification content 5",
        "status": "ARCHIVED",
        "redirect_to": "https://www.google.com/",
    },
    {
        "id": 6,
        "user_id": UUID("525e1b0e-6000-4ca3-a7e7-617fdf4a4714"),
        "title": "notification 6",
        "content": "notification content 6",
        "status": "NEW",
        "redirect_to": "https://www.google.com/",
    },
]
