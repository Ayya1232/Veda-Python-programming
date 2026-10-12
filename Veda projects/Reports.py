"""Basic business reports."""
from collections import Counter


def _table(title, counter):
    lines = [f"\n== {title} =="]
    lines += [f"  {k:<20} {v}" for k, v in sorted(counter.items())] or ["  (no data)"]
    return "\n".join(lines)


def summary_report(services, programs, customers, inquiries):
    out = [f"Customers: {len(customers.items)} | Services: {len(services.items)} "
           f"| Programs: {len(programs.items)} | Inquiries: {len(inquiries.items)}"]
    out.append(_table("Services by category", Counter(s["category"] for s in services.items)))
    out.append(_table("Programs by type", Counter(p["type"] for p in programs.items)))
    out.append(_table("Inquiries by status", Counter(i["status"] for i in inquiries.items)))
    seats = sum(p["seats"] for p in programs.items)
    used = sum(p["enrolled"] for p in programs.items)
    out.append(f"\nProgram seat utilization: {used}/{seats}" +
               (f" ({used / seats:.0%})" if seats else ""))
    revenue = sum(s["price"] for s in services.items if s["status"] == "Active")
    out.append(f"Total catalog value (active services): ${revenue:,.2f}")
    return "\n".join(out)