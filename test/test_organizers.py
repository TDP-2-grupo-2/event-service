from fastapi.testclient import TestClient
from fastapi import status
import pytest
from test import config
from event_service.app import app
from event_service.utils import jwt_handler

session = config.init_postg_db(app)
db = config.init_db()
client = TestClient(app)

json_rock_music_event = {
            "name": "Music Fest",  "owner": "Agustina Segura",  "description": "Musical de pop, rock y mucho más", 
            "location": "Av. Pres. Figueroa Alcorta 7597, C1428 CABA", "locationDescription": "Estadio River", "capacity": 5000, 
            "dateEvent": "2023-07-01", "attendance": 0, "eventType": "SHOW","tags": [ "MUSICA", "DIVERSION" ], "latitud": -34.6274931, 
            "longitud": -68.3252097, "start": "19:00", "end": "23:00", "faqs": [{'pregunta':'Como llegar?', 'respuesta':'Por medio del colectivo 152'}],
            "agenda": [{'time': "19:00", 'description': 'Arranca banda de rock'}, {'time': '20:00', 'description': 'comienza banda de pop'}] }


@pytest.fixture
def drop_collection_documents():
    config.clear_db_draft_event_collection(db)
    config.clear_db_events_collection(db)

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
    response = client.post("/organizers/draft_events", json=json_lollapalooza_first_date, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    data = data['message']
    assert data["name"] == "lollapalooza"
    assert data["ownerName"] == "Sol Fontenla"
    assert data['ownerId'] == actual['id']
    assert data['location'] == "Av. Bernabé Márquez 700, B1642 San Isidro, Provincia de Buenos Aires"

@pytest.mark.usefixtures("drop_collection_documents")
def test_when_getting_an_extining_draft_event_by_id_then_it_should_return_it():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token= response.json()
    actual= jwt_handler.decode_token(token)
    response = client.post("/organizers/draft_events", json=json_lollapalooza_first_date, headers={"Authorization": f"Bearer {token}"})
    data = response.json()
    evenet_id = data['message']['_id']['$oid']
    response = client.get(f"/organizers/draft_events/{evenet_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    print(data)
    data = data['message']
    assert data["name"] == "lollapalooza"
    assert data["ownerName"] == "Sol Fontenla"
    assert data['ownerId'] == actual['id']
    assert data['location'] == "Av. Bernabé Márquez 700, B1642 San Isidro, Provincia de Buenos Aires"

@pytest.mark.usefixtures("drop_collection_documents")
def test_when_getting_a_not_extining_draft_event_by_id_then_it_should_not_return_it():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token= response.json()
    actual= jwt_handler.decode_token(token)
    response = client.get(f"/organizers/draft_events/5428bd284042b5da2e28b6a1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "The event does not exists"



@pytest.mark.usefixtures("drop_collection_documents")
def test_when_getting_a_draft_event_by_owner_it_should_return_all_drfat_events_created_by_that_owner():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token= response.json()
    actual= jwt_handler.decode_token(token)
    client.post("/organizers/draft_events", json=json_lollapalooza_first_date, headers={"Authorization": f"Bearer {token}"})
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
    response = client.post("/organizers/draft_events", json=json_lollapalooza_first_date, headers={"Authorization": f"Bearer {token}"})
    info = response.json()
    info = info['message']
    event_id = info['_id']['$oid']

    response = client.patch(f"/organizers/draft_events/{event_id}", 
                                json={"capacity": 100, "eventType": "TEATRO"}, 
                                headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == status.HTTP_200_OK, response.text
    
    data = response.json()
    data = data['message']

    assert data['capacity'] == 100
    assert data['eventType'] == "TEATRO"


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenGettingActiveEventsByOwner_TheOwnerDidNotCreateAnyYet_itShouldReturnAnEmptyList():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()
    response = client.get("/organizers/active_events", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK, response.text
    
    data = response.json()
    data = data['message']
    assert data == []


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenGettingActiveEventsByOwner_TheOwnerAlreadyCreatedOne_ItShouldReturnTheEvent():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()
    new_event = client.post("/organizers/event/", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    new_event = new_event.json()
    print(new_event)
    new_event_id = new_event['message']['_id']['$oid']

    active_events = client.get("/organizers/active_events", headers={"Authorization": f"Bearer {token}"})
    assert active_events.status_code == status.HTTP_200_OK, active_events.text
    
    active_events = active_events.json()
    active_events = active_events['message']

    assert len(active_events) == 1
    assert new_event_id == active_events[0]['_id']['$oid']

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenGettingActiveEventsByOwner_TheOwnerCreatedOneAndCancelesIt_ItShouldReturnAnEmptyList():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()
    new_event = client.post("/organizers/event/", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    new_event = new_event.json()
 
    new_event_id = new_event['message']['_id']['$oid']

    responsss = client.patch(f"/organizers/canceled_events/{new_event_id}", headers={"Authorization": f"Bearer {token}"})
    
    active_events = client.get("/organizers/active_events", headers={"Authorization": f"Bearer {token}"})
    
    active_events = active_events.json()
    active_events = active_events['message']

    assert active_events == []


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTryingToCancelAnEvent_TheUserCancellingTheEventIsNotTheOwner_ItShouldReturnError():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()
    new_event = client.post("/organizers/event/", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    new_event = new_event.json()

    another_user_login_response = client.post("/organizers/loginGoogle", json={"email": "agussegura@gmail.com", "name": "Agus Segura"})
    another_user_token = another_user_login_response.json()
 
    new_event_id = new_event['message']['_id']['$oid']

    response_to_cancel = client.patch(f"/organizers/canceled_events/{new_event_id}", headers={"Authorization": f"Bearer {another_user_token}"})
    assert response_to_cancel.status_code == status.HTTP_401_UNAUTHORIZED, response_to_cancel.text
    data = response_to_cancel.json()
    assert data["detail"] == "The user is not authorize"




