"""Data models for Varta Pulse integration."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class VartaPulseData:
    """Unified data model for all Varta Pulse endpoint data."""

    info: dict[str, str | int]
    param: dict[str, str | int]
    wr_data: dict[str, str | int | float]
    emeter_data: dict[str, str | int | float]
    charger_data: dict[str, dict | str | int | float]
    battery_data: list[dict[str, Any]]
    time: str | datetime
    error_list: list[str]
    na_error_list: list[tuple[int, int]]
