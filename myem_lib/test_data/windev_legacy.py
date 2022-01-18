"""Windev legacy data."""

from datetime import datetime, timedelta


formulas = [{"id": 1, "title": "formula1"}, {"id": 2, "title": "formula2"}]

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
