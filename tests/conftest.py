import pytest

from core.analytics import Analytics
from core.manager import StudentManager
from storage.database import DatabaseHandler


@pytest.fixture
def db():
    handler = DatabaseHandler(db_path=":memory:")
    return handler


@pytest.fixture
def manager(db):
    return StudentManager(db)


@pytest.fixture
def analytics(manager):
    return Analytics(manager)


@pytest.fixture
def seeded_manager(manager):
    manager.add_student("Alice Smith", 20, "Computer Science", [80, 75, 90], "alice@test.com")
    manager.add_student("Bob Jones", 21, "Data Science", [35, 40, 30], "bob@test.com")
    manager.add_student("Carol White", 22, "Computer Science", [60, 65, 70], "carol@test.com")
    manager.add_student("Dan Brown", 19, "Cybersecurity", [90, 85, 95], "dan@test.com")
    return manager
