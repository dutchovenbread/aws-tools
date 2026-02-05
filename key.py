from __future__ import annotations

from datetime import datetime


def create_key() -> str:
  datetime_string = datetime.now().strftime("%Y%m%d%H%M%S")
  return f"{datetime_string}"
