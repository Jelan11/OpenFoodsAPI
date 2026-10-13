import json
import requests

BASE_URL = "http://127.0.0.1:5000"


# Send requests to the API
def api_request(method, path, data=None):
    try:
        response = requests.request(
            method,
            BASE_URL + path,
            json=data,
            timeout=10
        )
        return response.status_code, response.json()

    except requests.RequestException:
        print("Could not connect to the API.")
        return None, None

    except ValueError:
        return response.status_code, {"error": "Invalid response"}


# Display results
def show(status, result):
    if status is None:
        return

    print(f"\nHTTP {status}")
    print(json.dumps(result, indent=2))


# List inventory
def list_inventory():
    status, items = api_request("GET", "/inventory")

    if status == 200 and items:
        print(f"\n{'ID':<5}{'Product':<25}{'Brand':<18}{'Price':>8}{'Qty':>6}")

        for item in items:
            print(
                f"{item['id']:<5}"
                f"{item['product_name'][:23]:<25}"
                f"{item['brands'][:16]:<18}"
                f"{item['price']:>8.2f}"
                f"{item['quantity']:>6}"
            )

    elif status == 200:
        print("Inventory is empty.")

    else:
        show(status, items)


# View one product
def view_product():
    product_id = input("Enter product ID: ")
    result = api_request("GET", f"/inventory/{product_id}")

    if isinstance(result, tuple):
        show(*result)


# Add a product
def add_product():
    product = {
        "product_name": input("Product name: ").strip(),
        "barcode": input("Barcode: ").strip(),
        "brands": input("Brand: ").strip(),
        "ingredients_text": input("Ingredients: ").strip(),
        "price": float(input("Price: ")),
        "quantity": int(input("Quantity: "))
    }

    result = api_request("POST", "/inventory", product)

    if isinstance(result, tuple):
        show(*result)


# Update product price and quantity
def update_product():
    product_id = input("Enter product ID: ")

    changes = {
        "price": float(input("New price: ")),
        "quantity": int(input("New quantity: "))
    }

    result = api_request(
        "PATCH", f"/inventory/{product_id}", changes
    )

    if isinstance(result, tuple):
        show(*result)


# Delete a product
def delete_product():
    product_id = input("Enter product ID: ")

    status, product = api_request(
        "GET", f"/inventory/{product_id}"
    )

    if status != 200:
        show(status, product)
        return

    confirm = input(
        f"Delete {product.get('product_name', 'this product')}? (y/n): "
    )

    if confirm.lower() == "y":
        result = api_request(
            "DELETE", f"/inventory/{product_id}"
        )

        if isinstance(result, tuple):
            show(*result)
    else:
        print("Deletion cancelled.")


# Search OpenFoodFacts by barcode or name
def search_product():
    choice = input("Search by 1. Barcode or 2. Name: ")

    if choice == "1":
        value = input("Enter barcode: ")
        params = {"barcode": value}

    elif choice == "2":
        value = input("Enter product name: ")
        params = {"name": value}

    else:
        print("Invalid choice.")
        return

    path = "/lookup?" + requests.compat.urlencode(params)
    result = api_request("GET", path)

    if isinstance(result, tuple):
        show(*result)


# Get details from OpenFoodsFacts 
def enrich_product():
    product_id = input("Enter product ID: ")

    result = api_request(
        "POST", f"/inventory/{product_id}/enrich"
    )

    if isinstance(result, tuple):
        show(*result)


# Main menu
def main():
    while True:
        print("\n=== Inventory Management System ===")
        print("1. List inventory")
        print("2. View product")
        print("3. Add product")
        print("4. Update price / quantity")
        print("5. Delete product")
        print("6. Search OpenFoodFacts")
        print("7. Enrich product from OpenFoodFacts")
        print("0. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            list_inventory()
        elif choice == "2":
            view_product()
        elif choice == "3":
            add_product()
        elif choice == "4":
            update_product()
        elif choice == "5":
            delete_product()
        elif choice == "6":
            search_product()
        elif choice == "7":
            enrich_product()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()