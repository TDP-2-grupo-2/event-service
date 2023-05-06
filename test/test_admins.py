from fastapi.testclient import TestClient
from fastapi import status
from event_service.app import app

from test import config

session = config.init_postg_db(app)
client = TestClient(app)



def test_when_admin_login_with_correct_email_and_password_it_should_allow_it():

    response = client.post("/admins/login", json={"email":"admin@gmail.com", "password": "admintdp2"})

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data['message'] == 'Ok'

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