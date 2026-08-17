# Android / Termux Setup

## Requirements

- Android phone
- Termux
- Python 3
- LIFX color bulb on the same Wi-Fi network as the phone

## Install

```bash
pkg update
pkg install python git -y
git clone https://github.com/DJTheNetrunna/LIFX-LAN-FX.git
cd LIFX-LAN-FX
```

No third-party Python package is required for the core controller.

## Test discovery

```bash
python lifxfx.py list
```

Then run an effect:

```bash
python lifxfx.py plasma
```

If no bulb is found, verify that Android and the bulb are on the same LAN and that the network permits local UDP broadcast traffic.

## Web controller

```bash
python lifx-web.py
```

Open this on the same phone:

```text
http://127.0.0.1:8080
```

## Stop an effect

For CLI effects, press `Ctrl+C`.

For the web UI, use `STOP FX` or `LIGHTS OFF`.

## Notes

LIFX LAN traffic uses UDP port `56700`.
