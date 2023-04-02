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
    config.clear_db_collection(db)

json_rock_music_event = {
            "name": "Music Fest",  "owner": "Agustina Segura",  "description": "Musical de pop, rock y mucho más", 
            "location": "Av. Pres. Figueroa Alcorta 7597, C1428 CABA",
            "locationDescription": "Estadio River", "capacity": 5000, "dateEvent": "2023-06-01", "attendance": 0, 
            "tags": [ "MUSICA", "DIVERSION" ], "latitud": 8.9, "longitud": 6.8, "start": "19:00", "end": "23:00" }

json_theatre_event = {
            "name": "Tootsie",  "owner": "Nico Vazquez",  "description": "La comedia del 2023",
            "location": "Av. Corrientes 1280, C1043AAZ CABA",
            "locationDescription": "Teatro Lola Membrives", "capacity": 400, "dateEvent": "2023-04-30", "attendance": 0, 
            "tags": [ "TEATRO", "FAMILIAR", "ENTRETENIMIENTO" ], "latitud": 8.9, "longitud": 6.8, "start": "21.00", "end": "22:30" }

json_programming_event = {
            "name": "Aprendé a programar en python!",  "owner": "Sol Fontenla",  "description": "Aprende a programar en python desde cero",
            "location": "Av. Paseo Colón 850, C1063 CABA",
            "locationDescription": "Facultad de Ingenieria - UBA", "capacity": 100, "dateEvent": "2023-07-07", "attendance": 0, 
            "tags": [ "PROGRAMACION", "APRENDIZAJE", ], "latitud": 8.9, "longitud": 6.8, "start": "21.00", "end": "22:30" }

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

    config.clear_db_collection(db)


@pytest.mark.usefixtures("drop_collection_documents")
def test_given_a_date_that_passed_when_creating_an_event_then_it_should_not_create_it():

    json_event_with_invalid_date = json_rock_music_event.copy()
    json_event_with_invalid_date["dateEvent"] = "2023-01-01"
    response = client.post("/events/", json=json_event_with_invalid_date,)
    assert response.status_code == status.HTTP_409_CONFLICT, response.text
    data = response.json()

    assert data["detail"] == "the chosen date has passed"

    config.clear_db_collection(db)


@pytest.mark.usefixtures("drop_collection_documents")
def test_given_an_event_when_the_event_exists_then_it_should_return_it():
    response = client.post("/events/", json=json_rock_music_event)

    data = response.json()

    data = data['message']
    path_end = "/events/" + data['_id']['$oid']
    response = client.get(path_end)
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

    config.clear_db_collection(db)


@pytest.mark.usefixtures("drop_collection_documents")
def test_given_an_event_when_the_event_does_not_exist_then_it_should_not_return_it():
    response = client.get("/events/5428bd284042b5da2e28b6a1")
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
    
    
