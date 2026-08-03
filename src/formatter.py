from datetime import date
from typing import List, Tuple

from src.weather import DailyForecast, WeatherReport


Style = str
Line = Tuple[Style, str]


def center(text: str, width: int, fill: str = " ") -> str:
    if len(text) >= width:
        return text
    left = (width - len(text)) // 2
    right = width - len(text) - left
    return fill * left + text + fill * right


def left(text: str, width: int) -> str:
    return text + " " * max(0, width - len(text))


def right(text: str, width: int) -> str:
    return " " * max(0, width - len(text)) + text


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
    """Shorten weather descriptions for the forecast column."""
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
    return mapping.get(description, description[:6])


def forecast_row(day_text: str, desc: str, temp_text: str, width: int = 21) -> str:
    """Build a three-column forecast row: date | weather | temp."""
    col1_w = 6
    col3_w = 7
    col2_w = width - col1_w - col3_w
    return left(day_text, col1_w) + center(desc, col2_w)[:col2_w] + right(temp_text, col3_w)


def format_weather_report(report: WeatherReport, columns: int = 21) -> List[Line]:
    lines: List[Line] = []

    # All text now prints with Font A, so every line must fit within 'columns'.
    w = columns

    # Top decoration
    lines.append(("normal_sep", "=" * w))
    lines.append(("big_center", "Today's Weather"))
    lines.append(("normal_sep", "=" * w))
    lines.append(("blank", ""))

    # Location and date
    lines.append(("big_center", report.location_name))
    lines.append(("normal_center", report.current.updated_at.strftime("%Y-%m-%d %H:%M")))
    lines.append(("blank", ""))

    # Current weather summary
    lines.append(("big_center", report.current.description))
    lines.append(("big_center", f"{report.current.temperature:.1f}C"))
    lines.append(("blank", ""))

    # Detail rows (normal font)
    lines.append(("normal_left", f"Feels like: {report.current.apparent_temperature:.1f}C"))
    lines.append(("normal_left", f"Humidity: {report.current.humidity}%"))
    lines.append(("normal_left", f"Wind: {report.current.wind_speed:.1f}m/s"))
    lines.append(("normal_left", f"Precip: {report.current.precipitation:.1f}mm"))
    lines.append(("blank", ""))

    # Forecast header (big)
    lines.append(("big_center", "3-Day Forecast"))
    lines.append(("normal_sep", "=" * w))
    for forecast in report.daily_forecasts:
        day_text = format_day_label(forecast.date)
        temp_text = f"{forecast.temp_min:.0f}/{forecast.temp_max:.0f}C"
        desc = short_weather(forecast.description)
        lines.append(("small_left", forecast_row(day_text, desc, temp_text, w)))
    lines.append(("blank", ""))

    # Footer
    lines.append(("normal_center", "Open-Meteo"))
    lines.append(("normal_sep", "=" * w))

    return lines
