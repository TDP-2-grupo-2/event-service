import datetime
from fastapi.testclient import TestClient
from fastapi import status
from event_service.app import app
import pytest
from event_service.utils import jwt_handler
from test import config

session = config.init_postg_db(app)
client = TestClient(app)
events_db = config.init_db()
reports_db = config.init_reports_db()


@pytest.fixture
def drop_collection_documents():
    config.clear_db_draft_event_collection(events_db)
    config.clear_db_events_collection(events_db)
    config.clear_db_reservations_collection(events_db)
    config.clear_db_events_reports_collection(reports_db)

json_rock_music_event = {
            "name": "Music Fest",  "ownerName": "Agustina Segura",  "description": "Musical de pop, rock y mucho más", 
            "location": "Av. Pres. Figueroa Alcorta 7597, C1428 CABA", "locationDescription": "Estadio River", "capacity": 5000, 
            "dateEvent": "2023-07-01", "attendance": 0, "eventType": "SHOW","tags": [ "MUSICA", "DIVERSION" ], "latitud": -34.6274931, 
            "longitud": -68.3252097, "start": "19:00", "end": "23:00", "tags":["DIVERSION"], "faqs": [{'pregunta':'Como llegar?', 'respuesta':'Por medio del colectivo 152'}],
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
def test_WhenTryingToGetAttendeesOrderedByTheAmountOfReports_ThereAreNoReportsYet_ItShouldReturnAnEmptyList():

    admin_login_response = client.post("/admins/login", json={"email":"admin@gmail.com", "password": "admintdp2"})
    admin_login_response = admin_login_response.json()
    admin_token = admin_login_response['message']

    attendees_reports_response = client.get("/admins/reports/attendees", headers={"Authorization": f"Bearer {admin_token}"})

    assert attendees_reports_response.status_code == status.HTTP_200_OK
    reports = attendees_reports_response.json()["message"]

    assert reports == []


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTryingToGetAttendeesOrderedByTheAmountOfReports_OneAttendeeReportedOneTime_ItShouldReturnOneDocument():
    #organizer login create one event
    organizer_response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    organizer_token = organizer_response.json()
    new_event = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {organizer_token}"})
    new_event = new_event.json()
    new_event_id = new_event["message"]['_id']['$oid']


    # attendee login and report
    attendee_response = client.post("/attendees/loginGoogle", json={"email": "agustina@gmail.com", "name": "agustina segura"})
    attendee_token = attendee_response.json()

    report = {
        "event_id": new_event_id,
        "event_name": "Concierto", 
        "event_description": "Concierto de rock",
        "report_date": datetime.date.today().isoformat(),
        "reason": "seems fake",
        "user_email": "agustina@gmail.com", 
        "user_name": "agustina segura",
        "organizer_name": "sol fontenla"
    }

    client.post("/attendees/report/event", json=report, headers={"Authorization": f"Bearer {attendee_token}"})

    # admin login and get reports
    admin_login_response = client.post("/admins/login", json={"email":"admin@gmail.com", "password": "admintdp2"})
    admin_login_response = admin_login_response.json()
    admin_token = admin_login_response['message']

    attendees_reports_response = client.get("/admins/reports/attendees", headers={"Authorization": f"Bearer {admin_token}"})

    assert attendees_reports_response.status_code == status.HTTP_200_OK
    reports = attendees_reports_response.json()["message"]
    
    assert len(reports) == 1
    assert reports[0]['user_email'] == 'agustina@gmail.com'
    assert reports[0]['user_name'] == 'agustina segura'
    assert reports[0]['most_frecuent_reason'] == 'seems fake'
    assert reports[0]['amount_of_reports'] == 1


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTryingToGetAttendeesOrderedByTheAmountOfReports_OneAttendeeReportedThreeEvents_ItShouldReturnOneDocument():
    #organizer login create one event
    organizer_response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    organizer_token = organizer_response.json()
    first_new_event = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {organizer_token}"})
    second_new_event = client.post("/organizers/active_events", json=json_lollapalooza_first_date, headers={"Authorization": f"Bearer {organizer_token}"})
    third_new_event = client.post("/organizers/active_events", json=json_theatre_event, headers={"Authorization": f"Bearer {organizer_token}"})

    first_new_event_id = first_new_event.json()["message"]['_id']['$oid']
    second_new_event_id = second_new_event.json()["message"]['_id']['$oid']
    third_new_event_id = third_new_event.json()["message"]['_id']['$oid']


    # attendee login and report
    attendee_response = client.post("/attendees/loginGoogle", json={"email": "agustina@gmail.com", "name": "agustina segura"})
    attendee_token = attendee_response.json()

    report1 = {
        "event_id": first_new_event_id,
        "event_name": "Concierto", 
        "event_description": "Concierto de rock",
        "report_date": datetime.date.today().isoformat(),
        "reason": "seems fake",
        "user_email": "agustina@gmail.com", 
        "user_name": "agustina segura",
        "organizer_name": "sol fontenla"
    }

    report2 = {
        "event_id": second_new_event_id,
        "event_name": "lollapalooza", 
        "event_description": "Veni a disfrutar del primer dia de esta nueva edición",
        "report_date": datetime.date.today().isoformat(),
        "reason": "seems fake",
        "user_email": "agustina@gmail.com", 
        "user_name": "agustina segura",
        "organizer_name": "sol fontenla"
    }

    report3 = {
        "event_id": third_new_event_id,
        "event_name": "Tootsie" , 
        "event_description": "La comedia del 2023",
        "report_date": datetime.date.today().isoformat(),
        "reason": "spam",
        "user_email": "agustina@gmail.com", 
        "user_name": "agustina segura",
        "organizer_name": "sol fontenla"
    }

    client.post("/attendees/report/event", json=report1, headers={"Authorization": f"Bearer {attendee_token}"})
    client.post("/attendees/report/event", json=report2, headers={"Authorization": f"Bearer {attendee_token}"})
    client.post("/attendees/report/event", json=report3, headers={"Authorization": f"Bearer {attendee_token}"})


    # admin login and get reports
    admin_login_response = client.post("/admins/login", json={"email":"admin@gmail.com", "password": "admintdp2"})
    admin_login_response = admin_login_response.json()
    admin_token = admin_login_response['message']

    attendees_reports_response = client.get("/admins/reports/attendees", headers={"Authorization": f"Bearer {admin_token}"})

    assert attendees_reports_response.status_code == status.HTTP_200_OK
    reports = attendees_reports_response.json()["message"]
    
    assert len(reports) == 1
    assert reports[0]['user_email'] == 'agustina@gmail.com'
    assert reports[0]['user_name'] == 'agustina segura'
    assert reports[0]['most_frecuent_reason'] == 'seems fake'
    assert reports[0]['amount_of_reports'] == 3



@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTryingToGetAttendeesOrderedByTheAmountOfReports_TwoAttendeesReportedThreeEvents_ItShouldReturnOneDocument():
    #organizer login create one event
    organizer_response = client.post("/organizers/loginGoogle", json={"email": "solfontenla@gmail.com", "name": "sol fontenla"})
    organizer_token = organizer_response.json()
    first_new_event = client.post("/organizers/active_events", json=json_rock_music_event, headers={"Authorization": f"Bearer {organizer_token}"})
    second_new_event = client.post("/organizers/active_events", json=json_lollapalooza_first_date, headers={"Authorization": f"Bearer {organizer_token}"})
    third_new_event = client.post("/organizers/active_events", json=json_theatre_event, headers={"Authorization": f"Bearer {organizer_token}"})

    first_new_event_id = first_new_event.json()["message"]['_id']['$oid']
    second_new_event_id = second_new_event.json()["message"]['_id']['$oid']
    third_new_event_id = third_new_event.json()["message"]['_id']['$oid']


    # attendee login and report
    first_attendee_response = client.post("/attendees/loginGoogle", json={"email": "agustina@gmail.com", "name": "agustina segura"})
    first_attendee_token = first_attendee_response.json()

    second_attendee_response = client.post("/attendees/loginGoogle", json={"email": "mariaperez@gmail.com", "name": "Maria Perez"})
    second_attendee_token = second_attendee_response.json()


    report1 = {
        "event_id": first_new_event_id,
        "event_name": "Concierto", 
        "event_description": "Concierto de rock",
        "report_date": datetime.date.today().isoformat(),
        "reason": "seems fake",
        "user_email": "mariaperez@gmail.com", 
        "user_name": "Maria Perez",
        "organizer_name": "sol fontenla"
    }

    report2 = {
        "event_id": second_new_event_id,
        "event_name": "lollapalooza", 
        "event_description": "Veni a disfrutar del primer dia de esta nueva edición",
        "report_date": datetime.date.today().isoformat(),
        "reason": "seems fake",
        "user_email": "agustina@gmail.com", 
        "user_name": "agustina segura",
        "organizer_name": "sol fontenla"
    }

    report3 = {
        "event_id": third_new_event_id,
        "event_name": "Tootsie" , 
        "event_description": "La comedia del 2023",
        "report_date": datetime.date.today().isoformat(),
        "reason": "spam",
        "user_email": "agustina@gmail.com", 
        "user_name": "agustina segura",
        "organizer_name": "sol fontenla"
    }

    client.post("/attendees/report/event", json=report1, headers={"Authorization": f"Bearer {second_attendee_token}"})
    client.post("/attendees/report/event", json=report2, headers={"Authorization": f"Bearer {first_attendee_token}"})
    client.post("/attendees/report/event", json=report3, headers={"Authorization": f"Bearer {first_attendee_token}"})


    # admin login and get reports
    admin_login_response = client.post("/admins/login", json={"email":"admin@gmail.com", "password": "admintdp2"})
    admin_login_response = admin_login_response.json()
    admin_token = admin_login_response['message']

    attendees_reports_response = client.get("/admins/reports/attendees", headers={"Authorization": f"Bearer {admin_token}"})
    
    assert attendees_reports_response.status_code == status.HTTP_200_OK
    reports = attendees_reports_response.json()["message"]
    print('reporteees', reports)
    assert len(reports) == 2
    assert reports[0]['user_email'] == 'agustina@gmail.com'
    assert reports[0]['user_name'] == 'agustina segura'
    assert reports[0]['amount_of_reports'] == 2
    assert reports[1]['user_email'] == 'mariaperez@gmail.com'
    assert reports[1]['user_name'] == 'Maria Perez'
    assert reports[1]['most_frecuent_reason'] == 'seems fake'
    assert reports[1]['amount_of_reports'] == 1