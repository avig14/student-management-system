import os
import tempfile

import pytest

from reports.exporter import ReportExporter


@pytest.fixture
def exporter():
    return ReportExporter()


def test_export_students_csv(seeded_manager, exporter):
    students = seeded_manager.get_all_students()
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
        path = f.name
    try:
        result = exporter.export_students_csv(students, path=path)
        assert os.path.exists(result)
        with open(result, "r") as f:
            content = f.read()
        assert "Student ID" in content
        assert "Alice Smith" in content
    finally:
        os.unlink(path)


def test_export_analytics_txt(seeded_manager, exporter):
    from core.analytics import Analytics
    analytics = Analytics(seeded_manager)
    analytics_data = {
        "highest_scorer": analytics.highest_scorer().to_dict(),
        "lowest_scorer": analytics.lowest_scorer().to_dict(),
        "course_averages": analytics.course_averages(),
        "pass_fail": analytics.pass_fail_report(),
        "averages": analytics.average_per_student(),
    }
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
        path = f.name
    try:
        result = exporter.export_analytics_txt(analytics_data, path=path)
        assert os.path.exists(result)
        with open(result, "r") as f:
            content = f.read()
        assert "STUDENT ANALYTICS REPORT" in content
        assert "HIGHEST SCORER" in content
        assert "PASS / FAIL SUMMARY" in content
    finally:
        os.unlink(path)


def test_csv_has_correct_columns(seeded_manager, exporter):
    students = seeded_manager.get_all_students()
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
        path = f.name
    try:
        exporter.export_students_csv(students, path=path)
        with open(path, "r") as f:
            header = f.readline()
        assert "Average" in header
        assert "Status" in header
        assert "Email" in header
    finally:
        os.unlink(path)
