import hashlib
import json
from datetime import datetime, timezone
from uuid import uuid4


class AppError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def uid():
    return str(uuid4())


def digest(value):
    return hashlib.sha256(value.encode("utf-8") if isinstance(value, str) else value).hexdigest()


def dumps(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
