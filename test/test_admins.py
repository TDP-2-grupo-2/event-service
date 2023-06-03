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
reports_db = config.init_reports_db(app)


@pytest.fixture
def drop_collection_documents():
    config.clear_db_draft_event_collection(events_db)
    config.clear_db_events_collection(events_db)
    config.clear_db_reservations_collection(events_db)
    config.clear_db_events_reports_collection(reports_db)
    config.clear_postgres_db(session)

@pytest.fixture
def drop_users_only():
    config.clear_postgres_db(session)


def login_attendee(email, name): 
    attendee_response = client.post("/attendees/loginGoogle", json={"email": email, "name": name})
    return attendee_response.json()

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

json_programming_event = {
            "name": "Aprendé a programar en python!",  "ownerName": "Sol Fontenla",  "description": "Aprende a programar en python desde cero",
            "location": "Av. Paseo Colón 850, C1063 CABA",
            "locationDescription": "Facultad de Ingenieria - UBA", "capacity": 100, "dateEvent": "2023-08-07", "attendance": 0, "eventType": "TECNOLOGIA",
            "tags": [ "PROGRAMACION", "APRENDIZAJE", ], "latitud": 8.9, "longitud": 6.8, "start": "21:00", "end": "22:30" }


json_theatre_event = {
            "name": "Tootsie",  "ownerName": "Nico Vazquez",  "description": "La comedia del 2023",
            "location": "Av. Corrientes 1280, C1043AAZ CABA", "locationDescription": "Teatro Lola Membrives", 
            "capacity": 400, "dateEvent": "2023-10-30", "attendance": 0, "eventType": "TEATRO", 
            "tags": [ "COMEDIA", "FAMILIAR", "ENTRETENIMIENTO" ], "latitud": -34.6019915, "longitud": -58.3711065, "start": "21:00", "end": "22:30" }

def admin_login():
    admin_login_response = client.post("/admins/login", json={"email":"admin@gmail.com", "password": "admintdp2"})
    admin_login_response = admin_login_response.json()
    return admin_login_response['message']

def create_event(event_json, organizer_token):
    new_event = client.post("/organizers/active_events", json=event_json, headers={"Authorization": f"Bearer {organizer_token}"})
    return new_event.json()['message']

def login_organizer(organizer_email, organizer_name):
    organizer = client.post("/organizers/loginGoogle", json={"email": organizer_email, "name": organizer_name})
    return organizer.json()


@pytest.mark.usefixtures("drop_users_only")
def test_when_admin_login_with_correct_email_and_password_it_should_allow_it():

    response = client.post("/admins/login", json={"email":"admin@gmail.com", "password": "admintdp2"})

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    data = data['message']
    info = jwt_handler.decode_token(data)

    assert info['id'] == 0
    assert info['rol'] == 'admin'

@pytest.mark.usefixtures("drop_users_only")
def test_when_admin_login_with_incorrect_email_it_not_should_allow_it():

    response = client.post("/admins/login", json={"email":"aaadmiin@gmail.com", "password": "admintdp2"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    data = response.json()

    assert data['detail'] == "El usuario/contraseña es incorrecta"

@pytest.mark.usefixtures("drop_users_only")
def test_when_admin_login_with_incorrect_password_it_not_should_allow_it():

    response = client.post("/admins/login", json={"email":"admin@gmail.com", "password": "adminnntdpp2"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    data = response.json()

    assert data['detail'] == "El usuario/contraseña es incorrecta"


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTryingToSuspendAnEvent_TheUserSuspendingTheEventIsNotAdmin_ItShouldReturnError():
    organizer_token = login_organizer("solfontenla@gmail.com", "sol fontenla")
    new_event = create_event(json_rock_music_event, organizer_token)

    another_user_token = login_organizer("agussegura@gmail.com", "Agus Segura")

    new_event_id = new_event['_id']['$oid']

    response_to_cancel = client.patch(f"/admins/suspended_events/{new_event_id}?motive=SPAM", headers={"Authorization": f"Bearer {another_user_token}"})
    assert response_to_cancel.status_code == status.HTTP_401_UNAUTHORIZED, response_to_cancel.text
    data = response_to_cancel.json()
    
    assert data["detail"] == "El usuario no esta autorizado"



@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTryingToSuspendAnActiveEvent_TheUserSuspendingTheEventIsAdmin_ItShouldSuspendTheEvent():
    organizer_token = login_organizer("solfontenla@gmail.com", "sol fontenla")

    new_event = create_event(json_rock_music_event, organizer_token)

    admin_token = admin_login()

    new_event_id = new_event['_id']['$oid']
    motive="SPAM"
    response_to_suspend = client.patch(f"/admins/suspended_events/{new_event_id}?motive={motive}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response_to_suspend.status_code == status.HTTP_200_OK
    response_to_suspend = response_to_suspend.json()["message"]
    assert response_to_suspend['_id']['$oid'] == new_event_id
    assert response_to_suspend['status'] == 'suspended'
    assert response_to_suspend['suspendMotive'] == motive


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTryingToGetAttendeesOrderedByTheAmountOfReports_ThereAreNoReportsYet_ItShouldReturnAnEmptyList():
    
    admin_token = admin_login()

    attendees_reports_response = client.get("/admins/reports/attendees", headers={"Authorization": f"Bearer {admin_token}"})

    assert attendees_reports_response.status_code == status.HTTP_200_OK
    reports = attendees_reports_response.json()["message"]

    assert reports == []


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTryingToGetAttendeesOrderedByTheAmountOfReports_OneAttendeeReportedOneTime_ItShouldReturnOneDocument():
    #organizer login create one event
    organizer_token = login_organizer("solfontenla@gmail.com", "sol fontenla")
    new_event = create_event(json_rock_music_event, organizer_token)

    new_event_id = new_event['_id']['$oid']


    # attendee login and report
    attendee_token = login_attendee("agustina@gmail.com", "agustina segura")

    report = {
        "event_id": new_event_id,
        "reason": "seems fake",
    }

    client.post("/attendees/report/event", json=report, headers={"Authorization": f"Bearer {attendee_token}"})

    # admin login and get reports
    admin_token = admin_login()

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
    organizer_token = login_organizer("solfontenla@gmail.com", "sol fontenla")

    first_new_event = create_event(json_rock_music_event, organizer_token)
    second_new_event = create_event(json_lollapalooza_first_date, organizer_token)
    third_new_event = create_event(json_theatre_event, organizer_token)

    first_new_event_id = first_new_event['_id']['$oid']
    second_new_event_id = second_new_event['_id']['$oid']
    third_new_event_id = third_new_event['_id']['$oid']


    # attendee login and report
    attendee_token = login_attendee("agustina@gmail.com", "agustina segura")

    report1 = {
        "event_id": first_new_event_id,
        "reason": "seems fake",
    }

    report2 = {
        "event_id": second_new_event_id,
        "reason": "seems fake",
    }

    report3 = {
        "event_id": third_new_event_id,
        "reason": "spam",
    }

    client.post("/attendees/report/event", json=report1, headers={"Authorization": f"Bearer {attendee_token}"})
    client.post("/attendees/report/event", json=report2, headers={"Authorization": f"Bearer {attendee_token}"})
    client.post("/attendees/report/event", json=report3, headers={"Authorization": f"Bearer {attendee_token}"})


    # admin login and get reports
    admin_token = admin_login()

    attendees_reports_response = client.get("/admins/reports/attendees", headers={"Authorization": f"Bearer {admin_token}"})

    assert attendees_reports_response.status_code == status.HTTP_200_OK
    reports = attendees_reports_response.json()["message"]
    
    assert len(reports) == 1
    assert reports[0]['user_email'] == 'agustina@gmail.com'
    assert reports[0]['user_name'] == 'agustina segura'
    assert reports[0]['most_frecuent_reason'] == "seems fake"
    assert reports[0]['amount_of_reports'] == 3



@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTryingToGetAttendeesOrderedByTheAmountOfReports_TwoAttendeesReportedThreeEvents_ItShouldReturnTwoDocuments():
    #organizer login create one event
    organizer_token = login_organizer("solfontenla@gmail.com", "sol fontenla")
    first_new_event = create_event(json_rock_music_event, organizer_token)
    second_new_event = create_event(json_lollapalooza_first_date, organizer_token)
    third_new_event = create_event(json_theatre_event, organizer_token)

    first_new_event_id = first_new_event['_id']['$oid']
    second_new_event_id = second_new_event['_id']['$oid']
    third_new_event_id = third_new_event['_id']['$oid']


    # attendee login and report
    first_attendee_token = login_attendee("agustina@gmail.com", "agustina segura")
    second_attendee_token = login_attendee("mariaperez@gmail.com", "Maria Perez")


    report1 = {
        "event_id": first_new_event_id,
        "reason": "seems fake",
    }

    report2 = {
        "event_id": second_new_event_id,
        "reason": "seems fake",
    }

    report3 = {
        "event_id": third_new_event_id,
        "reason": "spam",
    }

    client.post("/attendees/report/event", json=report1, headers={"Authorization": f"Bearer {second_attendee_token}"})
    client.post("/attendees/report/event", json=report2, headers={"Authorization": f"Bearer {first_attendee_token}"})
    client.post("/attendees/report/event", json=report3, headers={"Authorization": f"Bearer {first_attendee_token}"})


    # admin login and get reports
    admin_token = admin_login()

    attendees_reports_response = client.get("/admins/reports/attendees", headers={"Authorization": f"Bearer {admin_token}"})
    
    assert attendees_reports_response.status_code == status.HTTP_200_OK
    reports = attendees_reports_response.json()["message"]

    assert len(reports) == 2
    assert reports[0]['user_email'] == 'agustina@gmail.com'
    assert reports[0]['user_name'] == 'agustina segura'
    assert reports[0]['amount_of_reports'] == 2
    assert reports[1]['user_email'] == 'mariaperez@gmail.com'
    assert reports[1]['user_name'] == 'Maria Perez'
    assert reports[1]['most_frecuent_reason'] == 'seems fake'
    assert reports[1]['amount_of_reports'] == 1


 

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTryingToGetAttendeesOrderedByTheAmountOfReports_OneAttendeeReportedOneTime_ItShouldReturnOneDocument():
    #organizer login create one event
    organizer_token = login_organizer("solfontenla@gmail.com", "sol fontenla")
    new_event = create_event(json_rock_music_event, organizer_token)
    new_event_id = new_event['_id']['$oid']

    # attendee login and report
    attendee_token = login_attendee("agustina@gmail.com", "agustina segura")

    report = {
        "event_id": new_event_id,
        "reason": "seems fake",
    }

    client.post("/attendees/report/event", json=report, headers={"Authorization": f"Bearer {attendee_token}"})

    # admin login and get reports
    admin_token = admin_login()

    attendees_reports_response = client.get("/admins/reports/attendees", headers={"Authorization": f"Bearer {admin_token}"})

    assert attendees_reports_response.status_code == status.HTTP_200_OK
    reports = attendees_reports_response.json()["message"]
    
    assert len(reports) == 1
    assert reports[0]['user_email'] == 'agustina@gmail.com'
    assert reports[0]['user_name'] == 'agustina segura'
    assert reports[0]['most_frecuent_reason'] == 'seems fake'
    assert reports[0]['amount_of_reports'] == 1


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTryingToGetAttendeesOrderedByTheAmountOfReportsInDateRange_OneAttendeeReportedThreeEvents_ItShouldReturnOneDocument():
    #organizer login create one event
    organizer_token = login_organizer("solfontenla@gmail.com", "sol fontenla")
    first_new_event = create_event(json_rock_music_event, organizer_token)
    second_new_event = create_event(json_lollapalooza_first_date, organizer_token)
    third_new_event = create_event(json_theatre_event, organizer_token)

    first_new_event_id = first_new_event['_id']['$oid']
    second_new_event_id = second_new_event['_id']['$oid']
    third_new_event_id = third_new_event['_id']['$oid']


    # attendee login and report
    attendee_token = login_attendee("agustina@gmail.com", "agustina segura")

    yesterday = (datetime.date.today() + datetime.timedelta(days=-1)).isoformat()
    today = datetime.date.today().isoformat()
    three_days_from_today = (datetime.date.today() + datetime.timedelta(days=3)).isoformat()

    report1 = {
        "event_id": first_new_event_id,
        "reason": "seems fake",
    }

    report2 = {
        "event_id": second_new_event_id,
        "reason": "seems fake",
    }

    report3 = {
        "event_id": third_new_event_id,
        "reason": "spam",
    }

    client.post("/attendees/report/event", json=report1, headers={"Authorization": f"Bearer {attendee_token}"})
    client.post("/attendees/report/event", json=report2, headers={"Authorization": f"Bearer {attendee_token}"})
    client.post("/attendees/report/event", json=report3, headers={"Authorization": f"Bearer {attendee_token}"})


    # admin login and get reports
    admin_token = admin_login()

    attendees_reports_response = client.get("/admins/reports/attendees", params={"from_date": yesterday, "to_date": today}, headers={"Authorization": f"Bearer {admin_token}"})

    assert attendees_reports_response.status_code == status.HTTP_200_OK
    reports = attendees_reports_response.json()["message"]
    
    assert len(reports) == 1
    assert reports[0]['user_email'] == 'agustina@gmail.com'
    assert reports[0]['user_name'] == 'agustina segura'
    assert reports[0]['amount_of_reports'] == 3


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTryingToGetAttendeesOrderedByTheAmountOfReportsFromCertainDate_OneAttendeeReportedThreeEvents_ItShouldReturnOneDocument():
    #organizer login create one event
    organizer_token = login_organizer("solfontenla@gmail.com", "sol fontenla")
    first_new_event = create_event(json_rock_music_event, organizer_token)
    second_new_event = create_event(json_lollapalooza_first_date, organizer_token)
    third_new_event = create_event(json_theatre_event, organizer_token)

    first_new_event_id = first_new_event['_id']['$oid']
    second_new_event_id = second_new_event['_id']['$oid']
    third_new_event_id = third_new_event['_id']['$oid']


    # attendee login and report
    attendee_token = login_attendee("agustina@gmail.com", "agustina segura")

    yesterday = (datetime.date.today() + datetime.timedelta(days=-1)).isoformat()
    today = datetime.date.today().isoformat()
    three_days_from_today = (datetime.date.today() + datetime.timedelta(days=3)).isoformat()

    report1 = {
        "event_id": first_new_event_id,
        "reason": "seems fake",
    }

    report2 = {
        "event_id": second_new_event_id,
        "reason": "seems fake",
    }

    report3 = {
        "event_id": third_new_event_id,
        "reason": "spam",
    }

    client.post("/attendees/report/event", json=report1, headers={"Authorization": f"Bearer {attendee_token}"})
    client.post("/attendees/report/event", json=report2, headers={"Authorization": f"Bearer {attendee_token}"})
    client.post("/attendees/report/event", json=report3, headers={"Authorization": f"Bearer {attendee_token}"})


    # admin login and get reports
    admin_token = admin_login()

    attendees_reports_response = client.get("/admins/reports/attendees", params={"from_date": yesterday}, headers={"Authorization": f"Bearer {admin_token}"})

    assert attendees_reports_response.status_code == status.HTTP_200_OK
    reports = attendees_reports_response.json()["message"]
    
    assert len(reports) == 1
    assert reports[0]['user_email'] == 'agustina@gmail.com'
    assert reports[0]['user_name'] == 'agustina segura'
    assert reports[0]['most_frecuent_reason'] == 'seems fake'
    assert reports[0]['amount_of_reports'] == 3



@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenTryingToGetAttendeesOrderedByTheAmountOfReportsUpToCertainDate_OneAttendeeReportedThreeEvents_ItShouldReturnOneDocument():
    #organizer login create one event
    organizer_token = login_organizer("solfontenla@gmail.com", "sol fontenla")
    first_new_event = create_event(json_rock_music_event, organizer_token)
    second_new_event = create_event(json_lollapalooza_first_date, organizer_token)
    third_new_event = create_event(json_theatre_event, organizer_token)

    first_new_event_id = first_new_event['_id']['$oid']
    second_new_event_id = second_new_event['_id']['$oid']
    third_new_event_id = third_new_event['_id']['$oid']


    # attendee login and report
    attendee_token = login_attendee("agustina@gmail.com", "agustina segura")

    yesterday = (datetime.date.today() + datetime.timedelta(days=-1)).isoformat()
    today = datetime.date.today().isoformat()
    three_days_from_today = (datetime.date.today() + datetime.timedelta(days=3)).isoformat()

    report1 = {
        "event_id": first_new_event_id,
        "reason": "seems fake",
    }

    report2 = {
        "event_id": second_new_event_id,
        "reason": "seems fake",
    }

    report3 = {
        "event_id": third_new_event_id,
        "reason": "spam",
    }

    client.post("/attendees/report/event", json=report1, headers={"Authorization": f"Bearer {attendee_token}"})
    client.post("/attendees/report/event", json=report2, headers={"Authorization": f"Bearer {attendee_token}"})
    client.post("/attendees/report/event", json=report3, headers={"Authorization": f"Bearer {attendee_token}"})


    # admin login and get reports
    admin_token = admin_login()

    attendees_reports_response = client.get("/admins/reports/attendees", params={"to_date": today}, headers={"Authorization": f"Bearer {admin_token}"})

    assert attendees_reports_response.status_code == status.HTTP_200_OK
    reports = attendees_reports_response.json()["message"]
    
    assert len(reports) == 1
    assert reports[0]['user_email'] == 'agustina@gmail.com'
    assert reports[0]['user_name'] == 'agustina segura'
    assert reports[0]['amount_of_reports'] == 3




@pytest.mark.usefixtures("drop_collection_documents")
def test_when_an_admin_is_trying_to_susped_an_organizer_tha_not_exits_then_it_should_not_suspend_the_organizer():
    admin_token = admin_login()

    blockResponse = client.patch(f"/admins/suspended_organizers/100",headers={"Authorization": f"Bearer {admin_token}"})

    assert blockResponse.status_code == status.HTTP_404_NOT_FOUND
    blockResponse = blockResponse.json()
    assert blockResponse['detail'] == "El usuario no existe"


@pytest.mark.usefixtures("drop_collection_documents")
def test_When_getting_events_ordered_by_the_amount_of_reports_with_no_reports_then_it_should_return_an_empty_list():
    admin_token = admin_login()

    attendees_reports_response = client.get("/admins/reports/events", headers={"Authorization": f"Bearer {admin_token}"})

    assert attendees_reports_response.status_code == status.HTTP_200_OK
    reports = attendees_reports_response.json()["message"]

    assert reports == []


@pytest.mark.usefixtures("drop_collection_documents")
def test_when_getting_events_reported_with_one_report_then_it_should_return_it():
   
    organizer_token = login_organizer("solfontenla@gmail.com", "sol fontenla")
    new_event = create_event(json_rock_music_event, organizer_token)
    new_event_id = new_event['_id']['$oid']

    attendee_token = login_attendee("agustina@gmail.com", "agustina segura")

    report = {
        "event_id": new_event_id,
        "reason": "seems fake",
    }

    client.post("/attendees/report/event", json=report, headers={"Authorization": f"Bearer {attendee_token}"})

    admin_token = admin_login()

    events_reports_response = client.get("/admins/reports/events", headers={"Authorization": f"Bearer {admin_token}"})

    assert events_reports_response.status_code == status.HTTP_200_OK
    reports = events_reports_response.json()["message"]
    
    assert len(reports) == 1
    assert reports[0]['event_id'] == new_event_id
    assert reports[0]['event_name'] == json_rock_music_event['name']
    assert reports[0]['event_description'] == json_rock_music_event['description']
    assert reports[0]['organizer_name'] == json_rock_music_event['ownerName']
    assert reports[0]['organizer_id'] == 1
    assert reports[0]['most_frecuent_reason'] == 'seems fake'
    assert reports[0]['amount_of_reports'] == 1

@pytest.mark.usefixtures("drop_collection_documents")
def test_when_event_get_3_reports_it_should_return_the_event_with_amount_report_3_and_the_most_frecuent_reason():
    organizer_token = login_organizer("solfontenla@gmail.com", "sol fontenla")
    new_event = create_event(json_rock_music_event, organizer_token)
    new_event_id = new_event['_id']['$oid']

    first_attendee_token = login_attendee("agustina@gmail.com", "agustina segura")

    report = {
        "event_id": new_event_id,
        "reason": "seems fake",
    }
    client.post("/attendees/report/event", json=report, headers={"Authorization": f"Bearer {first_attendee_token}"})

    second_attendee_token = login_attendee("rama@gmail.com", "rama sanchez")
    report = {
        "event_id": new_event_id,
        "reason": "spam",
    }
    client.post("/attendees/report/event", json=report, headers={"Authorization": f"Bearer {second_attendee_token}"})

    third_attendee_token = login_attendee("pedro@gmail.com", "pedro sanchez")

    report = {
        "event_id": new_event_id,
        "reason": "spam",
    }
    client.post("/attendees/report/event", json=report, headers={"Authorization": f"Bearer {third_attendee_token}"})

    admin_token = admin_login()

    events_reports_response = client.get("/admins/reports/events", headers={"Authorization": f"Bearer {admin_token}"})

    assert events_reports_response.status_code == status.HTTP_200_OK
    reports = events_reports_response.json()["message"]

    assert len(reports) == 1
    assert reports[0]['event_id'] == new_event_id
    assert reports[0]['event_name'] == json_rock_music_event['name']
    assert reports[0]['event_description'] == json_rock_music_event['description']
    assert reports[0]['organizer_name'] == json_rock_music_event['ownerName']
    assert reports[0]['organizer_id'] == 1
    assert reports[0]['most_frecuent_reason'] == 'spam'
    assert reports[0]['amount_of_reports'] == 3


@pytest.mark.usefixtures("drop_collection_documents")
def test_when_organizer_gets_4_reports_for_2_events_getting_reported_events__should_return_the_events_in_the_right_order():
    organizer_token = login_organizer("solfontenla@gmail.com", "sol fontenla")

    new_event = create_event(json_lollapalooza_first_date, organizer_token)
    new_event_id = new_event['_id']['$oid']

    other_event = create_event(json_programming_event, organizer_token)
    other_event_id = other_event['_id']['$oid']

    first_attendee_token = login_attendee("agustina@gmail.com", "agustina segura")
    report1 = {
        "event_id": new_event_id,
        "reason": "seems fake",
    }

    report2 = {
        "event_id": other_event_id,
        "reason": "seems fake",
    }
    client.post("/attendees/report/event", json=report1, headers={"Authorization": f"Bearer {first_attendee_token}"})
    client.post("/attendees/report/event", json=report2, headers={"Authorization": f"Bearer {first_attendee_token}"})
    second_attendee_token = login_attendee("rama@gmail.com", "rama sanchez")

    report3 = {
        "event_id": new_event_id,
        "reason": "spam",
    }
    client.post("/attendees/report/event", json=report3, headers={"Authorization": f"Bearer {second_attendee_token}"})
    
    third_attendee_token = login_attendee("pedro@gmail.com", "pedro sanchez")
    
    report4 = {
        "event_id": new_event_id,
        "reason": "spam",
    }
    client.post("/attendees/report/event", json=report4, headers={"Authorization": f"Bearer {third_attendee_token}"})

    admin_token = admin_login()

    events_reports_response = client.get("/admins/reports/events", headers={"Authorization": f"Bearer {admin_token}"})

    assert events_reports_response.status_code == status.HTTP_200_OK
    reports = events_reports_response.json()["message"]
    

    assert len(reports) == 2
    assert reports[0]['event_id'] == new_event_id
    assert reports[0]['event_name'] == json_lollapalooza_first_date['name']
    assert reports[0]['event_description'] == json_lollapalooza_first_date['description']
    assert reports[0]['organizer_name'] == json_lollapalooza_first_date['ownerName']
    assert reports[0]['organizer_id'] == 1
    assert reports[0]['most_frecuent_reason'] == 'spam'
    assert reports[0]['amount_of_reports'] == 3
    assert reports[1]['event_id'] == other_event_id
    assert reports[1]['event_name'] == json_programming_event['name']
    assert reports[1]['event_description'] == json_programming_event['description']
    assert reports[1]['organizer_name'] == json_programming_event['ownerName']
    assert reports[1]['organizer_id'] == 1
    assert reports[1]['most_frecuent_reason'] == 'seems fake'
    assert reports[1]['amount_of_reports'] == 1


@pytest.mark.usefixtures("drop_collection_documents")
def test_when_suspending_a_Reported_event_then_it_should_not_apper_in_repported_events():
    organizer_token = login_organizer("solfontenla@gmail.com", "sol fontenla")
    new_event = create_event(json_rock_music_event, organizer_token)
    new_event_id = new_event['_id']['$oid']
    attendee_token = login_attendee("agustina@gmail.com", "agustina segura")

    report = {
        "event_id": new_event_id,
        "reason": "seems fake",
    }

    todays_date = datetime.date.today().isoformat()

    client.post("/attendees/report/event", json=report, headers={"Authorization": f"Bearer {attendee_token}"})

    admin_token = admin_login()

    events_reports_response = client.get(f"/admins/reports/events?from_date=2023-04-24&to_date={todays_date}", headers={"Authorization": f"Bearer {admin_token}"})

    assert events_reports_response.status_code == status.HTTP_200_OK
    reports = events_reports_response.json()["message"]
    
    assert len(reports) == 1
    response_to_cancel = client.patch(f"/admins/suspended_events/{new_event_id}?motive=SPAM", headers={"Authorization": f"Bearer {admin_token}"})
    
    assert response_to_cancel.status_code == status.HTTP_200_OK
    events_reports_response = client.get("/admins/reports/events?from_date=2023-04-24&to_date=2023-05-14", headers={"Authorization": f"Bearer {admin_token}"})

    assert events_reports_response.status_code == status.HTTP_200_OK
    reports = events_reports_response.json()["message"]
    
    assert len(reports) == 0


@pytest.mark.usefixtures("drop_collection_documents")
def test_when_suspending_one_of_two_Reported_event_then_it_should_not_apper_in_repported_events():
    organizer_token = login_organizer("solfontenla@gmail.com", "sol fontenla")
    
    event_1 = create_event(json_rock_music_event, organizer_token)
    event_1_id = event_1['_id']['$oid']
    event_2 = create_event(json_lollapalooza_first_date, organizer_token)
    event_id_2 = event_2['_id']['$oid']

    attendee_token = login_attendee("agustina@gmail.com", "agustina segura")
    todays_date = datetime.date.today().isoformat()


    report = {
        "event_id": event_1_id,
        "reason": "seems fake",
    }
    client.post("/attendees/report/event", json=report, headers={"Authorization": f"Bearer {attendee_token}"})
    report2 = {
        "event_id":event_id_2,
        "reason": "seems fake",
    }
    client.post("/attendees/report/event", json=report2, headers={"Authorization": f"Bearer {attendee_token}"})
    admin_token = admin_login()
    events_reports_response = client.get(f"/admins/reports/events?from_date=2023-04-24&to_date={todays_date}", headers={"Authorization": f"Bearer {admin_token}"})

    assert events_reports_response.status_code == status.HTTP_200_OK
    reports = events_reports_response.json()["message"]
    
    assert len(reports) == 2
    response_to_cancel = client.patch(f"/admins/suspended_events/{event_1_id}?motive=seems fake", headers={"Authorization": f"Bearer {admin_token}"})
    
    assert response_to_cancel.status_code == status.HTTP_200_OK
    events_reports_response = client.get("/admins/reports/events", headers={"Authorization": f"Bearer {admin_token}"})
    assert events_reports_response.status_code == status.HTTP_200_OK
    reports = events_reports_response.json()["message"]

    assert len(reports) == 1
    
@pytest.mark.usefixtures("drop_collection_documents")
def test_when_suspending_an_organizer_then_it_should_not_appear_in_repported_events():
    organizer_token = login_organizer("solfontenla@gmail.com", "sol fontenla")
    todays_date = datetime.date.today().isoformat()

    organizer_id = jwt_handler.decode_token(organizer_token)['id']
    event_1 = create_event(json_rock_music_event, organizer_token)
    event_1_id = event_1['_id']['$oid']
    event_2 = create_event(json_lollapalooza_first_date, organizer_token)
    event_id_2 = event_2['_id']['$oid']
    attendee_token = login_attendee("agustina@gmail.com", "agustina segura")

    report = {
        "event_id": event_1_id,
        "reason": "seems fake",
    }
    client.post("/attendees/report/event", json=report, headers={"Authorization": f"Bearer {attendee_token}"})
    report2 = {
        "event_id":event_id_2,
        "reason": "seems fake",
    }
    client.post("/attendees/report/event", json=report2, headers={"Authorization": f"Bearer {attendee_token}"})
    admin_token = admin_login()
    events_reports_response = client.get(f"/admins/reports/events?from_date=2023-04-24&to_date={todays_date}", headers={"Authorization": f"Bearer {admin_token}"})

    assert events_reports_response.status_code == status.HTTP_200_OK
    reports = events_reports_response.json()["message"]
    
    assert len(reports) == 2
    response_to_cancel = client.patch(f"/admins/suspended_organizers/{organizer_id}", headers={"Authorization": f"Bearer {admin_token}"})
    
    assert response_to_cancel.status_code == status.HTTP_200_OK
    data = response_to_cancel.json()
    events_reports_response = client.get(f"/admins/reports/events?from_date=2023-04-24&to_date={todays_date}", headers={"Authorization": f"Bearer {admin_token}"})

    assert events_reports_response.status_code == status.HTTP_200_OK
    reports = events_reports_response.json()["message"]
    
    assert len(reports) == 0

@pytest.mark.usefixtures("drop_collection_documents")
def test_when_getting_reported_events_by_date_from_and_to_it_should_return_the_correct_ones():
    organizer_token = login_organizer("solfontenla@gmail.com", "sol fontenla")
    new_event = create_event(json_rock_music_event, organizer_token)
    new_event_id = new_event['_id']['$oid']
    first_attendee_token = login_attendee("agustina@gmail.com", "agustina segura")
    report = {
        "event_id": new_event_id,
        "reason": "seems fake",
    }
    client.post("/attendees/report/event", json=report, headers={"Authorization": f"Bearer {first_attendee_token}"})
    second_attendee_token = login_attendee("rama@gmail.com", "rama sanchez")
    report = {
        "event_id": new_event_id,
        "reason": "spam",
    }
    client.post("/attendees/report/event", json=report, headers={"Authorization": f"Bearer {second_attendee_token}"})
    third_attendee_token = login_attendee("pedro@gmail.com", "pedro sanchez")
    report = {
        "event_id": new_event_id,
        "reason": "spam",
    }
    client.post("/attendees/report/event", json=report, headers={"Authorization": f"Bearer {third_attendee_token}"})
    admin_token = admin_login()

    todays_date = datetime.date.today().isoformat()

    events_reports_response = client.get(f"/admins/reports/events?from_date=2023-04-24&to_date={todays_date}", headers={"Authorization": f"Bearer {admin_token}"})
    assert events_reports_response.status_code == status.HTTP_200_OK
    reports = events_reports_response.json()["message"]

    assert len(reports) == 1
    assert reports[0]['event_id'] == new_event_id
    assert reports[0]['event_name'] == 'Music Fest'
    assert reports[0]['event_description'] == "Musical de pop, rock y mucho más"
    assert reports[0]['organizer_name'] == "Agustina Segura"
    assert reports[0]['organizer_id'] == 1
    assert reports[0]['most_frecuent_reason'] == 'spam'
    assert reports[0]['amount_of_reports'] == 3

@pytest.mark.usefixtures("drop_collection_documents")
def test_when_getting_reported_events_by_date_from_should_return_the_correct_ones():
    organizer_token = login_organizer("solfontenla@gmail.com", "sol fontenla")
    new_event = create_event(json_rock_music_event, organizer_token)
    new_event_id = new_event['_id']['$oid']
    first_attendee_token = login_attendee("agustina@gmail.com", "agustina segura")
    report = {
        "event_id": new_event_id,
        "reason": "seems fake",
    }
    client.post("/attendees/report/event", json=report, headers={"Authorization": f"Bearer {first_attendee_token}"})
    second_attendee_token = login_attendee("rama@gmail.com", "rama sanchez")
    report = {
        "event_id": new_event_id,
        "reason": "spam",
    }
    client.post("/attendees/report/event", json=report, headers={"Authorization": f"Bearer {second_attendee_token}"})
    third_attendee_token = login_attendee("pedro@gmail.com", "pedro sanchez")
    report = {
        "event_id": new_event_id,
        "reason": "spam",
    }
    client.post("/attendees/report/event", json=report, headers={"Authorization": f"Bearer {third_attendee_token}"})
    admin_token = admin_login()

    events_reports_response = client.get("/admins/reports/events?from_date=2023-04-24", headers={"Authorization": f"Bearer {admin_token}"})
    assert events_reports_response.status_code == status.HTTP_200_OK
    reports = events_reports_response.json()["message"]

    assert len(reports) == 1
    assert reports[0]['event_id'] == new_event_id
    assert reports[0]['event_name'] == 'Music Fest'
    assert reports[0]['event_description'] == "Musical de pop, rock y mucho más"
    assert reports[0]['organizer_name'] == "Agustina Segura"
    assert reports[0]['organizer_id'] == 1
    assert reports[0]['most_frecuent_reason'] == 'spam'
    assert reports[0]['amount_of_reports'] == 3

@pytest.mark.usefixtures("drop_collection_documents")
def test_when_getting_reported_events_by_date_to_should_return_empty_list():
    organizer_token = login_organizer("solfontenla@gmail.com", "sol fontenla")
    new_event = create_event(json_rock_music_event, organizer_token)
    new_event_id = new_event['_id']['$oid']
    first_attendee_token = login_attendee("agustina@gmail.com", "agustina segura")

    report = {
        "event_id": new_event_id,
        "reason": "seems fake",
    }
    client.post("/attendees/report/event", json=report, headers={"Authorization": f"Bearer {first_attendee_token}"})

    second_attendee_token = login_attendee("rama@gmail.com", "rama sanchez")
    report = {
        "event_id": new_event_id,
        "reason": "spam",
    }
    client.post("/attendees/report/event", json=report, headers={"Authorization": f"Bearer {second_attendee_token}"})
    attendee_token = login_attendee("pedro@gmail.com", "pedro sanchez")
    report = {
        "event_id": new_event_id,
        "reason": "seems fake",
    }
    client.post("/attendees/report/event", json=report, headers={"Authorization": f"Bearer {attendee_token}"})
    admin_token = admin_login()

    events_reports_response = client.get("/admins/reports/events?to_date=2023-04-24", headers={"Authorization": f"Bearer {admin_token}"})
    assert events_reports_response.status_code == status.HTTP_200_OK
    reports = events_reports_response.json()["message"]

    assert len(reports) == 0

@pytest.mark.usefixtures("drop_collection_documents")
def test_when_an_admin_is_trying_to_susped_an_organizer_then_it_should_suspend_the_organizer():
    organizer_token = login_organizer("solfontenla@gmail.com", "sol fontenla")
    actual = jwt_handler.decode_token(organizer_token)
    organizer_id = actual['id']

    event_1 = create_event(json_rock_music_event, organizer_token)
    event_2 = create_event(json_theatre_event, organizer_token)

    event_1_id = event_1['_id']["$oid"]
    event_2_id = event_2['_id']["$oid"]

    attendee_token = login_attendee("agustina@gmail.com", "agustina segura")

    response_to_reservation_1 = client.post(f"/events/reservations/user/{str(attendee_token)}/event/{event_1_id}")
    response_to_reservation_1 = response_to_reservation_1.json()["message"]
    reservation_1 = response_to_reservation_1["_id"]["$oid"]
    response_to_reservation_2 = client.post(f"/events/reservations/user/{attendee_token}/event/{event_2_id}")
    response_to_reservation_2 = response_to_reservation_2.json()["message"]
    reservation_2 = response_to_reservation_2["_id"]["$oid"]

    admin_token = admin_login()

    blockResponse = client.patch(f"/admins/suspended_organizers/{organizer_id}",headers={"Authorization": f"Bearer {admin_token}"})
    assert blockResponse.status_code == status.HTTP_200_OK
    blockResponse = blockResponse.json()['message']

    assert blockResponse[0] == reservation_1
    assert blockResponse[1] == reservation_2  


@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenAnAdminGetsTheEventsTypesStatistics_ThereAreNoneEventsYet_ItShouldReturnCeroOfEachType():
    admin_token = admin_login()

    response = client.get("/admins/statistics/events/types", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == status.HTTP_200_OK
    event_types_statistics = response.json()["message"]

    assert event_types_statistics["CONFERENCIA"] == 0
    assert event_types_statistics["CINE"] == 0
    assert event_types_statistics["TEATRO"] == 0
    assert event_types_statistics["SHOW"] == 0
    assert event_types_statistics["CONCIERTO"] == 0
    assert event_types_statistics["OTRO"] == 0
    

@pytest.mark.usefixtures("drop_collection_documents")
def test_WhenAnAdminGetsTheEventsTypesStatistics_ThereIsOneEvent_ItShouldReturnOneOfShowType():
    organizer_token = login_organizer("solfontenla@gmail.com", "sol fontenla")
    create_event(json_rock_music_event, organizer_token)

    admin_token = admin_login()

    response = client.get("/admins/statistics/events/types", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == status.HTTP_200_OK
    event_types_statistics = response.json()["message"]

    assert event_types_statistics["CONFERENCIA"] == 0
    assert event_types_statistics["CINE"] == 0
    assert event_types_statistics["TEATRO"] == 0
    assert event_types_statistics["SHOW"] == 1
    assert event_types_statistics["CONCIERTO"] == 0
    assert event_types_statistics["OTRO"] == 0




