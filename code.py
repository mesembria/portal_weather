"""
Weather Display for Matrix Portal
--------------------------------
This module controls a LED matrix display showing current weather conditions,
including temperature, time, and sun position. It uses the OpenWeather API
for weather data and supports both real and simulated data for testing.

Author: [Your Name]
Last Modified: 2024-02-19
"""

import board
import terminalio
import displayio
import math
from adafruit_display_text.label import Label
from adafruit_matrixportal.matrix import Matrix
from adafruit_matrixportal.network import Network
import adafruit_fakerequests as requests
from secrets import secrets
import json
from fake_weather import FAKE_RESPONSE

# Configuration Constants
UPDATE_DELAY = 1800  # Weather update interval (30 minutes)
DISPLAY_UPDATE_INTERVAL = 60  # Display refresh interval (1 minute)
WEATHER_UPDATE_INTERVAL = 300  # Weather data refresh interval (5 minutes)
UTC_OFFSET = -5  # EST timezone offset

# Display Configuration
DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 32
DISPLAY_BIT_DEPTH = 4

# Temperature Display Configuration
TEMP_MIN = 20  # Minimum temperature for color mapping (°F)
TEMP_MAX = 90  # Maximum temperature for color mapping (°F)
TEMP_RANGE_WIDTH = 2  # Width of temperature range display
TEMP_RANGE_HEIGHT = 16  # Height of temperature range display
TEMP_RANGE_TOP = 2  # Top position of temperature range
TEMP_RANGE_BOTTOM = 13  # Bottom position of temperature range
TEMP_RANGE_BAR_X = 0  # X position of temperature range bar (using full width)

def get_data_source_url(lat, long):
    """
    Construct the OpenWeather API URL with the given coordinates.
    
    Args:
        lat: Latitude coordinate
        long: Longitude coordinate
    
    Returns:
        str: Formatted API URL
    """
    return "https://api.openweathermap.org/data/3.0/onecall?lat={}&lon={}&units=imperial&exclude=minutely,hourly,alerts&appid={}".format(
        lat, long, secrets['openweather_token']
    )

# Initialize display hardware
matrix = Matrix(width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, bit_depth=DISPLAY_BIT_DEPTH)
display = matrix.display
network = Network(status_neopixel=board.NEOPIXEL, debug=True)

print("Starting up...")

group = displayio.Group()
display.show(group)

# Load weather icons bitmap
icons_bitmap = displayio.OnDiskBitmap("weather-icons.bmp")
icons = displayio.TileGrid(
    icons_bitmap,
    pixel_shader=icons_bitmap.pixel_shader,
    tile_width=16,
    tile_height=16,
    x=44,  # Move slightly left from edge
    y=0    # Move to top
)

def temp_to_color(temp):
    """
    Map temperature to color spectrum from purple (<=20°F) to dark red (>=90°F).
    
    Args:
        temp: Temperature in Fahrenheit
    
    Returns:
        int: RGB color value as a 24-bit integer
    """
    if temp <= 20:
        return 0x800080  # Purple
    if temp >= 90:
        return 0x800000  # Dark red
        
    # Map temperature to a position in the color spectrum
    # Create a gradient from purple->blue->green->yellow->red
    if temp < 35:  # Purple to Blue (20-35°F)
        ratio = (temp - 20) / 15
        r = int(128 * (1 - ratio))  # Fade from 128 to 0
        b = int(128 + (127 * ratio))  # Increase from 128 to 255
        return (r << 16) | b
    elif temp < 50:  # Blue to Green (35-50°F)
        ratio = (temp - 35) / 15
        b = int(255 * (1 - ratio))  # Fade from 255 to 0
        g = int(255 * ratio)  # Increase from 0 to 255
        return (g << 8) | b
    elif temp < 70:  # Green to Yellow (50-70°F)
        ratio = (temp - 50) / 20
        r = int(255 * ratio)  # Increase from 0 to 255
        return (r << 16) | (255 << 8)  # Keep green at 255
    else:  # Yellow to Dark Red (70-90°F)
        ratio = (temp - 70) / 20
        g = int(255 * (1 - ratio))  # Decrease from 255 to 0
        r = int(255 * (1 - (ratio/2)))  # Decrease from 255 to 128
        return (r << 16) | (g << 8)

# Weather icon indices - matches layout in weather-icons.bmp:
# Two columns (d=day, n=night) with rows ordered as:
# 01=clear, 02=partly cloudy, 03=cloudy, 04=broken clouds,
# 09=shower rain, 10=rain, 11=thunderstorm, 13=snow, 50=mist
ICON_MAP = {
    "01d": 0,   # Clear day (row 0, col 0)
    "01n": 1,   # Clear night (row 0, col 1)
    "02d": 2,   # Partly cloudy day (row 1, col 0)
    "02n": 3,   # Partly cloudy night (row 1, col 1)
    "03d": 4,   # Cloudy day (row 2, col 0)
    "03n": 5,   # Cloudy night (row 2, col 1)
    "04d": 6,   # Broken clouds day (row 3, col 0)
    "04n": 7,   # Broken clouds night (row 3, col 1)
    "09d": 8,   # Shower rain day (row 4, col 0)
    "09n": 9,   # Shower rain night (row 4, col 1)
    "10d": 10,  # Rain day (row 5, col 0)
    "10n": 11,  # Rain night (row 5, col 1)
    "11d": 12,  # Thunderstorm day (row 6, col 0)
    "11n": 13,  # Thunderstorm night (row 6, col 1)
    "13d": 14,  # Snow day (row 7, col 0)
    "13n": 15,  # Snow night (row 7, col 1)
    "50d": 16,  # Mist day (row 8, col 0)
    "50n": 17   # Mist night (row 8, col 1)
}

# Create display labels
time_label = Label(terminalio.FONT, text="00:00", color=0xFFFFFF)
time_label.x = 2
time_label.y = 6

temp_label = Label(terminalio.FONT, text="--°F", color=0xFFFFFF)
temp_label.x = 5
temp_label.y = 24

# Center temperature label vertically in bottom half, shifted up by 1
temp_label.y = 15 + (16 // 2)  # Center in bottom half, shifted up

# Create palettes
temp_range_palette = displayio.Palette(16)
temp_range_palette[0] = 0x000000  # Black (transparent)
for i in range(12):
    # Map palette indices 1-12 to temperature range 20-90°F
    temp = 20 + (i * 70/11)  # Spread across the full temperature range
    temp_range_palette[12-i] = temp_to_color(temp)  # Store in reverse order so cold colors are at high indices
temp_range_palette[13] = 0xFFFFFF  # White for min/max markers
temp_range_palette[14] = 0xFFFFFF  # White for current temp marker

sun_palette = displayio.Palette(3)
sun_palette[0] = 0x000000  # Black (transparent)
sun_palette[1] = 0x444444  # Dark gray for arc
sun_palette[2] = 0xFFAA00  # Orange-yellow for sun

# Create bitmaps
temp_range_bitmap = displayio.Bitmap(TEMP_RANGE_WIDTH, TEMP_RANGE_HEIGHT, 16)  # Use 16 colors to match palette
temp_range = displayio.TileGrid(temp_range_bitmap, pixel_shader=temp_range_palette, x=2, y=16)  # Positioned near left edge

# Create sun path bitmap (20x16 for bottom right corner)
sun_path_bitmap = displayio.Bitmap(20, 16, 3)
sun_path = displayio.TileGrid(sun_path_bitmap, pixel_shader=sun_palette, x=42, y=22)  # Position from bottom

def draw_temp_range(bitmap, current, min_temp, max_temp):
    """
    Draw the temperature range visualization on the given bitmap.
    
    Args:
        bitmap: The bitmap to draw on
        current: Current temperature
        min_temp: Minimum temperature for the day
        max_temp: Maximum temperature for the day
    """
    bitmap.fill(0)  # Clear bitmap
    
    # Calculate temperature to index mapping constants
    temp_range = max_temp - min_temp
    pixel_range = TEMP_RANGE_BOTTOM - TEMP_RANGE_TOP
    scale = pixel_range / temp_range
    
    # Draw temperature gradient bar
    for y in range(TEMP_RANGE_TOP, TEMP_RANGE_BOTTOM + 1):
        # Map y position to temperature
        temp = max_temp - ((y - TEMP_RANGE_TOP) / scale)
        # Get palette index for temperature
        index = max(1, min(12, int(12 - ((temp - 20) * 11 / 70))))
        # Draw gradient bar (full width since we're only 2 pixels wide)
        for x in range(TEMP_RANGE_WIDTH):
            bitmap[x, y] = index
    
    
    # Calculate and draw current temperature marker
    current_y = int(TEMP_RANGE_BOTTOM - ((current - min_temp) * scale))
    current_y = max(TEMP_RANGE_TOP, min(TEMP_RANGE_BOTTOM, current_y))
    
    # Draw current temperature marker (white line)
    for x in range(TEMP_RANGE_WIDTH):
        bitmap[x, current_y] = 14

def draw_sun_path(bitmap, current_time, sunrise_time, sunset_time):
    """
    Draw the sun path arc and current sun position on the given bitmap.
    
    Args:
        bitmap: The bitmap to draw on
        current_time: Current Unix timestamp
        sunrise_time: Sunrise Unix timestamp
        sunset_time: Sunset Unix timestamp
    """
    bitmap.fill(0)  # Clear bitmap
            
    
    # Calculate and draw sun first (if it should be visible)
    if sunrise_time <= current_time <= sunset_time:
        # Calculate sun's horizontal position (0 to 19)
        progress = (current_time - sunrise_time) / (sunset_time - sunrise_time)
        sun_x = int(progress * 19)
        
        # Calculate sun's vertical position using sine wave
        # Adjust phase to match arc position
        angle = (sun_x / 19.0) * math.pi
        sun_y = int(8 - 6 * math.sin(angle))  # Changed base from 6 to 8
        
        # Move sun above the arc
        sun_y = max(2, sun_y - 2)  # Keep at least 2 pixels from top
 
        
        # Draw sun and glow first
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if 0 <= sun_x + dx < 20 and 0 <= sun_y + dy < 16:
                    bitmap[sun_x + dx, sun_y + dy] = 2  # Draw glow
        bitmap[sun_x, sun_y] = 2  # Draw sun center last to ensure it's visible
    
    # Draw the arc second (so it appears behind the sun)
    for x in range(20):
        y = int(8 - 6 * math.sin(math.pi * x / 19))  # Changed base from 6 to 8
        if y < 16:
            # Only draw arc where there isn't already a sun or glow
            if bitmap[x, y] == 0:
                bitmap[x, y] = 1  # Arc color

# Add elements to group
group.append(time_label)
group.append(temp_label)
group.append(icons)
group.append(temp_range)
group.append(sun_path)

def get_icon(code):
    """
    Get the icon index for a given weather condition code.
    
    Args:
        code: OpenWeather icon code (e.g., '01d' for clear day)
    
    Returns:
        int: Index of the icon in the sprite sheet
    """
    # Optimized lookup: try exact match first, then try base condition with 'd' suffix
    return ICON_MAP.get(code) or ICON_MAP.get(code[:2] + 'd', 0)

def get_weather():
    """
    Fetch current weather data from OpenWeather API or use fake data for testing.
    
    Returns:
        Tuple containing:
        - current temperature (int)
        - weather icon code (str)
        - current timestamp (int)
        - sunrise time (int)
        - sunset time (int)
        - daily minimum temperature (int)
        - daily maximum temperature (int)
    
    Note:
        Returns default values if the fetch fails:
        (70°F, clear day, current time, current time, current time + 12h, 60°F, 80°F)
    """
    try:
        # Determine data source based on configuration
        if secrets.get('use_fake_data', False):
            response = type('Response', (), {'text': json.dumps(FAKE_RESPONSE)})()
            print("\nUsing Fake Data:")
        else:
            response = network.fetch(get_data_source_url(secrets['lat'], secrets['long']))
            print("\nAPI Response:")
            
        print(response.text)
        data = json.loads(response.text)
        
        # Extract weather data
        current_data = data['current']
        daily_data = data['daily'][0]['temp']
        
        return (
            int(current_data['temp']),
            current_data['weather'][0]['icon'],
            current_data['dt'],
            current_data['sunrise'],
            current_data['sunset'],
            int(daily_data['min']),
            int(daily_data['max'])
        )
        
    except Exception as e:
        print("Weather fetch error: {}".format(e))
        # Return default values on error
        return (70, "01d", 0, 0, 43200, 60, 80)  # Use 0 for time values

# Initialize with default values
last_weather_update = -UPDATE_DELAY  # Force immediate update on first loop
current_temp = 70
icon_code = "01d"
current_dt = 0  # Will be updated from API
sunrise_time = 0  # Will be updated from API
sunset_time = 43200  # 12 hours by default
min_temp = 60
max_temp = 80

# Initial display updates
local_timestamp = current_dt + (UTC_OFFSET * 3600)
hour = (local_timestamp % 86400) // 3600
minute = (local_timestamp % 3600) // 60
period = "PM" if hour >= 12 else "AM"
display_hour = hour if hour <= 12 else hour - 12
display_hour = 12 if display_hour == 0 else display_hour
current_time = "{:02d}:{:02d}".format(display_hour, minute)
time_label.text = current_time

temp_label.text = "{}°F".format(current_temp)
temp_label.color = temp_to_color(current_temp)

# Initial weather icon update
icons[0] = ICON_MAP.get(icon_code, 0)

# Initial display updates for temperature range and sun path
draw_sun_path(sun_path_bitmap, current_dt, sunrise_time, sunset_time)
draw_temp_range(temp_range_bitmap, current_temp, min_temp, max_temp)

last_minute = minute  # Track the last minute we updated the display

def update_time_display(hour, minute):
    """
    Update the time display with the given hour and minute.
    
    Args:
        hour: Hour in 24-hour format
        minute: Minute
    """
    period = "PM" if hour >= 12 else "AM"
    display_hour = hour if hour <= 12 else hour - 12
    display_hour = 12 if display_hour == 0 else display_hour
    time_label.text = "{:02d}:{:02d}".format(display_hour, minute)

def update_weather_display(weather_data):
    """
    Update all weather-related display elements with new data.
    
    Args:
        weather_data: Tuple containing current weather data
            (temp, icon_code, timestamp, sunrise, sunset, min_temp, max_temp)
    """
    current_temp, icon_code, timestamp, sunrise, sunset, min_temp, max_temp = weather_data
    
    icons[0] = get_icon(icon_code)
    temp_label.text = "{}°F".format(current_temp)
    temp_label.color = temp_to_color(current_temp)
    draw_sun_path(sun_path_bitmap, timestamp, sunrise, sunset)
    draw_temp_range(temp_range_bitmap, current_temp, min_temp, max_temp)

# Main loop
while True:
    # Get current time from weather data timestamp
    local_timestamp = current_dt + (UTC_OFFSET * 3600)
    hour = (local_timestamp % 86400) // 3600
    minute = (local_timestamp % 3600) // 60
    
    # Update time display when minute changes
    if minute != last_minute:
        update_time_display(hour, minute)
        last_minute = minute

    # Update weather data every WEATHER_UPDATE_INTERVAL seconds
    if last_weather_update < 0:  # First update
        weather_data = get_weather()
        current_dt = weather_data[2]  # Update current time from API
        update_weather_display(weather_data)
        last_weather_update = 0
    elif current_dt - last_weather_update > WEATHER_UPDATE_INTERVAL:
        weather_data = get_weather()
        current_dt = weather_data[2]  # Update current time from API
        update_weather_display(weather_data)
        last_weather_update = current_dt
    
    # No sleep needed - the display hardware handles the refresh rate
