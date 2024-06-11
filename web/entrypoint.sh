#!/bin/bash

# Initial migration
flask db init
# Start migration
flask db migrate -m "Initial db migration"
# Apply migration
flask db upgrade

# Start the flask app
exec python3 wsgi.py