"""Constants for the i-Vent integration."""
DOMAIN = "ivent"
CONF_API_KEY = "api_key"
CONF_LOCATION_ID = "location_id"

API_BASE_URL = "https://cloud.i-vent.com/api/v1"
DEFAULT_SCAN_INTERVAL = 30

# Work modes
WORK_MODES = [
    "IVentWorkOff",
    "IVentOn", 
    "IVentCustom",
    "IVentRecuperation1",
    "IVentRecuperation2", 
    "IVentRecuperation3",
    "IVentBypass1",
    "IVentBypass2",
    "IVentBypass3"
]

# Special modes
SPECIAL_MODES = [
    "IVentSpecialOff",
    "IVentBoost",
    "IVentSnooze", 
    "IVentNight1",
    "IVentNight2"
]