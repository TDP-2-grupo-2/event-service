from fastapi.testclient import TestClient
from fastapi import status
from test import config
from event_service.app import app
db = config.init_db()
from pymongo.results import InsertOneResult
from bson.objectid import ObjectId
import pytest

client = TestClient(app)
@pytest.fixture
def drop_collection_documents():
    config.clear_db_events_collection(db)
    config.clear_db_favourites_collection(db)
    config.clear_db_reservations_collection(db)


json_rock_music_event = {
            "name": "Music Fest",  "owner": "Agustina Segura",  "description": "Musical de pop, rock y mucho más", 
            "location": "Av. Pres. Figueroa Alcorta 7597, C1428 CABA", "locationDescription": "Estadio River", "capacity": 5000, 
            "dateEvent": "2023-06-01", "attendance": 0, "eventType": "SHOW","tags": [ "MUSICA", "DIVERSION" ], "latitud": 8.9, 
            "longitud": 6.8, "start": "19:00", "end": "23:00", "faqs": [{'pregunta':'Como llegar?', 'respuesta':'Por medio del colectivo 152'}],
            "agenda": [{'time': "19:00", 'description': 'Arranca banda de rock'}, {'time': '20:00', 'description': 'comienza banda de pop'}] }

json_lollapalooza_first_date = {
            "name": "lollapalooza",  "owner": "Sol Fontenla",  "description": "Veni a disfrutar del primer dia de esta nueva edición", 
            "location": "Av. Bernabé Márquez 700, B1642 San Isidro, Provincia de Buenos Aires", "locationDescription": "Hipodromo de San Isidro",
            "capacity": 200000, "dateEvent": "2024-03-28", "attendance": 300, "eventType": "SHOW", "tags": [ "MuSiCa", "DiVeRsIoN", "FESTIVAL" ],
            "latitud": 8.9, "longitud": 6.8, "start": "11:00", "end": "23:00" }


json_theatre_event = {
            "name": "Tootsie",  "owner": "Nico Vazquez",  "description": "La comedia del 2023",
            "location": "Av. Corrientes 1280, C1043AAZ CABA", "locationDescription": "Teatro Lola Membrives", 
            "capacity": 400, "dateEvent": "2023-04-30", "attendance": 0, "eventType": "TEATRO", 
            "tags": [ "COMEDIA", "FAMILIAR", "ENTRETENIMIENTO" ], "latitud": 8.9, "longitud": 6.8, "start": "21:00", "end": "22:30" }

json_programming_event = {
            "name": "Aprendé a programar en python!",  "owner": "Sol Fontenla",  "description": "Aprende a programar en python desde cero",
            "location": "Av. Paseo Colón 850, C1063 CABA",
            "locationDescription": "Facultad de Ingenieria - UBA", "capacity": 100, "dateEvent": "2023-07-07", "attendance": 0, "eventType": "TECNOLOGIA",
            "tags": [ "PROGRAMACION", "APRENDIZAJE", ], "latitud": 8.9, "longitud": 6.8, "start": "21:00", "end": "22:30" }

@pytest.mark.usefixtures("drop_collection_documents")
def test_given_a_new_event_when_an_organizer_wants_to_created_then_it_should_create_it():
    response = client.post("/events/", json=json_rock_music_event)
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    data = data['message']
    
    assert data["name"] == "Music Fest"
    assert data["owner"] == "Agustina Segura"
    assert data["description"] == "Musical de pop, rock y mucho más"
    assert data["location"] == "Av. Pres. Figueroa Alcorta 7597, C1428 CABA"
    assert data["locationDescription"] == "Estadio River"
    assert data["capacity"] == 5000
    assert data["dateEvent"] == "2023-06-01"
    assert data["attendance"]== 0
    assert data["latitud"] == 8.9
    assert data["longitud"] == 6.8
    assert data["start"]=="19:00:00"
    assert data["end"]=="23:00:00"
    assert data['faqs'][0]['pregunta'] == 'Como llegar?'
    assert data['faqs'][0]['respuesta'] == 'Por medio del colectivo 152'
    assert data['agenda'][0]['time'] == "19:00"
    assert data['agenda'][0]['description'] == 'Arranca banda de rock'
    assert data['agenda'][1]['time'] == "20:00"
    assert data['agenda'][1]['description'] ==  'comienza banda de pop'


@pytest.mark.usefixtures("drop_collection_documents")
def test_given_a_date_that_passed_when_creating_an_event_then_it_should_not_create_it():

    json_event_with_invalid_date = json_rock_music_event.copy()
    json_event_with_invalid_date["dateEvent"] = "2023-01-01"
    response = client.post("/events/", json=json_event_with_invalid_date,)
    assert response.status_code == status.HTTP_409_CONFLICT, response.text
    data = response.json()

    assert data["detail"] == "the chosen date has passed"


@pytest.mark.usefixtures("drop_collection_documents")
def test_given_an_event_when_the_event_exists_then_it_should_return_it():
    response = client.post("/events/", json=json_rock_music_event)

    data = response.json()
    path_end = "/events/" + data['message']['_id']['$oid']
    response = client.get(path_end)
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    data = data['message']

    assert data["name"] == "Music Fest"
    assert data["owner"] == "Agustina Segura"
    assert data["description"] == "Musical de pop, rock y mucho más"
    assert data["location"] == "Av. Pres. Figueroa Alcorta 7597, C1428 CABA"
    assert data["locationDescription"] == "Estadio River"
    assert data["capacity"] == 5000
    assert data["dateEvent"] == "2023-06-01"
    assert data["attendance"]== 0
    assert data["latitud"] == 8.9
    assert data["longitud"] == 6.8
    assert data["start"]=="19:00:00"
    assert data["end"]=="23:00:00"
    


@pytest.mark.usefixtures("drop_collection_documents")
def test_given_an_event_when_the_event_does_not_exist_then_it_should_not_return_it():
    response = client.get("/events/5428bd284042b5da2e28b6a1")
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    data = response.json()

    assert data["detail"] == "The event does not exists"


@pytest.mark.usefixtures("drop_collection_documents")
def test_given_an_exiting_event_when_i_want_to_deleted_then_it_should_do_it():
    response = client.post("/events/", json=json_rock_music_event)
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
    client.post("/events/", json=json_rock_music_event)
    client.post("/events/", json=json_theatre_event)
    client.post("/events/", json=json_programming_event)

    response = client.get("/events/")
    data = response.json()
    events = data['message']

    assert len(events) == 3
    
    
@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetEventsByName_NoneMatch_TheAppReturnsAnEmptyList():
    client.post("/events/", json=json_rock_music_event)
    client.post("/events/", json=json_theatre_event)

    response = client.get("/events?name=Festival")
    data = response.json()
    data = data['message']

    assert response.status_code == status.HTTP_200_OK
    assert data == []


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetEventsByOwner_OneMatches_TheAppReturnsTheEventCorrectly():
    client.post("/events/", json=json_rock_music_event)
    client.post("/events/", json=json_theatre_event)

    response = client.get("/events?owner=Nico Vazquez")
    data = response.json()
    data = data['message']

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 1
    assert data[0]["name"] == "Tootsie"
    assert data[0]["owner"] == "Nico Vazquez"
    assert data[0]["description"] == "La comedia del 2023"
    assert data[0]["location"] == "Av. Corrientes 1280, C1043AAZ CABA"
    assert data[0]["locationDescription"] == "Teatro Lola Membrives"
    assert data[0]["capacity"] == 400
    assert data[0]["dateEvent"] == "2023-04-30"
    assert data[0]["attendance"]== 0
    assert data[0]["tags"] == [ "COMEDIA", "FAMILIAR", "ENTRETENIMIENTO" ]
    assert data[0]["latitud"] == 8.9
    assert data[0]["longitud"] == 6.8
    assert data[0]["start"]== "21:00:00"
    assert data[0]["end"]== "22:30:00"


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetEventsByName_OneMatches_TheAppReturnsTheEventCorrectly():
    client.post("/events/", json=json_rock_music_event)
    client.post("/events/", json=json_theatre_event)

    response = client.get("/events?name=tootsie")
    data = response.json()
    data = data['message']

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 1
    assert data[0]["name"] == "Tootsie"
    assert data[0]["owner"] == "Nico Vazquez"
    assert data[0]["description"] == "La comedia del 2023"
    assert data[0]["location"] == "Av. Corrientes 1280, C1043AAZ CABA"
    assert data[0]["locationDescription"] == "Teatro Lola Membrives"
    assert data[0]["capacity"] == 400
    assert data[0]["dateEvent"] == "2023-04-30"
    assert data[0]["attendance"]== 0
    assert data[0]["tags"] == [ "COMEDIA", "FAMILIAR", "ENTRETENIMIENTO" ]
    assert data[0]["latitud"] == 8.9
    assert data[0]["longitud"] == 6.8
    assert data[0]["start"]== "21:00:00"
    assert data[0]["end"]== "22:30:00"



@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetEventsByIncompleteName_OneMatches_TheAppReturnsTheEventCorrectly():
    client.post("/events/", json=json_rock_music_event)
    client.post("/events/", json=json_theatre_event)
    response = client.get("/events?name=oot")
    data = response.json()
    data = data['message']

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 1
    assert data[0]["name"] == "Tootsie"
    assert data[0]["owner"] == "Nico Vazquez"
    assert data[0]["description"] == "La comedia del 2023"
    assert data[0]["location"] == "Av. Corrientes 1280, C1043AAZ CABA"
    assert data[0]["locationDescription"] == "Teatro Lola Membrives"
    assert data[0]["capacity"] == 400
    assert data[0]["dateEvent"] == "2023-04-30"
    assert data[0]["attendance"]== 0
    assert data[0]["tags"] == [ "COMEDIA", "FAMILIAR", "ENTRETENIMIENTO" ]
    assert data[0]["latitud"] == 8.9
    assert data[0]["longitud"] == 6.8
    assert data[0]["start"]== "21:00:00"
    assert data[0]["end"]== "22:30:00"


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetEventsByTags_NoneMatch_TheAppReturnsAnEmptyList():
    client.post("/events/", json=json_rock_music_event)
    client.post("/events/", json=json_theatre_event)

    response = client.get("/events", params={"taglist": "APRENDIZAJE"})
    data = response.json()
    data = data['message']

    assert response.status_code == status.HTTP_200_OK
    assert data == []


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetEventsByTwoTags_NoneMatch_TheAppReturnsAnEmptyList():
    client.post("/events/", json=json_rock_music_event)
    client.post("/events/", json=json_theatre_event)

    response = client.get("/events", params={"taglist": "APRENDIZAJE,DIVERSION"})
    data = response.json()
    data = data['message']

    assert response.status_code == status.HTTP_200_OK
    assert data == []


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetEventsByManyTags_ManyMatch_TheAppReturnsTheEventsCorrectly():
    client.post("/events/", json=json_rock_music_event)
    client.post("/events/", json=json_theatre_event)
    client.post("/events/", json=json_lollapalooza_first_date)

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
    client.post("/events/", json=json_rock_music_event)
    client.post("/events/", json=json_theatre_event)

    response = client.get("/events", params={"eventType": "CINE"})
    data = response.json()
    data = data['message']

    assert response.status_code == status.HTTP_200_OK
    assert data == []


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetEventsByType_TwoMatch_TheAppReturnsTheEventsCorrectly():
    client.post("/events/", json=json_rock_music_event)
    client.post("/events/", json=json_theatre_event)
    client.post("/events/", json=json_lollapalooza_first_date)

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
    client.post("/events/", json=json_rock_music_event)
    client.post("/events/", json=json_theatre_event)
    client.post("/events/", json=json_lollapalooza_first_date)

    response = client.get("/events", params={"eventType": "SHOW", "taglist": "MUSICA,FESTIVAL"})
    data = response.json()
    data = data['message']

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 1
    assert data[0]["name"] == "lollapalooza"
    assert data[0]["owner"] == "Sol Fontenla"
    assert data[0]["description"] == "Veni a disfrutar del primer dia de esta nueva edición"
    assert data[0]["location"] == "Av. Bernabé Márquez 700, B1642 San Isidro, Provincia de Buenos Aires"
    assert data[0]["locationDescription"] == "Hipodromo de San Isidro"
    assert data[0]["capacity"] == 200000
    assert data[0]["dateEvent"] == "2024-03-28"
    assert data[0]["eventType"] == "SHOW"
    assert data[0]["attendance"]== 300
    assert data[0]["tags"] == [ "MUSICA", "DIVERSION", "FESTIVAL" ]
    assert data[0]["latitud"] == 8.9
    assert data[0]["longitud"] == 6.8
    assert data[0]["start"]== "11:00:00"
    assert data[0]["end"]== "23:00:00"

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientTriesToGetEventsByTypeTagAndName_NoneMatches_TheAppReturnsAnEmptyList():
    client.post("/events/", json=json_rock_music_event)
    client.post("/events/", json=json_theatre_event)
    client.post("/events/", json=json_lollapalooza_first_date)

    response = client.get("/events", params={"eventType": "SHOW", "taglist": "MUSICA,FESTIVAL", "name":"Primavera Sound"})
    data = response.json()
    data = data['message']

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 0


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientMarksAsFavouriteAnExistingEvent_TheEventIsMarkedCorrectly_TheAppReturnsCorrectMessage():
    response = client.post("/events/", json=json_rock_music_event)
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    data = data['message']

    user_id = "1"

    response_to_favourite = client.patch(f"/events/favourites/{data['_id']['$oid']}/user/{user_id}")

    assert response_to_favourite.status_code == status.HTTP_200_OK, response.text
    data = response_to_favourite.json()
    data = data['message']

    assert data == "Se agregó como favorito el evento"


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientMarksAsFavouriteANonExistingEvent_TheAppReturnsCorrectMessage():
    user_id = "1"
    event_id = "6439a8d0c392bdf710446d31"

    response_to_favourite = client.patch(f"/events/favourites/{event_id}/user/{user_id}")

    assert response_to_favourite.status_code == status.HTTP_404_NOT_FOUND, response.text

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientMarksAsFavouriteTwiceAnExistingEvent_TheEventIsUnMarkedCorrectly_TheAppReturnsCorrectMessage():
    response = client.post("/events/", json=json_rock_music_event)
    data = response.json()
    data = data['message']
    user_id = "1"
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
    response = client.post("/events/", json=json_rock_music_event)
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    data = data['message']

    user_id = "1"
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
    response = client.post("/events/", json=json_rock_music_event)
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    data = data['message']

    user_id = "1"
    event_id = data['_id']['$oid']

    response_to_favourite = client.patch(f"/events/favourites/{event_id}/user/{user_id}")
    response_to_favourite = client.patch(f"/events/favourites/{event_id}/user/{user_id}")
    favourite_events = client.get(f"/events/favourites/{user_id}")
    data = favourite_events.json()
    data = data['message']

    assert len(data) == 0


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientHasNoFavouriteEvents_TheClientsAsksForFavouriteEventsOfUser_TheAppReturnsEmptyList():
    response = client.post("/events/", json=json_rock_music_event)
    data = response.json()
    data = data['message']

    user_id = "1"
    event_id = data['_id']['$oid']
    
    favourite_events = client.get(f"/events/favourites/{user_id}")
    data = favourite_events.json()
    data = data['message']

    assert len(data) == 0


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientReservesANonExistingEvent_TheAppReturnsCorrectErrorMessage():
    user_id = "1"
    event_id = "6439a8d0c392bdf710446d31"

    response_to_reservation = client.post(f"/events/reservations/user/{user_id}/event/{event_id}")


    assert response_to_reservation.status_code == status.HTTP_404_NOT_FOUND, response.text


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientReservesAnExistingEvent_TheEventIsReservedCorrectly_TheAppReturnsCorrectMessage():
    response = client.post("/events/", json=json_programming_event)
    data = response.json()
    data = data['message']
    user_id = "1"
    event_id = data['_id']['$oid']

    response_to_reservation = client.post(f"/events/reservations/user/{user_id}/event/{event_id}")
    assert response_to_reservation.status_code == status.HTTP_201_CREATED, response.text
    data = response_to_reservation.json()
    data = data['message']
    assert data == "Se reservo el evento exitosamente"


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientReservesAnEventTwice_TheAppReturnsCorrectErrorMessage():
    response = client.post("/events/", json=json_programming_event)
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    data = data['message']
    user_id = "1"
    event_id = data['_id']['$oid']

    client.post(f"/events/reservations/user/{user_id}/event/{event_id}")

    response_to_reservation = client.post(f"/events/reservations/user/{user_id}/event/{event_id}")
    assert response_to_reservation.status_code == status.HTTP_409_CONFLICT, response.text

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientGetsReservedEventsForUser_ThereAreNon_TheAppReturnsEmptyList():
    user_id = "1"
    response_to_reservations = client.get(f"/events/reservations/user/{user_id}")
    assert response_to_reservations.status_code == status.HTTP_200_OK, response_to_reservations.text
    data = response_to_reservations.json()
    data = data['message']

    assert len(data) == 0


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTheClientReservesAnExistingEvent_TheClientGetsTheReservedEvents_TheAppReturnsTheEventCorrectly():
    response = client.post("/events/", json=json_programming_event)
    assert response.status_code == status.HTTP_201_CREATED, response.text

    data = response.json()
    data = data['message']
    user_id = "1"
    event_id = data['_id']['$oid']

    client.post(f"/events/reservations/user/{user_id}/event/{event_id}")
    assert response.status_code == status.HTTP_201_CREATED, response.text
    
    reservation = client.get(f"/events/reservations/user/{user_id}")
    assert reservation.status_code == status.HTTP_200_OK, response.text
    data = reservation.json()
    data = data['message']
    assert len(data) == 1
    assert data[0]['_id']['$oid'] == event_id
    assert data[0]["name"] == "Aprendé a programar en python!"
