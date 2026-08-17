# LIFX-LAN-FX

Local LIFX lighting effects for Android/Termux using the LIFX LAN protocol.

No cloud API token is required. The controller discovers compatible LIFX bulbs on your local Wi-Fi and sends LIFX LAN packets directly over UDP.

## Features

- Android + Termux friendly
- Pure Python standard library for the core controller
- Automatic local bulb discovery
- One- or multi-bulb support
- Dozens of custom effects
- Natural, energy, cyber, horror, experimental, and after-dark effect groups
- Two-bulb choreography such as chase, clash, portal, and cross-pulse
- Touch-friendly local web controller
- No LIFX cloud token required

## Quick start on Android

```bash
pkg update
pkg install python git -y
git clone https://github.com/DJTheNetrunna/LIFX-LAN-FX.git
cd LIFX-LAN-FX
python lifxfx.py list
python lifxfx.py plasma
```

Your phone and LIFX bulbs must be on the same local Wi-Fi network.

To launch the web controller:

```bash
python lifx-web.py
```

Then open:

```text
http://127.0.0.1:8080
```

## Example effects

```bash
python lifxfx.py fire
python lifxfx.py storm
python lifxfx.py plasma
python lifxfx.py awakening
python lifxfx.py cyber
python lifxfx.py haunted
python lifxfx.py entropy
python lifxfx.py redroom
python lifxfx.py afterdark
```

Stop a looping effect with `Ctrl+C`.

Turn discovered lights off with:

```bash
python lifxfx.py off
```

## Safety

Some effects contain rapid brightness changes or flashing. Avoid strobe-like effects around anyone with photosensitive epilepsy or sensitivity to flashing light.

## Compatibility

The project targets color-capable LIFX bulbs that support the LIFX LAN protocol. It was initially developed and tested from Android/Termux against a full-color LIFX Mini.

## Documentation

- `docs/effects.md` — effect catalog
- `docs/termux-setup.md` — Android/Termux setup

## Project layout

```text
LIFX-LAN-FX/
├── lifxfx.py
├── lifx-web.py
├── README.md
├── LICENSE
├── .gitignore
└── docs/
    ├── effects.md
    └── termux-setup.md
```

## Disclaimer

This is an unofficial community project and is not affiliated with or endorsed by LIFX.

## License

MIT
