from fastapi.testclient import TestClient
from fastapi import status
from event_service.app import app
import pytest
from event_service.utils import jwt_handler
from test import config

session = config.init_postg_db(app)
client = TestClient(app)
db = config.init_db()


@pytest.fixture
def drop_collection_documents():
    config.clear_db_draft_event_collection(db)
    config.clear_db_events_collection(db)
    config.clear_db_reservations_collection(db)

json_rock_music_event = {
            "name": "Music Fest",  "ownerName": "Agustina Segura",  "description": "Musical de pop, rock y mucho más", 
            "location": "Av. Pres. Figueroa Alcorta 7597, C1428 CABA", "locationDescription": "Estadio River", "capacity": 5000, 
            "dateEvent": "2023-07-01", "attendance": 0, "eventType": "SHOW","tags": [ "MUSICA", "DIVERSION" ], "latitud": -34.6274931, 
            "longitud": -68.3252097, "start": "19:00", "end": "23:00", "tags":["DIVERSION"], "faqs": [{'pregunta':'Como llegar?', 'respuesta':'Por medio del colectivo 152'}],
            "agenda": [{'time': "19:00", 'description': 'Arranca banda de rock'}, {'time': '20:00', 'description': 'comienza banda de pop'}] }


def test_when_admin_login_with_correct_email_and_password_it_should_allow_it():

    response = client.post("/admins/login", json={"email":"admin@gmail.com", "password": "admintdp2"})

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    data = data['message']
    info = jwt_handler.decode_token(data)

    assert info['id'] == 0
    assert info['rol'] == 'admin'

def test_when_admin_login_with_incorrect_email_it_not_should_allow_it():

    response = client.post("/admins/login", json={"email":"aaadmiin@gmail.com", "password": "admintdp2"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    data = response.json()

    assert data['detail'] == "The username/password is incorrect"

def test_when_admin_login_with_incorrect_password_it_not_should_allow_it():

    response = client.post("/admins/login", json={"email":"admin@gmail.com", "password": "adminnntdpp2"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    data = response.json()

    assert data['detail'] == "The username/password is incorrect"


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTryingToSuspendAnEvent_TheUserSuspendingTheEventIsNotAdmin_ItShouldReturnError():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()
    new_event = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    new_event = new_event.json()

    another_user_login_response = client.post("/organizers/loginGoogle", json={"email": "agussegura@gmail.com", "name": "Agus Segura"})
    another_user_token = another_user_login_response.json()
 
    new_event_id = new_event['message']['_id']['$oid']

    response_to_cancel = client.patch(f"/admins/suspended_events/{new_event_id}", headers={"Authorization": f"Bearer {another_user_token}"})
    assert response_to_cancel.status_code == status.HTTP_401_UNAUTHORIZED, response_to_cancel.text
    data = response_to_cancel.json()
    assert data["detail"] == "The user is not authorize"



@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTryingToSuspendAnActiveEvent_TheUserSuspendingTheEventIsAdmin_ItShouldSuspendTheEvent():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()
    new_event = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    new_event = new_event.json()

    response = client.post("/admins/login", json={"email":"admin@gmail.com", "password": "admintdp2"})
    admin_token = response.json()["message"]
 
    new_event_id = new_event['message']['_id']['$oid']

    response_to_suspend = client.patch(f"/admins/suspended_events/{new_event_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response_to_suspend.status_code == status.HTTP_200_OK
    response_to_suspend = response_to_suspend.json()["message"]

    assert response_to_suspend['_id']['$oid'] == new_event_id
    assert response_to_suspend['status'] == 'suspended'

@pytest.mark.usefixtures("drop_collection_documents")
def test_when_an_admin_is_trying_to_susped_an_organizer_then_it_should_suspend_the_organizer():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    data = response.json()
    actual = jwt_handler.decode_token(data)
    organizer_id = actual['id']
    response = client.post("/admins/login", json={"email":"admin@gmail.com", "password": "admintdp2"})
    admin_token = response.json()["message"]

    blockResponse = client.patch(f"/admins/suspended_organizers/{organizer_id}",headers={"Authorization": f"Bearer {admin_token}"})

    assert blockResponse.status_code == status.HTTP_200_OK

    blockResponse = blockResponse.json()['message']
    print(blockResponse)
    assert blockResponse['isBlock'] == True


@pytest.mark.usefixtures("drop_collection_documents")
def test_when_an_admin_is_trying_to_susped_an_organizer_tha_not_exits_then_it_should_not_suspend_the_organizer():
    response = client.post("/admins/login", json={"email":"admin@gmail.com", "password": "admintdp2"})
    admin_token = response.json()["message"]

    blockResponse = client.patch(f"/admins/suspended_organizers/100",headers={"Authorization": f"Bearer {admin_token}"})

    assert blockResponse.status_code == status.HTTP_404_NOT_FOUND
    blockResponse = blockResponse.json()
    assert blockResponse['detail'] == "The user does not exists"


