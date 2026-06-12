# ────────────────────────────────────────────────────────────────
#  RSA Digital Signature App — Docker Image
#  Access via browser at http://localhost:8080 (noVNC)
# ────────────────────────────────────────────────────────────────
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# ── System dependencies ─────────────────────────────────────────
# All GUI, VNC, and Qt runtime libraries in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Virtual display & VNC
    xvfb \
    x11vnc \
    novnc \
    websockify \
    openbox \
    # OpenGL / EGL (required by PyQt6)
    libgl1 \
    libegl1 \
    libegl-mesa0 \
    libopengl0 \
    libglvnd0 \
    libglx0 \
    libglx-mesa0 \
    # Qt runtime
    libglib2.0-0 \
    libdbus-1-3 \
    libxkbcommon-x11-0 \
    libxkbcommon0 \
    # XCB platform plugin dependencies
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xfixes0 \
    libxcb-shape0 \
    libxcb-cursor0 \
    libxcb-util1 \
    libxcb1 \
    && rm -rf /var/lib/apt/lists/*

# noVNC index alias
RUN ln -sf /usr/share/novnc/vnc.html /usr/share/novnc/index.html

# ── Python dependencies ─────────────────────────────────────────
WORKDIR /app

COPY rsa_app/requirements.txt /app/rsa_app/requirements.txt

# Pre-downloaded wheels (avoids slow in-container pip download)
COPY wheels /app/wheels

RUN pip install --no-cache-dir --no-index \
    --find-links=/app/wheels \
    -r rsa_app/requirements.txt \
    && rm -rf /app/wheels

# ── Application source ──────────────────────────────────────────
COPY rsa_app/ /app/rsa_app/

# ── Startup script ──────────────────────────────────────────────
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# ── Runtime config ──────────────────────────────────────────────
ENV DISPLAY=:99
ENV QT_QPA_PLATFORM=xcb

EXPOSE 8080 5900

ENTRYPOINT ["/app/entrypoint.sh"]
