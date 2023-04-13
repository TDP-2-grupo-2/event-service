from fastapi.testclient import TestClient
from fastapi import status
from test import config
from event_service.app import app

session = config.init_postg_db(app)
config.init_firebase(app)
client = TestClient(app)

userfireabaseAgus =  {
        "token": "hfjdshfuidhysvcsbvs83hfsdf",
        "googleId": "asdasdasdslwlewed1213123",
        "email": "agus@gmail.com",
        "name": "agus",
        "picture": "picture",
    }

def test_when_login_for_the_first_time_an_attende_then_it_returns_its_token():

    response = client.post("/attendees/loginGoogle", json={"token": userfireabaseAgus['token']})
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data['id'] == 1
    assert data['googleId'] == userfireabaseAgus['googleId']
    assert data['name'] == userfireabaseAgus['name']
    assert data['email'] == userfireabaseAgus['email']
    assert data['picture'] == userfireabaseAgus['picture']