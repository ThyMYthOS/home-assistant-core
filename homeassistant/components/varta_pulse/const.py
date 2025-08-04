"""Constants for Varta Pulse integration."""

DOMAIN = "varta_pulse"
DEFAULT_PORT = 80
DEFAULT_SCAN_INTERVAL = 30  # seconds

# Device info
MANUFACTURER = "VARTA AG"
MODEL = "Pulse"

# Endpoints
ENDPOINT_INFO = "/cgi/info.js"
ENDPOINT_PARAM = "/cgi/param"
ENDPOINT_EMS_CONF = "/cgi/ems_conf.js"
ENDPOINT_EMS_DATA = "/cgi/ems_data.js"
ENDPOINT_ERROR = "/cgi/error.js"
