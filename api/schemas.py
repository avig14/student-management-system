from typing import List, Optional
from pydantic import BaseModel, EmailStr, field_validator


class StudentCreate(BaseModel):
    name: str
    age: int
    course: str
    marks: List[float]
    email: EmailStr

    @field_validator("marks")
    @classmethod
    def check_marks(cls, v):
        if len(v) != 3:
            raise ValueError("Exactly 3 marks are required.")
        for m in v:
            if not (0 <= m <= 100):
                raise ValueError(f"Each mark must be between 0 and 100.")
        return v

    @field_validator("age")
    @classmethod
    def check_age(cls, v):
        if not (10 <= v <= 100):
            raise ValueError("Age must be between 10 and 100.")
        return v


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    course: Optional[str] = None
    marks: Optional[List[float]] = None
    email: Optional[EmailStr] = None


class StudentResponse(BaseModel):
    student_id: str
    name: str
    age: int
    course: str
    marks: List[float]
    email: str
    average: float
    status: str


class UserCreate(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def check_username(cls, v):
        if not v or not v.strip():
            raise ValueError("Username cannot be empty.")
        return v.strip()

    @field_validator("password")
    @classmethod
    def check_password(cls, v):
        if not v:
            raise ValueError("Password cannot be empty.")
        if len(v) < 4:
            raise ValueError("Password must be at least 4 characters.")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
