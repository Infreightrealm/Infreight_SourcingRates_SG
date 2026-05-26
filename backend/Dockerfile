FROM python:3.12-slim

# Install system dependencies for Playwright + VNC/noVNC HITL
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    # VNC/noVNC dependencies
    xvfb \
    x11vnc \
    novnc \
    websockify \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# ── Install real Google Chrome Stable ──────────────────────────────────────
# DataDome hard-blocks Patchright's bundled Chromium in production.
# Real Chrome is indistinguishable from a normal user browsing session.
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (for ONE connector which uses standard Playwright)
RUN playwright install chromium

# Install Patchright Chromium (fallback, but we prefer real Chrome for anti-bot carriers)
RUN patchright install chromium

# Copy application code
COPY . .

# Set display for Xvfb
ENV DISPLAY=:99

# Expose port (nginx reverse proxy handles routing)
EXPOSE 8000

# Start all services via supervisord
CMD ["supervisord", "-c", "/app/supervisord.conf"]
