import pytest

from core.manager import StudentManager


def test_add_student(manager):
    s = manager.add_student("John Doe", 20, "CS", [70, 80, 75], "john@test.com")
    assert s.student_id == "STU-0001"
    assert s.name == "John Doe"
    assert s.marks == [70.0, 80.0, 75.0]


def test_add_student_auto_increment(manager):
    manager.add_student("Alex", 18, "CS", [50, 60, 55], "a@test.com")
    s2 = manager.add_student("Beth", 19, "DS", [40, 45, 50], "b@test.com")
    assert s2.student_id == "STU-0002"


def test_add_duplicate_email_raises(manager):
    manager.add_student("Alice", 20, "CS", [70, 80, 75], "same@test.com")
    with pytest.raises(ValueError, match="already exists"):
        manager.add_student("Bob", 21, "DS", [60, 65, 70], "same@test.com")


def test_add_invalid_marks_raises(manager):
    with pytest.raises(ValueError):
        manager.add_student("Test", 20, "CS", [101, 50, 60], "x@test.com")


def test_add_invalid_age_raises(manager):
    with pytest.raises(ValueError):
        manager.add_student("Test", 5, "CS", [50, 60, 70], "y@test.com")


def test_add_invalid_email_raises(manager):
    with pytest.raises(ValueError):
        manager.add_student("Test", 20, "CS", [50, 60, 70], "not-an-email")


def test_get_all_students(seeded_manager):
    students = seeded_manager.get_all_students()
    assert len(students) == 4


def test_get_student_by_id(seeded_manager):
    students = seeded_manager.get_all_students()
    sid = students[0].student_id
    found = seeded_manager.get_student(sid)
    assert found is not None
    assert found.student_id == sid


def test_get_nonexistent_student(manager):
    result = manager.get_student("STU-9999")
    assert result is None


def test_update_student(manager):
    s = manager.add_student("Old Name", 20, "CS", [50, 60, 70], "old@test.com")
    updated = manager.update_student(s.student_id, name="New Name", age=21)
    assert updated.name == "New Name"
    assert updated.age == 21


def test_update_nonexistent_raises(manager):
    with pytest.raises(ValueError, match="No student found"):
        manager.update_student("STU-9999", name="X")


def test_delete_student(manager):
    s = manager.add_student("Delete Me", 18, "CS", [40, 50, 60], "del@test.com")
    result = manager.delete_student(s.student_id)
    assert result is True
    assert manager.get_student(s.student_id) is None


def test_delete_nonexistent(manager):
    assert manager.delete_student("STU-9999") is False


def test_search_by_name(seeded_manager):
    results = seeded_manager.search("alice", "name")
    assert len(results) == 1
    assert results[0].name == "Alice Smith"


def test_search_by_course(seeded_manager):
    results = seeded_manager.search("Computer Science", "course")
    assert len(results) == 2


def test_search_by_id(seeded_manager):
    students = seeded_manager.get_all_students()
    sid = students[0].student_id
    results = seeded_manager.search(sid, "id")
    assert len(results) == 1


def test_search_invalid_field(manager):
    with pytest.raises(ValueError):
        manager.search("test", "invalid_field")
