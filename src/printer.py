import logging
from typing import Dict, List, Tuple

from escpos.exceptions import Error as EscposError
from escpos.printer import File, Usb

logger = logging.getLogger(__name__)

# (style, text) tuples from formatter
Line = Tuple[str, str]

# ESC/POS raw command fragments
LEFT = b"\x1b\x61\x00"
CENTER = b"\x1b\x61\x01"
RIGHT = b"\x1b\x61\x02"
BOLD_ON = b"\x1b\x45\x01"
BOLD_OFF = b"\x1b\x45\x00"
FONT_A = b"\x1b\x4d\x00"
FONT_B = b"\x1b\x4d\x01"
SIZE_1X1 = b"\x1d\x21\x00"
SIZE_1X2 = b"\x1d\x21\x10"
SIZE_2X2 = b"\x1d\x21\x11"


def build_printer(config: Dict):
    if "usb" in config:
        usb_config = config["usb"]
        vendor_id = int(usb_config.get("vendor_id", 0), 16)
        product_id = int(usb_config.get("product_id", 0), 16)
        in_ep = int(usb_config.get("in_ep", 0x82), 16) if usb_config.get("in_ep") else 0x82
        out_ep = int(usb_config.get("out_ep", 0x01), 16) if usb_config.get("out_ep") else 0x01
        profile = usb_config.get("profile")
        return Usb(
            idVendor=vendor_id,
            idProduct=product_id,
            in_ep=in_ep,
            out_ep=out_ep,
            profile=profile,
        )

    device = config.get("device", "/dev/usb/lp0")
    return File(devfile=device)


def _set_line_spacing(printer, spacing: int = 24) -> None:
    """ESC 3 n: set line spacing in 1/180 inches (default ~24)."""
    printer._raw(bytes([0x1B, 0x33, spacing]))


def _apply_style(printer, style: str) -> None:
    """Apply ESC/POS font, size, alignment and bold by raw bytes."""
    if style == "big_center":
        printer._raw(FONT_A + CENTER + BOLD_ON + SIZE_1X2)
    elif style == "normal_center":
        printer._raw(FONT_A + CENTER + BOLD_OFF + SIZE_1X1)
    elif style == "normal_left":
        printer._raw(FONT_A + LEFT + BOLD_OFF + SIZE_1X1)
    elif style == "normal_sep":
        printer._raw(FONT_A + LEFT + BOLD_OFF + SIZE_1X1)
    elif style == "small_left":
        printer._raw(FONT_B + LEFT + BOLD_OFF + SIZE_1X1)
    elif style == "small_sep":
        printer._raw(FONT_B + LEFT + BOLD_OFF + SIZE_1X1)


def print_receipt(lines: List[Line], printer_config: Dict) -> None:
    try:
        p = build_printer(printer_config)
    except EscposError as exc:
        logger.error("Printer connection failed: %s", exc)
        raise

    try:
        p.codepage = "CP437"
        _set_line_spacing(p, 24)

        for style, text in lines:
            if style == "blank":
                p.text("\n")
                continue
            _apply_style(p, style)
            p.text(text + "\n")

        if printer_config.get("cut", True):
            try:
                p.cut()
            except Exception as exc:
                logger.warning("Cut failed (printer may not support it): %s", exc)

        p.close()
    except Exception as exc:
        logger.error("Error during printing: %s", exc)
        raise


def print_to_console(lines: List[Line]) -> None:
    """Print to console for testing without a physical printer."""
    for style, text in lines:
        if style == "blank":
            print()
        else:
            print(text)
