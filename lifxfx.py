#!/usr/bin/env python3

import math
import argparse
import ipaddress
import random
import socket
import struct
import sys
import time

PORT = 56700
SOURCE = random.randint(2, 0xFFFFFFFF)
SEQ = 0


def hsv(degrees):
    return int((degrees % 360) / 360 * 65535)


def make_packet(msg_type, payload=b"", tagged=True):
    global SEQ
    size = 36 + len(payload)
    flags = 1024 | (1 << 12)
    if tagged:
        flags |= (1 << 13)

    header = struct.pack("<HHI", size, flags, SOURCE)
    header += b"\x00" * 8
    header += b"\x00" * 6
    header += b"\x00"
    header += struct.pack("<B", SEQ)
    SEQ = (SEQ + 1) % 256
    header += b"\x00" * 8
    header += struct.pack("<H", msg_type)
    header += b"\x00" * 2
    return header + payload


def discover(timeout=2.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(0.30)
    sock.bind(("", 0))
    packet = make_packet(2)

    broadcasts = {"255.255.255.255", "192.168.0.255", "192.168.1.255", "10.0.0.255"}
    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None, socket.AF_INET):
            address = info[4][0]
            if not address.startswith("127."):
                # Most home LANs use /24 networks. Directed broadcasts improve
                # discovery on Fedora systems with more than one interface.
                broadcasts.add(str(ipaddress.ip_network(f"{address}/24", strict=False).broadcast_address))
    except OSError:
        pass

    for addr in sorted(broadcasts):
        try:
            sock.sendto(packet, (addr, PORT))
        except OSError:
            pass

    devices = set()
    end = time.time() + timeout
    while time.time() < end:
        try:
            _, addr = sock.recvfrom(2048)
            devices.add(addr[0])
        except socket.timeout:
            continue
        except OSError:
            break
    sock.close()
    return sorted(devices)


def send(ip, msg_type, payload=b""):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(make_packet(msg_type, payload), (ip, PORT))
    sock.close()


def power(ip, state=True):
    send(ip, 21, struct.pack("<H", 65535 if state else 0))


def color(ip, hue, sat=65535, bri=65535, kelvin=3500, duration=100):
    payload = struct.pack(
        "<BHHHHI",
        0,
        int(hue) % 65536,
        max(0, min(65535, int(sat))),
        max(0, min(65535, int(bri))),
        max(1500, min(9000, int(kelvin))),
        max(0, int(duration)),
    )
    send(ip, 102, payload)


def all_color(devices, hue, sat=65535, bri=65535, kelvin=3500, duration=100):
    for ip in devices:
        color(ip, hue, sat, bri, kelvin, duration)


def wait(seconds):
    time.sleep(max(0.001, seconds))


def flash(devices, hue=0, sat=0, bri=65535, kelvin=7000, on=.05, off=.07):
    all_color(devices, hue, sat, bri, kelvin, 0)
    wait(on)
    all_color(devices, hue, sat, 500, kelvin, 20)
    wait(off)


def pulse(devices, hue, sat=65535, low=2500, high=55000, steps=24, delay=.06):
    for i in range(steps):
        x = i / max(1, steps - 1)
        bri = low + (high - low) * math.sin(x * math.pi)
        all_color(devices, hue, sat, bri, 3500, int(delay * 1000))
        wait(delay)


# ---------- Natural ----------

def fire(devices):
    while True:
        for ip in devices:
            color(ip, hsv(random.randint(0, 38)), random.randint(50000, 65535), random.randint(16000, 62000), 2400, random.randint(40, 150))
        wait(random.uniform(.04, .15))


def campfire(devices):
    while True:
        all_color(devices, hsv(random.randint(10, 32)), random.randint(50000, 65535), random.randint(16000, 47000), 2200, random.randint(100, 350))
        wait(random.uniform(.12, .35))


def candle(devices):
    while True:
        all_color(devices, hsv(random.randint(28, 45)), random.randint(25000, 45000), random.randint(18000, 36000), random.randint(1800, 2600), random.randint(100, 250))
        wait(random.uniform(.08, .25))


def storm(devices):
    while True:
        all_color(devices, hsv(230), 45000, 4000, 7000, 300)
        wait(random.uniform(1, 5))
        for _ in range(random.randint(1, 4)):
            flash(devices, hsv(215), 8000, 65535, 9000, random.uniform(.02, .1), random.uniform(.04, .2))


def ocean(devices):
    while True:
        pulse(devices, hsv(random.choice([180, 195, 210, 225])), 50000, 6000, 35000, 28, .10)


def aurora(devices):
    while True:
        for deg in (120, 150, 180, 210, 260, 290, 220, 160):
            all_color(devices, hsv(deg), 50000, 30000, 4000, 1800)
            wait(1.8)


# ---------- Energy / sci-fi ----------

def plasma(devices):
    while True:
        all_color(devices, hsv(random.randint(190, 310)), 65535, random.randint(18000, 62000), 5000, random.randint(30, 160))
        wait(random.uniform(.03, .15))


def reactor(devices):
    while True:
        pulse(devices, hsv(185), 55000, 8000, 45000, 25, .055)
        if random.random() < .25:
            flash(devices, hsv(180), 15000, 65535, 8500, .04, .08)


def tesla(devices):
    while True:
        wait(random.uniform(.2, 1.5))
        for _ in range(random.randint(1, 6)):
            flash(devices, hsv(random.randint(205, 235)), random.randint(5000, 25000), 65535, 9000, .025, .035)


def portal(devices):
    while True:
        for deg in list(range(250, 180, -4)) + list(range(180, 300, 4)):
            all_color(devices, hsv(deg), 65535, 40000, 4500, 80)
            wait(.07)


def warp(devices):
    delay = .35
    while True:
        all_color(devices, hsv(220), 60000, 45000, 7000, 50)
        wait(delay)
        all_color(devices, hsv(195), 30000, 8000, 7000, 50)
        wait(delay)
        delay *= .94
        if delay < .025:
            for _ in range(5):
                flash(devices, hsv(210), 5000, 65535, 9000, .03, .03)
            delay = .35


# ---------- Aura / cyber ----------

def aura(devices, base_degree):
    while True:
        all_color(devices, hsv(base_degree + random.randint(-10, 10)), 65535, random.randint(18000, 65535), 5000, random.randint(40, 130))
        wait(random.uniform(.035, .12))


def blueaura(devices): aura(devices, 220)
def redaura(devices): aura(devices, 0)
def goldaura(devices): aura(devices, 48)
def violetaura(devices): aura(devices, 280)


def awakening(devices):
    all_color(devices, hsv(230), 65535, 1000, 5000, 500)
    delay = .4
    for level in range(18):
        brightness = min(65000, 5000 + level * 3200)
        all_color(devices, hsv(random.randint(205, 235)), 65535, brightness, 5000, 80)
        wait(delay)
        all_color(devices, hsv(230), 65535, max(1000, brightness // 4), 5000, 60)
        wait(delay)
        delay = max(.04, delay * .86)
    for _ in range(5):
        flash(devices, 0, 0, 65535, 9000, .045, .045)
    aura(devices, 220)


def cyber(devices):
    palette = [180, 195, 220, 275, 300, 325]
    while True:
        all_color(devices, hsv(random.choice(palette)), 65535, random.randint(25000, 60000), 4500, random.randint(100, 450))
        wait(random.uniform(.08, .4))


def synthwave(devices):
    while True:
        for deg in (280, 300, 320, 345, 25):
            all_color(devices, hsv(deg), 60000, 36000, 4000, 1200)
            wait(1.2)


def matrix(devices):
    while True:
        all_color(devices, hsv(random.randint(105, 135)), 65535, random.randint(3000, 30000), 4000, random.randint(20, 160))
        if random.random() < .08:
            all_color(devices, hsv(120), 65535, 60000, 4000, 0)
        wait(random.uniform(.03, .2))


def glitch(devices):
    while True:
        if random.random() < .3:
            flash(devices, hsv(random.randint(0, 359)), 65535, 60000, 6000, .02, .03)
        else:
            all_color(devices, hsv(random.choice([180, 220, 290, 320])), 65535, random.randint(5000, 45000), 4500, 0)
        wait(random.uniform(.015, .25))


# ---------- Horror / experimental ----------

def heartbeat(devices):
    while True:
        for bri, pause in ((60000, .09), (3000, .12), (45000, .08), (1500, .75)):
            all_color(devices, hsv(0), 65535, bri, 3000, 40)
            wait(pause)


def haunted(devices):
    while True:
        all_color(devices, hsv(random.choice([90, 120, 180, 270, 290])), random.randint(35000, 65535), random.randint(1500, 16000), 4500, random.randint(400, 2000))
        wait(random.uniform(.5, 2.5))
        if random.random() < .1:
            flash(devices, 0, 0, 30000, 8000, .06, .2)


def failinglight(devices):
    while True:
        all_color(devices, 0, 0, 35000, 5000, 50)
        wait(random.uniform(.2, 3))
        for _ in range(random.randint(1, 7)):
            all_color(devices, 0, 0, random.choice([0, 5000, 65535]), 5000, 0)
            wait(random.uniform(.015, .12))


def randomwalk(devices):
    hue = random.randint(0, 65535)
    while True:
        hue = (hue + random.randint(-2500, 2500)) % 65536
        all_color(devices, hue, random.randint(35000, 65535), random.randint(12000, 48000), 4500, 500)
        wait(.5)


def entropy(devices):
    delay, spread = .5, 2
    while True:
        all_color(devices, hsv(220 + random.randint(-spread, spread)), 65535, random.randint(18000, 50000), 5000, int(delay * 1000))
        wait(delay)
        spread = min(180, spread + 2)
        delay = max(.025, delay * .985)
        if spread >= 180 and delay <= .03:
            delay, spread = .5, 2


# ---------- After dark ----------

def redroom(devices):
    while True:
        pulse(devices, hsv(random.randint(345, 359)), 65535, 2500, random.randint(28000, 50000), random.randint(28, 42), random.uniform(.06, .10))


def desire(devices):
    while True:
        pulse(devices, hsv(random.choice([330, 340, 350, 0, 310, 325])), random.randint(56000, 65535), random.randint(1500, 5000), random.randint(35000, 60000), random.randint(18, 32), random.uniform(.045, .09))
        wait(random.uniform(.1, .6))


def slowheat(devices):
    palette = [(275, 9000), (300, 14000), (320, 20000), (340, 28000), (355, 36000), (5, 43000), (18, 50000)]
    while True:
        for deg, bri in palette + list(reversed(palette)):
            all_color(devices, hsv(deg), 60000, bri, 3000, 1800)
            wait(1.8)


def tease(devices):
    while True:
        all_color(devices, hsv(random.choice([300, 320, 340, 355])), 65535, random.randint(800, 4000), 3000, random.randint(700, 1800))
        wait(random.uniform(.6, 2.6))
        if random.random() < .75:
            h = hsv(random.choice([325, 340, 350, 0]))
            for bri in range(5000, random.randint(38000, 60000), 4000):
                all_color(devices, h, 65535, bri, 3000, 100)
                wait(random.uniform(.035, .085))
            all_color(devices, h, 65535, 1200, 3000, 500)


def build(devices):
    delay, peak = .75, 15000
    while True:
        for _ in range(2):
            all_color(devices, hsv(random.randint(325, 359)), 65535, peak, 3000, 70)
            wait(.08)
            all_color(devices, hsv(340), 65535, 1200, 2800, 70)
            wait(.10)
        wait(delay)
        delay = max(.06, delay * .94)
        peak = min(65535, peak + 1800)
        if peak >= 64000 and delay <= .07:
            for _ in range(12):
                all_color(devices, hsv(random.choice([315, 330, 345, 355, 0])), 65535, random.randint(50000, 65535), 3500, 20)
                wait(.045)
            all_color(devices, hsv(350), 55000, 9000, 2500, 1800)
            wait(2)
            delay, peak = .75, 15000


def afterdark(devices):
    while True:
        for _ in range(6):
            all_color(devices, hsv(random.choice([290, 310, 330])), 65535, random.randint(800, 5000), 2700, 700)
            wait(random.uniform(.5, 1.5))
        for _ in range(5):
            pulse(devices, hsv(random.choice([320, 335, 350])), 65535, 1000, random.randint(28000, 46000), 16, .075)
        delay = .18
        for _ in range(30):
            all_color(devices, hsv(random.choice([305, 320, 335, 350, 0])), 65535, random.randint(38000, 65535), 3200, 30)
            wait(delay)
            all_color(devices, hsv(345), 65535, random.randint(500, 2500), 2700, 25)
            wait(delay * .6)
            delay = max(.03, delay * .94)
        all_color(devices, hsv(340), 65535, 250, 2500, 0)
        wait(random.uniform(1, 3))


# ---------- Multi-bulb ----------

def chase(devices):
    while True:
        if len(devices) == 1:
            pulse(devices, hsv(200), 65535, 3000, 55000, 18, .04)
            continue
        for ip in devices:
            for other in devices:
                color(other, hsv(220), 65535, 3000 if other != ip else 60000, 5000, 80)
            wait(.12)


def clash(devices):
    if len(devices) < 2:
        return plasma(devices)
    while True:
        color(devices[0], hsv(220), 65535, 55000, 5000, 100)
        color(devices[1], hsv(0), 65535, 55000, 3500, 100)
        wait(.3)
        for _ in range(random.randint(2, 5)):
            flash(devices, 0, 0, 65535, 9000, .035, .04)
        wait(random.uniform(.4, 1.2))


def crosspulse(devices):
    if len(devices) < 2:
        return desire(devices)
    while True:
        for index, ip in enumerate(devices):
            other = devices[(index + 1) % len(devices)]
            color(ip, hsv(random.choice([330, 345, 355])), 65535, 58000, 3000, 70)
            color(other, hsv(300), 65535, 1800, 2800, 70)
            wait(.13)


EFFECTS = {
    "fire": fire,
    "campfire": campfire,
    "candle": candle,
    "storm": storm,
    "ocean": ocean,
    "aurora": aurora,
    "plasma": plasma,
    "reactor": reactor,
    "tesla": tesla,
    "portal": portal,
    "warp": warp,
    "blueaura": blueaura,
    "redaura": redaura,
    "goldaura": goldaura,
    "violetaura": violetaura,
    "awakening": awakening,
    "cyber": cyber,
    "synthwave": synthwave,
    "matrix": matrix,
    "glitch": glitch,
    "heartbeat": heartbeat,
    "haunted": haunted,
    "failinglight": failinglight,
    "randomwalk": randomwalk,
    "entropy": entropy,
    "redroom": redroom,
    "desire": desire,
    "slowheat": slowheat,
    "tease": tease,
    "build": build,
    "afterdark": afterdark,
    "chase": chase,
    "clash": clash,
    "crosspulse": crosspulse,
}


def show_effects():
    groups = {
        "Natural": ["fire", "campfire", "candle", "storm", "ocean", "aurora"],
        "Energy / Sci-Fi": ["plasma", "reactor", "tesla", "portal", "warp"],
        "Aura / Cyber": ["blueaura", "redaura", "goldaura", "violetaura", "awakening", "cyber", "synthwave", "matrix", "glitch"],
        "Horror / Experimental": ["heartbeat", "haunted", "failinglight", "randomwalk", "entropy"],
        "After Dark": ["redroom", "desire", "slowheat", "tease", "build", "afterdark"],
        "Multi-bulb": ["chase", "clash", "crosspulse"],
    }
    print("LIFX-LAN-FX\n")
    for title, names in groups.items():
        print(title)
        print("  " + "  ".join(names))
        print()
    print("Control\n  list  off")


def main():
    parser = argparse.ArgumentParser(description="Local LIFX LAN effects controller")
    parser.add_argument("effect", nargs="?", default="list", help="effect name, list, discover, or off")
    parser.add_argument("--ip", action="append", dest="ips", help="bulb IP; repeat for multiple bulbs")
    parser.add_argument("--timeout", type=float, default=2.0, help="discovery timeout in seconds")
    args = parser.parse_args()

    if args.effect.lower() in ("list", "help"):
        show_effects()
        return

    effect = args.effect.lower()
    if args.ips:
        devices = args.ips
    else:
        print("Searching for LIFX bulbs on the local network...")
        devices = discover(args.timeout)
    if not devices:
        print("No LIFX bulbs found. Make sure this computer and the bulbs are on the same LAN.")
        print("Try a known address: lifxfx EFFECT --ip 192.168.1.50")
        return

    print("Found:", ", ".join(devices))

    if effect == "discover":
        return

    if effect == "off":
        for ip in devices:
            power(ip, False)
        print("Lights off.")
        return

    if effect not in EFFECTS:
        print("Unknown effect:", effect)
        show_effects()
        return

    for ip in devices:
        power(ip, True)
    wait(.25)

    try:
        print(f"Running {effect}. Ctrl+C to stop.")
        EFFECTS[effect](devices)
    except KeyboardInterrupt:
        print("\nEffect stopped.")


if __name__ == "__main__":
    main()
