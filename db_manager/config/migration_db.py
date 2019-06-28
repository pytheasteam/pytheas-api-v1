import os

USERNAME = 'pytheas'
PASSWORD = os.environ.get("MIGRATION_DB_PASSWORD")
HOST = 'pytheas-db.cofwkbzadfp1.eu-west-3.rds.amazonaws.com'  # pytheas app
DATABASE_NAME = 'pytheas'

DB_URI = f'mysql://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE_NAME}'
