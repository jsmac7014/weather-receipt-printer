from dataclasses import dataclass
from datetime import date, datetime
from typing import List

import httpx


# WMO Weather interpretation codes (WW)
# https://open-meteo.com/en/docs
WEATHER_CODE_MAP = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


@dataclass
class CurrentWeather:
    temperature: float
    apparent_temperature: float
    humidity: int
    wind_speed: float
    precipitation: float
    weather_code: int
    description: str
    updated_at: datetime


@dataclass
class DailyForecast:
    date: date
    weather_code: int
    description: str
    temp_max: float
    temp_min: float


@dataclass
class WeatherReport:
    location_name: str
    current: CurrentWeather
    daily_forecasts: List[DailyForecast]


def describe_weather(code: int) -> str:
    return WEATHER_CODE_MAP.get(code, "Other")


def fetch_weather(
    latitude: float,
    longitude: float,
    location_name: str,
    timezone: str = "Asia/Seoul",
) -> WeatherReport:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,showers,snowfall,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "timezone": timezone,
        "forecast_days": 3,
    }

    response = httpx.get(url, params=params, timeout=30.0)
    response.raise_for_status()
    data = response.json()

    current = data.get("current", {})
    current_weather = CurrentWeather(
        temperature=float(current.get("temperature_2m", 0)),
        apparent_temperature=float(current.get("apparent_temperature", 0)),
        humidity=int(current.get("relative_humidity_2m", 0)),
        wind_speed=float(current.get("wind_speed_10m", 0)),
        precipitation=float(current.get("precipitation", 0)),
        weather_code=int(current.get("weather_code", 0)),
        description=describe_weather(int(current.get("weather_code", 0))),
        updated_at=datetime.now(),
    )

    daily = data.get("daily", {})
    daily_forecasts: List[DailyForecast] = []
    dates = [datetime.strptime(d, "%Y-%m-%d").date() for d in daily.get("time", [])]
    codes = daily.get("weather_code", [])
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])

    for i in range(len(dates)):
        daily_forecasts.append(
            DailyForecast(
                date=dates[i],
                weather_code=int(codes[i]) if i < len(codes) else 0,
                description=describe_weather(int(codes[i]) if i < len(codes) else 0),
                temp_max=float(max_temps[i]) if i < len(max_temps) else 0.0,
                temp_min=float(min_temps[i]) if i < len(min_temps) else 0.0,
            )
        )

    return WeatherReport(
        location_name=location_name,
        current=current_weather,
        daily_forecasts=daily_forecasts,
    )
