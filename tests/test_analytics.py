import pytest

from core.analytics import Analytics


def test_highest_scorer(seeded_manager, analytics):
    top = analytics.highest_scorer()
    assert top.name == "Dan Brown"


def test_lowest_scorer(seeded_manager, analytics):
    bot = analytics.lowest_scorer()
    assert bot.name == "Bob Jones"


def test_average_per_student(seeded_manager, analytics):
    avgs = analytics.average_per_student()
    assert len(avgs) == 4
    for entry in avgs:
        assert "name" in entry
        assert "average" in entry


def test_course_averages(seeded_manager, analytics):
    course_avgs = analytics.course_averages()
    assert "Computer Science" in course_avgs
    assert "Data Science" in course_avgs
    assert "Cybersecurity" in course_avgs


def test_pass_fail_report(seeded_manager, analytics):
    pf = analytics.pass_fail_report()
    assert pf["total"] == 4
    assert pf["passed"] + pf["failed"] == pf["total"]
    assert 0 <= pf["pass_rate"] <= 100


def test_bob_is_failing(seeded_manager, analytics):
    pf = analytics.pass_fail_report()
    failed_names = [s["name"] for s in pf["failed_students"]]
    assert "Bob Jones" in failed_names


def test_analytics_empty_db_raises(analytics):
    with pytest.raises(ValueError, match="No student records found"):
        analytics.highest_scorer()
