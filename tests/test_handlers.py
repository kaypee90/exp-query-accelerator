import datetime
import decimal
import json
import uuid

from src.handlers import encode_json


def test_encode_json_handles_database_types():
    row = [
        decimal.Decimal("1.10"),
        datetime.datetime(2026, 1, 2, 3, 4, 5),
        datetime.date(2026, 1, 2),
        uuid.UUID(int=1),
        b"\x00",
    ]

    assert json.loads(encode_json(row)) == [
        "1.10",
        "2026-01-02T03:04:05",
        "2026-01-02",
        "00000000-0000-0000-0000-000000000001",
        "AA==",
    ]
