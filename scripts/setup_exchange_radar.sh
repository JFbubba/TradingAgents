#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/root/TradingAgents}"
DATABASE_PATH="${DATABASE_PATH:-storage/events.sqlite}"
ALERT_MIN_SCORE="${ALERT_MIN_SCORE:-70}"
SERVICE_NAME="exchange-intel-radar"
PYTHON_BIN="${PROJECT_DIR}/.venv/bin/python3"

require_root() {
  if [ "$(id -u)" -ne 0 ]; then
    echo "Run this script as root on the VPS."
    exit 1
  fi
}

read_secret() {
  local var_name="$1"
  local prompt="$2"
  local current_value="${!var_name:-}"
  if [ -n "$current_value" ]; then
    return 0
  fi
  read -r -s -p "$prompt: " value
  echo
  export "$var_name=$value"
}

install_os_packages() {
  apt update
  apt install -y git python3 python3-venv python3-pip sqlite3 ca-certificates curl
}

ensure_repo() {
  if [ -d "$PROJECT_DIR/.git" ]; then
    cd "$PROJECT_DIR"
    git pull
  else
    mkdir -p "$(dirname "$PROJECT_DIR")"
    git clone https://github.com/JFbubba/TradingAgents.git "$PROJECT_DIR"
    cd "$PROJECT_DIR"
  fi
}

install_python_deps() {
  cd "$PROJECT_DIR"
  python3 -m venv .venv
  "$PYTHON_BIN" -m pip install --upgrade pip
  "$PYTHON_BIN" -m pip install -r requirements.txt
}

write_env_file() {
  read_secret TELEGRAM_BOT_TOKEN "Paste TELEGRAM_BOT_TOKEN"
  read_secret TELEGRAM_CHAT_ID "Paste TELEGRAM_CHAT_ID"

  cat > "${PROJECT_DIR}/.env" << EOF_ENV
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
DATABASE_PATH=${DATABASE_PATH}
ALERT_MIN_SCORE=${ALERT_MIN_SCORE}
EOF_ENV

  chmod 600 "${PROJECT_DIR}/.env"
}

test_telegram() {
  cd "$PROJECT_DIR"
  "$PYTHON_BIN" - << 'EOF_PY'
from dotenv import load_dotenv
import os
import requests

load_dotenv('/root/TradingAgents/.env')
token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

if not token or not chat_id:
    raise SystemExit('Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID')

response = requests.post(
    f'https://api.telegram.org/bot{token}/sendMessage',
    json={
        'chat_id': chat_id,
        'text': 'TradingAgents Radar: Telegram test OK.'
    },
    timeout=20,
)
print(response.status_code)
print(response.text)
response.raise_for_status()
EOF_PY
}

run_once() {
  cd "$PROJECT_DIR"
  "$PYTHON_BIN" exchange_intel_radar.py
}

install_systemd_timer() {
  cat > "/etc/systemd/system/${SERVICE_NAME}.service" << EOF_SERVICE
[Unit]
Description=TradingAgents Exchange Intel Radar
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
WorkingDirectory=${PROJECT_DIR}
EnvironmentFile=${PROJECT_DIR}/.env
ExecStart=${PYTHON_BIN} ${PROJECT_DIR}/exchange_intel_radar.py
EOF_SERVICE

  cat > "/etc/systemd/system/${SERVICE_NAME}.timer" << EOF_TIMER
[Unit]
Description=Run TradingAgents Exchange Intel Radar every 5 minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=5min
Unit=${SERVICE_NAME}.service
Persistent=true

[Install]
WantedBy=timers.target
EOF_TIMER

  systemctl daemon-reload
  systemctl enable --now "${SERVICE_NAME}.timer"
}

show_status() {
  systemctl status "${SERVICE_NAME}.timer" --no-pager || true
  echo
  echo "Logs: journalctl -u ${SERVICE_NAME}.service -n 80 --no-pager"
  echo "Manual run: cd ${PROJECT_DIR} && ${PYTHON_BIN} exchange_intel_radar.py"
}

main() {
  require_root
  install_os_packages
  ensure_repo
  install_python_deps
  write_env_file
  test_telegram
  run_once
  install_systemd_timer
  show_status
}

main "$@"
