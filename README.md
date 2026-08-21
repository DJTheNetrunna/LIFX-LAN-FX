# LIFX-LAN-FX

Local LIFX lighting effects for the Fedora Linux console using the LIFX LAN protocol.

No cloud API token is required. The controller discovers compatible LIFX bulbs on your local Wi-Fi and sends LIFX LAN packets directly over UDP.

## Features

- Fedora console friendly
- Pure Python standard library for the core controller
- Automatic local bulb discovery
- One- or multi-bulb support
- Dozens of custom effects
- Natural, energy, cyber, horror, experimental, and after-dark effect groups
- Two-bulb choreography such as chase, clash, portal, and cross-pulse
- Full-spectrum color wheel with brightness and white-temperature controls
- Select and control individual bulbs or all lights together
- Touch-friendly local web controller with discovery refresh and live status
- No LIFX cloud token required

## Quick start on Fedora

```bash
sudo dnf install -y python3 git
git clone https://github.com/DJTheNetrunna/LIFX-LAN-FX.git
cd LIFX-LAN-FX
./install-fedora.sh
lifxfx list
lifxfx discover
lifxfx plasma
```

Your Fedora computer and LIFX bulbs must be on the same local network.

To launch the web controller:

```bash
lifxfx-web
```

Then open:

```text
http://127.0.0.1:8080
```

## Example effects

```bash
lifxfx fire
lifxfx storm
lifxfx plasma
lifxfx awakening
lifxfx cyber
lifxfx haunted
lifxfx entropy
lifxfx redroom
lifxfx afterdark
```

Stop a looping effect with `Ctrl+C`.

Turn discovered lights off with:

```bash
lifxfx off
```

## Safety

Some effects contain rapid brightness changes or flashing. Avoid strobe-like effects around anyone with photosensitive epilepsy or sensitivity to flashing light.

## Compatibility

The project targets color-capable LIFX bulbs that support the LIFX LAN protocol. The controller uses only Python's standard library and does not require a cloud account or API token.

## Documentation

- `docs/effects.md` — effect catalog
- `docs/fedora-setup.md` — Fedora installation and troubleshooting

## Project layout

```text
LIFX-LAN-FX/
├── lifxfx.py
├── lifx-web.py
├── install-fedora.sh
├── README.md
├── LICENSE
├── .gitignore
└── docs/
    ├── effects.md
    └── fedora-setup.md
```

## Disclaimer

This is an unofficial community project and is not affiliated with or endorsed by LIFX.

## License

MIT
