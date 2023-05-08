import datetime
from fastapi.testclient import TestClient
from fastapi import status
from test import config
from event_service.app import app
from event_service.utils import jwt_handler

session = config.init_postg_db(app)

db = config.init_db()

import pytest

COORDENADAS_CIUDAD_DE_CORDOBA = "-31.399377,-64.3344291"
COORDENAS_OBELISCO = "-34.6034353,-58.4143837"

client = TestClient(app)
@pytest.fixture
def drop_collection_documents():
    config.clear_db_events_collection(db)
    config.clear_db_favourites_collection(db)
    config.clear_db_reservations_collection(db)


json_rock_music_event = {
            "name": "Music Fest",  "ownerName": "Agustina Segura",  "description": "Musical de pop, rock y mucho más", 
            "location": "Av. Pres. Figueroa Alcorta 7597, C1428 CABA", "locationDescription": "Estadio River", "capacity": 5000, 
            "dateEvent": "2023-07-01", "attendance": 0, "eventType": "SHOW","tags": [ "MUSICA", "DIVERSION" ], "latitud": -34.6274931, 
            "longitud": -68.3252097, "start": "19:00", "end": "23:00", "faqs": [{'pregunta':'Como llegar?', 'respuesta':'Por medio del colectivo 152'}],
            "agenda": [{'time': "19:00", 'description': 'Arranca banda de rock'}, {'time': '20:00', 'description': 'comienza banda de pop'}] }

json_lollapalooza_first_date = {
            "name": "lollapalooza",  "ownerName": "Sol Fontenla",  "description": "Veni a disfrutar del primer dia de esta nueva edición", 
            "location": "Av. Bernabé Márquez 700, B1642 San Isidro, Provincia de Buenos Aires", "locationDescription": "Hipodromo de San Isidro",
            "capacity": 200000, "dateEvent": "2024-01-28", "attendance": 300, "eventType": "SHOW", "tags": [ "MuSiCa", "DiVeRsIoN", "FESTIVAL" ],
            "latitud": -34.4811222, "longitud": -58.526158, "start": "11:00", "end": "23:00" }


json_theatre_event = {
            "name": "Tootsie",  "ownerName": "Nico Vazquez",  "description": "La comedia del 2023",
            "location": "Av. Corrientes 1280, C1043AAZ CABA", "locationDescription": "Teatro Lola Membrives", 
            "capacity": 400, "dateEvent": "2023-10-30", "attendance": 0, "eventType": "TEATRO", 
            "tags": [ "COMEDIA", "FAMILIAR", "ENTRETENIMIENTO" ], "latitud": -34.6019915, "longitud": -58.3711065, "start": "21:00", "end": "22:30" }

json_programming_event = {
            "name": "Aprendé a programar en python!",  "ownerName": "Sol Fontenla",  "description": "Aprende a programar en python desde cero",
            "location": "Av. Paseo Colón 850, C1063 CABA",
            "locationDescription": "Facultad de Ingenieria - UBA", "capacity": 100, "dateEvent": "2023-08-07", "attendance": 0, "eventType": "TECNOLOGIA",
            "tags": [ "PROGRAMACION", "APRENDIZAJE", ], "latitud": 8.9, "longitud": 6.8, "start": "21:00", "end": "22:30" }

def login_user():
    response = client.post("/attendees/loginGoogle", json={"email": "agustina@gmail.com", "name": "agustina segura"})
    data = response.json()
    return data


@pytest.mark.usefixtures("drop_collection_documents")
def test_given_a_new_event_when_an_organizer_wants_to_created_then_it_should_create_it():
    token = jwt_handler.create_access_token("1", 'organizer')
    response = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    data = data['message']
    
    assert data["name"] == "Music Fest"
    assert data["ownerName"] == "Agustina Segura"
    assert data["description"] == "Musical de pop, rock y mucho más"
    assert data["location"] == "Av. Pres. Figueroa Alcorta 7597, C1428 CABA"
    assert data["locationDescription"] == "Estadio River"
    assert data["capacity"] == 5000
    assert data["dateEvent"] == "2023-07-01"
    assert data["attendance"]== 0
    assert data["latitud"] == -34.6274931
    assert data["longitud"] == -68.3252097
    assert data["start"]=="19:00:00"
    assert data["end"]=="23:00:00"
    assert data['faqs'][0]['pregunta'] == 'Como llegar?'
    assert data['faqs'][0]['respuesta'] == 'Por medio del colectivo 152'
    assert data['agenda'][0]['time'] == "19:00"
    assert data['agenda'][0]['description'] == 'Arranca banda de rock'
    assert data['agenda'][1]['time'] == "20:00"
    assert data['agenda'][1]['description'] ==  'comienza banda de pop'
    assert data['status']=="active"


@pytest.mark.usefixtures("drop_collection_documents")
def test_given_a_date_that_passed_when_creating_an_event_then_it_should_not_create_it():
    token = jwt_handler.create_access_token("1", 'organizer')
    json_event_with_invalid_date = json_rock_music_event.copy()
    json_event_with_invalid_date["dateEvent"] = "2023-01-01"
    response = client.post("/organizers/active_events", json=json_event_with_invalid_date, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_409_CONFLICT, response.text
    data = response.json()

    assert data["detail"] == "the chosen date has passed"


@pytest.mark.usefixtures("drop_collection_documents")
def test_given_an_event_when_the_event_exists_then_it_should_return_it():
    token = jwt_handler.create_access_token("1", 'organizer')
    response = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_201_CREATED, response.text

    data = response.json()
    path_end = "/events/" + data['message']['_id']['$oid']
    response = client.get(path_end)
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    data = data['message']

    assert data["name"] == "Music Fest"
    assert data["ownerName"] == "Agustina Segura"
    assert data["description"] == "Musical de pop, rock y mucho más"
    assert data["location"] == "Av. Pres. Figueroa Alcorta 7597, C1428 CABA"
    assert data["locationDescription"] == "Estadio River"
    assert data["capacity"] == 5000
    assert data["dateEvent"] == "2023-07-01"
    assert data["attendance"]== 0
    assert data["latitud"] == -34.6274931
    assert data["longitud"] == -68.3252097
    assert data["start"]=="19:00:00"
    assert data["end"]=="23:00:00"
    assert data['status']=="active"   


@pytest.mark.usefixtures("drop_collection_documents")
def test_given_an_event_when_the_event_does_not_exist_then_it_should_not_return_it():
    response = client.get("/events/5428bd284042b5da2e28b6a1")
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    data = response.json()

    assert data["detail"] == "The event does not exists"


@pytest.mark.usefixtures("drop_collection_documents")
def test_given_an_exiting_event_when_i_want_to_deleted_then_it_should_do_it():
    token = jwt_handler.create_access_token("1", 'organizer')
    response = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    data = response.json()
    path_end = "/events/" + data['message']['_id']['$oid']
    response = client.delete(path_end)
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert 'ok' == data['message']


@pytest.mark.usefixtures("drop_collection_documents")
def test_given_an_event_that_dont_exists_when_i_want_to_delete_it_then_it_should_not_do_it():
    response = client.delete("/events/5428bd284042b5da2e28b6a1")
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    data = response.json()

    assert data["detail"] == "The event does not exists"


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetAllTheEvents_ThereAreNoEventsYet_TheAppReturnsAnEmptyList():
    response = client.get("/events/")
    data = response.json()
    data = data['message']

    assert response.status_code == status.HTTP_200_OK
    assert data == []


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetAllTheEvents_ThereAreThreeEvents_TheAppReturnsAListWithAllThreeEvents():
    token = jwt_handler.create_access_token("1", 'organizer')
    client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    client.post("/organizers/active_events", json=json_theatre_event, headers={"Authorization": f"Bearer {token}"})
    client.post("/organizers/active_events", json=json_programming_event, headers={"Authorization": f"Bearer {token}"})

    response = client.get("/events/")
    data = response.json()
    events = data['message']

    assert len(events) == 3

    
@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetEventsByName_NoneMatch_TheAppReturnsAnEmptyList():
    token = jwt_handler.create_access_token("1", 'organizer')
    client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    client.post("/organizers/active_events", json=json_theatre_event, headers={"Authorization": f"Bearer {token}"})

    response = client.get("/events?name=Festival")
    data = response.json()
    data = data['message']

    assert response.status_code == status.HTTP_200_OK
    assert data == []


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetEventsByOwner_OneMatches_TheAppReturnsTheEventCorrectly():
    token = jwt_handler.create_access_token("1", 'organizer')
    client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    client.post("/organizers/active_events", json=json_theatre_event, headers={"Authorization": f"Bearer {token}"})

    response = client.get("/events?ownerName=Nico Vazquez")
    data = response.json()
    data = data['message']

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 1
    assert data[0]["name"] == "Tootsie"
    assert data[0]["ownerName"] == "Nico Vazquez"
    assert data[0]["description"] == "La comedia del 2023"
    assert data[0]["location"] == "Av. Corrientes 1280, C1043AAZ CABA"
    assert data[0]["locationDescription"] == "Teatro Lola Membrives"
    assert data[0]["capacity"] == 400
    assert data[0]["dateEvent"] == "2023-10-30"
    assert data[0]["attendance"]== 0
    assert data[0]["tags"] == [ "COMEDIA", "FAMILIAR", "ENTRETENIMIENTO" ]
    assert data[0]["latitud"] == -34.6019915 
    assert data[0]["longitud"] == -58.3711065
    assert data[0]["start"]== "21:00:00"
    assert data[0]["end"]== "22:30:00"
    assert data[0]['status']=="active"



@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetEventsByName_OneMatches_TheAppReturnsTheEventCorrectly():
    token = jwt_handler.create_access_token("1", 'organizer')
    client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    client.post("/organizers/active_events", json=json_theatre_event, headers={"Authorization": f"Bearer {token}"})

    response = client.get("/events?name=tootsie")
    data = response.json()
    data = data['message']
    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 1
    assert data[0]["name"] == "Tootsie"
    assert data[0]["ownerName"] == "Nico Vazquez"
    assert data[0]["description"] == "La comedia del 2023"
    assert data[0]["location"] == "Av. Corrientes 1280, C1043AAZ CABA"
    assert data[0]["locationDescription"] == "Teatro Lola Membrives"
    assert data[0]["capacity"] == 400
    assert data[0]["dateEvent"] == "2023-10-30"
    assert data[0]["attendance"]== 0
    assert data[0]["tags"] == [ "COMEDIA", "FAMILIAR", "ENTRETENIMIENTO" ]
    assert data[0]["latitud"] == -34.6019915 
    assert data[0]["longitud"] == -58.3711065
    assert data[0]["start"]== "21:00:00"
    assert data[0]["end"]== "22:30:00"
    assert data[0]['status']=="active"
    

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetEventsByIncompleteName_OneMatches_TheAppReturnsTheEventCorrectly():
    token = jwt_handler.create_access_token("1", 'organizer')
    client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    client.post("/organizers/active_events", json=json_theatre_event, headers={"Authorization": f"Bearer {token}"})
    response = client.get("/events?name=oot")
    data = response.json()
    data = data['message']

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 1
    assert data[0]["name"] == "Tootsie"
    assert data[0]["ownerName"] == "Nico Vazquez"
    assert data[0]["description"] == "La comedia del 2023"
    assert data[0]["location"] == "Av. Corrientes 1280, C1043AAZ CABA"
    assert data[0]["locationDescription"] == "Teatro Lola Membrives"
    assert data[0]["capacity"] == 400
    assert data[0]["dateEvent"] == "2023-10-30"
    assert data[0]["attendance"]== 0
    assert data[0]["tags"] == [ "COMEDIA", "FAMILIAR", "ENTRETENIMIENTO" ]
    assert data[0]["latitud"] == -34.6019915 
    assert data[0]["longitud"] == -58.3711065
    assert data[0]["start"]== "21:00:00"
    assert data[0]["end"]== "22:30:00"


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetEventsByTags_NoneMatch_TheAppReturnsAnEmptyList():
    token = jwt_handler.create_access_token("1", 'organizer')
    client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    client.post("/organizers/active_events", json=json_theatre_event, headers={"Authorization": f"Bearer {token}"})

    response = client.get("/events", params={"taglist": "APRENDIZAJE"})
    data = response.json()
    data = data['message']

    assert response.status_code == status.HTTP_200_OK
    assert data == []


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetEventsByTwoTags_NoneMatch_TheAppReturnsAnEmptyList():
    token = jwt_handler.create_access_token("1", 'organizer')
    client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    client.post("/organizers/active_events", json=json_theatre_event, headers={"Authorization": f"Bearer {token}"})

    response = client.get("/events", params={"taglist": "APRENDIZAJE,DIVERSION"})
    data = response.json()
    data = data['message']

    assert response.status_code == status.HTTP_200_OK
    assert data == []


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetEventsByManyTags_ManyMatch_TheAppReturnsTheEventsCorrectly():
    token = jwt_handler.create_access_token("1", 'organizer')
    client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    client.post("/organizers/active_events", json=json_theatre_event, headers={"Authorization": f"Bearer {token}"})
    client.post("/organizers/active_events", json=json_lollapalooza_first_date, headers={"Authorization": f"Bearer {token}"})

    response = client.get("/events", params={"taglist": "MUSICA,DIVERSION"})
    data = response.json()
    data = data['message']

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 2
    json_theatre_event_in_response = False
    for i in data:
        if i["name"] == json_theatre_event["name"]:
            json_theatre_event_in_response = True

    assert not json_theatre_event_in_response

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetEventsByType_NoneMatch_TheAppReturnsAnEmptyList():
    token = jwt_handler.create_access_token("1", 'organizer')
    client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    client.post("/organizers/active_events", json=json_theatre_event, headers={"Authorization": f"Bearer {token}"})

    response = client.get("/events", params={"eventType": "CINE"})
    data = response.json()
    data = data['message']

    assert response.status_code == status.HTTP_200_OK
    assert data == []


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetEventsByType_TwoMatch_TheAppReturnsTheEventsCorrectly():
    token = jwt_handler.create_access_token("1", 'organizer')
    client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    client.post("/organizers/active_events", json=json_theatre_event, headers={"Authorization": f"Bearer {token}"})
    client.post("/organizers/active_events", json=json_lollapalooza_first_date, headers={"Authorization": f"Bearer {token}"})

    response = client.get("/events", params={"eventType": "SHOW"})
    data = response.json()
    data = data['message']

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 2
    json_theatre_event_in_response = False
    for i in data:
        if i["name"] == json_theatre_event["name"]:
            json_theatre_event_in_response = True

    assert not json_theatre_event_in_response

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetEventsByTypeAndTag_OneMatches_TheAppReturnsTheEventCorrectly():
    token = jwt_handler.create_access_token("1", 'organizer')
    client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    client.post("/organizers/active_events", json=json_theatre_event, headers={"Authorization": f"Bearer {token}"})
    client.post("/organizers/active_events", json=json_lollapalooza_first_date, headers={"Authorization": f"Bearer {token}"})

    response = client.get("/events", params={"eventType": "SHOW", "taglist": "MUSICA,FESTIVAL"})
    data = response.json()
    data = data['message']

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 1
    assert data[0]["name"] == "lollapalooza"
    assert data[0]["ownerName"] == "Sol Fontenla"
    assert data[0]["description"] == "Veni a disfrutar del primer dia de esta nueva edición"
    assert data[0]["location"] == "Av. Bernabé Márquez 700, B1642 San Isidro, Provincia de Buenos Aires"
    assert data[0]["locationDescription"] == "Hipodromo de San Isidro"
    assert data[0]["capacity"] == 200000
    assert data[0]["dateEvent"] == "2024-01-28"
    assert data[0]["eventType"] == "SHOW"
    assert data[0]["attendance"]== 300
    assert data[0]["tags"] == [ "MUSICA", "DIVERSION", "FESTIVAL" ]
    assert data[0]["latitud"] == -34.4811222
    assert data[0]["longitud"] == -58.526158
    assert data[0]["start"]== "11:00:00"
    assert data[0]["end"]== "23:00:00"

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetEventsByTypeTagAndName_NoneMatches_TheAppReturnsAnEmptyList():
    token = jwt_handler.create_access_token("1", 'organizer')
    client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    client.post("/organizers/active_events", json=json_theatre_event, headers={"Authorization": f"Bearer {token}"})
    client.post("/organizers/active_events", json=json_lollapalooza_first_date, headers={"Authorization": f"Bearer {token}"})

    response = client.get("/events", params={"eventType": "SHOW", "taglist": "MUSICA,FESTIVAL", "name":"Primavera Sound"})
    data = response.json()
    data = data['message']

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 0


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientMarksAsFavouriteAnExistingEvent_TheEventIsMarkedCorrectly_TheAppReturnsCorrectMessage():
    token = jwt_handler.create_access_token("1", 'organizer')
    response = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    data = data['message']

    user_id = login_user()

    response_to_favourite = client.patch(f"/events/favourites/{data['_id']['$oid']}/user/{user_id}")

    assert response_to_favourite.status_code == status.HTTP_200_OK, response.text
    data = response_to_favourite.json()
    data = data['message']

    assert data == "Se agregó como favorito el evento"


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientMarksAsFavouriteANonExistingEvent_TheAppReturnsCorrectMessage():
    user_id = login_user()
    event_id = "6439a8d0c392bdf710446d31"

    response_to_favourite = client.patch(f"/events/favourites/{event_id}/user/{user_id}")

    assert response_to_favourite.status_code == status.HTTP_404_NOT_FOUND, response_to_favourite.text


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientMarksAsFavouriteTwiceAnExistingEvent_TheEventIsUnMarkedCorrectly_TheAppReturnsCorrectMessage():
    token = jwt_handler.create_access_token("1", 'organizer')
    response = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    data = response.json()
    data = data['message']
    user_id = login_user()
    event_id = data['_id']['$oid']

    response_to_favourite = client.patch(f"/events/favourites/{event_id}/user/{user_id}")
    assert response_to_favourite.status_code == status.HTTP_200_OK, response.text
    data = response_to_favourite.json()
    data = data['message']
    assert data == "Se agregó como favorito el evento"

    response_to_unfavourite = client.patch(f"/events/favourites/{event_id}/user/{user_id}")
    data = response_to_unfavourite.json()
    data = data['message']
    assert data == "Se eliminó como favorito el evento"


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientMarksAsFavouriteAnExistingEvent_TheClientsAsksForFavouriteEventsOfUser_TheAppReturnsTheEventCorrectly():
    token = jwt_handler.create_access_token("1", 'organizer')
    response = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    data = data['message']

    user_id = login_user()
    event_id = data['_id']['$oid']

    response_to_favourite = client.patch(f"/events/favourites/{event_id}/user/{user_id}")
    favourite_events = client.get(f"/events/favourites/{user_id}")
    data = favourite_events.json()
    data = data['message']

    assert len(data) == 1
    assert data[0]['_id']['$oid'] == event_id
    assert data[0]["name"] == "Music Fest"


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientMarksAsFavouriteTwiceAnExistingEvent_TheClientsAsksForFavouriteEventsOfUser_TheAppReturnsEmptyList():
    token = jwt_handler.create_access_token("1", 'organizer')
    response = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    data = data['message']

    user_id = login_user()
    event_id = data['_id']['$oid']

    response_to_favourite = client.patch(f"/events/favourites/{event_id}/user/{user_id}")
    response_to_favourite = client.patch(f"/events/favourites/{event_id}/user/{user_id}")
    favourite_events = client.get(f"/events/favourites/{user_id}")
    data = favourite_events.json()
    data = data['message']

    assert len(data) == 0

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientHasNoFavouriteEvents_TheClientsAsksForFavouriteEventsOfUser_TheAppReturnsEmptyList():
    token = jwt_handler.create_access_token("1", 'organizer')
    response = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    data = response.json()
    data = data['message']

    user_id = login_user()
    event_id = data['_id']['$oid']
    
    favourite_events = client.get(f"/events/favourites/{user_id}")
    data = favourite_events.json()
    data = data['message']

    assert len(data) == 0


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientMarksAsFavouriteAnExistingEvent_TheClientsAsksIfIsFavouriteEvent_TheAppReturnsTrue():
    token = jwt_handler.create_access_token("1", 'organizer')
    response = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    data = data['message']

    user_id = login_user()

    client.patch(f"/events/favourites/{data['_id']['$oid']}/user/{user_id}")
    response_to_favourite = client.get(f"/events/favourites/{data['_id']['$oid']}/user/{user_id}")

    assert response_to_favourite.status_code == status.HTTP_200_OK, response.text
    data = response_to_favourite.json()
    data = data['message']

    assert data == True


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientMarksAsFavouriteAnExistingEventTwice_TheClientsAsksIfIsFavouriteEvent_TheAppReturnsFalse():
    token = jwt_handler.create_access_token("1", 'organizer')
    response = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    data = data['message']

    user_id = login_user()

    client.patch(f"/events/favourites/{data['_id']['$oid']}/user/{user_id}")
    client.patch(f"/events/favourites/{data['_id']['$oid']}/user/{user_id}")
    response_to_favourite = client.get(f"/events/favourites/{data['_id']['$oid']}/user/{user_id}")

    assert response_to_favourite.status_code == status.HTTP_200_OK, response.text
    data = response_to_favourite.json()
    data = data['message']

    assert data == False


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientAsksIfANoneExistingEventIsFavourite_TheAppReturnsCorrectMessage():
    user_id = login_user()
    event_id = "6439a8d0c392bdf710446d31"

    response_to_favourite = client.get(f"/events/favourites/{event_id}/user/{user_id}")

    assert response_to_favourite.status_code == status.HTTP_404_NOT_FOUND, response_to_favourite.text


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetEventsBetween0And40KM_NoneMatch_TheAppReturnsAnEmptyList():
    token = jwt_handler.create_access_token("1", 'organizer')
    client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    client.post("/organizers/active_events", json=json_theatre_event, headers={"Authorization": f"Bearer {token}"})
    client.post("/organizers/active_events", json=json_lollapalooza_first_date, headers={"Authorization": f"Bearer {token}"})

    response = client.get("/events", params={"coordinates": COORDENADAS_CIUDAD_DE_CORDOBA, "distances_range": "0,40"})
    data = response.json()
    data = data['message']

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 0


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetEventsBetween0And40KM_TwoMatch_TheAppReturnsTheEventsCorrectly():
    token = jwt_handler.create_access_token("1", 'organizer')
    client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    client.post("/organizers/active_events", json=json_theatre_event, headers={"Authorization": f"Bearer {token}"})
    client.post("/organizers/active_events", json=json_lollapalooza_first_date, headers={"Authorization": f"Bearer {token}"})

    response = client.get("/events", params={"coordinates": COORDENAS_OBELISCO, "distances_range": "0,40"})
    data = response.json()
    data = data['message']

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 2


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetEventsBetween10And40KM_NoneMatch_TheAppReturnsAnEmptyList():
    token = jwt_handler.create_access_token("1", 'organizer')
    client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    client.post("/organizers/active_events", json=json_theatre_event, headers={"Authorization": f"Bearer {token}"})

    response = client.get("/events", params={"coordinates": COORDENAS_OBELISCO, "distances_range": "10,40"})
    data = response.json()
    data = data['message']

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 0

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetEventsBetween0And10KM_NoneMatch_TheAppReturnsAnEmptyList():
    token = jwt_handler.create_access_token("1", 'organizer')
    client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    client.post("/organizers/active_events", json=json_theatre_event, headers={"Authorization": f"Bearer {token}"})
    client.post("/organizers/active_events", json=json_lollapalooza_first_date, headers={"Authorization": f"Bearer {token}"})

    response = client.get("/events", params={"coordinates": COORDENAS_OBELISCO, "distances_range": "0,10"})
    data = response.json()
    data = data['message']

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 1 


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientReservesANonExistingEvent_TheAppReturnsCorrectErrorMessage():
    user_id = login_user()
    event_id = "6439a8d0c392bdf710446d31"

    response_to_reservation = client.post(f"/events/reservations/user/{user_id}/event/{event_id}")


    assert response_to_reservation.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientReservesAnExistingEvent_ThenItShouldIncreaseitAttendase():
    token = jwt_handler.create_access_token("1", 'organizer')
    response = client.post("/organizers/active_events", json=json_programming_event, headers={"Authorization": f"Bearer {token}"})

    data = response.json()
    data = data['message']
    event_id = data['_id']['$oid']
    user_id = login_user()
    client.post(f"/events/reservations/user/{user_id}/event/{event_id}")
    response_event = client.get(f"/events/{event_id}")

    data_event = response_event.json()
    assert 1 == data_event['message']['attendance']


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientReservesAnExistingEvent_TheEventIsReservedCorrectly_TheAppReturnsCorrectMessage():
    token = jwt_handler.create_access_token("1", 'organizer')
    response = client.post("/organizers/active_events", json=json_programming_event, headers={"Authorization": f"Bearer {token}"})
    data = response.json()
    data = data['message']
    user_id = login_user()
    event_id = data['_id']['$oid']

    response_to_reservation = client.post(f"/events/reservations/user/{user_id}/event/{event_id}")
    assert response_to_reservation.status_code == status.HTTP_201_CREATED, response.text
    data = response_to_reservation.json()
    data = data['message']
    assert type(data['_id']['$oid']) == str


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientReservesAnExistingEvent_TheEventClientGetsTheTicket_TheAppReturnsCorrectMessage():
    token = jwt_handler.create_access_token("1", 'organizer')
    response = client.post("/organizers/active_events", json=json_programming_event, headers={"Authorization": f"Bearer {token}"})
    data = response.json()
    data = data['message']
    user_id = login_user()
    event_id = data['_id']['$oid']

    response_to_reservation = client.post(f"/events/reservations/user/{user_id}/event/{event_id}")
    assert response_to_reservation.status_code == status.HTTP_201_CREATED, response.text
    reservation = client.get(f"/events/reservations/user/{user_id}/event/{event_id}")
    response_to_reservation  = response_to_reservation.json()
    response_to_reservation = response_to_reservation['message']
    reservation = reservation.json()
    reservation = reservation["message"]
    assert response_to_reservation['_id']['$oid'] == reservation['_id']['$oid']
    assert response_to_reservation['status'] == 'active'

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientReservesAnEventTwice_TheAppReturnsCorrectErrorMessage():
    token = jwt_handler.create_access_token("1", 'organizer')
    response = client.post("/organizers/active_events", json=json_programming_event, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    data = data['message']
    user_id = login_user()
    event_id = data["_id"]['$oid']

    client.post(f"/events/reservations/user/{user_id}/event/{event_id}")
    response_to_reservation = client.post(f"/events/reservations/user/{user_id}/event/{event_id}")
    assert response_to_reservation.status_code == status.HTTP_409_CONFLICT, response.text

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientGetsReservedEventsForUser_ThereAreNon_TheAppReturnsEmptyList():
    user_id = login_user()
    response_to_reservations = client.get(f"/events/reservations/user/{user_id}")
    assert response_to_reservations.status_code == status.HTTP_200_OK, response_to_reservations.text
    data = response_to_reservations.json()
    data = data['message']

    assert len(data) == 0


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientReservesAnExistingEvent_TheClientGetsTheReservedEvents_TheAppReturnsTheEventCorrectly():
    token = jwt_handler.create_access_token("1", 'organizer')
    response = client.post("/organizers/active_events", json=json_programming_event, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_201_CREATED, response.text

    data = response.json()
    data = data['message']
    user_id = login_user()
    event_id = data['_id']['$oid']

    response = client.post(f"/events/reservations/user/{user_id}/event/{event_id}")
    assert response.status_code == status.HTTP_201_CREATED, response.text
    
    reservation = client.get(f"/events/reservations/user/{user_id}")
    assert reservation.status_code == status.HTTP_200_OK, response.text
    reservation = reservation.json()
    (reservation)
    reservation = reservation['message']
    assert len(reservation) == 1
    assert reservation[0]['_id']['$oid'] == event_id
    assert reservation[0]["name"] == "Aprendé a programar en python!"


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenAnActiveEventIsCanceledAndTheDateHasNotYetPassed_TheEventIsCorrectlyCanceled():
    token = jwt_handler.create_access_token("1", 'organizer')
    response = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_201_CREATED, response.text

    data = response.json()
    data = data['message']
    event_id = data['_id']['$oid']

    canceled_event = client.patch(f"/orgainzers/canceled_events/{event_id}", headers={"Authorization": f"Bearer {token}"})
    assert canceled_event.status_code == status.HTTP_200_OK, canceled_event.text
    canceled_event = canceled_event.json()
    canceled_event = canceled_event['message']
    assert canceled_event["name"] == "Music Fest"
    assert canceled_event["ownerName"] == "Agustina Segura"
    assert canceled_event["description"] == "Musical de pop, rock y mucho más"
    assert canceled_event["location"] == "Av. Pres. Figueroa Alcorta 7597, C1428 CABA"
    assert canceled_event["locationDescription"] == "Estadio River"
    assert canceled_event["capacity"] == 5000
    assert canceled_event["dateEvent"] == "2023-07-01"
    assert canceled_event["attendance"]== 0
    assert canceled_event["latitud"] == -34.6274931
    assert canceled_event["longitud"] == -68.3252097
    assert canceled_event["start"]=="19:00:00"
    assert canceled_event["end"]=="23:00:00"
    assert canceled_event['faqs'][0]['pregunta'] == 'Como llegar?'
    assert canceled_event['faqs'][0]['respuesta'] == 'Por medio del colectivo 152'
    assert canceled_event['agenda'][0]['time'] == "19:00"
    assert canceled_event['agenda'][0]['description'] == 'Arranca banda de rock'
    assert canceled_event['agenda'][1]['time'] == "20:00"
    assert canceled_event['agenda'][1]['description'] ==  'comienza banda de pop'
    assert canceled_event['status'] == "canceled"

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenAnActiveEventIsCanceledAndTheDateHasNotYetPassed_TheEventIsCorrectlyCanceled():
    token = jwt_handler.create_access_token("1", 'organizer')
    response = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_201_CREATED, response.text

    data = response.json()
    data = data['message']
    event_id = data['_id']['$oid']

    client.patch(f"/organizers/canceled_events/{event_id}", headers={"Authorization": f"Bearer {token}"})
    canceled_event = client.patch(f"/organizers/canceled_events/{event_id}", headers={"Authorization": f"Bearer {token}"})

    assert canceled_event.status_code == status.HTTP_200_OK, canceled_event.text
    canceled_event = canceled_event.json()
    canceled_event = canceled_event['message']
    assert canceled_event["name"] == "Music Fest"
    assert canceled_event["ownerName"] == "Agustina Segura"
    assert canceled_event["description"] == "Musical de pop, rock y mucho más"
    assert canceled_event["location"] == "Av. Pres. Figueroa Alcorta 7597, C1428 CABA"
    assert canceled_event["locationDescription"] == "Estadio River"
    assert canceled_event["capacity"] == 5000
    assert canceled_event["dateEvent"] == "2023-07-01"
    assert canceled_event["attendance"]== 0
    assert canceled_event["latitud"] == -34.6274931
    assert canceled_event["longitud"] == -68.3252097
    assert canceled_event["start"]=="19:00:00"
    assert canceled_event["end"]=="23:00:00"
    assert canceled_event['faqs'][0]['pregunta'] == 'Como llegar?'
    assert canceled_event['faqs'][0]['respuesta'] == 'Por medio del colectivo 152'
    assert canceled_event['agenda'][0]['time'] == "19:00"
    assert canceled_event['agenda'][0]['description'] == 'Arranca banda de rock'
    assert canceled_event['agenda'][1]['time'] == "20:00"
    assert canceled_event['agenda'][1]['description'] ==  'comienza banda de pop'
    assert canceled_event['status'] == "canceled"


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenAnActiveEventIsCanceledAndTheDateHasYetPassed_TheEventIsCorrectlyCanceled():
    token = jwt_handler.create_access_token("1", 'organizer')
    json_event_with_invalid_date = json_rock_music_event.copy()
    json_event_with_invalid_date["dateEvent"] = "2023-01-01"
    json_event_with_invalid_date["ownerId"] = "1"
    
    inserted_event = db['events'].insert_one(json_event_with_invalid_date)
    event_id = inserted_event.inserted_id

    canceled_event = client.patch(f"/organizers/canceled_events/{event_id}", headers={"Authorization": f"Bearer {token}"})
    assert canceled_event.status_code == status.HTTP_409_CONFLICT, canceled_event.text

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTryingToReserveATicketOfACanceledEvent_ReturnsError():
    token = jwt_handler.create_access_token("1", 'organizer')
    response = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_201_CREATED, response.text

    data = response.json()
    data = data['message']
    user_id = login_user()
    event_id = data['_id']['$oid']


    client.patch(f"/organizers/canceled_events/{event_id}", headers={"Authorization": f"Bearer {token}"})
    response_to_reservation = client.post(f"/events/reservations/user/{user_id}/event/{event_id}")
    assert response_to_reservation.status_code == status.HTTP_409_CONFLICT, response_to_reservation.text
    data = response_to_reservation.json()

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenAnEventIsCanceled_TheTicketsOfThatEventHaveCanceledStatus():
    token = jwt_handler.create_access_token("1", 'organizer')
    response = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_201_CREATED, response.text

    data = response.json()
    data = data['message']
    user_id = login_user()
    event_id = data['_id']['$oid']


    response_to_reservation = client.post(f"/events/reservations/user/{user_id}/event/{event_id}")
    client.patch(f"/organizers/canceled_events/{event_id}", headers={"Authorization": f"Bearer {token}"})
    reservation = client.get(f"/events/reservations/user/{user_id}/event/{event_id}")
    response_to_reservation  = response_to_reservation.json()
    response_to_reservation = response_to_reservation['message']
    reservation = reservation.json()
    reservation = reservation["message"]
    assert response_to_reservation['_id']['$oid'] == reservation['_id']['$oid']
    assert reservation['status'] == 'canceled'
