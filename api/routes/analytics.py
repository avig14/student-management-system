from fastapi import APIRouter, Depends, HTTPException

from api.auth.dependencies import get_current_user
from core.analytics import Analytics
from core.manager import StudentManager
from storage.database import DatabaseHandler

router = APIRouter(prefix="/analytics", tags=["analytics"])


def get_analytics():
    return Analytics(StudentManager(DatabaseHandler()))


@router.get("/")
def get_analytics_summary(
    analytics: Analytics = Depends(get_analytics),
    _: str = Depends(get_current_user),
):
    try:
        return {
            "highest_scorer": analytics.highest_scorer().to_dict(),
            "lowest_scorer": analytics.lowest_scorer().to_dict(),
            "course_averages": analytics.course_averages(),
            "pass_fail": analytics.pass_fail_report(),
            "average_per_student": analytics.average_per_student(),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/course-averages")
def get_course_averages(
    analytics: Analytics = Depends(get_analytics),
    _: str = Depends(get_current_user),
):
    try:
        return analytics.course_averages()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
