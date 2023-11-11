import os

pgsql = {
    "host": "127.0.0.1",
    "username": os.environ['DB_USERNAME'],
    "password": os.environ['DB_PASSWORD'],
    "database": 'ecommerce',
}
