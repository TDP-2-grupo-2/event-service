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
    config.clear_db_draft_event_collection(db)

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
    assert data["name"] == "lollapalooza"
    assert data["ownerName"] == "Sol Fontenla"
    assert data['ownerId'] == actual['id']
    assert data['location'] == "Av. Bernabé Márquez 700, B1642 San Isidro, Provincia de Buenos Aires"

@pytest.mark.usefixtures("drop_collection_documents")
def test_when_getting_a_draft_event_by_owner_it_should_return_all_drfat_events_created_by_that_owner():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token= response.json()
    actual= jwt_handler.decode_token(token)
    client.post("/organizers/save_draft", json=json_lollapalooza_first_date, headers={"Authorization": f"Bearer {token}"})
    response = client.get("/organizers/draft_events", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK, response.text

    data = response.json()
    data = data['message']

    assert len(data) == 1

    assert data[0]['ownerName'] == "Sol Fontenla"
    assert data[0]['ownerId'] == actual['id']

@pytest.mark.usefixtures("drop_collection_documents")
def test_when_getting_a_draft_event_by_onwer_with_no_draft_events_thent_it_should_return_an_empty_list():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token= response.json()
    actual= jwt_handler.decode_token(token)
    response = client.get("/organizers/draft_events", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK, response.text

    data = response.json()
    data = data['message']

    assert len(data) == 0
    
@pytest.mark.usefixtures("drop_collection_documents")
def test_when_editing_an_exsting_draft_event_then_it_should_updated():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token= response.json()
    actual= jwt_handler.decode_token(token)
    response = client.post("/organizers/save_draft", json=json_lollapalooza_first_date, headers={"Authorization": f"Bearer {token}"})
    info = response.json()
    info = info['message']
    event_id = info['_id']['$oid']
    print(event_id)
    response = client.patch(f"/organizers/draft_events/{event_id}", 
                                json={"capacity": 100, "eventType": "TEATRO"}, 
                                headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == status.HTTP_200_OK, response.text
    
    data = response.json()
    data = data['message']
    print(data)
    assert data['capacity'] == 100
    assert data['eventType'] == "TEATRO"