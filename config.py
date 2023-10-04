import os

DB_CONFIG = {
    'host': os.environ.get('DB_HOSTNAME', 'localhost'),
    'user': os.environ.get('DB_USERNAME', 'sa'),
    'password': os.environ.get('DB_PASSWORD', 'default_password'),
    'database': 'auth'
}