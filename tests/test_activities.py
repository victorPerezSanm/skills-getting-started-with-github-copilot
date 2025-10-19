import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure the src folder is importable (the repository uses a plain src directory, not a package)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC_PATH = os.path.join(ROOT, 'src')
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

import app as app_module
app = app_module.app
activities = app_module.activities


@pytest.fixture(autouse=True)
def client():
    # Create TestClient and ensure activities are reset for each test
    original = {k: {**v, "participants": list(v["participants"])} for k, v in activities.items()}
    client = TestClient(app)
    yield client
    # restore original participants
    for k, v in original.items():
        activities[k]["participants"] = v["participants"]


def test_get_activities(client):
    res = client.get('/activities')
    assert res.status_code == 200
    data = res.json()
    assert 'Chess Club' in data
    assert isinstance(data['Chess Club']['participants'], list)


def test_signup_and_unregister(client):
    activity = 'Chess Club'
    email = 'teststudent@mergington.edu'

    # Signup
    res = client.post(f"/activities/{activity}/signup?email={email}")
    assert res.status_code == 200
    assert email in activities[activity]['participants']

    # Signup same student again should error
    res = client.post(f"/activities/{activity}/signup?email={email}")
    assert res.status_code == 400

    # Unregister
    res = client.post(f"/activities/{activity}/unregister?email={email}")
    assert res.status_code == 200
    assert email not in activities[activity]['participants']

    # Unregister non-existent should error
    res = client.post(f"/activities/{activity}/unregister?email={email}")
    assert res.status_code == 400
