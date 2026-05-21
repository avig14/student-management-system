from fastapi import APIRouter, Depends, HTTPException

from api.auth.dependencies import get_current_user
from core.analytics import Analytics
from core.manager import StudentManager
from reports.exporter import ReportExporter
from storage.database import DatabaseHandler

router = APIRouter(prefix="/reports", tags=["reports"])


def get_deps():
    db = DatabaseHandler()
    manager = StudentManager(db)
    analytics = Analytics(manager)
    exporter = ReportExporter()
    return manager, analytics, exporter


@router.post("/export")
def export_reports(_: str = Depends(get_current_user)):
    db = DatabaseHandler()
    manager = StudentManager(db)
    analytics = Analytics(manager)
    exporter = ReportExporter()

    students = manager.get_all_students()
    if not students:
        raise HTTPException(status_code=404, detail="No student data to export.")

    try:
        analytics_data = {
            "highest_scorer": analytics.highest_scorer().to_dict(),
            "lowest_scorer": analytics.lowest_scorer().to_dict(),
            "course_averages": analytics.course_averages(),
            "pass_fail": analytics.pass_fail_report(),
            "averages": analytics.average_per_student(),
        }
        csv_path = exporter.export_students_csv(students)
        txt_path = exporter.export_analytics_txt(analytics_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "message": "Reports exported successfully.",
        "students_csv": csv_path,
        "analytics_txt": txt_path,
    }
