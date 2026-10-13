# Inventory Management System

A Flask REST API with a CLI front end for managing retail inventory. Product
details can be enriched with data from the [OpenFoodFacts API](https://world.openfoodfacts.org/).

## Project structure

```
inventory-system/
├── app.py            # Flask REST API + mock in-memory database
├── off_client.py     # OpenFoodFacts API client
├── cli.py            # Command-line interface
├── tests/            # pytest suite (API, external API, CLI)
├── requirements.txt
└── README.md
```

## Installation and setup

```bash
git clone <your-repo-url>
cd inventory-system
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py                   # starts the API on http://127.0.0.1:5000 (debug mode)
```

Keep the server running, and open a second terminal for the CLI.

## API endpoints

| Method | Endpoint                    | Description                                   | Success | Errors   |
|--------|-----------------------------|-----------------------------------------------|---------|----------|
| GET    | `/inventory`                | Fetch all items                               | 200     |          |
| GET    | `/inventory/<id>`           | Fetch a single item                           | 200     | 404      |
| POST   | `/inventory`                | Add a new item (`product_name` required)      | 201     | 400      |
| PATCH  | `/inventory/<id>`           | Update any editable field(s)                  | 200     | 400, 404 |
| DELETE | `/inventory/<id>`           | Remove an item                                | 200     | 404      |
| GET    | `/lookup?barcode=` or `?name=` | Search OpenFoodFacts (inventory unchanged) | 200     | 400, 404, 502 |
| POST   | `/inventory/<id>/enrich`    | Fill brands/ingredients from OpenFoodFacts    | 200     | 404, 502 |

Item fields: `id` (auto), `barcode`, `product_name`, `brands`, `ingredients_text`,
`price` (number ≥ 0), `quantity` (integer ≥ 0).

Example item:
```json
{"id": 1, "barcode": "0025293000308", "product_name": "Organic Almond Milk",
 "brands": "Silk", "ingredients_text": "Filtered water, almonds, cane sugar",
 "price": 3.99, "quantity": 25}
```

Errors return `{"error": "message"}`. `502` means OpenFoodFacts was unreachable.

### curl / Postman examples
```bash
curl http://127.0.0.1:5000/inventory
curl -X POST http://127.0.0.1:5000/inventory -H "Content-Type: application/json" \
     -d '{"product_name":"Oat Milk","price":2.5,"quantity":10}'
curl -X PATCH http://127.0.0.1:5000/inventory/1 -H "Content-Type: application/json" \
     -d '{"quantity": 30}'
curl -X DELETE http://127.0.0.1:5000/inventory/1
```
In Postman, use the same URLs with body type **raw → JSON**.

## CLI usage

```bash
python cli.py list                                   # view all items
python cli.py view 1                                 # view one item
python cli.py add "Oat Milk" --brand Oatly --barcode 7394376616228 --price 2.5 --quantity 10
python cli.py update 1 --price 4.25 --quantity 18    # update price and/or stock
python cli.py delete 3                               # delete an item
python cli.py find --barcode 3017620422003           # search OpenFoodFacts by barcode
python cli.py find --name "nutella"                  # ...or by name
python cli.py enrich 2                               # add OpenFoodFacts details to item 2
```

Invalid input (bad IDs, negative numbers, server down, API failures) prints a
clear `Error: ...` message and exits with status 1.

| CLI command | API route called            |
|-------------|-----------------------------|
| list        | GET /inventory              |
| view        | GET /inventory/<id>         |
| add         | POST /inventory             |
| update      | PATCH /inventory/<id>       |
| delete      | DELETE /inventory/<id>      |
| find        | GET /lookup                 |
| enrich      | POST /inventory/<id>/enrich |

## OpenFoodFacts integration notes
Based on the [OpenFoodFacts API docs](https://openfoodfacts.github.io/openfoodfacts-server/api/):
- **Barcode lookup** uses `GET /api/v2/product/<barcode>.json` (response contains `"status": 1` when found).
  The docs mark v2 as deprecated in favour of v3, but v2 is still supported and matches the
  data shape used in this project.
- **Name lookup** uses the legacy `GET /cgi/search.pl` keyword search, because full-text search
  is not available in the v2/v3 API.
- **User-Agent:** the docs require `AppName/Version (ContactEmail)`. Edit `HEADERS` in
  `off_client.py` and put your own email.
- **Rate limits:** 15 requests/min for product reads, 10/min for searches. Hitting them
  returns HTTP 429/503, which the API reports as a `502` with a "rate limit" message.
- Data is community-contributed, so fields may be missing or inaccurate.

## Running the tests

```bash
pytest -v
```
Tests use `pytest` and `unittest.mock` so no network access or running server is needed.
They cover all endpoints (GET/POST/PATCH/DELETE), CLI commands, and external API
success, not-found, and failure cases.

## Debugging
- Run `python app.py` — Flask debug mode gives auto-reload and an interactive traceback.
- Use Postman to validate each endpoint's status codes and JSON bodies.

## Notes
Data is stored in an in-memory list and resets when the server restarts.
