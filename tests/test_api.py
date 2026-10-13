import pytest
import app as inventory_app


@pytest.fixture
def client():
    inventory_app.app.config["TESTING"] = True
    inventory_app.inventory.clear()
    inventory_app.next_id = 1

    with inventory_app.app.test_client() as client:
        yield client

    inventory_app.inventory.clear()
    inventory_app.next_id = 1


@pytest.fixture
def seeded(client):
    inventory_app.inventory.extend([
        {
            "id": 1,
            "barcode": "0025293000308",
            "product_name": "Organic Almond Milk",
            "brands": "Silk",
            "ingredients_text": "Water, almonds",
            "price": 3.99,
            "quantity": 25
        },
        {
            "id": 2,
            "barcode": "3017620422003",
            "product_name": "Nutella",
            "brands": "Ferrero",
            "ingredients_text": "Sugar, cocoa",
            "price": 4.50,
            "quantity": 40
        },
        {
            "id": 3,
            "barcode": "5449000000996",
            "product_name": "Coca-Cola",
            "brands": "Coca-Cola",
            "ingredients_text": "Water, sugar",
            "price": 1.50,
            "quantity": 100
        }
    ])

    inventory_app.next_id = 4
    return client