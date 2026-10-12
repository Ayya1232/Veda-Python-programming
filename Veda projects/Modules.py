"""Service, program, customer and inquiry management."""
from datetime import date
from Base import Manager


class ServiceManager(Manager):
    filename = "services.json"
    required = ["name", "category", "price"]
    choices = {"category": ["Web Development", "Cloud", "Data & AI", "Cybersecurity", "Consulting"],
               "status": ["Active", "Inactive"]}

    def add(self, **f):
        f["price"] = _to_number(f.get("price"), "price")
        f.setdefault("status", "Active")
        return super().add(**f)


class ProgramManager(Manager):
    filename = "programs.json"
    required = ["name", "type", "seats"]
    choices = {"type": ["Training", "Internship"],
               "status": ["Open", "Ongoing", "Completed"]}

    def add(self, **f):
        f["seats"] = int(_to_number(f.get("seats"), "seats"))
        f.setdefault("enrolled", 0)
        f.setdefault("status", "Open")
        return super().add(**f)

    def enroll(self, program_id):
        p = self.get(program_id)
        if p["enrolled"] >= p["seats"]:
            raise ValueError("Program is full.")
        p["enrolled"] += 1
        self.save()
        return p


class CustomerManager(Manager):
    filename = "customers.json"
    required = ["name", "email"]

    def validate(self, record):
        super().validate(record)
        if "@" not in record["email"] or "." not in record["email"].split("@")[-1]:
            raise ValueError("Invalid email address.")


class InquiryManager(Manager):
    filename = "inquiries.json"
    required = ["customer_id", "subject", "kind"]
    choices = {"kind": ["Inquiry", "Service Request"],
               "status": ["Open", "In Progress", "Resolved"]}

    def add(self, **f):
        f.setdefault("status", "Open")
        f.setdefault("created", date.today().isoformat())
        return super().add(**f)


def _to_number(value, field):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"'{field}' must be a number.")
    if number < 0:
        raise ValueError(f"'{field}' cannot be negative.")
    return number