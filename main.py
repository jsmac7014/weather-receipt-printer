import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import get_location, get_printer_config, load_config
from src.formatter import format_weather_report
from src.printer import print_receipt, print_to_console
from src.weather import fetch_weather, get_upcoming_hourly


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def choose_mode(now: datetime) -> str:
    """Morning prints daily forecast; afternoon/evening prints hourly forecast."""
    hour = now.hour
    if hour < 12:
        return "morning"
    return "afternoon"


def main(config_path: str, dry_run: bool = False, mode: str = None) -> int:
    try:
        config = load_config(config_path)
    except FileNotFoundError:
        logger.error("Config file not found: %s", config_path)
        return 1
    except Exception as exc:
        logger.error("Failed to load config: %s", exc)
        return 1

    location = get_location(config)
    printer_config = get_printer_config(config)

    if mode is None:
        mode = choose_mode(datetime.now())
    logger.info("Running in %s mode for: %s", mode, location["name"])

    try:
        report = fetch_weather(
            latitude=location["latitude"],
            longitude=location["longitude"],
            location_name=location["name"],
        )
    except Exception as exc:
        logger.error("Failed to fetch weather: %s", exc)
        return 1

    if mode == "afternoon":
        report.hourly_forecasts = get_upcoming_hourly(
            report.hourly_forecasts,
            from_time=datetime.now(),
            hours=5,
        )

    lines = format_weather_report(
        report,
        mode=mode,
        columns=int(printer_config.get("columns", 21)),
    )

    if dry_run:
        logger.info("Dry-run mode: printing to console only.")
        print_to_console(lines)
        return 0

    logger.info("Starting receipt print.")
    try:
        print_receipt(lines, printer_config)
    except Exception as exc:
        logger.error("Print failed: %s", exc)
        return 1

    logger.info("Print complete.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Weather receipt printer")
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config file (default: config.yaml)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print to console instead of the physical printer",
    )
    parser.add_argument(
        "--mode",
        choices=["morning", "afternoon"],
        help="Override print mode (default: auto by current hour)",
    )
    args = parser.parse_args()

    sys.exit(main(args.config, args.dry_run, args.mode))
