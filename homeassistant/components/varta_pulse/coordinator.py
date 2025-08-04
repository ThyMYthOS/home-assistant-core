"""Data update coordinator for Varta Pulse battery."""

from __future__ import annotations

import ast
import contextlib
from datetime import datetime, timedelta
import logging
import re

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    ENDPOINT_EMS_CONF,
    ENDPOINT_EMS_DATA,
    ENDPOINT_ERROR,
    ENDPOINT_INFO,
    ENDPOINT_PARAM,
)
from .models import VartaPulseEmsData, VartaPulseError, VartaPulseInfo, VartaPulseParam

_LOGGER = logging.getLogger(__name__)


class VartaPulseCoordinator(DataUpdateCoordinator):
    """Data update coordinator for Varta Pulse battery."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the coordinator.

        Args:
            hass: Home Assistant instance.
            config_entry: The config entry for this integration.
        """
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
            config_entry=config_entry,
        )
        self.host = config_entry.data["host"]
        self.port = config_entry.data.get("port", 80)
        self.session = aiohttp.ClientSession()
        self.info = None
        self.ems_conf = None

    async def _async_update_data(self):
        """Fetch data from Varta Pulse endpoints."""
        param = None
        ems_data = None
        error = None
        info = self.info
        ems_conf = self.ems_conf
        try:
            if info is None:
                info = await self._fetch_info()
                self.info = info
            if ems_conf is None:
                ems_conf = await self._fetch_ems_conf()
                self.ems_conf = ems_conf
            param = await self._fetch_param()
            ems_data = await self._fetch_ems_data(ems_conf)
            error = await self._fetch_error()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with Varta Pulse: {err}") from err
        else:
            return {
                "info": info,
                "param": param,
                "ems_data": ems_data,
                "error": error,
                "ems_conf": ems_conf,
            }

    async def _fetch_param(self) -> VartaPulseParam:
        """Fetch /cgi/param endpoint."""
        url = f"http://{self.host}:{self.port}{ENDPOINT_PARAM}"
        async with self.session.get(url) as resp:
            text = await resp.text()
        return self._parse_key_value(text, VartaPulseParam)

    async def _fetch_info(self) -> VartaPulseInfo:
        """Fetch /cgi/info.js endpoint and parse its content."""
        url = f"http://{self.host}:{self.port}{ENDPOINT_INFO}"
        async with self.session.get(url) as resp:
            text = await resp.text()
        return self._parse_key_value(text, VartaPulseInfo)

    def _parse_key_value(self, text: str, model_cls):
        """Parse key-value pairs from info/param endpoints into model."""

        def parse_line(line: str) -> tuple[str, str | int] | None:
            if "=" not in line:
                return None
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip(' ;"')
            with contextlib.suppress(ValueError):
                value = int(value)
            return key, value

        data = {
            k: v
            for k, v in (parse_line(line) for line in text.splitlines())
            if k is not None and v is not None
        }
        return model_cls(data=data)

    async def _fetch_ems_conf(self) -> dict[str, list[str]]:
        """Fetch /cgi/ems_conf.js and parse value names."""
        url = f"http://{self.host}:{self.port}{ENDPOINT_EMS_CONF}"
        async with self.session.get(url) as resp:
            text = await resp.text()
        # Parse JS arrays
        conf = {}
        for key in (
            "WR_Conf",
            "EMETER_Conf",
            "Charger_Conf",
            "Batt_Conf",
            "Modul_Conf",
        ):
            arr = re.search(rf"{key}\s*=\s*\[(.*?)\];", text, re.DOTALL)
            if arr:
                try:
                    conf[key] = ast.literal_eval(f"[{arr.group(1)}]")
                except (ValueError, SyntaxError):
                    conf[key] = []
        return conf

    async def _fetch_ems_data(
        self, ems_conf: dict[str, list[str]]
    ) -> VartaPulseEmsData:
        """Fetch /cgi/ems_data.js endpoint and parse values as dicts."""
        url = f"http://{self.host}:{self.port}{ENDPOINT_EMS_DATA}"
        async with self.session.get(url) as resp:
            text = await resp.text()
        return self._parse_ems_data(text, ems_conf)

    async def _fetch_error(self) -> VartaPulseError:
        """Fetch /cgi/error.js endpoint."""
        url = f"http://{self.host}:{self.port}{ENDPOINT_ERROR}"
        async with self.session.get(url) as resp:
            text = await resp.text()
        return self._parse_error(text)

    def _parse_ems_data(
        self, text: str, ems_conf: dict[str, list[str]]
    ) -> VartaPulseEmsData:
        """Parse /cgi/ems_data.js response into VartaPulseEmsData with named dicts."""
        zeit = re.search(r'Zeit\s*=\s*"([^"]+)";', text)
        wr_data = re.search(r"WR_Data\s*=\s*\[(.*?)\];", text, re.DOTALL)
        emeter_data = re.search(r"EMETER_Data\s*=\s*\[(.*?)\];", text, re.DOTALL)
        charger_data = re.search(r"Charger_Data\s*=\s*\[(.*?)\];", text, re.DOTALL)

        def parse_array(arr):
            try:
                return ast.literal_eval(f"[{arr}]")
            except (ValueError, SyntaxError):
                return []

        wr_names = ems_conf.get("WR_Conf", [])
        emeter_names = ems_conf.get("EMETER_Conf", [])
        charger_names = ems_conf.get("Charger_Conf", [])
        module_names = ems_conf.get("Modul_Conf", [])
        wr_values = parse_array(wr_data.group(1)) if wr_data else []
        emeter_values = parse_array(emeter_data.group(1)) if emeter_data else []
        charger_values = parse_array(charger_data.group(1)) if charger_data else []
        wr_dict = dict(zip(wr_names, wr_values, strict=True))
        emeter_dict = dict(zip(emeter_names, emeter_values, strict=True))
        charger_dict = dict(zip(charger_names, charger_values, strict=True))
        modules_list = [
            dict(zip(cv, module_names, strict=True)) for cv in charger_values[1:]
        ]

        # Parse zeit as datetime if possible, else fallback to string
        zeit = zeit.group(1) if zeit else ""
        with contextlib.suppress(ValueError):
            zeit = datetime.strptime(zeit, "%d.%m.%Y %H:%M:%S")

        return VartaPulseEmsData(
            zeit=zeit,
            wr_data=wr_dict,
            emeter_data=emeter_dict,
            charger_data=charger_dict,
            modules_data=modules_list,
        )

    def _parse_error(self, text: str) -> VartaPulseError:
        """Parse /cgi/error.js response into VartaPulseError."""
        error_list = re.search(r"ErrorList\s*=\s*(\[.*?\]);", text, re.DOTALL)
        na_error_list = re.search(r"NA_ErrorList\s*=\s*(\[.*?\]);", text, re.DOTALL)

        def parse_array(arr):
            try:
                return ast.literal_eval(arr)
            except (ValueError, SyntaxError):
                return []

        return VartaPulseError(
            error_list=parse_array(error_list.group(1)) if error_list else [],
            na_error_list=parse_array(na_error_list.group(1)) if na_error_list else [],
        )

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator and close the session."""
        await self.session.close()
