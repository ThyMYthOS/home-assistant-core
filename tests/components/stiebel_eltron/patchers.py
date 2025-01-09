"""General STIEBEL ELTRON patchers."""

from unittest.mock import patch

SETUP_ENTRY_PATCHER = patch(
    "homeassistant.components.stiebel_eltron.async_setup_entry", return_value=True
)

DEVICE_FOUND_PATCHER = patch(
    "homeassistant.components.stiebel_eltron.config_flow.validate_input",
    return_value=True,
)

NO_DEVICE_PATCHER = patch(
    "homeassistant.components.stiebel_eltron.config_flow.validate_input",
    return_value=False,
)
