from bson import ObjectId
from fastapi.testclient import TestClient
from fastapi import status
import pytest
from test import config
from event_service.app import app
from event_service.utils import jwt_handler

session = config.init_postg_db(app)
db = config.init_db()
client = TestClient(app)

json_programming_event = {
            "name": "Aprendé a programar en python!",  "ownerName": "Sol Fontenla",  "description": "Aprende a programar en python desde cero",
            "location": "Av. Paseo Colón 850, C1063 CABA",
            "locationDescription": "Facultad de Ingenieria - UBA", "capacity": 100, "dateEvent": "2023-08-07", "attendance": 0, "eventType": "TECNOLOGIA",
            "tags": [ "PROGRAMACION", "APRENDIZAJE", ], "latitud": 8.9, "longitud": 6.8, "start": "21:00", "end": "22:30" }



json_rock_music_event = {
            "name": "Music Fest",  "ownerName": "Agustina Segura",  "description": "Musical de pop, rock y mucho más", 
            "location": "Av. Pres. Figueroa Alcorta 7597, C1428 CABA", "locationDescription": "Estadio River", "capacity": 5000, 
            "dateEvent": "2023-07-01", "attendance": 0, "eventType": "SHOW","tags": [ "MUSICA", "DIVERSION" ], "latitud": -34.6274931, 
            "longitud": -68.3252097, "start": "19:00", "end": "23:00", "tags":["DIVERSION"], "faqs": [{'pregunta':'Como llegar?', 'respuesta':'Por medio del colectivo 152'}],
            "agenda": [{'time': "19:00", 'description': 'Arranca banda de rock'}, {'time': '20:00', 'description': 'comienza banda de pop'}] }
@pytest.fixture
def drop_collection_documents():
    config.clear_db_draft_event_collection(db)
    config.clear_db_events_collection(db)
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
    assert data["detail"] == "Este evento no existe"



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
    print(data)
    data = data['message']

    assert data['capacity'] == 100
    assert data['eventType'] == "TEATRO"

@pytest.mark.usefixtures("drop_collection_documents")
def test_when_editing_an_exsting_active_event_then_it_should_updated():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token= response.json()
    response = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    info = response.json()
    print(info)
    info = info['message']
    event_id = info['_id']['$oid']

    response = client.patch(f"/organizers/active_events/{event_id}", 
                                json={"descripcion": "Primer dia en el lolla", "start": "20:00"}, 
                                headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == status.HTTP_200_OK, response.text
    
    data = response.json()
    print(data)
    data = data['message']

    assert data['descripcion'] == "Primer dia en el lolla"
    assert data['start'] == "20:00"

@pytest.mark.usefixtures("drop_collection_documents")
def test_when_editing_an_non_exsting_active_event_then_it_should_not_be_updated():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token= response.json()

    response = client.patch(f"/organizers/active_events/6439a8d0c392bdf710446d31", 
                                json={"descripcion": "Primer dia en el lolla", "start": "20:00"}, 
                                headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    



@pytest.mark.usefixtures("drop_collection_documents")
def test_GivenADraftEvent_WhenTheClientPublishesIt_ItPublishedItCorrectly():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json() 
    actual_user = jwt_handler.decode_token(token)

    draft_event = client.post("/organizers/draft_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    draft_event = draft_event.json()
    draft_event = draft_event['message']

    draft_response = client.get(f"/organizers/draft_events/{draft_event['_id']['$oid']}", headers={"Authorization": f"Bearer {token}"})

    draft_response = draft_response.json()
    draft_response = draft_response['message']
    draft_response['draftId'] = draft_response['_id']['$oid']
    del draft_response['_id']


    new_event = client.post("/organizers/active_events", json=draft_response, headers={"Authorization": f"Bearer {token}"})
    assert new_event.status_code == status.HTTP_201_CREATED, new_event.text
    new_event = new_event.json()
    new_event = new_event['message']


    assert new_event["name"] == "Music Fest"
    assert new_event["ownerName"] == "Agustina Segura"
    assert new_event['ownerId'] == actual_user['id']


@pytest.mark.usefixtures("drop_collection_documents")
def test_GivenADraftEvent_WhenTheClientPublishesItWiThMissingFields_ItReturnsError():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json() 

    draft_event = client.post("/organizers/draft_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    draft_event = draft_event.json()
    draft_event = draft_event['message']

    draft_response = client.get(f"/organizers/draft_events/{draft_event['_id']['$oid']}", headers={"Authorization": f"Bearer {token}"})

    draft_response = draft_response.json()
    draft_response = draft_response['message']
    draft_response['draftId'] = draft_response['_id']['$oid']
    del draft_response['_id']
    del draft_response['tags']
    del draft_response['name']
    del draft_response['ownerName']


    new_event = client.post("/organizers/active_events", json=draft_response, headers={"Authorization": f"Bearer {token}"})
    assert new_event.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, new_event.text


@pytest.mark.usefixtures("drop_collection_documents")
def test_GivenADraftEvent_WhenTheClientPublishesIt_TheDraftIsRemoved():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json() 

    draft_event = client.post("/organizers/draft_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    draft_event = draft_event.json()
    draft_event = draft_event['message']

    draft_response = client.get(f"/organizers/draft_events/{draft_event['_id']['$oid']}", headers={"Authorization": f"Bearer {token}"})

    draft_response = draft_response.json()
    draft_response = draft_response['message']
    draft_response['draftId'] = draft_response['_id']['$oid']
    del draft_response['_id']

    client.post("/organizers/active_events", json=draft_response, headers={"Authorization": f"Bearer {token}"})
    
    old_draft = client.get(f"/organizers/draft_events/{draft_event['_id']['$oid']}", headers={"Authorization": f"Bearer {token}"})
    assert old_draft.status_code == status.HTTP_404_NOT_FOUND, old_draft.text


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenGettingActiveEventsByOwner_TheOwnerDidNotCreateAnyYet_itShouldReturnAnEmptyList():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()
    response = client.get("/organizers/events", params={"status": "active"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK, response.text
    
    data = response.json()
    data = data['message']
    assert data == []


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenGettingActiveEventsByOwner_TheOwnerAlreadyCreatedOne_ItShouldReturnTheEvent():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()
    new_event = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    new_event = new_event.json()
    new_event_id = new_event['message']['_id']['$oid']

    active_events = client.get("/organizers/events", params={"status": "active"}, headers={"Authorization": f"Bearer {token}"})
    assert active_events.status_code == status.HTTP_200_OK, active_events.text
    
    active_events = active_events.json()
    active_events = active_events['message']

    assert len(active_events) == 1
    assert new_event_id == active_events[0]['_id']['$oid']


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenGettingActiveEventsByOwner_TheOwnerCreatedOneAndCancelesIt_ItShouldReturnAnEmptyList():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()
    new_event = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    new_event = new_event.json()
 
    new_event_id = new_event['message']['_id']['$oid']

    client.patch(f"/organizers/canceled_events/{new_event_id}", headers={"Authorization": f"Bearer {token}"})
    
    active_events = client.get("/organizers/events", params={'status': 'active'}, headers={"Authorization": f"Bearer {token}"})
    
    active_events = active_events.json()
    active_events = active_events['message']

    assert active_events == []


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTryingToCancelAnEvent_TheUserCancellingTheEventIsNotTheOwner_ItShouldReturnError():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()
    new_event = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    new_event = new_event.json()

    another_user_login_response = client.post("/organizers/loginGoogle", json={"email": "agussegura@gmail.com", "name": "Agus Segura"})
    another_user_token = another_user_login_response.json()
 
    new_event_id = new_event['message']['_id']['$oid']

    response_to_cancel = client.patch(f"/organizers/canceled_events/{new_event_id}", headers={"Authorization": f"Bearer {another_user_token}"})
    assert response_to_cancel.status_code == status.HTTP_401_UNAUTHORIZED, response_to_cancel.text
    data = response_to_cancel.json()
    assert data["detail"] == "The user is not authorize"

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenGettingCanceledEventsByOwner_TheOwnerDidNotCancelAnyYet_itShouldReturnAnEmptyList():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()
    response = client.get("/organizers/events", params={"status": "canceled"},  headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK, response.text
    
    data = response.json()
    data = data['message']
    assert data == []


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenGettingCanceledEventsByOwner_TheOwnerAlreadyCanceledOne_ItShouldReturnTheEvent():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()
    new_event = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    new_event = new_event.json()
    
    new_event_id = new_event['message']['_id']['$oid']

    client.patch(f"/organizers/canceled_events/{new_event_id}", headers={"Authorization": f"Bearer {token}"})
    canceled_events = client.get("/organizers/events", params={"status": "canceled"}, headers={"Authorization": f"Bearer {token}"})
    assert canceled_events.status_code == status.HTTP_200_OK, canceled_events.text
    
    canceled_events = canceled_events.json()
    canceled_events = canceled_events['message']

    assert len(canceled_events) == 1
    assert new_event_id == canceled_events[0]['_id']['$oid']

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenGettingCanceledEventsByOwner_AnotherUserGetsTheEvents_ItShouldReturnAnEmptyList():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()
    new_event = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    new_event = new_event.json()
    
    new_event_id = new_event['message']['_id']['$oid']
    client.patch(f"/organizers/canceled_events/{new_event_id}", headers={"Authorization": f"Bearer {token}"})

    another_user_login_response = client.post("/organizers/loginGoogle", json={"email": "agussegura@gmail.com", "name": "Agus Segura"})
    another_user_token = another_user_login_response.json()

    canceled_events = client.get("/organizers/events", params={"status": "canceled"}, headers={"Authorization": f"Bearer {another_user_token}"})
    assert canceled_events.status_code == status.HTTP_200_OK, canceled_events.text
    
    canceled_events = canceled_events.json()
    canceled_events = canceled_events['message']

    assert canceled_events == []


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenGettingFinishedEventsByOwner_TheOwnerDoesNotHaveFinishedEventsYet_itShouldReturnAnEmptyList():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()
    response = client.get("/organizers/events", params={"status": "finished"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK, response.text
    
    data = response.json()
    data = data['message']
    assert data == []


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenGettingFinishedEventsByOwner_TheOwnerHasOneFinishedEvent_ItShouldReturnTheEvent():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()

    json_event_with_finished_status = json_rock_music_event.copy()
    json_event_with_finished_status['status'] = 'finished'
    json_event_with_finished_status['dateEvent'] = "2023-01-01"
    json_event_with_finished_status['ownerId'] = jwt_handler.decode_token(token)['id']

    inserted_event = db['events'].insert_one(json_event_with_finished_status)
    new_event_id = inserted_event.inserted_id

    finished_events = client.get("/organizers/events", params={"status": "finished"}, headers={"Authorization": f"Bearer {token}"})
    assert finished_events.status_code == status.HTTP_200_OK, finished_events.text
    
    finished_events = finished_events.json()
    finished_events = finished_events['message']

    assert len(finished_events) == 1
    assert str(new_event_id) == finished_events[0]['_id']['$oid']

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenGettingFinishedEventsByOwner_AnotherUserGetsTheEvents_ItShouldReturnAnEmptyList():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()
    
    json_event_with_finished_status = json_rock_music_event.copy()
    json_event_with_finished_status['status'] = 'finished'
    json_event_with_finished_status['dateEvent'] = "2023-01-01"
    json_event_with_finished_status['ownerId'] = jwt_handler.decode_token(token)['id']

    inserted_event = db['events'].insert_one(json_event_with_finished_status)
    new_event_id = inserted_event.inserted_id


    another_user_login_response = client.post("/organizers/loginGoogle", json={"email": "agussegura@gmail.com", "name": "Agus Segura"})
    another_user_token = another_user_login_response.json()

    finished_events = client.get("/organizers/events", params={"status": "finished"}, headers={"Authorization": f"Bearer {another_user_token}"})
    assert finished_events.status_code == status.HTTP_200_OK, finished_events.text
    
    finished_events = finished_events.json()
    finished_events = finished_events['message']

    assert finished_events == []


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheOrganizerTriesToGetItsEvents_ThereIsOnlyOneWhichDateAlreadyPassed_TheAppReturnsAnEmptyList():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()

    json_rock_music_event_already_passed = json_rock_music_event.copy()
    json_rock_music_event_already_passed['dateEvent'] = "2022-01-01"
    db['events'].insert_one(json_rock_music_event_already_passed)

    response = client.get("/organizers/events", params={"status": "active"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    data = data['message']
    assert data == []



@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenGettingActiveEventsByOwner_TheOwnerAlreadyCreatedOne_ItShouldReturnTheEvent():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()
    new_event = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    new_event = new_event.json()
    new_event_id = new_event['message']['_id']['$oid']

    active_events = client.get("/organizers/events", headers={"Authorization": f"Bearer {token}"})
    assert active_events.status_code == status.HTTP_200_OK, active_events.text
    
    active_events = active_events.json()
    active_events = active_events['message']

    assert len(active_events) == 1
    assert new_event_id == active_events[0]['_id']['$oid']
 

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenValidatingATicketFromAnEventThatDoesNotExist_TheTicketIsNotValid_ItShouldReturnError():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()
    new_event = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    new_event = new_event.json()
    new_event_id = new_event["message"]['_id']['$oid']
    random_user = client.post("/attendees/loginGoogle", json={"email": "agustina@gmail.com", "name": "agustina segura"})
    random_user_id = random_user.json()

    response_to_reservation = client.post(f"/events/reservations/user/{random_user_id}/event/{new_event_id}", headers={"Authorization": f"Bearer {token}"})
    response_to_reservation = response_to_reservation.json()

    ticket_id = response_to_reservation["message"]['_id']['$oid']
    non_existing_event_id = "645a3fc2ea405ca4e60e411a"
    validation_response = client.patch(f"/organizers/events/{non_existing_event_id}/ticket_validation/{ticket_id}", headers={"Authorization": f"Bearer {token}"})

    assert validation_response.status_code == status.HTTP_404_NOT_FOUND, response.text
    validation_response = validation_response.json()
    assert validation_response["detail"] == "Este evento no existe"
    

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenValidatingATicketThatDoesNotExist_TheTicketIsNotValid_ItShouldReturnError():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()
    new_event = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    new_event = new_event.json()
    new_event_id = new_event["message"]['_id']['$oid']
    fake_ticket_id = "645a3fc2ea405ca4e60e411a"
    validation_response = client.patch(f"/organizers/events/{new_event_id}/ticket_validation/{fake_ticket_id}", headers={"Authorization": f"Bearer {token}"})

    assert validation_response.status_code == status.HTTP_409_CONFLICT, validation_response.text
    validation_response = validation_response.json()
    assert validation_response["detail"] == "Este ticket no pertenece a este evento"



@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenValidatingATicketFromAnEventThatExists_TheTicketIsValidAndHasNotBeenUsedYet_ItShouldReturnThatIsValid():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()
    new_event = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    new_event = new_event.json()
    new_event_id = new_event["message"]['_id']['$oid']
    random_user = client.post("/attendees/loginGoogle", json={"email": "agustina@gmail.com", "name": "agustina segura"})
    random_user_id = random_user.json()

    response_to_reservation = client.post(f"/events/reservations/user/{random_user_id}/event/{new_event_id}", headers={"Authorization": f"Bearer {token}"})
    response_to_reservation = response_to_reservation.json()

    ticket_id = response_to_reservation["message"]['_id']['$oid']
    validation_response = client.patch(f"/organizers/events/{new_event_id}/ticket_validation/{ticket_id}", headers={"Authorization": f"Bearer {token}"})

    assert validation_response.status_code == status.HTTP_200_OK, response.text
    validation_response = validation_response.json()
    validation_response = validation_response["message"]
    assert validation_response['_id']['$oid'] == ticket_id
    #TODO: devolver el token en esta posicion
    #assert validation_response['user_id'] == random_user_id
    assert validation_response['event_id'] == new_event_id
    assert validation_response['status'] == 'used'



@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenValidatingATicketFromAnEventThatExists_TheTicketIsValidAndHasBeenUsed_ItShouldReturnThatIsNotValid():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()
    new_event = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    new_event = new_event.json()
    new_event_id = new_event["message"]['_id']['$oid']

    random_user = client.post("/attendees/loginGoogle", json={"email": "agustina@gmail.com", "name": "agustina segura"})
    random_user_id = random_user.json()

    response_to_reservation = client.post(f"/events/reservations/user/{random_user_id}/event/{new_event_id}", headers={"Authorization": f"Bearer {token}"})
    response_to_reservation = response_to_reservation.json()

    ticket_id = response_to_reservation["message"]['_id']['$oid']
    client.patch(f"/organizers/events/{new_event_id}/ticket_validation/{ticket_id}", headers={"Authorization": f"Bearer {token}"})
    validation_response = client.patch(f"/organizers/events/{new_event_id}/ticket_validation/{ticket_id}", headers={"Authorization": f"Bearer {token}"})

    assert validation_response.status_code == status.HTTP_409_CONFLICT, response.text
    validation_response = validation_response.json()
    assert validation_response["detail"] == "Este ticket ya fue utilizado"
    

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenValidatingATicketFromAnEventThatExists_TheEventHasAlreadyFinished_ItShouldReturnThatIsNotValid():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()

    new_event = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    new_event = new_event.json()
    new_event_id = new_event["message"]['_id']['$oid']
    
    random_user = client.post("/attendees/loginGoogle", json={"email": "agustina@gmail.com", "name": "agustina segura"})
    random_user_id = random_user.json()

    response_to_reservation = client.post(f"/events/reservations/user/{random_user_id}/event/{new_event_id}", headers={"Authorization": f"Bearer {token}"})
    response_to_reservation = response_to_reservation.json()

    db['events'].update_one({'_id': ObjectId(new_event_id)}, {"$set": {'status': 'finished', 'dateEvent': "2023-01-01"}})
   
    ticket_id = response_to_reservation["message"]['_id']['$oid']
    validation_response = client.patch(f"/organizers/events/{new_event_id}/ticket_validation/{ticket_id}", headers={"Authorization": f"Bearer {token}"})

    assert validation_response.status_code == status.HTTP_409_CONFLICT, response.text
    validation_response = validation_response.json()
    assert validation_response["detail"] == "Este evento ya finalizo"


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenValidatingATicketFromAnEventThatExists_TheEventHasBeenCanceled_ItShouldReturnThatIsNotValid():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()

    new_event = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    new_event = new_event.json()
    new_event_id = new_event["message"]['_id']['$oid']
    
    random_user = client.post("/attendees/loginGoogle", json={"email": "agustina@gmail.com", "name": "agustina segura"})
    random_user_id = random_user.json()

    response_to_reservation = client.post(f"/events/reservations/user/{random_user_id}/event/{new_event_id}", headers={"Authorization": f"Bearer {token}"})
    response_to_reservation = response_to_reservation.json()

    client.patch(f"/organizers/canceled_events/{new_event_id}", headers={"Authorization": f"Bearer {token}"})
   
    ticket_id = response_to_reservation["message"]['_id']['$oid']
    validation_response = client.patch(f"/organizers/events/{new_event_id}/ticket_validation/{ticket_id}", headers={"Authorization": f"Bearer {token}"})

    assert validation_response.status_code == status.HTTP_409_CONFLICT, response.text
    validation_response = validation_response.json()
    assert validation_response["detail"] == "Este evento fue cancelado"


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenValidatingATicketFromAnEventThatExists_TheEventHasBeenSuspended_ItShouldReturnThatIsNotValid():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()

    new_event = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    new_event = new_event.json()
    new_event_id = new_event["message"]['_id']['$oid']
    
    random_user = client.post("/attendees/loginGoogle", json={"email": "agustina@gmail.com", "name": "agustina segura"})
    random_user_id = random_user.json()

    response_to_reservation = client.post(f"/events/reservations/user/{random_user_id}/event/{new_event_id}", headers={"Authorization": f"Bearer {token}"})
    response_to_reservation = response_to_reservation.json()

    db['events'].update_one({'_id': ObjectId(new_event_id)}, {"$set": {'status': 'suspended'}})
   
    ticket_id = response_to_reservation["message"]['_id']['$oid']
    validation_response = client.patch(f"/organizers/events/{new_event_id}/ticket_validation/{ticket_id}", headers={"Authorization": f"Bearer {token}"})

    assert validation_response.status_code == status.HTTP_409_CONFLICT, response.text
    validation_response = validation_response.json()
    assert validation_response["detail"] == "Este evento fue suspendido"


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenGettingSuspendedEventsByOwner_TheOwnerHasNoSuspendedEventsYet_itShouldReturnAnEmptyList():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()
    response = client.get("/organizers/events", params={"status": "suspended"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK, response.text
    
    data = response.json()
    data = data['message']
    assert data == []


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenGettingSuspendedEventsByOwner_TheOwnerHasOneSuspendedEvent_itShouldReturnTheEvent():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()
    new_event = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    new_event = new_event.json()
    new_event_id = new_event['message']['_id']['$oid']
    
    db['events'].update_one({'_id': ObjectId(new_event_id)}, {"$set": {'status': 'suspended'}})

    suspended_events = client.get("/organizers/events", params={"status": "suspended"}, headers={"Authorization": f"Bearer {token}"})
    assert suspended_events.status_code == status.HTTP_200_OK, suspended_events.text
    
    suspended_events = suspended_events.json()
    suspended_events = suspended_events['message']

    assert len(suspended_events) == 1
    assert new_event_id == suspended_events[0]['_id']['$oid']
 

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenGettingSuspendedEventsByOwner_TheOwnerHasOneFromTwoSuspendedEvents_itShouldReturnTheEvent():
    response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    token = response.json()
    new_event = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    new_event = client.post("/organizers/active_events", json=json_programming_event, headers={"Authorization": f"Bearer {token}"})

    new_event = new_event.json()
    print(new_event)
    new_event_id = new_event['message']['_id']['$oid']
    
    db['events'].update_one({'_id': ObjectId(new_event_id)}, {"$set": {'status': 'suspended'}})

    suspended_events = client.get("/organizers/events", params={"status": "suspended"}, headers={"Authorization": f"Bearer {token}"})
    assert suspended_events.status_code == status.HTTP_200_OK, suspended_events.text
    
    suspended_events = suspended_events.json()
    suspended_events = suspended_events['message']

    assert len(suspended_events) == 1
    assert new_event_id == suspended_events[0]['_id']['$oid']