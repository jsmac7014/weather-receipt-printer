import os
from typing import Any, Dict

import yaml


DEFAULT_CONFIG_PATH = "config.yaml"


def load_config(path: str = DEFAULT_CONFIG_PATH) -> Dict[str, Any]:
    if not os.path.isabs(path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir, "..", path)
        path = os.path.abspath(path)

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_location(config: Dict[str, Any]) -> Dict[str, Any]:
    location = config.get("location", {})
    return {
        "latitude": float(location.get("latitude", 37.5665)),
        "longitude": float(location.get("longitude", 126.9780)),
        "name": location.get("name", "Unknown"),
    }


def get_printer_config(config: Dict[str, Any]) -> Dict[str, Any]:
    return config.get(
        "printer",
        {"device": "/dev/usb/lp0", "columns": 32, "cut": True},
    )


def get_schedule(config: Dict[str, Any]) -> str:
    return config.get("schedule", {}).get("print_time", "07:00")
