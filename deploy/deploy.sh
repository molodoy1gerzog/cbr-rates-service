#!/usr/bin/env bash
set -euo pipefail

APP_DIR=/opt/cbr-rates
SRC="$APP_DIR/src"

echo ">>> Updating code"
sudo -u cbr git -C "$SRC" pull --ff-only

echo ">>> Installing dependencies"
sudo -u cbr "$APP_DIR/venv/bin/pip" install \
    -r "$SRC/requirements.txt"

echo ">>> Installing service config"
sudo install -m 644 "$SRC/deploy/cbr-rates.service" \
    /etc/systemd/system/cbr-rates.service

sudo systemctl daemon-reload

echo ">>> Installing nginx config"
sudo install -m 644 "$SRC/deploy/nginx/cbr-rates.conf" \
    /etc/nginx/sites-available/cbr-rates

sudo nginx -t
sudo systemctl reload nginx

echo ">>> Restarting service"
sudo systemctl restart cbr-rates

echo ">>> Checking health"
for attempt in {1..10}; do
    if curl --fail --silent --show-error --max-time 2 \
        http://127.0.0.1:8000/health > /dev/null; then
        echo "OK: application responded successfully"
        exit 0
    fi
    sleep 1
done

echo "ERROR: application did not pass health check" >&2
sudo journalctl -u cbr-rates -n 20 --no-pager
exit 1