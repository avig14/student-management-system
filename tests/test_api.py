import pytest
from fastapi.testclient import TestClient

from api.app import app
from storage.database import DatabaseHandler

_test_db = DatabaseHandler(db_path=":memory:")


def override_db():
    return _test_db


app.dependency_overrides = {}

from api.routes.students import get_manager as students_get_manager
from api.routes.analytics import get_analytics as analytics_get_analytics
from api.routes.reports import get_deps as reports_get_deps
from api.auth.routes import get_db as auth_get_db
from core.manager import StudentManager
from core.analytics import Analytics
from reports.exporter import ReportExporter


def _make_manager():
    return StudentManager(_test_db)


def _make_analytics():
    return Analytics(_make_manager())


def _make_deps():
    m = _make_manager()
    return m, Analytics(m), ReportExporter()


app.dependency_overrides[students_get_manager] = _make_manager
app.dependency_overrides[analytics_get_analytics] = _make_analytics
app.dependency_overrides[auth_get_db] = override_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    conn = _test_db._get_conn()
    conn.execute("DELETE FROM students")
    conn.execute("DELETE FROM users")
    conn.commit()
    yield


def get_token():
    client.post("/auth/register", json={"username": "testuser", "password": "testpass"})
    resp = client.post("/auth/login", data={"username": "testuser", "password": "testpass"})
    return resp.json()["access_token"]


def auth_headers():
    return {"Authorization": f"Bearer {get_token()}"}


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "running" in resp.json()["message"]


def test_register():
    resp = client.post("/auth/register", json={"username": "newuser", "password": "pass123"})
    assert resp.status_code == 201


def test_register_duplicate_username():
    client.post("/auth/register", json={"username": "dup", "password": "pass"})
    resp = client.post("/auth/register", json={"username": "dup", "password": "pass"})
    assert resp.status_code == 400


def test_login_success():
    client.post("/auth/register", json={"username": "loginuser", "password": "pass"})
    resp = client.post("/auth/login", data={"username": "loginuser", "password": "pass"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password():
    client.post("/auth/register", json={"username": "user2", "password": "correct"})
    resp = client.post("/auth/login", data={"username": "user2", "password": "wrong"})
    assert resp.status_code == 401


def test_add_student():
    headers = auth_headers()
    payload = {
        "name": "Test Student",
        "age": 20,
        "course": "CS",
        "marks": [70, 80, 75],
        "email": "teststudent@example.com",
    }
    resp = client.post("/students/", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Student"
    assert data["average"] == 75.0


def test_get_all_students():
    headers = auth_headers()
    client.post("/students/", json={"name": "Amy Lee", "age": 18, "course": "CS", "marks": [50, 60, 55], "email": "amy@e.com"}, headers=headers)
    resp = client.get("/students/", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_get_student_by_id():
    headers = auth_headers()
    post = client.post("/students/", json={"name": "Ben Roy", "age": 19, "course": "DS", "marks": [60, 70, 65], "email": "ben@e.com"}, headers=headers)
    sid = post.json()["student_id"]
    resp = client.get(f"/students/{sid}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["student_id"] == sid


def test_get_nonexistent_student():
    headers = auth_headers()
    resp = client.get("/students/STU-9999", headers=headers)
    assert resp.status_code == 404


def test_update_student():
    headers = auth_headers()
    post = client.post("/students/", json={"name": "Old", "age": 20, "course": "CS", "marks": [50, 60, 70], "email": "old@e.com"}, headers=headers)
    sid = post.json()["student_id"]
    resp = client.put(f"/students/{sid}", json={"name": "New"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "New"


def test_delete_student():
    headers = auth_headers()
    post = client.post("/students/", json={"name": "Del", "age": 20, "course": "CS", "marks": [50, 50, 50], "email": "del@e.com"}, headers=headers)
    sid = post.json()["student_id"]
    resp = client.delete(f"/students/{sid}", headers=headers)
    assert resp.status_code == 204


def test_search_students():
    headers = auth_headers()
    client.post("/students/", json={"name": "Search Me", "age": 20, "course": "CS", "marks": [60, 65, 70], "email": "search@e.com"}, headers=headers)
    resp = client.get("/students/search?q=Search&field=name", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_unauthorized_access():
    resp = client.get("/students/")
    assert resp.status_code == 401


def test_analytics_no_data():
    headers = auth_headers()
    resp = client.get("/analytics/", headers=headers)
    assert resp.status_code == 404


def test_analytics_with_data():
    headers = auth_headers()
    client.post("/students/", json={"name": "Anna Kay", "age": 20, "course": "CS", "marks": [70, 80, 75], "email": "anna@e.com"}, headers=headers)
    resp = client.get("/analytics/", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "highest_scorer" in data
    assert "pass_fail" in data
