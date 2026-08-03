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


def pad_right(text: str, width: int) -> str:
    return text + " " * max(0, width - len(text))


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
    """Shorten weather descriptions so they fit on small font lines."""
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


def format_weather_report(report: WeatherReport, columns: int = 21) -> List[Line]:
    lines: List[Line] = []

    # Large font width (Font A on the paper)
    big_w = columns
    # Small font width (Font B; adjust if text still wraps or drifts)
    small_w = 35

    # Top decoration
    lines.append(("sep", "=" * big_w))
    lines.append(("big_center", "Today's Weather"))
    lines.append(("sep", "=" * big_w))
    lines.append(("blank", ""))

    # Location and date
    lines.append(("big_center", report.location_name))
    lines.append(("small_center", report.current.updated_at.strftime("%Y-%m-%d %H:%M")))
    lines.append(("blank", ""))

    # Current weather summary
    lines.append(("big_center", report.current.description))
    lines.append(("big_center", f"{report.current.temperature:.1f}C"))
    lines.append(("blank", ""))

    # Detail rows (small font, simple Label: Value)
    lines.append(("small_left", f"Feels like: {report.current.apparent_temperature:.1f}C"))
    lines.append(("small_left", f"Humidity: {report.current.humidity}%"))
    lines.append(("small_left", f"Wind: {report.current.wind_speed:.1f}m/s"))
    lines.append(("small_left", f"Precip: {report.current.precipitation:.1f}mm"))
    lines.append(("blank", ""))

    # Forecast header
    lines.append(("small_center", "3-Day Forecast"))
    lines.append(("sep", "-" * small_w))
    for forecast in report.daily_forecasts:
        day_text = format_day_label(forecast.date)
        temp_text = f"{forecast.temp_min:.0f}/{forecast.temp_max:.0f}C"
        desc = short_weather(forecast.description)
        base = f"{day_text} {desc} {temp_text}"
        if len(base) > small_w:
            avail = small_w - len(day_text) - len(temp_text) - 2
            desc = desc[:max(avail, 3)]
            base = f"{day_text} {desc} {temp_text}"
        lines.append(("small_left", base))
    lines.append(("blank", ""))

    # Footer
    lines.append(("small_center", "Open-Meteo"))
    lines.append(("sep", "=" * big_w))

    return lines
