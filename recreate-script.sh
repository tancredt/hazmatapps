#!/bin/bash
set -e
# ---------------------------------------------------------
# Load environment variables from .env file
# ---------------------------------------------------------
set -a
[ -f .env ] && source ./.env
set +a

# Helper function to run a command, check its status, and print a message
run_step() {
    local step_name="$1"
    shift
    local cmd=("$@")
    echo "------------------------------------------------------------"
    echo "🚀 Starting: $step_name"
    echo "Command: ${cmd[*]}"
    echo "------------------------------------------------------------"
    
    # Execute the command
    "${cmd[@]}"
    local status=$?
    
    if [ $status -eq 0 ]; then
        echo "✅ SUCCESS: $step_name completed successfully."
        echo ""
    else
        echo "❌ FAILURE: $step_name failed with exit code $status."
        echo "🛑 Aborting the rest of the script."
        exit $status
    fi
}

# 1. Tear down existing containers and volumes
run_step "Tearing down existing containers and volumes" docker-compose down -v

# 2. Rebuild and start containers
run_step "Rebuilding and starting containers" docker-compose up -d --build

# 3. Make migrations
run_step "Creating new migrations" docker-compose exec web python manage.py makemigrations

# 4. Apply migrations
# (Using the dedicated 'migrate' service which already has admin credentials mapped in docker-compose.yml)
run_step "Applying migrations" docker compose exec -e DB_USER="$DB_ADMIN_USER" -e DB_PASSWORD="$DB_ADMIN_PASSWORD" web python manage.py migrate

# 5. Create superuser
# NOTE: This command is interactive. It will pause and wait for you to type the username/email/password.
run_step "Creating superuser" docker compose exec -e DB_USER="$DB_ADMIN_USER" -e DB_PASSWORD="$DB_ADMIN_PASSWORD" -e DJANGO_SUPERUSER_USERNAME="$DJ_SUPERUSER_USERNAME" -e DJANGO_SUPERUSER_EMAIL="admin@example.com" -e DJANGO_SUPERUSER_PASSWORD="$DJ_SUPERUSER_PASSWORD" web python manage.py createsuperuser --noinput

# 6. Import CSV data and reset sequences
run_step "Importing CSV data" docker compose exec -e DB_USER="$DB_ADMIN_USER" -e DB_PASSWORD="$DB_ADMIN_PASSWORD" web python manage.py import_csv --dir ./csv_import --reset-seq

echo "============================================================"
echo "🎉 ALL STEPS COMPLETED SUCCESSFULLY! 🎉"
echo "============================================================"
