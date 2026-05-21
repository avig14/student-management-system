import sqlite3
from typing import List, Optional

from core.models import Student
from storage.database import DatabaseHandler
from utils.logger import get_logger
from utils.validators import validate_age, validate_email, validate_marks, validate_name

logger = get_logger(__name__)


def _generate_id(existing_ids: list) -> str:
    nums = []
    for sid in existing_ids:
        try:
            nums.append(int(sid.split("-")[1]))
        except (IndexError, ValueError):
            pass
    next_num = max(nums, default=0) + 1
    return f"STU-{next_num:04d}"


def _row_to_student(row: dict) -> Student:
    return Student(
        student_id=row["student_id"],
        name=row["name"],
        age=row["age"],
        course=row["course"],
        marks=[row["marks_s1"], row["marks_s2"], row["marks_s3"]],
        email=row["email"],
    )


class StudentManager:
    def __init__(self, db: DatabaseHandler):
        self.db = db

    def add_student(self, name: str, age, course: str, marks: list, email: str) -> Student:
        name = validate_name(name)
        age = validate_age(age)
        marks = validate_marks(marks)
        email = validate_email(email)

        existing = self.db.fetch_all()
        existing_ids = [r["student_id"] for r in existing]

        for r in existing:
            if r["email"] == email:
                raise ValueError(f"A student with email '{email}' already exists.")

        student_id = _generate_id(existing_ids)
        self.db.insert_student(student_id, name, age, course.strip(), marks, email)
        logger.info(f"Added student {student_id} - {name}")
        return self.get_student(student_id)

    def get_all_students(self) -> List[Student]:
        rows = self.db.fetch_all()
        return [_row_to_student(r) for r in rows]

    def get_student(self, student_id: str) -> Optional[Student]:
        row = self.db.fetch_by_id(student_id)
        if not row:
            return None
        return _row_to_student(row)

    def update_student(self, student_id: str, **kwargs) -> Student:
        existing = self.get_student(student_id)
        if not existing:
            raise ValueError(f"No student found with ID: {student_id}")

        db_fields = {}

        if "name" in kwargs:
            db_fields["name"] = validate_name(kwargs["name"])
        if "age" in kwargs:
            db_fields["age"] = validate_age(kwargs["age"])
        if "course" in kwargs:
            db_fields["course"] = kwargs["course"].strip()
        if "email" in kwargs:
            db_fields["email"] = validate_email(kwargs["email"])
        if "marks" in kwargs:
            validated = validate_marks(kwargs["marks"])
            db_fields["marks_s1"] = validated[0]
            db_fields["marks_s2"] = validated[1]
            db_fields["marks_s3"] = validated[2]

        try:
            self.db.update_student(student_id, db_fields)
        except sqlite3.IntegrityError:
            raise ValueError("A student with that email already exists.")
        logger.info(f"Updated student {student_id}")
        return self.get_student(student_id)

    def delete_student(self, student_id: str) -> bool:
        deleted = self.db.delete_student(student_id)
        if deleted:
            logger.info(f"Deleted student {student_id}")
        else:
            logger.warning(f"Tried to delete non-existent student {student_id}")
        return deleted

    def search(self, query: str, field: str = "name") -> List[Student]:
        if field not in ("name", "id", "course"):
            raise ValueError("Search field must be 'name', 'id', or 'course'.")
        rows = self.db.search_students(query.strip(), field)
        return [_row_to_student(r) for r in rows]
