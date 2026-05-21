from dataclasses import dataclass, field
from typing import List


@dataclass
class Student:
    student_id: str
    name: str
    age: int
    course: str
    marks: List[float]
    email: str

    @property
    def average(self) -> float:
        return round(sum(self.marks) / len(self.marks), 2)

    @property
    def is_passing(self) -> bool:
        return self.average >= 40.0

    def to_dict(self) -> dict:
        return {
            "student_id": self.student_id,
            "name": self.name,
            "age": self.age,
            "course": self.course,
            "marks": self.marks,
            "email": self.email,
            "average": self.average,
            "status": "Pass" if self.is_passing else "Fail",
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        return cls(
            student_id=data["student_id"],
            name=data["name"],
            age=data["age"],
            course=data["course"],
            marks=data["marks"],
            email=data["email"],
        )


@dataclass
class User:
    username: str
    hashed_password: str
