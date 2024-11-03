#!/bin/bash

# Get the working directory where this script is located
WORKDIR="$(dirname "$(realpath "$0")")"

# Get the parent directory name to use as the service name
SERVICE_NAME="$(basename "$WORKDIR")"

# Define the service file content
SERVICE_CONTENT="[Unit]
Description=${SERVICE_NAME} Python Service
After=multi-user.target
Conflicts=getty@tty1.service

[Service]
Type=simple
WorkingDirectory=${WORKDIR}
ExecStart=/usr/bin/python3 ${WORKDIR}/main.py
StandardInput=tty-force
RuntimeMaxSec=7d
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"

# Create the service file
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
echo "$SERVICE_CONTENT" | sudo tee "$SERVICE_FILE" > /dev/null

# Reload systemd, enable, and start the service
sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}.service"
sudo systemctl start "${SERVICE_NAME}.service"

echo "Service ${SERVICE_NAME} created, enabled, and started successfully."