"""Tests for Varta Pulse config flow."""

import pytest

from homeassistant import config_entries
from homeassistant.components.varta_pulse.const import DOMAIN
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from tests.test_util.aiohttp import AiohttpClientMocker


@pytest.mark.asyncio
async def test_user_flow_success(hass: HomeAssistant, varta_http_mocks) -> None:
    """Test successful user config flow."""

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    user_input = {CONF_HOST: "1.2.3.4", CONF_PORT: 80}
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=user_input
    )
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Varta Pulse 1.2.3.4"
    assert result2["data"] == user_input


@pytest.mark.asyncio
async def test_user_flow_cannot_connect(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Test config flow with connection error."""
    aioclient_mock.get("http://1.2.3.4:80/cgi/info.js", status=404)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    user_input = {CONF_HOST: "1.2.3.4", CONF_PORT: 80}
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=user_input
    )
    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}
