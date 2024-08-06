#!/bin/sh

# Set PYTHONPATH
export PYTHONPATH=/home/smartendance/web

# Wait for MySQL container to be ready
./wait-for-it.sh smartendance-db:3306 --timeout=30 --strict -- echo "MySQL is up"

# Initial migration
flask db init
# Start migration
flask db migrate -m "Initial db migration"
# Apply migration
flask db upgrade

# Run data initialization script
python3 -c "
from flask_app import create_app
from flask_app.extensions import db
from sqlalchemy import text

# Initialize the app.
app = create_app(testing=False)

# Fungsi untuk mengeksekusi query SQL
def execute_sql_file(pathfile, conn):
  with open(pathfile, 'r') as file:
    query = ''
    for line in file:
      stripped_line = line.strip()
      if stripped_line and not stripped_line.startswith('--'):
        query += ' ' + stripped_line
        if query.endswith(';'):
          query = query.strip()
          print(f'Executing SQL command: {query}')
          conn.execute(text(query))
          query = ''

# Eksekusi file 'init.sql' untuk inisialisasi data.
with app.app_context():
  with db.engine.connect() as db_conn:
    with db_conn.begin() as transaction:
      sql_file = '/home/smartendance/web/init.sql'
      execute_sql_file(sql_file, db_conn)
      transaction.commit()
"

# Start the flask app
exec python3 wsgi.py