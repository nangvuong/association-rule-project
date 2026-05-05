#!/bin/bash
# start.sh – Khởi động PostgreSQL (Docker) và Flask app

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Association Rule Mining – Web Demo"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Khởi động PostgreSQL qua Docker Compose (chỉ service db)
echo ""
echo "▶ Khởi động PostgreSQL..."
docker compose up -d db

# 2. Chờ Postgres sẵn sàng
echo "  Chờ PostgreSQL khởi động..."
until docker compose exec -T db pg_isready -U arm_user -d arm_db -q 2>/dev/null; do
  sleep 1
done
echo "  ✓ PostgreSQL sẵn sàng"

# 3. Cài dependencies vào venv nếu chưa có
if [ ! -f ".venv/bin/flask" ]; then
  echo ""
  echo "▶ Cài đặt web dependencies..."
  .venv/bin/pip install flask flask-sqlalchemy psycopg2-binary flask-cors -q
  echo "  ✓ Đã cài xong"
fi

# 4. Chạy Flask
echo ""
echo "▶ Khởi động Flask trên http://localhost:5000"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
DATABASE_URL="postgresql://arm_user:arm_password@localhost:5432/arm_db" \
  .venv/bin/python web/app.py
