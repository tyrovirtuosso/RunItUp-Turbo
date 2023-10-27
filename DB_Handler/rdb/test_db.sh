#!/bin/bash

# Make the Script Executable: `chmod +x your_script.sh`

# Source the .env file to load environment variables
source .env

# Check if PostgreSQL service is running
if pgrep -x "postgres" > /dev/null
then
    echo "PostgreSQL is running."
else
    echo "PostgreSQL is not running."
    exit 1
fi

# Check if the test database already exists
if sudo -u $PG_USERNAME psql -lqt | cut -d \| -f 1 | grep -qw "test_runitup"; then
    echo "Test database already exists. Deleting it..."
    sudo -u $PG_USERNAME dropdb test_runitup
fi

# Create a new test database
sudo -u $PG_USERNAME createdb test_runitup
echo "Test database 'test_runitup' created."
