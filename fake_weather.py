# Fake weather response for testing
FAKE_RESPONSE = {
    "lat": 37.2135,
    "lon": -80.0374,
    "timezone": "America/New_York",
    "timezone_offset": -18000,
    "current": {
        "dt": 1739992024,
        "sunrise": 1739966652,
        "sunset": 1740006242,
        "temp": 45.61,
        "feels_like": 13.12,
        "pressure": 1030,
        "humidity": 84,
        "dew_point": 19.96,
        "uvi": 0.39,
        "clouds": 100,
        "visibility": 2816,
        "wind_speed": 10.36,
        "wind_deg": 140,
        "weather": [
            {
                "id": 601,
                "main": "Snow",
                "description": "snow",
                "icon": "13d"
            }
        ],
        "snow": {
            "1h": 0.97
        }
    },
    "daily": [
        {
            "dt": 1739984400,
            "sunrise": 1739966652,
            "sunset": 1740006242,
            "moonrise": 1739941680,
            "moonset": 1739977920,
            "moon_phase": 0.72,
            "summary": "Expect a day of partly cloudy with snow",
            "temp": {
                "day": 25.2,
                "min": 40.36,
                "max": 60.72,
                "night": 21.81,
                "eve": 27,
                "morn": 25.43
            },
            "feels_like": {
                "day": 20.44,
                "night": 21.81,
                "eve": 23.59,
                "morn": 19.98
            },
            "pressure": 1028,
            "humidity": 86,
            "dew_point": 22.01,
            "wind_speed": 4.47,
            "wind_deg": 110,
            "wind_gust": 6.53,
            "weather": [
                {
                    "id": 601,
                    "main": "Snow",
                    "description": "snow",
                    "icon": "13d"
                }
            ],
            "clouds": 100,
            "pop": 1,
            "snow": 4.22,
            "uvi": 1.64
        }
    ]
}
