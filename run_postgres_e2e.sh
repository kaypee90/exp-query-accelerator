#!/bin/bash

# Configurable variables
POSTGRES_CONTAINER_NAME="e2e_postgres"
POSTGRES_DB="testdb"
POSTGRES_USER="testuser"
POSTGRES_PASSWORD="testpass"
POSTGRES_PORT="5432"

export POSTGRES_DB
export POSTGRES_USER
export POSTGRES_PASSWORD
export POSTGRES_PORT
export POSTGRES_HOST="localhost"
export DB_TYPE="postgres"

# Function to clean up the container after the test
cleanup() {
  echo "Stopping and removing PostgreSQL container..."
  docker stop $POSTGRES_CONTAINER_NAME >/dev/null
  docker rm $POSTGRES_CONTAINER_NAME >/dev/null
  echo "PostgreSQL container removed."
}

# Trap to ensure the cleanup happens even if the script is interrupted
trap cleanup EXIT

# Step 1: Spin up PostgreSQL container
echo "Starting PostgreSQL container..."
docker run -d --name $POSTGRES_CONTAINER_NAME \
  -e POSTGRES_DB=$POSTGRES_DB \
  -e POSTGRES_USER=$POSTGRES_USER \
  -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
  -p $POSTGRES_PORT:5432 \
  postgres:latest >/dev/null

# Step 2: Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until docker exec $POSTGRES_CONTAINER_NAME pg_isready -U $POSTGRES_USER >/dev/null 2>&1; do
  sleep 1
done
echo "PostgreSQL is ready."

# Step 3: Run E2E tests (replace this with your actual test command)
echo "Running end-to-end tests..."

pytest test_dispatcher_with_postgres.py

echo "Tests finished."

# Step 4: Cleanup is handled by the trap, so we don't need to explicitly call it.
