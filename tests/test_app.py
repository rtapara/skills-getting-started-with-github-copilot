import sys
import copy
from pathlib import Path

# Make sure we can import the app from src/app.py
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import app as app_module
from fastapi.testclient import TestClient


client = TestClient(app_module.app)


def setup_function():
    # keep a copy of initial activities to restore after each test
    app_module._test_backup_activities = copy.deepcopy(app_module.activities)


def teardown_function():
    # restore original state
    app_module.activities = copy.deepcopy(app_module._test_backup_activities)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_remove_participant_flow():
    activity = "Chess Club"
    email = "tester@example.com"

    # Sign up
    signup = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert signup.status_code == 200
    assert "Signed up" in signup.json().get("message", "")

    # Verify participant present
    data_after_signup = client.get("/activities").json()
    assert email in data_after_signup[activity]["participants"]

    # Remove participant
    delete = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert delete.status_code == 200
    assert "Removed" in delete.json().get("message", "")

    # Verify participant removed
    data_after_delete = client.get("/activities").json()
    assert email not in data_after_delete[activity]["participants"]
