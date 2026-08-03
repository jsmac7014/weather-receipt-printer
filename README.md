# Weather Receipt Printer

A Python automation that prints the daily weather forecast for a configured location on a USB ESC/POS thermal receipt printer every morning.

## Structure

- `main.py` — Entry point
- `config.yaml` — Location, schedule, and printer settings
- `src/weather.py` — Open-Meteo API client and weather-code mapping
- `src/formatter.py` — Receipt text layout
- `src/printer.py` — `python-escpos` printer control
- `src/config.py` — Configuration loader

## Requirements

- Python 3.10+
- Linux (tested on Ubuntu)
- USB ESC/POS thermal receipt printer
- Internet connection for Open-Meteo API

## Installation

1. Copy the project to the target machine.

```bash
cd /path/to/weather-receipt-printer
```

2. Install dependencies.

```bash
pip3 install -r requirements.txt
```

## Configuration

Edit `config.yaml` for your location and printer.

```yaml
location:
  latitude: 37.5665
  longitude: 126.9780
  name: "Seoul"

schedule:
  print_time: "07:00"

printer:
  device: "/dev/usb/lp0"
  columns: 48
  cut: true
```

### Find the printer device

Check which device node the printer is using.

```bash
lsusb
ls /dev/usb/
ls /dev/ttyUSB*
```

If the printer is on a different node, update `printer.device`.

To connect by USB vendor/product id instead of a file path:

```yaml
printer:
  usb:
    vendor_id: "0x04b8"
    product_id: "0x0202"
  columns: 48
  cut: true
```

### USB permissions (udev)

Allow a non-root user to access the printer.

```bash
# Replace with the vendor/product id from lsusb
sudo tee /etc/udev/rules.d/99-thermal-printer.rules <<'EOF'
SUBSYSTEM=="usb", ATTR{idVendor}=="04b8", ATTR{idProduct}=="0202", MODE="0666", GROUP="lp"
EOF

sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Testing

Print to the console only:

```bash
python3 main.py --dry-run
```

Print to the physical printer:

```bash
python3 main.py
```

## Cron setup (daily automatic print)

Open the crontab editor:

```bash
crontab -e
```

Add the following line, adjusting the path:

```cron
0 7 * * * /usr/bin/python3 /path/to/weather-receipt-printer/main.py >> /path/to/weather-receipt-printer/run.log 2>&1
```

The cron time is the actual execution time. Keep it in sync with `print_time` shown on the receipt.

## Logs

Check `run.log` for execution history and errors.

```bash
tail -f run.log
```

## Troubleshooting

- **Permission denied on `/dev/usb/lpX`**: Add the udev rule above, or temporarily test with `sudo $(which python3) main.py` while the venv is active.
- **Printer not found**: Verify `printer.device` or use `vendor_id`/`product_id` in `config.yaml`.
- **Weather fetch fails**: Check the internet connection and Open-Meteo availability.
- **Cut fails**: Set `cut: false` in `config.yaml`.
- **Columns look wrong**: Adjust `printer.columns` for your paper width (32 for 58mm, 48 for 80mm).

## License

MIT
