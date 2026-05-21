import csv
import os
from datetime import datetime
from typing import List

from core.models import Student

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_OUT_DIR = os.path.join(_BASE_DIR, "reports_output")
os.makedirs(_OUT_DIR, exist_ok=True)

_CSV_PATH = os.path.join(_OUT_DIR, "students_report.csv")
_TXT_PATH = os.path.join(_OUT_DIR, "analytics_report.txt")


class ReportExporter:
    def export_students_csv(
        self, students: List[Student], path: str = _CSV_PATH
    ) -> str:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["Student ID", "Name", "Age", "Course", "Subject 1", "Subject 2", "Subject 3", "Average", "Status", "Email"]
            )
            for s in students:
                writer.writerow([
                    s.student_id,
                    s.name,
                    s.age,
                    s.course,
                    s.marks[0],
                    s.marks[1],
                    s.marks[2],
                    s.average,
                    "Pass" if s.is_passing else "Fail",
                    s.email,
                ])
        return path

    def export_analytics_txt(self, analytics_data: dict, path: str = _TXT_PATH) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = []
        lines.append("=" * 55)
        lines.append("        STUDENT ANALYTICS REPORT")
        lines.append(f"        Generated: {now}")
        lines.append("=" * 55)

        lines.append("\n[HIGHEST SCORER]")
        top = analytics_data.get("highest_scorer", {})
        lines.append(f"  Name    : {top.get('name', 'N/A')}")
        lines.append(f"  ID      : {top.get('student_id', 'N/A')}")
        lines.append(f"  Average : {top.get('average', 'N/A')}")

        lines.append("\n[LOWEST SCORER]")
        bot = analytics_data.get("lowest_scorer", {})
        lines.append(f"  Name    : {bot.get('name', 'N/A')}")
        lines.append(f"  ID      : {bot.get('student_id', 'N/A')}")
        lines.append(f"  Average : {bot.get('average', 'N/A')}")

        lines.append("\n[COURSE-WISE AVERAGES]")
        for course, avg in analytics_data.get("course_averages", {}).items():
            lines.append(f"  {course:<30} {avg}")

        lines.append("\n[PASS / FAIL SUMMARY]")
        pf = analytics_data.get("pass_fail", {})
        lines.append(f"  Total Students : {pf.get('total', 0)}")
        lines.append(f"  Passed         : {pf.get('passed', 0)}")
        lines.append(f"  Failed         : {pf.get('failed', 0)}")
        lines.append(f"  Pass Rate      : {pf.get('pass_rate', 0)}%")

        lines.append("\n[AVERAGE MARKS PER STUDENT]")
        for entry in analytics_data.get("averages", []):
            lines.append(f"  {entry['name']:<28} {entry['average']}")

        lines.append("\n" + "=" * 55)

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return path
