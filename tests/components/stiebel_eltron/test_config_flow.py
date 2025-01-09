"""Test the STIEBEL ELTRON config flow."""

from homeassistant import config_entries
from homeassistant.components.stiebel_eltron.const import CONF_HUB, DOMAIN
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from .patchers import DEVICE_FOUND_PATCHER, NO_DEVICE_PATCHER, SETUP_ENTRY_PATCHER

from tests.common import MockConfigEntry


async def test_flow_user_fails_can_succeed(hass: HomeAssistant) -> None:
    """Test user initialized flow can still succeed after failure when modbus hub is available."""
    user_input = {CONF_NAME: "Test", CONF_HUB: "modbus_hub"}

    with NO_DEVICE_PATCHER, SETUP_ENTRY_PATCHER:
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_USER},
        )
        await hass.async_block_till_done()
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=user_input,
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.FORM
    assert result["errors"]

    with DEVICE_FOUND_PATCHER, SETUP_ENTRY_PATCHER:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=user_input,
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == user_input


async def test_flow_user_success(hass: HomeAssistant) -> None:
    """Test user initialized flow succeeds when modbus hub is available."""
    user_input = {CONF_NAME: "Test", CONF_HUB: "modbus_hub"}

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    await hass.async_block_till_done()
    with DEVICE_FOUND_PATCHER:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=user_input,
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == user_input


async def test_flow_user_duplicate_abort(hass: HomeAssistant) -> None:
    """Test user initialized flow aborts when device is already configured."""
    user_input = {CONF_NAME: "Test", CONF_HUB: "modbus_hub"}

    entry = MockConfigEntry(
        domain=DOMAIN,
        data=user_input,
        unique_id="modbus_hub",
        state=config_entries.ConfigEntryState.LOADED,
    )
    entry.add_to_hass(hass)

    with DEVICE_FOUND_PATCHER, SETUP_ENTRY_PATCHER:
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_USER},
        )
        await hass.async_block_till_done()
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=user_input,
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
