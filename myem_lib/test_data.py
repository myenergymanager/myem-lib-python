"""Integration test data."""
import json
from datetime import datetime, timedelta
from uuid import UUID


clients = [
    {
        "id": 1,
        "user_id": 1,
        "installer_id": "3b4408da-f0d6-446d-9b5c-fbe4735ff5e4",
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

equipments = [
    {
        "id": 1,
        "user_id": 1,
        "type": "SOLAR",
        "brand": "brand",
        "reference": "reference",
        "installed_at": datetime(2022, 1, 18),
    },
    {
        "id": 2,
        "user_id": 1,
        "type": "DEMOTIC",
        "brand": "brand",
        "reference": "reference",
        "installed_at": datetime(2022, 1, 18),
    },
    {
        "id": 3,
        "user_id": 1,
        "type": "SOLAR",
        "brand": "brand",
        "reference": "reference",
        "installed_at": datetime(2022, 1, 18),
    },
    {
        "id": 4,
        "user_id": 2,
        "type": "INVERTER",
        "brand": "brand",
        "reference": "reference",
        "installed_at": datetime(2022, 1, 18),
    },
]

roles = [{"id": 1, "name": "installer", "description": "installer"}]

installers = [
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
addresses = [
    {
        "id_address": 1,
        "street": "Pl. Pierre Renaudel, 69003 Lyon, France",
        "postal_code": "69001",
        "city": "Lyon",
        "country": "France",
        "latitude": 3.23,
        "longitude": 4.98,
    },
    {
        "id_address": 2,
        "street": "Gd Rue de Vaise, 69009 Lyon, France",
        "postal_code": "69003",
        "additional_data": "mma2",
        "city": "Lyon",
        "country": "France",
        "latitude": 0.23,
        "longitude": 0.98,
    },
]

customers = [
    {
        "id": 1,
        "id_formula": 1,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "id_address": 1,
    },
    {
        "id": 2,
        "id_formula": 2,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "id_address": 2,
    },
]

users = [
    {
        "id": 1,
        "email": "turing@myem.fr",
        "firstname": "Alan",
        "lastname": "Turing",
        "phone": "1111111111",
        "type": 1,
        "created_at": datetime.now(),
        "customer_id": 1,
    },
    {
        "id": 2,
        "email": "ritchie@myem.fr",
        "firstname": "Dennis",
        "lastname": "Ritchie",
        "phone": "2222222222",
        "type": 1,
        "created_at": datetime.now(),
        "customer_id": 2,
    },
]

meters = [
    {
        "id": 1,
        "guid": "23144138893314",
        "name": "Mon Compteur",
        "customer_id": 1,
        "created_at": datetime.utcnow() - timedelta(days=2),
        "updated_at": datetime.utcnow() - timedelta(days=2),
    },
    {
        "id": 2,
        "guid": "11111111111113",
        "name": "Mon Compteur 2",
        "customer_id": 1,
        "created_at": datetime.utcnow() - timedelta(days=1),
        "updated_at": datetime.utcnow() - timedelta(days=1),
    },
    {
        "id": 3,
        "guid": "19137481697692",
        "name": "Mon Compteur",
        "customer_id": 2,
        "created_at": datetime.utcnow() - timedelta(days=2),
        "updated_at": datetime.utcnow() - timedelta(days=2),
    },
]

consents_sources = [
    {
        "id": 1,
        "name": "DataConnect",
    },
    {
        "id": 3,
        "name": "Chameleon",
    },
]
consents = [
    {
        "id": 1,
        "id_meter": 1,
        "id_consent_source": 1,
        "revoked_at": datetime.utcnow() - timedelta(days=1),
    },
    {
        "id": 2,
        "id_meter": 1,
        "id_consent_source": 1,
    },
    {
        "id": 3,
        "id_meter": 1,
        "id_consent_source": 3,
        "revoked_at": datetime.utcnow() - timedelta(days=1),
        "meta_data": '{ "chm_guid":"0CA2F4076054D254" }',
    },
    {
        "id": 4,
        "id_meter": 1,
        "id_consent_source": 3,
        "meta_data": '{ "chm_guid":"0CA2F489FF0002A6" }',
    },
    {
        "id": 5,
        "id_meter": 3,
        "id_consent_source": 3,
        "meta_data": '{ "chm_guid": "0CA2F489FF0872A6" }',
    },
]
meter_metrics = [
    {"id": 1, "meter_id": 1, "created_at": datetime.utcnow() - timedelta(minutes=15)},
    {"id": 2, "meter_id": 1, "created_at": datetime.utcnow() - timedelta(minutes=120)},
    {"id": 3, "meter_id": 3, "created_at": datetime.utcnow() - timedelta(days=1)},
]

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

installation_requests = [
    {
        "id": 1,
        "user_id": 16,
        "status": "NEW",
        "budget": 10.13,
        "equipment_type": "SOLAR",
        "equipment_brand": "brand1",
        "equipment_model": "model1",
        "comment": "comment1",
    },
    {
        "id": 2,
        "user_id": 16,
        "status": "PENDING",
        "budget": 20.23,
        "equipment_type": "DEMOTIC",
        "equipment_brand": "brand1",
        "equipment_model": "model1",
        "comment": "comment1",
    },
    {
        "id": 3,
        "user_id": 20,
        "status": "NEW",
        "budget": 10.23,
        "equipment_type": "INVERTER",
        "equipment_brand": "brand2",
        "equipment_model": "model2",
        "comment": "comment2",
    },
    {
        "id": 4,
        "user_id": 20,
        "status": "CLOSED",
        "budget": 5.23,
        "equipment_type": "SOLAR",
        "equipment_brand": "brand2",
        "equipment_model": "model2",
        "comment": "comment2",
    },
]
