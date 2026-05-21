import sys

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from core.analytics import Analytics
from core.manager import StudentManager
from reports.exporter import ReportExporter
from storage.database import DatabaseHandler
from utils.logger import get_logger

console = Console()
logger = get_logger("cli")

db = DatabaseHandler()
manager = StudentManager(db)
analytics = Analytics(manager)
exporter = ReportExporter()


def print_header():
    console.print()
    console.print(Panel(
        Text.assemble(
            ("  Student Management & Analytics System\n", "bold white"),
            ("  Python Project  |  FastAPI + SQLite + JWT", "dim"),
        ),
        border_style="bright_blue",
        padding=(1, 4),
    ))


def section(title: str):
    console.print()
    console.print(Rule(f"[bold bright_blue]{title}[/bold bright_blue]", style="bright_blue"))
    console.print()


def success(msg: str):
    console.print(f"\n  [bold green]✔[/bold green]  {msg}")


def error(msg: str):
    console.print(f"\n  [bold red]✖[/bold red]  {msg}")


def show_menu():
    console.print()
    table = Table(box=box.ROUNDED, border_style="bright_blue", show_header=False, padding=(0, 2))
    table.add_column(justify="right", style="bold bright_blue", width=3)
    table.add_column()
    table.add_row("1", "Add Student")
    table.add_row("2", "View All Students")
    table.add_row("3", "Update Student")
    table.add_row("4", "Delete Student")
    table.add_row("5", "Search Students")
    table.add_row("6", "Analytics Dashboard")
    table.add_row("7", "Export Reports")
    table.add_row("8", "[dim]Exit[/dim]")
    console.print(table)
    console.print()


def render_students_table(students):
    if not students:
        console.print("  [yellow]No students to display.[/yellow]")
        return

    table = Table(
        box=box.SIMPLE_HEAVY,
        border_style="bright_blue",
        header_style="bold bright_blue",
        show_lines=False,
        padding=(0, 1),
    )
    table.add_column("ID", style="dim", no_wrap=True)
    table.add_column("Name", min_width=16)
    table.add_column("Age", justify="center")
    table.add_column("Course", min_width=14)
    table.add_column("Sub 1", justify="right")
    table.add_column("Sub 2", justify="right")
    table.add_column("Sub 3", justify="right")
    table.add_column("Avg", justify="right", style="bold")
    table.add_column("Status", justify="center")
    table.add_column("Email", style="dim")

    for s in students:
        status = "[bold green]PASS[/bold green]" if s.is_passing else "[bold red]FAIL[/bold red]"
        avg_style = "green" if s.is_passing else "red"
        table.add_row(
            s.student_id,
            s.name,
            str(s.age),
            s.course,
            str(s.marks[0]),
            str(s.marks[1]),
            str(s.marks[2]),
            f"[{avg_style}]{s.average}[/{avg_style}]",
            status,
            s.email,
        )

    console.print(table)
    console.print(f"  [dim]{len(students)} student(s) listed.[/dim]")


def handle_add():
    section("Add New Student")
    try:
        name   = input("  Full Name      : ").strip()
        age    = input("  Age            : ").strip()
        course = input("  Course         : ").strip()
        m1     = input("  Subject 1 Mark : ").strip()
        m2     = input("  Subject 2 Mark : ").strip()
        m3     = input("  Subject 3 Mark : ").strip()
        email  = input("  Email Address  : ").strip()

        student = manager.add_student(name, age, course, [m1, m2, m3], email)
        success(f"Student added — ID: [bold]{student.student_id}[/bold]  |  Avg: {student.average}  |  Status: {'[green]Pass[/green]' if student.is_passing else '[red]Fail[/red]'}")
    except ValueError as e:
        error(str(e))


def handle_view():
    section("All Students")
    students = manager.get_all_students()
    render_students_table(students)


def handle_update():
    section("Update Student")
    student_id = input("  Student ID : ").strip()
    student = manager.get_student(student_id)
    if not student:
        error(f"No student found with ID: {student_id}")
        return

    console.print(f"\n  Editing [bold]{student.name}[/bold] — leave a field blank to keep current value.\n")

    updates = {}
    name = input(f"  Name   [{student.name}] : ").strip()
    if name:
        updates["name"] = name
    age = input(f"  Age    [{student.age}] : ").strip()
    if age:
        updates["age"] = age
    course = input(f"  Course [{student.course}] : ").strip()
    if course:
        updates["course"] = course
    email = input(f"  Email  [{student.email}] : ").strip()
    if email:
        updates["email"] = email

    change_marks = input("\n  Update subject marks? (y/n) : ").strip().lower()
    if change_marks == "y":
        m1 = input(f"  Subject 1 [{student.marks[0]}] : ").strip()
        m2 = input(f"  Subject 2 [{student.marks[1]}] : ").strip()
        m3 = input(f"  Subject 3 [{student.marks[2]}] : ").strip()
        updates["marks"] = [m1 or student.marks[0], m2 or student.marks[1], m3 or student.marks[2]]

    try:
        updated = manager.update_student(student_id, **updates)
        success("Student updated successfully.")
        console.print()
        render_students_table([updated])
    except ValueError as e:
        error(str(e))


def handle_delete():
    section("Delete Student")
    student_id = input("  Student ID : ").strip()
    student = manager.get_student(student_id)
    if not student:
        error(f"No student found with ID: {student_id}")
        return

    console.print(f"\n  [yellow]You are about to delete:[/yellow] [bold]{student.name}[/bold] ({student.student_id})")
    confirm = input("  Type 'yes' to confirm : ").strip().lower()
    if confirm == "yes":
        manager.delete_student(student_id)
        success(f"{student.name} has been removed.")
    else:
        console.print("\n  [yellow]Cancelled.[/yellow]")


def handle_search():
    section("Search Students")
    console.print("  Search by:  [bold bright_blue]1[/bold bright_blue] Name   [bold bright_blue]2[/bold bright_blue] ID   [bold bright_blue]3[/bold bright_blue] Course\n")
    choice = input("  Choose (1/2/3) : ").strip()
    field_map = {"1": "name", "2": "id", "3": "course"}
    field = field_map.get(choice, "name")
    query = input("  Search term    : ").strip()
    results = manager.search(query, field)
    console.print(f"\n  [dim]Found {len(results)} result(s) for \"{query}\"[/dim]\n")
    render_students_table(results)


def handle_analytics():
    section("Analytics Dashboard")
    try:
        top = analytics.highest_scorer()
        bot = analytics.lowest_scorer()
        course_avgs = analytics.course_averages()
        pf = analytics.pass_fail_report()
        avgs = analytics.average_per_student()

        summary = Table(box=box.ROUNDED, border_style="bright_blue", show_header=False, padding=(0, 2))
        summary.add_column(style="dim", width=22)
        summary.add_column(style="bold")
        summary.add_row("Highest Scorer", f"[green]{top.name}[/green]  ({top.student_id})  —  avg {top.average}")
        summary.add_row("Lowest Scorer", f"[red]{bot.name}[/red]  ({bot.student_id})  —  avg {bot.average}")
        summary.add_row("Total Students", str(pf["total"]))
        summary.add_row("Passed", f"[green]{pf['passed']}[/green]")
        summary.add_row("Failed", f"[red]{pf['failed']}[/red]")
        summary.add_row("Pass Rate", f"[bold]{pf['pass_rate']}%[/bold]")
        console.print(summary)

        console.print()
        console.print(Rule("[dim]Course-wise Averages[/dim]", style="dim"))
        console.print()

        course_table = Table(box=box.SIMPLE, show_header=True, header_style="bold bright_blue", padding=(0, 2))
        course_table.add_column("Course")
        course_table.add_column("Average Marks", justify="right")
        for course, avg in sorted(course_avgs.items(), key=lambda x: x[1], reverse=True):
            course_table.add_row(course, f"[bold]{avg}[/bold]")
        console.print(course_table)

        console.print()
        console.print(Rule("[dim]Per-Student Averages[/dim]", style="dim"))
        console.print()

        avg_table = Table(box=box.SIMPLE, show_header=True, header_style="bold bright_blue", padding=(0, 2))
        avg_table.add_column("Student")
        avg_table.add_column("ID", style="dim")
        avg_table.add_column("Average", justify="right")
        avg_table.add_column("Status", justify="center")
        for entry in sorted(avgs, key=lambda x: x["average"], reverse=True):
            is_pass = entry["average"] >= 40.0
            avg_table.add_row(
                entry["name"],
                entry["id"],
                f"{'[green]' if is_pass else '[red]'}{entry['average']}{'[/green]' if is_pass else '[/red]'}",
                "[green]Pass[/green]" if is_pass else "[red]Fail[/red]",
            )
        console.print(avg_table)

    except ValueError as e:
        error(str(e))


def handle_export():
    section("Export Reports")
    try:
        students = manager.get_all_students()
        if not students:
            error("No student data available to export.")
            return

        top = analytics.highest_scorer()
        bot = analytics.lowest_scorer()
        course_avgs = analytics.course_averages()
        pf = analytics.pass_fail_report()
        avgs = analytics.average_per_student()

        analytics_data = {
            "highest_scorer": top.to_dict(),
            "lowest_scorer": bot.to_dict(),
            "course_averages": course_avgs,
            "pass_fail": pf,
            "averages": avgs,
        }

        csv_path = exporter.export_students_csv(students)
        txt_path = exporter.export_analytics_txt(analytics_data)

        console.print(Panel(
            f"[bold green]Reports exported successfully![/bold green]\n\n"
            f"  [dim]Students CSV  →[/dim]  {csv_path}\n"
            f"  [dim]Analytics TXT →[/dim]  {txt_path}",
            border_style="green",
            padding=(1, 2),
        ))

    except ValueError as e:
        error(str(e))


def main():
    print_header()
    handlers = {
        "1": handle_add,
        "2": handle_view,
        "3": handle_update,
        "4": handle_delete,
        "5": handle_search,
        "6": handle_analytics,
        "7": handle_export,
    }
    while True:
        show_menu()
        choice = input("  Choice : ").strip()
        if choice == "8":
            console.print("\n  [dim]Goodbye![/dim]\n")
            sys.exit(0)
        action = handlers.get(choice)
        if action:
            action()
        else:
            error("Invalid choice. Enter a number from 1 to 8.")


if __name__ == "__main__":
    main()
