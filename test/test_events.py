from fastapi.testclient import TestClient
from fastapi import status
from test import config
from event_service.app import app
config.init_db()

client = TestClient(app)




def create_event1():
    respose = client.post("/events/", json={
            "name": "Music Fest ",
            "owner": "Agustina Segura",
            "description": "Musical de pop, rock y mucho más",
            "location": "Estadio River ",
            "capacity": 5000,
            "dateEvent": "2023-06-01",
            "attendance": 0,
            "tags": [
                "MUSICA", "DIVERSION"
            ],
            "latitud": 8.9,
            "longitud": 6.8,
            "start": "19:00",
            "end": "23:00"
                    },)
    return respose

def create_event2():
    respose = client.post("/events/", json={
            "name": "Music Fest ",
            "owner": "Agustina Segura",
            "description": "Musical de pop, rock y mucho más",
            "location": "Estadio River ",
            "capacity": 5000,
            "dateEvent": "2023-01-01",
            "attendance": 0,
            "tags": [
                "MUSICA", "DIVERSION"
            ],
            "latitud": 8.9,
            "longitud": 6.8,
            "start": "19:00",
            "end": "23:00"
                    },)
    return respose


def test_given_a_new_event_when_an_organizer_wants_to_created_then_it_should_create_it():

    response = create_event1()
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    data = data['message']
    
    assert data["name"] == "Music Fest "
    assert data["owner"] == "Agustina Segura"
    assert data["description"] == "Musical de pop, rock y mucho más"
    assert data["location"] == "Estadio River "
    assert data["capacity"] == 5000
    assert data["dateEvent"] == "2023-06-01"
    assert data["attendance"]== 0
    assert data["latitud"] == 8.9
    assert data["longitud"] == 6.8
    assert data["start"]=="19:00:00"
    assert data["end"]=="23:00:00"


def test_given_a_test_that_passed_when_creating_an_event_then_it_should_not_create_it():

    response = create_event2()
    assert response.status_code == status.HTTP_409_CONFLICT, response.text
    data = response.json()

    assert data["detail"] == "the chosen date has passed"

def test_given_an_event_when_the_event_exits_then_it_should_return_it():
    response = create_event1()
    data = response.json()
    data = data['message']
    print(data)
    path_end = "/events/" + data['_id']['$oid']
    print(path_end)
    response = client.get(path_end)
    print(response)
    data = response.json()
    data = data['message']
    assert data["name"] == "Music Fest "
    assert data["owner"] == "Agustina Segura"
    assert data["description"] == "Musical de pop, rock y mucho más"
    assert data["location"] == "Estadio River "
    assert data["capacity"] == 5000
    assert data["dateEvent"] == "2023-06-01"
    assert data["attendance"]== 0
    assert data["latitud"] == 8.9
    assert data["longitud"] == 6.8
    assert data["start"]=="19:00:00"
    assert data["end"]=="23:00:00"

def test_given_an_event_when_the_event_does_not_exits_then_it_should_not_return_it():
    response = client.get("/events/5428bd284042b5da2e28b6a1")
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    data = response.json()

    assert data["detail"] == "The event does not exists"