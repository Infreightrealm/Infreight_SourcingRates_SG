#!/bin/bash
set -e

echo "Starting Infreight Sourcing Backend installation for Raspberry Pi 400 (ARM64)..."

# 1. Update packages and install dependencies
echo "Updating apt packages..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip curl

# Install dependencies required by Chromium/Playwright on Debian-based systems
echo "Installing Chromium system dependencies..."
sudo apt install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2

# 2. Setup Python Virtual Environment
echo "Setting up Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# 3. Install Python requirements
echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Install Patchright (ARM64 chromium)
echo "Installing Patchright browsers..."
patchright install chromium
patchright install-deps chromium

# 5. Download and install Cloudflared (ARM64)
echo "Installing Cloudflare Tunnels (cloudflared)..."
if ! command -v cloudflared &> /dev/null; then
    curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
    sudo dpkg -i cloudflared.deb
    rm cloudflared.deb
    echo "cloudflared installed successfully."
else
    echo "cloudflared is already installed."
fi

# 6. Setup systemd service
echo "Setting up systemd service for the backend..."
SERVICE_FILE="/etc/systemd/system/infreight-backend.service"
sudo cp infreight-backend.service $SERVICE_FILE

# Fix the paths in the service file dynamically based on current directory
CURRENT_DIR=$(pwd)
sudo sed -i "s|/home/pi/Infreight_Sourcing_New/backend|$CURRENT_DIR|g" $SERVICE_FILE

sudo systemctl daemon-reload
sudo systemctl enable infreight-backend.service

echo "================================================================="
echo "Installation Complete!"
echo "Next steps:"
echo "1. Run 'sudo systemctl start infreight-backend.service' to start the backend."
echo "2. Run 'cloudflared tunnel --url http://localhost:8000' to create a free temporary tunnel."
echo "   (It will print a https://something.trycloudflare.com URL that you can use in your frontend!)"
echo "================================================================="
