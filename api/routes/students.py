import sqlite3
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from api.auth.dependencies import get_current_user
from api.schemas import StudentCreate, StudentResponse, StudentUpdate
from core.analytics import Analytics
from core.manager import StudentManager
from storage.database import DatabaseHandler

router = APIRouter(prefix="/students", tags=["students"])


def get_manager():
    return StudentManager(DatabaseHandler())


@router.get("/search", response_model=List[StudentResponse])
def search_students(
    q: str = Query(..., description="Search term"),
    field: str = Query("name", description="Field to search: name, id, or course"),
    manager: StudentManager = Depends(get_manager),
    _: str = Depends(get_current_user),
):
    try:
        results = manager.search(q, field)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return [s.to_dict() for s in results]


@router.get("/", response_model=List[StudentResponse])
def get_all_students(
    manager: StudentManager = Depends(get_manager),
    _: str = Depends(get_current_user),
):
    return [s.to_dict() for s in manager.get_all_students()]


@router.post("/", response_model=StudentResponse, status_code=201)
def add_student(
    payload: StudentCreate,
    manager: StudentManager = Depends(get_manager),
    _: str = Depends(get_current_user),
):
    try:
        student = manager.add_student(
            name=payload.name,
            age=payload.age,
            course=payload.course,
            marks=payload.marks,
            email=str(payload.email),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return student.to_dict()


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: str,
    manager: StudentManager = Depends(get_manager),
    _: str = Depends(get_current_user),
):
    student = manager.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found.")
    return student.to_dict()


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: str,
    payload: StudentUpdate,
    manager: StudentManager = Depends(get_manager),
    _: str = Depends(get_current_user),
):
    updates = payload.model_dump(exclude_none=True)
    if payload.email:
        updates["email"] = str(payload.email)
    try:
        student = manager.update_student(student_id, **updates)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="A student with that email already exists.")
    return student.to_dict()


@router.delete("/{student_id}", status_code=204)
def delete_student(
    student_id: str,
    manager: StudentManager = Depends(get_manager),
    _: str = Depends(get_current_user),
):
    deleted = manager.delete_student(student_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found.")
