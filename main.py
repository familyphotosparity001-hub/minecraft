import os, subprocess, threading, time, re, sys

# Fix - use runner's actual home not /root
HOME = os.path.expanduser('~')  # gets actual home = /home/runner
os.environ['DISPLAY'] = ':1'
os.environ['HOME'] = HOME
os.environ['XDG_RUNTIME_DIR'] = f'/tmp/runtime-runner'

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"[RUN] {cmd}")
    if result.stdout: print(result.stdout)
    if result.stderr: print(result.stderr)
    return result

def popen(cmd, **kwargs):
    print(f"[START] {cmd}")
    return subprocess.Popen(cmd, **kwargs)

sys.stdout.flush()
print("🔵 Step 1: Creating dirs...")
sys.stdout.flush()
run(f"mkdir -p {HOME}/.config/ibus/bus")
run(f"mkdir -p {HOME}/.cache/dconf")
run(f"chmod -R 777 {HOME}/.config {HOME}/.cache")
run("mkdir -p /tmp/runtime-runner")
run("chmod 700 /tmp/runtime-runner")

print("🔵 Step 2: Starting Xvfb...")
sys.stdout.flush()
xvfb = subprocess.Popen(
    ['Xvfb', ':1', '-screen', '0', '1280x800x24', '-ac'],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
time.sleep(2)
print(f"Xvfb PID: {xvfb.pid}, running: {xvfb.poll() is None}")
sys.stdout.flush()

print("🔵 Step 3: Starting x11vnc...")
sys.stdout.flush()
vnc = subprocess.Popen(
    ['x11vnc', '-display', ':1', '-nopw', '-listen', 'localhost', '-forever', '-shared', '-quiet'],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
time.sleep(2)
print(f"x11vnc PID: {vnc.pid}, running: {vnc.poll() is None}")
sys.stdout.flush()

print("🔵 Step 4: Starting XFCE...")
sys.stdout.flush()
xfce = subprocess.Popen(
    ['startxfce4'],
    env={**os.environ, 'DISPLAY': ':1', 'HOME': HOME},
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
time.sleep(6)
print(f"XFCE PID: {xfce.pid}, running: {xfce.poll() is None}")
sys.stdout.flush()

print("🔵 Step 5: Starting noVNC...")
sys.stdout.flush()
novnc = subprocess.Popen(
    ['websockify', '--web', '/opt/novnc', '6080', 'localhost:5900'],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
time.sleep(3)
print(f"noVNC PID: {novnc.pid}, running: {novnc.poll() is None}")
sys.stdout.flush()

print("🔵 Step 6: Starting Cloudflare tunnel...")
sys.stdout.flush()
cf = subprocess.Popen(
    ['cloudflared', 'tunnel', '--url', 'http://localhost:6080'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

url_found = False
for i in range(90):
    line = cf.stderr.readline().decode('utf-8', errors='ignore').strip()
    if line:
        print(f"[CF] {line}")
        sys.stdout.flush()
    match = re.search(r'https://[a-z0-9\-]+\.trycloudflare\.com', line)
    if match:
        url = match.group(0)
        print(f"\n{'='*50}")
        print(f"✅ YOUR DESKTOP IS READY!")
        print(f"🌐 {url}/vnc.html")
        print(f"{'='*50}\n")
        sys.stdout.flush()
        url_found = True
        break
    time.sleep(1)

if not url_found:
    print("❌ Cloudflare tunnel failed")
    sys.stdout.flush()

print("🔵 Step 7: Launching Firefox...")
sys.stdout.flush()
subprocess.Popen(
    ['firefox', '--display=:1', '--no-sandbox'],
    env={**os.environ, 'DISPLAY': ':1', 'HOME': HOME},
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)

print("✅ All done! Keeping alive...")
sys.stdout.flush()
while True:
    time.sleep(5)
