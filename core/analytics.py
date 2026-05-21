from typing import Dict, List

from core.manager import StudentManager
from core.models import Student


class Analytics:
    def __init__(self, manager: StudentManager):
        self.manager = manager

    def _get_students(self) -> List[Student]:
        students = self.manager.get_all_students()
        if not students:
            raise ValueError("No student records found.")
        return students

    def average_per_student(self) -> List[dict]:
        students = self._get_students()
        return [{"id": s.student_id, "name": s.name, "average": s.average} for s in students]

    def highest_scorer(self) -> Student:
        students = self._get_students()
        return max(students, key=lambda s: s.average)

    def lowest_scorer(self) -> Student:
        students = self._get_students()
        return min(students, key=lambda s: s.average)

    def course_averages(self) -> Dict[str, float]:
        students = self._get_students()
        course_data: Dict[str, List[float]] = {}
        for s in students:
            if s.course not in course_data:
                course_data[s.course] = []
            course_data[s.course].append(s.average)
        return {
            course: round(sum(avgs) / len(avgs), 2)
            for course, avgs in course_data.items()
        }

    def pass_fail_report(self) -> dict:
        students = self._get_students()
        passed = [s for s in students if s.is_passing]
        failed = [s for s in students if not s.is_passing]
        pass_rate = round(len(passed) / len(students) * 100, 1)
        return {
            "total": len(students),
            "passed": len(passed),
            "failed": len(failed),
            "pass_rate": pass_rate,
            "passed_students": [s.to_dict() for s in passed],
            "failed_students": [s.to_dict() for s in failed],
        }
