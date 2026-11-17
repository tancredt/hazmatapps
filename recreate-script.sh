#!/usr/bin/env bash
# deploy.sh — rebuild the stack WITHOUT wiping the database
#   ./deploy.sh                  rebuild, migrate, collectstatic, keep data
#   ./deploy.sh --import-csv     force a CSV re-import
#   ./deploy.sh --makemigrations generate migrations in the container first
#   ./deploy.sh --fresh          DESTRUCTIVE: delete db + media + static volumes
#   ./deploy.sh --fresh --yes    same, no confirmation
set -euo pipefail

FRESH=0; FORCE_IMPORT=0; DO_MAKEMIGRATIONS=0; ASSUME_YES=0
for arg in "$@"; do
  case "$arg" in
    --fresh)          FRESH=1 ;;
    --import-csv)     FORCE_IMPORT=1 ;;
    --makemigrations) DO_MAKEMIGRATIONS=1 ;;
    --yes|-y)         ASSUME_YES=1 ;;
    -h|--help)        sed -n '2,8p' "$0"; exit 0 ;;
    *) echo "Unknown option: $arg (try --help)"; exit 1 ;;
  esac
done

if [ -f .env ]; then set -a; . ./.env; set +a; fi

# web runs as DB_APP_USER; these steps need the admin role
ADMIN_ENV=(-e DB_USER="${DB_ADMIN_USER:-postgres}" -e DB_PASSWORD="${DB_ADMIN_PASSWORD:-}")

if docker compose version >/dev/null 2>&1; then
  DC=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  DC=(docker-compose)
else
  echo "❌ Docker Compose not found."; exit 1
fi

run_step() {
  local step_name="$1"; shift
  echo "------------------------------------------------------------"
  echo "🚀 $step_name"
  echo "------------------------------------------------------------"
  if "$@"; then
    echo "✅ SUCCESS: $step_name"; echo
  else
    local rc=$?
    echo "❌ FAILURE: $step_name (exit $rc)"; echo "🛑 Aborting."
    exit "$rc"
  fi
}

# 1. Only destroy data when explicitly asked
if [ "$FRESH" -eq 1 ]; then
  if [ "$ASSUME_YES" -ne 1 ]; then
    read -r -p "⚠️  --fresh deletes postgres_data, media_volume AND static_volume. Type 'yes': " reply
    [ "$reply" = "yes" ] || { echo "Aborted."; exit 1; }
  fi
  run_step "Removing containers and volumes" "${DC[@]}" down -v --remove-orphans
else
  echo "🔒 Preserving volumes (postgres_data, media_volume, static_volume)."
fi

# 2. Rebuild backend + nginx/Vue images, recreate containers, keep volumes
run_step "Building and starting containers" "${DC[@]}" up -d --build

# 3. db healthcheck + depends_on already gate this; just confirm Django can connect
echo "⏳ Confirming database connectivity…"
for i in $(seq 1 15); do
  if "${DC[@]}" exec -T web python manage.py shell -c \
       "from django.db import connection; connection.ensure_connection()" >/dev/null 2>&1; then
    echo "✅ Database reachable."; echo; break
  fi
  [ "$i" -eq 15 ] && { echo "❌ Database not reachable after 30s."; exit 1; }
  sleep 2
done

# 4. Migrations — apply only, as the admin role
if [ "$DO_MAKEMIGRATIONS" -eq 1 ]; then
  run_step "Creating new migrations" "${DC[@]}" exec -T "${ADMIN_ENV[@]}" web python manage.py makemigrations
fi
run_step "Applying migrations" "${DC[@]}" exec -T "${ADMIN_ENV[@]}" web python manage.py migrate --noinput

# 5. Static files — required because static_volume masks the image's copy
run_step "Collecting static files" "${DC[@]}" exec -T web python manage.py collectstatic --noinput --clear

# 6. Superuser — idempotent
run_step "Ensuring superuser exists" "${DC[@]}" exec -T "${ADMIN_ENV[@]}" \
  -e DJANGO_SUPERUSER_USERNAME="${DJ_SUPERUSER_USERNAME:-admin}" \
  -e DJANGO_SUPERUSER_EMAIL="${DJ_SUPERUSER_EMAIL:-admin@example.com}" \
  -e DJANGO_SUPERUSER_PASSWORD="${DJ_SUPERUSER_PASSWORD:-}" \
  web python manage.py shell -c '
import os
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ["DJANGO_SUPERUSER_USERNAME"]
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD") or ""
email    = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
if User.objects.filter(username=username).exists():
    print(f"Superuser {username} already exists - unchanged.")
elif not password:
    raise SystemExit("DJ_SUPERUSER_PASSWORD not set; cannot create superuser.")
else:
    User.objects.create_superuser(username, email, password)
    print(f"Superuser {username} created.")
'

# 7. CSV import — only into an empty DB, or when forced
ROW_COUNT="$("${DC[@]}" exec -T web python manage.py shell -c \
  'from stuff.models import Location; print(Location.objects.count())' | tr -d '[:space:]')"

if [ "$FORCE_IMPORT" -eq 1 ] || [ "$FRESH" -eq 1 ] || [ "$ROW_COUNT" = "0" ]; then
  run_step "Importing CSV data" "${DC[@]}" exec -T "${ADMIN_ENV[@]}" \
    web python manage.py import_csv --dir ./csv_import --reset-seq
else
  echo "⏭️  Skipping CSV import — DB already has $ROW_COUNT locations (--import-csv to override)."
fi

echo "============================================================"
echo "🎉 DONE — data preserved, backend + Vue rebuilt."
echo "============================================================"
