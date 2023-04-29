from fastapi.testclient import TestClient
from fastapi import status
import pytest
from test import config
from event_service.app import app
from event_service.utils import jwt_handler

session = config.init_postg_db(app)
db = config.init_db()
client = TestClient(app)

@pytest.fixture
def drop_collection_documents():
    config.clear_db_events_collection(db)
    config.clear_db_favourites_collection(db)
    config.clear_db_reservations_collection(db)

json_lollapalooza_first_date = {
            "name": "lollapalooza",  "ownerName": "Sol Fontenla",
            "location": "Av. Bernabé Márquez 700, B1642 San Isidro, Provincia de Buenos Aires",
            "capacity": 10000}


def test_when_login_for_the_first_time_an_attende_then_it_returns_its_token():

    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    actual = jwt_handler.decode_token(data)
    expected = {
        "id": 1,
        "rol": "organizer",
    }
    assert actual["id"] == expected["id"]
    assert actual["rol"] == expected["rol"]

@pytest.mark.usefixtures("drop_collection_documents")
def test_when_saving_a_draft_event_then_it_does_it():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token= response.json()
    actual= jwt_handler.decode_token(token)
    response = client.post("/organizers/save_draft", json=json_lollapalooza_first_date, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    data = data['message']
    print(data)
    assert data["name"] == "lollapalooza"
    assert data["ownerName"] == "Sol Fontenla"
    assert data['ownerId'] == actual['id']
    assert data['location'] == "Av. Bernabé Márquez 700, B1642 San Isidro, Provincia de Buenos Aires"
