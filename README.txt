--HOW TO RUN--
python3 main.py

--CONFIG--
export DB_USERNAME="dbuser"
export DB_PASSWORD="dbpassword"


--ROUTES--
1. GET /api/products
Examples:
http://localhost:8000/api/products/
http://localhost:8000/api/products/?search=s24&page=2&count=5
http://localhost:8000/api/products/?search=s24


2. PATCH /api/products/<product_id>
Examples:
PATCH /api/product/4 HTTP/1.1
Host: localhost:8000
X-User-Id: 4
Content-Type: application/json

{"price": 79999}

3. GET /api/store/<int:store_id>/products/
