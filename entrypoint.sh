#!/bin/bash
set -e

export DISPLAY=:99
export RESOLUTION="${RESOLUTION:-1280x800x24}"
export QT_QPA_PLATFORM=xcb
export QT_DEBUG_PLUGINS=0
export LIBGL_ALWAYS_SOFTWARE=0

echo "============================================="
echo " RSA Digital Signature App — Docker Container"
echo "============================================="

# 1. Virtual framebuffer
echo "[1/5] Starting Xvfb on display :99..."
Xvfb :99 -screen 0 "$RESOLUTION" &
sleep 1

# 2. Window manager (errors here are non-fatal)
echo "[2/5] Starting Openbox window manager..."
openbox &>/dev/null &
sleep 1

# 3. VNC server
echo "[3/5] Starting x11vnc on port 5900..."
x11vnc -display :99 -forever -shared -nopw -rfbport 5900 -quiet &
sleep 1

# 4. noVNC web server
echo "[4/5] Starting noVNC at http://localhost:8080 ..."
websockify --web=/usr/share/novnc 8080 localhost:5900 &
sleep 1

# 5. Launch the app
echo "[5/5] Launching RSA application..."
cd /app
exec python3 -m rsa_app.main
