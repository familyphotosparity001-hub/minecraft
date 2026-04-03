  # @title Desktop Initialization Block
import os, subprocess, threading, time, re

# Silence all output
os.environ['DISPLAY'] = ':1'

def run(cmd): subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def popen(cmd, **kwargs): return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kwargs)

print("⏳ Setting up your desktop, this might take a few minutes, grab yourself a Coffee meanwhile...")

run("apt-get update -q")
run("apt-get install -y xfce4 x11vnc xvfb wget arc-theme papirus-icon-theme fonts-roboto xdotool --fix-missing -q")
run("pip install websockify -q")

if not os.path.exists('/opt/novnc'):
    run("git clone https://github.com/novnc/noVNC.git /opt/novnc -q")

if not os.path.exists('/opt/firefox'):
    run("wget -q 'https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US' -O firefox.tar.xz")
    run("tar -xJf firefox.tar.xz -C /opt/")
    run("ln -sf /opt/firefox/firefox /usr/local/bin/firefox")

if not os.path.exists('/usr/local/bin/cloudflared'):
    run("wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /usr/local/bin/cloudflared")
    run("chmod +x /usr/local/bin/cloudflared")

popen(['Xvfb', ':1', '-screen', '0', '1280x800x24'])
time.sleep(1)
popen(['x11vnc', '-display', ':1', '-nopw', '-listen', 'localhost', '-forever', '-shared', '-ncache', '10', '-noxdamage'])
time.sleep(1)
popen(['startxfce4'], env={**os.environ, 'DISPLAY': ':1'})
time.sleep(3)

run("DISPLAY=:1 xfconf-query -c xfwm4 -p /general/use_compositing -s false")
run("DISPLAY=:1 xfconf-query -c xsettings -p /Net/ThemeName -s 'Arc-Dark'")
run("DISPLAY=:1 xfconf-query -c xsettings -p /Net/IconThemeName -s 'Papirus-Dark'")
run("DISPLAY=:1 xfconf-query -c xsettings -p /Gtk/FontName -s 'Roboto 11'")
run("DISPLAY=:1 xset s off && DISPLAY=:1 xset s noblank")

def keep_awake():
    while True:
        subprocess.run(['xdotool', 'mousemove_relative', '--', '1', '0'], env={'DISPLAY': ':1'}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(30)
threading.Thread(target=keep_awake, daemon=True).start()

popen(['websockify', '--web', '/opt/novnc', '6080', 'localhost:5900'])
time.sleep(2)

cf = subprocess.Popen(['cloudflared', 'tunnel', '--url', 'http://localhost:6080'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
for _ in range(30):
    line = cf.stderr.readline().decode()
    match = re.search(r'https://[a-z0-9\-]+\.trycloudflare\.com', line)
    if match:
        print(f"\n✅ Your desktop is ready! Open this link:\n\n{match.group(0)}/vnc.html\n")
        break
    time.sleep(1)





!wget -q "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US" -O firefox.tar.xz
!tar -xJf firefox.tar.xz -C /opt/
!ln -sf /opt/firefox/firefox /usr/local/bin/firefox
print("Firefox installed")
import subprocess
subprocess.Popen(['/opt/firefox/firefox'], env={'DISPLAY': ':1', 'HOME': '/root'})



import time
while True:
  time.sleep(5)
