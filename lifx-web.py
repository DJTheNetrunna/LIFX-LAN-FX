#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import html
import os
import subprocess
import sys

HOST = "127.0.0.1"
PORT = 8080
ROOT = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(ROOT, "lifxfx.py")

GROUPS = {
    "Natural": ["fire", "campfire", "candle", "storm", "ocean", "aurora"],
    "Energy / Sci-Fi": ["plasma", "reactor", "tesla", "portal", "warp"],
    "Aura / Cyber": ["blueaura", "redaura", "goldaura", "violetaura", "awakening", "cyber", "synthwave", "matrix", "glitch"],
    "Horror / Experimental": ["heartbeat", "haunted", "failinglight", "randomwalk", "entropy"],
    "After Dark": ["redroom", "desire", "slowheat", "tease", "build", "afterdark"],
    "Multi-bulb": ["chase", "clash", "crosspulse"],
}

current_process = None
current_effect = "None"


def stop_effect():
    global current_process, current_effect
    if current_process is not None:
        try:
            current_process.terminate()
            current_process.wait(timeout=1)
        except Exception:
            try:
                current_process.kill()
            except Exception:
                pass
    current_process = None
    current_effect = "None"


def start_effect(effect):
    global current_process, current_effect
    stop_effect()
    current_process = subprocess.Popen(
        [sys.executable, ENGINE, effect],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    current_effect = effect


def lights_off():
    global current_effect
    stop_effect()
    subprocess.Popen([sys.executable, ENGINE, "off"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    current_effect = "OFF"


def render_page():
    sections = []
    for title, effects in GROUPS.items():
        buttons = "".join(
            f'''<form method="POST"><input type="hidden" name="effect" value="{html.escape(effect)}"><button class="fx">{html.escape(effect.upper())}</button></form>'''
            for effect in effects
        )
        sections.append(f"<section><h2>{html.escape(title)}</h2><div class='grid'>{buttons}</div></section>")

    return f'''<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>LIFX-LAN-FX</title>
<style>
:root{{color-scheme:dark}}*{{box-sizing:border-box}}body{{margin:0;padding:18px;background:radial-gradient(circle at top,#35115c 0%,#09050f 38%,#030204 100%);color:#eee;font-family:system-ui,sans-serif}}header{{position:sticky;top:0;z-index:10;padding:16px;margin:-18px -18px 20px;background:rgba(5,3,8,.94);backdrop-filter:blur(12px);border-bottom:1px solid #44245f}}h1{{margin:0 0 7px;font-size:25px}}.status{{color:#c89cff;font-size:14px}}section{{margin-bottom:27px}}h2{{font-size:17px;color:#dcbaff;margin-bottom:10px}}.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:9px}}form{{margin:0}}button{{width:100%;border:0;border-radius:12px;padding:15px 8px;font-weight:700;color:white;cursor:pointer;touch-action:manipulation}}.fx{{background:linear-gradient(135deg,#5d258d,#a32173)}}.fx:active{{transform:scale(.96)}}.controls{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:12px}}.stop{{background:#444}}.off{{background:#9c182d}}footer{{text-align:center;color:#777;font-size:12px;padding:30px 0}}
</style>
</head>
<body>
<header>
<h1>LIFX-LAN-FX</h1>
<div class="status">Active: <strong>{html.escape(current_effect.upper())}</strong></div>
<div class="controls">
<form method="POST"><input type="hidden" name="action" value="stop"><button class="stop">STOP FX</button></form>
<form method="POST"><input type="hidden" name="action" value="off"><button class="off">LIGHTS OFF</button></form>
</div>
</header>
{''.join(sections)}
<footer>Local LIFX LAN Controller</footer>
</body>
</html>'''


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = render_page().encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data = parse_qs(self.rfile.read(length).decode())
        effect = data.get("effect", [None])[0]
        action = data.get("action", [None])[0]

        allowed = {name for effects in GROUPS.values() for name in effects}
        if action == "stop":
            stop_effect()
        elif action == "off":
            lights_off()
        elif effect in allowed:
            start_effect(effect)

        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), Handler)
    print(f"Open http://{HOST}:{PORT}")
    print("Ctrl+C stops the web controller.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        stop_effect()
    finally:
        server.server_close()
