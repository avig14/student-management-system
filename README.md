# Student Management & Analytics System

A Python application I built as part of my internship assignment. It manages student records, runs analytics on the data, and can export reports. I built it with both a CLI interface and a REST API backend.

---

## Features

### Required
- [x] Add, View, Update, Delete students
- [x] Search by Name, ID, or Course
- [x] Average marks per student
- [x] Highest and lowest scoring student
- [x] Course-wise average marks
- [x] Pass/Fail report (passing threshold: 40%)
- [x] Data persistence (SQLite database)
- [x] Export to `students_report.csv` and `analytics_report.txt`

### Bonus
- [x] OOP — `Student`, `StudentManager`, `Analytics`, `ReportExporter` classes
- [x] FastAPI REST API with full CRUD and analytics endpoints
- [x] SQLite database (via Python's built-in `sqlite3`)
- [x] JWT Authentication (register + login to get a Bearer token)
- [x] Python `logging` with rotating file handler
- [x] Unit tests with `pytest` (>85% coverage)

---

## Tech Stack

- Python 3.9+
- FastAPI + Uvicorn
- SQLite (sqlite3)
- Pydantic v2
- python-jose (JWT)
- passlib (password hashing)
- Rich (CLI tables and colors)
- pytest + httpx (testing)

---

## Project Structure

```
student_management/
├── main.py              # CLI app
├── run_api.py           # Start the FastAPI server
├── api/                 # FastAPI routes, auth, schemas
├── core/                # Business logic (models, manager, analytics)
├── storage/             # SQLite database handler
├── reports/             # CSV and TXT export
├── utils/               # Logger and validators
├── tests/               # pytest test suite
├── data/                # Sample student data (JSON)
└── logs/                # App logs (auto-created)
```

---

## Setup

**1. Clone the repository**
```bash
git clone https://github.com/avig14/student-management-system.git
cd student-management-system
```

**2. Create a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**
```bash
copy .env.example .env       # Windows
cp .env.example .env         # Mac/Linux
```
Optionally edit `.env` to set a custom `SECRET_KEY`. The defaults work fine for local development.

---

## Running the CLI

```bash
python main.py
```

You'll see a numbered menu. The CLI reads from and writes to `students.db`.

> **First run tip:** start the API server once first (`python run_api.py`) — it auto-loads the 10 sample students from `data/sample_students.json`. After that, both the CLI and the API share the same database.

---

## Running the REST API

```bash
python run_api.py
```

Server starts at `http://localhost:8000`

**Swagger UI (interactive docs):** `http://localhost:8000/docs`

### Authentication Flow

1. Register: `POST /auth/register` — `{"username": "admin", "password": "yourpass"}`
2. Login: `POST /auth/login` — returns a JWT token
3. Use the token in the `Authorization: Bearer <token>` header for all other requests

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and get JWT token |
| GET | `/students/` | List all students |
| POST | `/students/` | Add a student |
| GET | `/students/{id}` | Get student by ID |
| PUT | `/students/{id}` | Update student |
| DELETE | `/students/{id}` | Delete student |
| GET | `/students/search?q=&field=` | Search students |
| GET | `/analytics/` | Full analytics summary |
| GET | `/analytics/course-averages` | Course-wise averages |
| POST | `/reports/export` | Export CSV and TXT reports |

---

## Running Tests

```bash
pytest tests/ -v --cov=. --cov-report=term-missing
```

The tests use an in-memory SQLite database so they don't touch your actual data.

---

## Sample Data

The file `data/sample_students.json` has 10 pre-made student records across 3 courses with varying marks. When you start the API for the first time on an empty database, these get automatically loaded.

---

## Reports

After running export (option 7 in CLI or `POST /reports/export` in the API):

- `reports_output/students_report.csv` — full student list with marks and pass/fail status
- `reports_output/analytics_report.txt` — formatted analytics summary with highest/lowest scorer, course averages, and pass rate
