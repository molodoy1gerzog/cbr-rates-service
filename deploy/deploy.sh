#!/usr/bin/env bash
set -euo pipefail

APP_DIR=/opt/cbr-rates
SRC="$APP_DIR/src"

echo ">>> Updating code"
sudo -u cbr git -C "$SRC" pull --ff-only

echo ">>> Building and starting container"
cd "$SRC"
sudo docker compose up -d --build --wait --wait-timeout 120

echo ">>> Installing nginx config"
sudo install -m 644 "$SRC/deploy/nginx/cbr-rates.conf" \
    /etc/nginx/sites-available/cbr-rates

sudo nginx -t
sudo systemctl reload nginx

echo ">>> Checking health"
for attempt in {1..10}; do
    if curl --fail --silent --show-error --max-time 2 \
        http://127.0.0.1/health > /dev/null; then
        echo "OK: application responded successfully"
        exit 0
    fi
    sleep 1
done

echo "ERROR: application did not pass health check" >&2
sudo docker compose logs --tail 40 app

exit 1