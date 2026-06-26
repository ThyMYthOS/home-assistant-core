"""Support for Modbus."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, SERVICE_RELOAD
from homeassistant.core import Event, HomeAssistant, ServiceCall
from homeassistant.helpers.reload import async_integration_yaml_config
from homeassistant.helpers.service import async_register_admin_service
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, PLATFORMS
from .modbus import (
    DATA_MODBUS_CONFIG,
    DATA_MODBUS_HUBS,
    ModbusHub,
    async_modbus_setup,
    async_setup_services,
    get_hub as get_hub,
)
from .schemas import CONFIG_SCHEMA  # noqa: F401

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Modbus component."""
    if DOMAIN not in config:
        return True

    async def _reload_config(call: Event | ServiceCall) -> None:
        """Reload Modbus."""
        reload_config = await async_integration_yaml_config(hass, DOMAIN)

        if not reload_config or not reload_config.get(DOMAIN):
            for entry in list(hass.config_entries.async_entries(DOMAIN)):
                await hass.config_entries.async_remove(entry.entry_id)
            _LOGGER.debug("Modbus not present anymore")
            return

        _LOGGER.debug("Modbus reloading")
        await async_modbus_setup(hass, reload_config)

    async_register_admin_service(hass, DOMAIN, SERVICE_RELOAD, _reload_config)
    async_setup_services(hass)

    return await async_modbus_setup(hass, config)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a Modbus hub from a config entry."""
    name = entry.data[CONF_NAME]
    entity_config = hass.data.get(DATA_MODBUS_CONFIG, {}).get(name, {})

    hub = ModbusHub(hass, dict(entry.data))
    if not await hub.async_setup():
        return False

    hass.data.setdefault(DATA_MODBUS_HUBS, {})[name] = hub

    platforms_to_load = [p for p, conf_key in PLATFORMS if entity_config.get(conf_key)]
    entry.runtime_data = platforms_to_load
    await hass.config_entries.async_forward_entry_setups(entry, platforms_to_load)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Modbus hub config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, entry.runtime_data
    )
    if unload_ok:
        name = entry.data[CONF_NAME]
        hub = hass.data[DATA_MODBUS_HUBS].pop(name)
        await hub.async_close()
    return unload_ok
