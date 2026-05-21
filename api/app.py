import json
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.auth.routes import router as auth_router
from api.routes.analytics import router as analytics_router
from api.routes.reports import router as reports_router
from api.routes.students import router as students_router
from core.manager import StudentManager
from storage.database import DatabaseHandler


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = DatabaseHandler()
    manager = StudentManager(db)
    existing = manager.get_all_students()
    if not existing:
        seed_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_students.json")
        if os.path.exists(seed_path):
            with open(seed_path, "r") as f:
                sample = json.load(f)
            for s in sample:
                try:
                    manager.add_student(
                        name=s["name"],
                        age=s["age"],
                        course=s["course"],
                        marks=s["marks"],
                        email=s["email"],
                    )
                except ValueError:
                    pass
    yield


app = FastAPI(
    title="Student Management & Analytics System",
    description="REST API for managing student records with analytics and reporting.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(students_router)
app.include_router(analytics_router)
app.include_router(reports_router)


@app.get("/", tags=["root"])
def root():
    return {"message": "Student Management API is running. Visit /docs for the Swagger UI."}
