"""Data models for Varta Pulse integration."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class VartaPulseParam:
    """Represents the /cgi/param endpoint data from Varta Pulse."""

    data: dict[str, str | int]


@dataclass
class VartaPulseEmsData:
    """Represents the /cgi/ems_data.js endpoint data from Varta Pulse."""

    wr_data: dict[str, str | int | float]
    emeter_data: dict[str, str | int | float]
    charger_data: dict[str, str | int | float]
    module_data: list[dict[str, str | int | float]]
    zeit: str | datetime


@dataclass
class VartaPulseError:
    """Represents the /cgi/error.js endpoint data from Varta Pulse."""

    error_list: list[str]
    na_error_list: list[tuple[int, int]]
