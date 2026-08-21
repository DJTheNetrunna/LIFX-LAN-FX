# Fedora Console Setup

## Install

```bash
sudo dnf install -y python3 git
git clone https://github.com/DJTheNetrunna/LIFX-LAN-FX.git
cd LIFX-LAN-FX
chmod +x install-fedora.sh
./install-fedora.sh
```

The installer creates user-local commands in `~/.local/bin`; it does not need root access.

## Discover and control bulbs

```bash
lifxfx list
lifxfx discover
lifxfx plasma
lifxfx off
```

The computer and bulbs must be on the same LAN. LIFX LAN uses UDP port `56700`.

If broadcast discovery is blocked, use the bulb's IP address directly:

```bash
lifxfx plasma --ip 192.168.1.50
lifxfx chase --ip 192.168.1.50 --ip 192.168.1.51
```

To allow inbound LIFX replies through firewalld on a trusted home network:

```bash
sudo firewall-cmd --add-port=56700/udp
sudo firewall-cmd --permanent --add-port=56700/udp
```

Do not open that port on an untrusted public network.

## Web controller

```bash
lifxfx-web
```

Open `http://127.0.0.1:8080` on the Fedora computer. Use `Ctrl+C` to stop it.
