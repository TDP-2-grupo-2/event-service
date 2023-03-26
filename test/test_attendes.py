from fastapi.testclient import TestClient
from fastapi import status
import sys
sys.path.append("..")
from app import app

client = TestClient(app)

def test_prueba():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK