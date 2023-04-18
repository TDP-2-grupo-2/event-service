from fastapi.testclient import TestClient
from fastapi import status
from test import config
from event_service.app import app
from event_service.utils import jwt_handler

session = config.init_postg_db(app)

client = TestClient(app)



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