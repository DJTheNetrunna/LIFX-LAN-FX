#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs
import colorsys, html, os, subprocess, sys
import lifxfx

HOST, PORT = "127.0.0.1", 8080
ENGINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lifxfx.py")
GROUPS = {
    "Natural": ["fire", "campfire", "candle", "storm", "ocean", "aurora"],
    "Energy / Sci-Fi": ["plasma", "reactor", "tesla", "portal", "warp"],
    "Aura / Cyber": ["blueaura", "redaura", "goldaura", "violetaura", "awakening", "cyber", "synthwave", "matrix", "glitch"],
    "Horror / Experimental": ["heartbeat", "haunted", "failinglight", "randomwalk", "entropy"],
    "After Dark": ["redroom", "desire", "slowheat", "tease", "build", "afterdark"],
    "Multi-bulb": ["chase", "clash", "crosspulse"],
}
current_process, current_effect, devices = None, "None", []
selected_devices = set()

def refresh_devices():
    global devices
    devices = lifxfx.discover(2.0)
    selected_devices.intersection_update(devices)
    if not selected_devices: selected_devices.update(devices)

def stop_effect():
    global current_process, current_effect
    if current_process:
        try:
            current_process.terminate(); current_process.wait(timeout=1)
        except Exception:
            try: current_process.kill()
            except Exception: pass
    current_process, current_effect = None, "None"

def targets(data):
    chosen = [ip for ip in data.get("device", []) if ip in devices]
    return chosen or list(devices)

def remember(chosen):
    selected_devices.clear(); selected_devices.update(chosen)

def start_effect(effect, chosen):
    global current_process, current_effect
    stop_effect()
    command = [sys.executable, ENGINE, effect]
    for ip in chosen: command.extend(["--ip", ip])
    current_process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    current_effect = effect

def set_power(chosen, state):
    global current_effect
    stop_effect()
    for ip in chosen: lifxfx.power(ip, state)
    current_effect = "ON" if state else "OFF"

def apply_color(chosen, hex_color, brightness, kelvin):
    global current_effect
    stop_effect()
    value = hex_color.lstrip("#") if len(hex_color.lstrip("#")) == 6 else "ff00aa"
    rgb = [int(value[i:i+2], 16) / 255 for i in (0, 2, 4)]
    hue, saturation, _ = colorsys.rgb_to_hsv(*rgb)
    level = max(1, min(100, int(brightness)))
    warmth = max(1500, min(9000, int(kelvin)))
    for ip in chosen:
        lifxfx.power(ip, True)
        lifxfx.color(ip, int(hue*65535), int(saturation*65535), int(level/100*65535), warmth, 250)
    current_effect = f"COLOR #{value.upper()}"

def render_page():
    bulbs = "".join(f'''<label class="bulb"><input type="checkbox" name="device" value="{html.escape(ip)}" {'checked' if ip in selected_devices else ''}><span class="orb"></span><span><strong>LIGHT {n}</strong><small>{html.escape(ip)}</small></span></label>''' for n, ip in enumerate(devices, 1)) or "<div class='empty'>No bulbs found. Check Wi-Fi, then press REFRESH.</div>"
    sections = []
    for title, effects in GROUPS.items():
        buttons = "".join(f'<button class="fx" name="effect" value="{html.escape(e)}">{html.escape(e.upper())}</button>' for e in effects)
        sections.append(f"<section><h2>{html.escape(title)}</h2><div class='grid'>{buttons}</div></section>")
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1"><title>LIFX-LAN-FX</title>
<style>
:root{{color-scheme:dark;--pink:#ff2aa3;--violet:#8b5cff;--cyan:#36dcff}}*{{box-sizing:border-box}}body{{margin:0;background:#06040a;color:#f5f2fa;font-family:Inter,system-ui,sans-serif}}.wrap{{max-width:980px;margin:auto;padding:18px}}header{{position:sticky;top:0;z-index:10;background:#06040aeb;backdrop-filter:blur(15px);border-bottom:1px solid #30243c}}h1{{font-size:25px;margin:0}}.status{{color:#d5baff;margin-top:5px;font-size:13px}}h2{{font-size:15px;letter-spacing:.08em;color:#d8c7eb;text-transform:uppercase}}.panel{{background:linear-gradient(145deg,#171020,#0c0911);border:1px solid #32243d;border-radius:20px;padding:16px;margin:18px 0;box-shadow:0 12px 40px #0008}}.bulbs{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:9px}}.bulb{{display:flex;align-items:center;gap:10px;padding:12px;border:1px solid #372942;border-radius:14px;background:#100b16;cursor:pointer}}.bulb:has(input:checked){{border-color:var(--cyan);box-shadow:0 0 18px #36dcff30}}.bulb input{{accent-color:var(--cyan)}}.orb{{width:22px;height:22px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#fff,#ff4dc4 35%,#6731ff 75%);box-shadow:0 0 14px #e13cff}}small{{display:block;color:#968aa2;margin-top:2px}}.wheel{{display:grid;grid-template-columns:minmax(130px,220px) 1fr;gap:20px;align-items:center}}input[type=color]{{width:100%;aspect-ratio:1;border:0;padding:0;border-radius:50%;overflow:hidden;background:conic-gradient(red,#ff0,#0f0,#0ff,#00f,#f0f,red);box-shadow:0 0 30px #942fff55;cursor:pointer}}input[type=color]::-webkit-color-swatch-wrapper{{padding:10px}}input[type=color]::-webkit-color-swatch,input[type=color]::-moz-color-swatch{{border:0;border-radius:50%}}.sliders label{{display:block;margin:15px 0;color:#cdbedf}}input[type=range]{{width:100%;accent-color:var(--pink)}}button{{border:0;border-radius:12px;padding:13px 10px;font-weight:800;color:#fff;cursor:pointer;background:#33283d}}button:hover{{filter:brightness(1.18)}}.apply{{width:100%;background:linear-gradient(120deg,var(--violet),var(--pink),#ff6a3d);margin-top:10px}}.controls,.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:9px}}.controls{{margin-top:12px}}.on{{background:#147c69}}.off{{background:#a51d3d}}.refresh{{background:#28558d}}.stop{{background:#4a4050}}.fx{{background:linear-gradient(135deg,#48266d,#8d226b);font-size:12px}}section{{margin:24px 0}}.empty{{color:#a99caf}}@media(max-width:560px){{.wheel{{grid-template-columns:1fr}}input[type=color]{{max-width:190px;margin:auto}}}}
</style></head><body><header><div class="wrap"><h1>LIFX-LAN-FX</h1><div class="status">ACTIVE: <strong>{html.escape(current_effect.upper())}</strong> · {len(devices)} LIGHT(S) FOUND</div></div></header>
<main class="wrap"><form method="POST"><div class="panel"><h2>Choose lights</h2><div class="bulbs">{bulbs}</div><div class="controls"><button class="on" name="action" value="on">POWER ON</button><button class="off" name="action" value="off">POWER OFF</button><button class="stop" name="action" value="stop">STOP FX</button><button class="refresh" name="action" value="refresh">REFRESH</button></div></div>
<div class="panel"><h2>Full-spectrum color lab</h2><div class="wheel"><input type="color" name="color" value="#ff00aa" aria-label="Choose color"><div class="sliders"><label>Brightness: <output id="briOut">70%</output><input id="bri" type="range" name="brightness" min="1" max="100" value="70"></label><label>White temperature: <output id="kelvinOut">3500K</output><input id="kelvin" type="range" name="kelvin" min="1500" max="9000" step="100" value="3500"></label><button class="apply" name="action" value="color">APPLY COLOR TO SELECTED</button></div></div></div>
<div class="panel"><h2>Effects</h2>{''.join(sections)}</div></form></main><script>const b=document.querySelector('#bri'),k=document.querySelector('#kelvin');b.oninput=()=>briOut.value=b.value+'%';k.oninput=()=>kelvinOut.value=k.value+'K';</script></body></html>'''

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = render_page().encode(); self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_POST(self):
        data = parse_qs(self.rfile.read(int(self.headers.get("Content-Length", 0))).decode())
        chosen = targets(data); remember(chosen)
        effect, action = data.get("effect", [None])[0], data.get("action", [None])[0]
        allowed = {name for effects in GROUPS.values() for name in effects}
        if action == "refresh": refresh_devices()
        elif action == "stop": stop_effect()
        elif action == "on": set_power(chosen, True)
        elif action == "off": set_power(chosen, False)
        elif action == "color": apply_color(chosen, data.get("color", ["#ff00aa"])[0], data.get("brightness", ["70"])[0], data.get("kelvin", ["3500"])[0])
        elif effect in allowed: start_effect(effect, chosen)
        self.send_response(303); self.send_header("Location", "/"); self.end_headers()
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    print("Discovering LIFX bulbs..."); refresh_devices()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Open http://{HOST}:{PORT}\nCtrl+C stops the web controller.")
    try: server.serve_forever()
    except KeyboardInterrupt: stop_effect()
    finally: server.server_close()
