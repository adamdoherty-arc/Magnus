#!/bin/bash

echo "Setting up PostgreSQL for Wheel Strategy System..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo -e "${RED}PostgreSQL is not installed.${NC}"
    echo "Install PostgreSQL:"
    echo "  Mac: brew install postgresql && brew services start postgresql"
    echo "  Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
    echo "  RHEL/CentOS: sudo yum install postgresql-server postgresql-contrib"
    exit 1
fi

echo -e "${GREEN}PostgreSQL found.${NC}"
echo ""

# Set database credentials
DB_USER="postgres"
DB_NAME="wheel_strategy"
DB_PASSWORD="${PGPASSWORD:-postgres}"

echo "Using database: $DB_NAME"
echo "Using user: $DB_USER"
echo ""

# Create database
echo "Creating database '$DB_NAME'..."
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Database created successfully.${NC}"
else
    echo -e "${YELLOW}Database might already exist or there was an error.${NC}"
fi
echo ""

# Install TimescaleDB extension
echo "Installing TimescaleDB extension..."
sudo -u postgres psql -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}TimescaleDB extension installed.${NC}"
else
    echo -e "${YELLOW}TimescaleDB might not be installed.${NC}"
    echo "Install from: https://www.timescale.com/"
fi
echo ""

# Run schema
echo "Running database schema..."
if [ -f "database_schema.sql" ]; then
    sudo -u postgres psql -d $DB_NAME -f database_schema.sql
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Schema created successfully!${NC}"
    else
        echo -e "${RED}Error creating schema. Check database_schema.sql for issues.${NC}"
    fi
else
    echo -e "${RED}database_schema.sql not found!${NC}"
fi

echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "Connection details:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo "  Password: $DB_PASSWORD"
echo ""
echo "Update config.json with these details."
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env <<EOF
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME
PGUSER=$DB_USER
PGPASSWORD=$DB_PASSWORD
PGHOST=localhost
PGPORT=5432
PGDATABASE=$DB_NAME

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
EOF
    echo -e "${GREEN}.env file created${NC}"
fi