import logging
from typing import Dict, List, Tuple

from escpos.exceptions import Error as EscposError
from escpos.printer import File, Usb

logger = logging.getLogger(__name__)

Line = Tuple[str, str]


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


def _apply_style(printer, style: str) -> None:
    """Apply style using only python-escpos high-level set() calls."""
    if style == "big_center":
        printer.set(
            align="center",
            bold=True,
            double_height=False,
            double_width=False,
            custom_size=True,
            width=1,
            height=2,
        )
    elif style in ("normal_center", "big_sep"):
        printer.set(
            align="center",
            bold=False,
            double_height=False,
            double_width=False,
            custom_size=True,
            width=1,
            height=1,
        )
    elif style == "normal_left":
        printer.set(
            align="left",
            bold=False,
            double_height=False,
            double_width=False,
            custom_size=True,
            width=1,
            height=1,
        )
    elif style == "normal_sep":
        printer.set(
            align="left",
            bold=False,
            double_height=False,
            double_width=False,
            custom_size=True,
            width=1,
            height=1,
        )
    elif style in ("small_left", "small_sep"):
        # Without raw commands we cannot select Font B, so small uses the
        # same 1x1 Font A size as normal text.
        printer.set(
            align="left",
            bold=False,
            double_height=False,
            double_width=False,
            custom_size=True,
            width=1,
            height=1,
        )


def print_receipt(lines: List[Line], printer_config: Dict) -> None:
    try:
        p = build_printer(printer_config)
    except EscposError as exc:
        logger.error("Printer connection failed: %s", exc)
        raise

    try:
        p.codepage = "CP437"

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
