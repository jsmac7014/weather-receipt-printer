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
        "Mainly clear": "Mainly clr",
        "Partly cloudy": "Part cldy",
        "Clear sky": "Clear",
        "Overcast": "Cloudy",
        "Light drizzle": "L drizzle",
        "Moderate drizzle": "Drizzle",
        "Dense drizzle": "H drizzle",
        "Slight rain": "L rain",
        "Moderate rain": "Rain",
        "Heavy rain": "H rain",
        "Slight snow": "L snow",
        "Moderate snow": "Snow",
        "Heavy snow": "H snow",
        "Thunderstorm": "T-storm",
        "Thunderstorm with slight hail": "T-storm+hail",
        "Thunderstorm with heavy hail": "T-storm+hail",
        "Slight rain showers": "L showers",
        "Moderate rain showers": "Showers",
        "Violent rain showers": "H showers",
    }
    return mapping.get(description, description[:12])


def forecast_row(day_text: str, desc: str, temp_text: str, width: int = 42) -> str:
    """Build a three-column forecast row: date | weather | temp."""
    col1_w = 8
    col3_w = 12
    col2_w = width - col1_w - col3_w
    return left(day_text, col1_w) + center(desc, col2_w)[:col2_w] + right(temp_text, col3_w)


def format_weather_report(report: WeatherReport, columns: int = 21) -> List[Line]:
    lines: List[Line] = []

    # Large font width (Font A, height 2x)
    big_w = columns
    # Normal font width (Font A, height 1x)
    normal_w = columns
    # Small font width (Font B, height 1x)
    small_w = columns * 2

    # Top decoration
    lines.append(("normal_sep", "=" * normal_w))
    lines.append(("big_center", "Today's Weather"))
    lines.append(("normal_sep", "=" * normal_w))
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
    lines.append(("normal_sep", "=" * normal_w))
    for forecast in report.daily_forecasts:
        day_text = format_day_label(forecast.date)
        temp_text = f"{forecast.temp_min:.0f}/{forecast.temp_max:.0f}C"
        desc = short_weather(forecast.description)
        lines.append(("small_left", forecast_row(day_text, desc, temp_text, small_w)))
    lines.append(("blank", ""))

    # Footer
    lines.append(("normal_center", "Open-Meteo"))
    lines.append(("normal_sep", "=" * normal_w))

    return lines
