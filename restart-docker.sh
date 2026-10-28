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

# 1. Start containers (without destroying volumes or rebuilding images)
run_step "Starting containers" docker-compose up -d

# 2. Apply any pending migrations (safe to run even if DB is up-to-date)
run_step "Applying migrations" docker-compose exec web python manage.py migrate

echo "============================================================"
echo "🎉 APPLICATION STARTED SUCCESSFULLY! 🎉"
echo "============================================================"
