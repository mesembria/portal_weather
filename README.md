# Portal Weather Display

A CircuitPython application for Matrix Portal that displays real-time weather information on an LED matrix display. The display shows current temperature, time, weather conditions, and sun position throughout the day.


## Features

- Real-time weather data from OpenWeather API
- Current time display 
- Dynamic weather icons for different conditions
- Temperature visualization with color gradient
- Sun path visualization showing sunrise/sunset progress
- Configurable update intervals
- Test mode with simulated weather data

## Hardware Requirements

- [Adafruit Matrix Portal](https://www.adafruit.com/product/4745)
- 64x32 RGB LED matrix display
- USB-C cable for power and programming
- WiFi connection

## Software Dependencies

The following CircuitPython libraries are required (included in /lib):

- adafruit_bitmap_font
- adafruit_bus_device
- adafruit_display_text
- adafruit_esp32spi
- adafruit_io
- adafruit_matrixportal
- adafruit_minimqtt
- adafruit_portalbase
- adafruit_fakerequests
- adafruit_requests
- neopixel
- simpleio

## Setup Instructions

1. Install CircuitPython on your Matrix Portal if you haven't already.
2. Copy all files from this repository to your CIRCUITPY drive.
3. Create a `secrets.py` file based on `example_secrets.py`:
   ```python
   secrets = {
       'ssid': 'your_wifi_ssid',
       'password': 'your_wifi_password',
       'lat': 'your_latitude',
       'long': 'your_longitude',
       'openweather_token': 'your_openweather_api_key',
       'use_fake_data': False  # Set to True for testing
   }
   ```

## Configuration

The application can be configured by modifying constants in `code.py`:

- `UPDATE_DELAY`: Weather update interval (default: 30 minutes)
- `DISPLAY_UPDATE_INTERVAL`: Display refresh interval (default: 1 minute)
- `WEATHER_UPDATE_INTERVAL`: Weather data refresh interval (default: 5 minutes)
- `UTC_OFFSET`: Timezone offset (default: -5 for EST)
- Display dimensions and temperature range settings can also be adjusted

## Display Features

### Temperature Display
- Shows current temperature in Fahrenheit
- Color-coded from purple (≤20°F) to dark red (≥90°F)
- Vertical bar shows daily temperature range
- Current temperature marker on range bar

### Weather Icons
- Dynamic icons for different weather conditions
- Day/night variants for each condition
- Supports clear, partly cloudy, cloudy, rain, snow, thunderstorm, and more

### Sun Position
- Arc visualization showing sun's position
- Updates throughout the day
- Shows sunrise to sunset progress
- Glowing sun indicator moves along the arc

## Testing

The application includes a test mode using simulated weather data:

1. Set `use_fake_data = True` in `secrets.py`
2. The display will use data from `fake_weather.py`
3. Useful for development and testing without API calls

## Troubleshooting

- If the display shows "Loading..." continuously, check your WiFi credentials and OpenWeather API key
- Verify your latitude/longitude coordinates are correct
- Check the Matrix Portal's USB connection if the display is unresponsive
- Monitor the serial console for detailed error messages

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.

### You are free to:

- Share — copy and redistribute the material in any medium or format
- Adapt — remix, transform, and build upon the material

### Under the following terms:

- Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made
- NonCommercial — You may not use the material for commercial purposes

[View the full license](https://creativecommons.org/licenses/by-nc/4.0/legalcode)

## Credits

- Weather data provided by [OpenWeather API](https://openweathermap.org/api)
- Built with [CircuitPython](https://circuitpython.org/) and [Adafruit libraries](https://github.com/adafruit/Adafruit_CircuitPython_Bundle)
- Weather icons designed for optimal visibility on LED matrix displays
