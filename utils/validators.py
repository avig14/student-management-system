import re


def validate_email(email: str) -> str:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    if not re.match(pattern, email):
        raise ValueError(f"Invalid email address: {email}")
    return email.lower()


def validate_marks(marks: list) -> list:
    if len(marks) != 3:
        raise ValueError("Exactly 3 subject marks are required.")
    result = []
    for m in marks:
        try:
            val = float(m)
        except (TypeError, ValueError):
            raise ValueError(f"Mark must be a number, got: {m}")
        if not (0 <= val <= 100):
            raise ValueError(f"Mark must be between 0 and 100, got: {val}")
        result.append(round(val, 2))
    return result


def validate_age(age) -> int:
    try:
        val = int(age)
    except (TypeError, ValueError):
        raise ValueError("Age must be a whole number.")
    if not (10 <= val <= 100):
        raise ValueError(f"Age must be between 10 and 100, got: {val}")
    return val


def validate_name(name: str) -> str:
    name = name.strip()
    if len(name) < 2:
        raise ValueError("Name must be at least 2 characters.")
    return name
