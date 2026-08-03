from datetime import date, datetime
from typing import List, Tuple

from src.weather import DailyForecast, HourlyForecast, WeatherReport


Style = str
Line = Tuple[Style, str]


def center(text: str, width: int, fill: str = " ") -> str:
    if len(text) >= width:
        return text
    left = (width - len(text)) // 2
    right = width - len(text) - left
    return fill * left + text + fill * right


def format_day_label(d: date) -> str:
    today = date.today()
    label = f"{d.month}/{d.day}"
    if d == today:
        label += " T"
    elif d == date.fromordinal(today.toordinal() + 1):
        label += " Tm"
    elif d == date.fromordinal(today.toordinal() + 2):
        label += " Da"
    return label


def short_weather(description: str) -> str:
    """Shorten weather descriptions for the forecast row."""
    mapping = {
        "Mainly clear": "M clear",
        "Partly cloudy": "P cldy",
        "Clear sky": "Clear",
        "Overcast": "Cloudy",
        "Light drizzle": "L drzl",
        "Moderate drizzle": "Drzl",
        "Dense drizzle": "H drzl",
        "Slight rain": "L rain",
        "Moderate rain": "Rain",
        "Heavy rain": "H rain",
        "Slight snow": "L snow",
        "Moderate snow": "Snow",
        "Heavy snow": "H snow",
        "Thunderstorm": "Tstorm",
        "Thunderstorm with slight hail": "T+hail",
        "Thunderstorm with heavy hail": "T+hail",
        "Slight rain showers": "L shwr",
        "Moderate rain showers": "Shower",
        "Violent rain showers": "H shwr",
    }
    return mapping.get(description, description[:7])


def _common_header(report: WeatherReport, w: int) -> List[Line]:
    lines: List[Line] = []
    lines.append(("normal_sep", "=" * w))
    lines.append(("big_center", "Today's Weather"))
    lines.append(("normal_sep", "=" * w))
    lines.append(("blank", ""))
    lines.append(("big_center", report.location_name))
    lines.append(("normal_center", report.current.updated_at.strftime("%Y-%m-%d %H:%M")))
    lines.append(("blank", ""))
    lines.append(("big_center", report.current.description))
    lines.append(("big_center", f"{report.current.temperature:.1f}C"))
    lines.append(("blank", ""))
    lines.append(("normal_center", f"Feels like: {report.current.apparent_temperature:.1f}C"))
    lines.append(("normal_center", f"Humidity: {report.current.humidity}%"))
    lines.append(("normal_center", f"Wind: {report.current.wind_speed:.1f}m/s"))
    lines.append(("normal_center", f"Precip: {report.current.precipitation:.1f}mm"))
    lines.append(("blank", ""))
    return lines


def _daily_forecast_section(forecasts: List[DailyForecast], w: int) -> List[Line]:
    lines: List[Line] = []
    lines.append(("big_center", "3-Day Forecast"))
    lines.append(("normal_sep", "=" * w))
    for forecast in forecasts:
        day_text = format_day_label(forecast.date)
        temp_text = f"{forecast.temp_min:.0f}/{forecast.temp_max:.0f}C"
        desc = short_weather(forecast.description)
        row = f"{day_text} {desc} {temp_text}"
        if len(row) > w:
            avail = w - len(day_text) - len(temp_text) - 2
            desc = desc[:max(avail, 3)]
            row = f"{day_text} {desc} {temp_text}"
        lines.append(("normal_center", row))
    return lines


def _hourly_forecast_section(forecasts: List[HourlyForecast], w: int) -> List[Line]:
    lines: List[Line] = []
    lines.append(("big_center", "Hourly Forecast"))
    lines.append(("normal_sep", "=" * w))
    for forecast in forecasts:
        time_text = forecast.time.strftime("%H:%M")
        desc = short_weather(forecast.description)
        temp_text = f"{forecast.temperature:.1f}C"
        row = f"{time_text} {desc} {temp_text}"
        if len(row) > w:
            avail = w - len(time_text) - len(temp_text) - 2
            desc = desc[:max(avail, 3)]
            row = f"{time_text} {desc} {temp_text}"
        lines.append(("normal_center", row))
    return lines


def format_weather_report(
    report: WeatherReport,
    mode: str = "morning",
    columns: int = 21,
) -> List[Line]:
    w = columns
    lines: List[Line] = _common_header(report, w)

    if mode == "morning":
        lines.extend(_daily_forecast_section(report.daily_forecasts, w))
    else:
        lines.extend(_hourly_forecast_section(report.hourly_forecasts, w))

    lines.append(("blank", ""))
    lines.append(("normal_center", "Open-Meteo"))
    lines.append(("normal_sep", "=" * w))
    lines.append(("blank", ""))
    lines.append(("blank", ""))

    return lines
