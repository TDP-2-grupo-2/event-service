import datetime
from fastapi.testclient import TestClient
from fastapi import status
from test import config
from event_service.app import app
from event_service.utils import jwt_handler
import pytest

session = config.init_postg_db(app)
reports_db = config.init_reports_db()
events_db = config.init_db()

client = TestClient(app)

non_existing_event_report = {"event_id": "6439a8d0c392bdf710446d31", "report_date": "2024-01-28", "reason": "seems fake" }

json_rock_music_event = {
            "name": "Music Fest",  "ownerName": "Agustina Segura",  "description": "Musical de pop, rock y mucho más", 
            "location": "Av. Pres. Figueroa Alcorta 7597, C1428 CABA", "locationDescription": "Estadio River", "capacity": 5000, 
            "dateEvent": "2023-07-01", "attendance": 0, "eventType": "SHOW","tags": [ "MUSICA", "DIVERSION" ], "latitud": -34.6274931, 
            "longitud": -68.3252097, "start": "19:00", "end": "23:00", "tags":["DIVERSION"], "faqs": [{'pregunta':'Como llegar?', 'respuesta':'Por medio del colectivo 152'}],
            "agenda": [{'time': "19:00", 'description': 'Arranca banda de rock'}, {'time': '20:00', 'description': 'comienza banda de pop'}] }


@pytest.fixture
def drop_collection_documents():
    config.clear_db_events_reports_collection(reports_db)


@pytest.mark.usefixtures("drop_collection_documents")
def test_when_login_for_the_first_time_an_attende_then_it_returns_its_token():

    response = client.post("/attendees/loginGoogle", json={"email": "agustina@gmail.com", "name": "agustina segura"})
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    actual = jwt_handler.decode_token(data)
    expected = {
        "id": 1,
        "rol": "attendee",
    }
    assert actual["id"] == expected["id"]
    assert actual["rol"] == expected["rol"]


@pytest.mark.usefixtures("drop_collection_documents")
def test_whenAUserTriesToReportANonExistingEvent_theReportCannotBeCompleted_theAppReturnsError():

    response = client.post("/attendees/loginGoogle", json={"email": "agustina@gmail.com", "name": "agustina segura"})
    assert response.status_code == status.HTTP_200_OK, response.text
    token = response.json()
    report_event_response = client.post("/attendees/report/event",json=non_existing_event_report, headers={"Authorization": f"Bearer {token}"})
    assert report_event_response.status_code == status.HTTP_404_NOT_FOUND, response.text
    reponse_text = report_event_response.json()
    reponse_text = reponse_text['detail']

    assert reponse_text == "Este evento no existe"
    

@pytest.mark.usefixtures("drop_collection_documents")
def test_whenAUserTriesToReportAnExistingEvent_theReportCanBeCompleted_theAppReturnsError():

    organizer_response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    organizer_token = organizer_response.json()
    new_event = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {organizer_token}"})
    new_event = new_event.json()
    new_event_id = new_event["message"]['_id']['$oid']


    attendee_response = client.post("/attendees/loginGoogle", json={"email": "agustina@gmail.com", "name": "agustina segura"})
    attendee_token = attendee_response.json()

    report = {
        "event_id": new_event_id,
        "report_date": datetime.date.today().isoformat(),
        "reason": "seems fake"
    }
    report_event_response = client.post("/attendees/report/event", json=report, headers={"Authorization": f"Bearer {attendee_token}"})
    assert report_event_response.status_code == status.HTTP_201_CREATED, report_event_response.text
    data = report_event_response.json()
    data = data['message']

    assert data['event_id'] == report['event_id']
    assert data['report_date'] == report['report_date']
    assert data['reason'] == report['reason']



@pytest.mark.usefixtures("drop_collection_documents")
def test_whenAUserAlreadyReportedAnExistingEvent_theReportCannotBeCompleted_theAppReturnsError():

    organizer_response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    organizer_token = organizer_response.json()
    new_event = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {organizer_token}"})
    new_event = new_event.json()
    new_event_id = new_event["message"]['_id']['$oid']


    attendee_response = client.post("/attendees/loginGoogle", json={"email": "agustina@gmail.com", "name": "agustina segura"})
    attendee_token = attendee_response.json()

    report = {
        "event_id": new_event_id,
        "report_date": datetime.date.today().isoformat(),
        "reason": "seems fake"
    }

    client.post("/attendees/report/event", json=report, headers={"Authorization": f"Bearer {attendee_token}"})
    report_event_response = client.post("/attendees/report/event", json=report, headers={"Authorization": f"Bearer {attendee_token}"})

    assert report_event_response.status_code == status.HTTP_409_CONFLICT, report_event_response.text
    reponse_text = report_event_response.json()
    reponse_text = reponse_text['detail']

    assert reponse_text == "Este evento ya fue reportado por este usuario"


