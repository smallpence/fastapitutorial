"testing for the app"

from fastapi.testclient import TestClient

import main

client = TestClient(main.app)

def test_read_main():
    "test that hello world is returned from root"
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {'hello': "world"}
