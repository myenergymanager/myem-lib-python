"""User managements data."""

import json


roles = [{"id": 1, "name": "installer", "description": "installer"}]

users = [
    {
        "id": "3b4408da-f0d6-446d-9b5c-fbe4735ff5e4",
        "email": "email@test.fr",
        "hashed_password": "hashed_password",
        "is_active": True,
        "is_superuser": False,
        "is_verified": True,
        "first_name": "user1",
        "last_name": "user1",
        "phone": "0786237863",
        "address": {
            "name": "name",
            "address_addition": "address_addition",
            "zip_code": "12345",
            "city": "Lyon",
            "country": "France",
            "lat": 0.21,
            "lng": 0.23,
            "extra_data": json.dumps({"dummy": "data"}),
        },
        "role": "installer",
    },
    {
        "id": "525e1b0e-6000-4ca3-a7e7-617fdf4a4714",
        "email": "email2@test.fr",
        "hashed_password": "hashed_password2",
        "is_active": True,
        "is_superuser": False,
        "is_verified": True,
        "first_name": "user2",
        "last_name": "user2",
        "phone": "0786287697",
        "address": {
            "name": "name",
            "address_addition": "address_addition",
            "zip_code": "12345",
            "city": "Lyon",
            "country": "France",
            "lat": 0.21,
            "lng": 0.23,
            "extra_data": json.dumps({"dummy": "data"}),
        },
        "role": "installer",
    },
]
