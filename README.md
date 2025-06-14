# i-Vent Smart Home Integration for Home Assistant

This integration allows you to control your i-Vent smart home ventilation system directly from Home Assistant.

## Installation

### HACS (Recommended)

1. Add this repository to HACS as a custom repository
2. Install "i-Vent Smart Home" from HACS
3. Restart Home Assistant
4. Add the integration via the UI

### Manual Installation

1. Copy the `custom_components/ivent` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Add the integration via the UI

## Configuration

1. Go to Settings → Devices & Services
2. Click "Add Integration" and search for "i-Vent"
3. Enter your API key and Location ID
4. Click Submit

## Usage

The integration will automatically create entities for all your groups and devices:

- **Switches**: Control each group on/off
- **Sensors**: Monitor device status, speeds, modes
- **Selects**: Choose work modes and special modes
- **Numbers**: Set fan speeds

## Services

- `ivent.set_work_mode`: Set the work mode for a group
- `ivent.set_special_mode`: Set special mode (boost, night, etc.)