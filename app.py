import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

inventory = [
    {"id": 1, "barcode": "0025293000308", "product_name": "Organic Almond Milk",
     "brands": "Silk", "ingredients_text": "Water, almonds",
     "price": 3.99, "quantity": 25},
    {"id": 2, "barcode": "3017620422003", "product_name": "Nutella",
     "brands": "Ferrero", "ingredients_text": "Sugar, cocoa",
     "price": 4.50, "quantity": 40},
    {"id": 3, "barcode": "5449000000996", "product_name": "Coca-Cola",
     "brands": "Coca-Cola", "ingredients_text": "Water, sugar",
     "price": 1.50, "quantity": 100}
]

next_id = 4


def error(message, status):
    return jsonify({"error": message}), status


def find_item(item_id):
    return next((item for item in inventory
                 if item["id"] == item_id), None)


# OpenFoodFacts search product
def search_product(barcode="", name=""):
    try:
        if barcode:
            url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != 1:
                return None

            product = data["product"]
        else:
            response = requests.get(
                "https://world.openfoodfacts.org/cgi/search.pl",
                params={"search_terms": name, "json": 1, "page_size": 1},
                timeout=10
            )
            response.raise_for_status()
            products = response.json().get("products", [])

            if not products:
                return None

            product = products[0]

        return {
            "product_name": product.get("product_name", ""),
            "brands": product.get("brands", ""),
            "ingredients_text": product.get("ingredients_text", "")
        }

    except (HTTPError, URLError, TimeoutError, ValueError):
        return {"error": "OpenFoodFacts is unavailable"}


# Get all products
@app.get("/inventory")
def get_all():
    return jsonify(inventory)


# Get one product
@app.get("/inventory/<int:item_id>")
def get_one(item_id):
    item = find_item(item_id)
    return (jsonify(item), 200) if item else error("Item not found", 404)


# Add product
@app.post("/inventory")
def create():
    global next_id
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data.get("product_name", "").strip():
        return error("Product name is required", 400)

    for field in ("price", "quantity"):
        if field in data:
            value = data[field]
            if (isinstance(value, bool) or
                    not isinstance(value, (int, float)) or value < 0 or
                    (field == "quantity" and not isinstance(value, int))):
                return error(f"Invalid {field}", 400)

    allowed = {"product_name", "barcode", "brands", "ingredients_text",
               "price", "quantity"}

    if set(data) - allowed:
        return error("Unknown field", 400)

    data = {k: v.strip() if isinstance(v, str) else v
            for k, v in data.items()}

    barcode = data.get("barcode", "")
    if barcode and not barcode.isdigit():
        return error("Barcode must contain digits only", 400)

    if barcode and any(i["barcode"] == barcode for i in inventory):
        return error("Duplicate barcode", 409)

    item = {
        "id": next_id, "barcode": "", "brands": "",
        "ingredients_text": "", "price": 0.0, "quantity": 0,
        **data
    }
    inventory.append(item)
    next_id += 1
    return jsonify(item), 201


# Update product
@app.patch("/inventory/<int:item_id>")
def update(item_id):
    item = find_item(item_id)
    if not item:
        return error("Item not found", 404)

    data = request.get_json(silent=True)
    allowed = {"product_name", "barcode", "brands", "ingredients_text",
               "price", "quantity"}

    if not isinstance(data, dict) or not data or set(data) - allowed:
        return error("Invalid update data", 400)

    if "price" in data and (
        isinstance(data["price"], bool) or
        not isinstance(data["price"], (int, float)) or data["price"] < 0
    ):
        return error("Invalid price", 400)

    if "quantity" in data and (
        isinstance(data["quantity"], bool) or
        not isinstance(data["quantity"], int) or data["quantity"] < 0
    ):
        return error("Invalid quantity", 400)

    if "barcode" in data:
        barcode = data["barcode"]
        if not isinstance(barcode, str) or (
            barcode and not barcode.isdigit()
        ):
            return error("Invalid barcode", 400)

        if barcode and any(
            i["barcode"] == barcode and i["id"] != item_id
            for i in inventory
        ):
            return error("Duplicate barcode", 409)

    for key, value in data.items():
        item[key] = value.strip() if isinstance(value, str) else value

    return jsonify(item)


# Delete product
@app.delete("/inventory/<int:item_id>")
def delete(item_id):
    item = find_item(item_id)
    if not item:
        return error("Item not found", 404)

    inventory.remove(item)
    return jsonify({"message": "Product deleted"})


# Search OpenFoodFacts using barcode or name
@app.get("/search")
def search():
    barcode = request.args.get("barcode", "").strip()
    name = request.args.get("name", "").strip()

    if bool(barcode) == bool(name):
        return error("Enter a barcode or product name", 400)

    product = search_product(barcode, name)

    if product is None:
        return error("Product not found", 404)
    if "error" in product:
        return error(product["error"], 502)

    return jsonify(product)


# Enrich inventory product from OpenFoodFacts
@app.post("/inventory/<int:item_id>/enrich")
def enrich(item_id):
    item = find_item(item_id)
    if not item:
        return error("Item not found", 404)

    product = search_product(item["barcode"], item["product_name"])

    if not product:
        return error("Product not found", 404)
    if "error" in product:
        return error(product["error"], 502)

    for field in ("product_name", "brands", "ingredients_text"):
        if product.get(field):
            item[field] = product[field]

    return jsonify(item)


if __name__ == "__main__":
    app.run(debug=True)