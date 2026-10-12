"""Generic record manager reused by every module."""
import os
import Storage

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class RecordNotFound(Exception):
    pass


class Manager:
    filename = "records.json"
    required = []          # fields that must be non-empty
    choices = {}           # field -> allowed values

    def __init__(self):
        self.path = os.path.join(DATA_DIR, self.filename)
        self.items = Storage.load(self.path)

    # ---- validation ----
    def validate(self, record):
        for field in self.required:
            if not str(record.get(field, "")).strip():
                raise ValueError(f"'{field}' is required.")
        for field, allowed in self.choices.items():
            if field in record and record[field] not in allowed:
                raise ValueError(f"'{field}' must be one of: {', '.join(allowed)}")

    # ---- CRUD ----
    def add(self, **fields):
        self.validate(fields)
        record = {"id": self._next_id(), **fields}
        self.items.append(record)
        self.save()
        return record

    def get(self, record_id):
        for item in self.items:
            if item["id"] == record_id:
                return item
        raise RecordNotFound(f"No record with id {record_id}.")

    def update(self, record_id, **changes):
        record = self.get(record_id)
        candidate = {**record, **changes}
        self.validate(candidate)
        record.update(changes)
        self.save()
        return record

    def delete(self, record_id):
        self.items.remove(self.get(record_id))
        self.save()

    # ---- search / filter ----
    def search(self, text="", **filters):
        """Case-insensitive text search across all fields plus exact filters."""
        text = text.lower().strip()
        results = []
        for item in self.items:
            if text and text not in " ".join(str(v) for v in item.values()).lower():
                continue
            if all(str(item.get(k, "")).lower() == str(v).lower()
                   for k, v in filters.items() if v):
                results.append(item)
        return results

    def save(self):
        Storage.save(self.path, self.items)

    def _next_id(self):
        return max((i["id"] for i in self.items), default=0) + 1