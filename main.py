import os, subprocess, threading, time, re

# ── Environment ──────────────────────────────────────────
os.environ['DISPLAY'] = ':1'
os.environ['HOME'] = '/root'
os.environ['DBUS_SESSION_BUS_ADDRESS'] = 'autolaunch:'

def run(cmd):
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def popen(cmd, **kwargs):
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kwargs)

print("⏳ Starting desktop environment...")

# ── Writable dirs for Firefox/dconf ──────────────────────
run("mkdir -p /root/.config/ibus/bus")
run("mkdir -p /root/.cache/dconf")
run("chmod -R 777 /root/.config /root/.cache")

# ── Start virtual display ─────────────────────────────────
popen(['Xvfb', ':1', '-screen', '0', '1280x800x24', '-ac'])
time.sleep(2)
print("✅ Virtual display started")

# ── Start DBus ────────────────────────────────────────────
run("dbus-launch --auto-syntax")
time.sleep(1)

# ── Start VNC server ──────────────────────────────────────
popen([
    'x11vnc',
    '-display', ':1',
    '-nopw',
    '-listen', 'localhost',
    '-forever',
    '-shared',
    '-noxdamage',
    '-noxfixes',
    '-noxrecord',
    '-quiet'
])
time.sleep(2)
print("✅ VNC server started")

# ── Start XFCE desktop ────────────────────────────────────
popen(['startxfce4'], env={**os.environ, 'DISPLAY': ':1'})
time.sleep(6)
print("✅ XFCE desktop started")

# ── Desktop tweaks ────────────────────────────────────────
run("DISPLAY=:1 xfconf-query -c xfwm4 -p /general/use_compositing -s false")
run("DISPLAY=:1 xfconf-query -c xsettings -p /Net/ThemeName -s 'Arc-Dark'")
run("DISPLAY=:1 xfconf-query -c xsettings -p /Net/IconThemeName -s 'Papirus-Dark'")
run("DISPLAY=:1 xfconf-query -c xsettings -p /Gtk/FontName -s 'Roboto 11'")
run("DISPLAY=:1 xset s off")
run("DISPLAY=:1 xset s noblank")
run("DISPLAY=:1 xset -dpms")

# ── Keep awake thread ─────────────────────────────────────
def keep_awake():
    while True:
        subprocess.run(
            ['xdotool', 'mousemove_relative', '--', '1', '0'],
            env={'DISPLAY': ':1'},
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(30)

threading.Thread(target=keep_awake, daemon=True).start()

# ── Start noVNC ───────────────────────────────────────────
popen(['websockify', '--web', '/opt/novnc', '6080', 'localhost:5900'])
time.sleep(3)
print("✅ noVNC started on port 6080")

# ── Start Cloudflare tunnel ───────────────────────────────
print("🚀 Starting Cloudflare tunnel...")
cf = subprocess.Popen(
    ['cloudflared', 'tunnel', '--url', 'http://localhost:6080'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

url_found = False
for _ in range(90):
    line = cf.stderr.readline().decode('utf-8', errors='ignore').strip()
    if line:
        print(line)
    match = re.search(r'https://[a-z0-9\-]+\.trycloudflare\.com', line)
    if match:
        url = match.group(0)
        print(f"\n{'='*50}")
        print(f"✅ YOUR DESKTOP IS READY!")
        print(f"🌐 Open this in your browser:")
        print(f"\n   {url}/vnc.html\n")
        print(f"{'='*50}\n")
        url_found = True
        break
    time.sleep(1)

if not url_found:
    print("❌ Could not get Cloudflare URL - check logs above")

# ── Launch Firefox ────────────────────────────────────────
time.sleep(2)
subprocess.Popen(
    ['firefox', '--display=:1', '--no-sandbox'],
    env={**os.environ, 'DISPLAY': ':1', 'HOME': '/root'},
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
print("✅ Firefox launched")

# ── Keep alive ────────────────────────────────────────────
print("⏱️  Session will last up to 6 hours")
while True:
    time.sleep(5)
