import os

USERNAME = 'root'
PASSWORD = os.environ.get('PYTHEAS_DB_PASSWORD')
HOST = 'pytheas-db.cofwkbzadfp1.eu-west-3.rds.amazonaws.com'
DATABASE_NAME = 'pytheas'
CONNECTION_NAME = 'sigma-chemist-235920:europe-west1:pytheas-app'

DB_URI = f'mysql://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE_NAME}'
