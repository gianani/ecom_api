from application import app
import database
from flask import request, jsonify
from urllib.parse import urlencode


def fetch_products_query(search_q, page, count, store=None):
    if page.isnumeric() and page != "0":
        page = int(page)
    else:
        raise ValueError("Invalid value for param page!")

    if count.isnumeric() and count != "0":
        count = int(count)
    else:
        raise ValueError("Invalid value for param count!")

    offset = (page - 1) * count
    db = database.Pgsql()
    if search_q is not None:
        like_pattern = "%{}%".format(search_q)
        db.query(
            "select count(id) from product where product_name ILIKE %s", (like_pattern,)
        )
        total = db.cur.fetchone()[0]
        if offset > total:
            raise ValueError("Out of range value for param page")
        db.query(
            "select id,product_name,price from product where product_name ILIKE %s order by id asc limit %s offset %s",
            (like_pattern, count, offset),
        )
    else:
        store_join = ''
        args_total = []
        args = [count, offset]
        if store is not None:
            store_join = " JOIN store_product on store_product.product_id=product.id WHERE store_product.store_id=%s"
            args_total = [store]
            args = [store, count, offset]
        db.query("select count(id) from product" + store_join, args_total)
        total = db.cur.fetchone()[0]
        if offset > total:
            raise ValueError("Out of range value for param page")
        db.query(
            "select id,product_name,price from product" + store_join + " order by id asc limit %s offset %s",
            args,
        )

    row_count = db.cur.rowcount
    res = [
        {"id": col1, "product_name": col2, "price": col3}
        for (col1, col2, col3) in db.cur.fetchall()
    ]
    db.close
    response = {"total": total, "page": page, "products": res}
    if total > row_count + offset:
        args = request.args.to_dict()
        args["page"] = page + 1
        response["next"] = request.path + "?" + urlencode(args)
    return response


# Routes
@app.get("/api/products/")
def get_products():

    page = request.args.get("page", "1")
    count = request.args.get("count", "10")
    search_q = request.args.get("search")
    if search_q is not None and len(search_q) < 3:
        raise InvalidAPIUsage("Please enter at least 3 characters!")

    try:
        return fetch_products_query(search_q, page, count)
    except ValueError as e:
        raise InvalidAPIUsage(str(e))


@app.get("/api/store/<int:store_id>/products/")
def get_Store_products(store_id):
    page = request.args.get("page", "1")
    count = request.args.get("count", "10")

    try:
        return fetch_products_query(None, page, count, store_id)
    except ValueError as e:
        raise InvalidAPIUsage(str(e))


@app.route("/api/product/<int:id>/", methods=["PATCH"])
def update_product(id):
    user_id = request.headers.get("X-User-Id")
    if user_id is not None:
        body = request.get_json()
        if "price" in body:
            price = body["price"]
            if type(price) == int and price > 0:
                price = int(price)
                db = database.Pgsql()
                db.query(
                    "UPDATE product SET price = %s WHERE id = %s RETURNING id, product_name, price",
                    (price, id),
                )
                res = db.cur.fetchone()

                if res is not None:
                    return {
                        "product": {
                            "id": res[0],
                            "product_name": res[1],
                            "price": res[2],
                        }
                    }
                else:
                    raise InvalidAPIUsage("Product not found!", 404)
            else:
                raise InvalidAPIUsage("Incorrect format for param price!")
        else:
            raise InvalidAPIUsage("Missing required param price!")
    else:
        raise InvalidAPIUsage("Authorization missing for user!", 401)


class InvalidAPIUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(e):
    return jsonify(e.to_dict()), e.status_code
