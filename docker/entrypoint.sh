#!/bin/bash
set -e

echo "Starting BIA Tool Docker Container..."

# Wait for database if using MariaDB
if [ "$DATABASE_TYPE" = "mariadb" ]; then
    echo "Waiting for MariaDB to be ready..."
    
    max_retries=30
    retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        if python -c "
import os
import sys
import time
import pymysql

try:
    connection = pymysql.connect(
        host=os.environ.get('DB_HOST', 'mariadb'),
        port=int(os.environ.get('DB_PORT', 3306)),
        user=os.environ.get('DB_USER', 'bia_user'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME', 'bia_tool')
    )
    connection.close()
    print('Database connection successful')
    sys.exit(0)
except Exception as e:
    print(f'Database connection failed: {e}')
    sys.exit(1)
"; then
            echo "Database is ready!"
            break
        else
            retry_count=$((retry_count + 1))
            echo "Database not ready (attempt $retry_count/$max_retries)"
            sleep 2
        fi
    done
    
    if [ $retry_count -eq $max_retries ]; then
        echo "Database failed to become ready"
        exit 1
    fi
fi

# Initialize database
echo "Initializing database..."
python -c "
from app import create_app, db
from app.models import User
import os

app = create_app()
with app.app_context():
    # Create tables if they don't exist
    db.create_all()
    
    # Create admin user if it doesn't exist
    admin_email = os.environ.get('ADMIN_EMAIL')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    
    if admin_email and admin_password:
        existing_admin = User.query.filter_by(email=admin_email).first()
        if not existing_admin:
            try:
                from app.commands import create_admin_user
                create_admin_user()
                print(f'Admin user created: {admin_email}')
            except Exception as e:
                print(f'Could not create admin user: {e}')
        else:
            print(f'Admin user already exists: {admin_email}')
"

echo "Starting Flask application..."
exec python run.py