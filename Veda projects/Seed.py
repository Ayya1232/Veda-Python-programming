"""Synthetic starter data, created only when data files are empty."""
def seed(services, programs, customers, inquiries):
    if not services.items:
        for n, c, p in [("Custom Web App", "Web Development", 4500),
                        ("Cloud Migration", "Cloud", 8000),
                        ("Data Dashboard", "Data & AI", 3000),
                        ("Security Audit", "Cybersecurity", 2500),
                        ("IT Strategy Session", "Consulting", 900)]:
            services.add(name=n, category=c, price=p)
    if not programs.items:
        programs.add(name="Python Bootcamp", type="Training", seats=30)
        programs.add(name="Cloud Fundamentals", type="Training", seats=25)
        programs.add(name="Summer Dev Internship", type="Internship", seats=10)
    if not customers.items:
        customers.add(name="Asha Rao", email="asha@example.com")
        customers.add(name="Ben Carter", email="ben@example.com")
    if not inquiries.items:
        inquiries.add(customer_id=1, subject="Quote for web app", kind="Inquiry")
        inquiries.add(customer_id=2, subject="Need security audit", kind="Service Request")