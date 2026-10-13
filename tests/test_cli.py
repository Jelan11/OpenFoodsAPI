from unittest.mock import patch
import cli


def test_list_inventory(capsys):
    products = [
        {
            "id": 1,
            "product_name": "Oat Milk",
            "brands": "Example Brand",
            "price": 2.50,
            "quantity": 10,
            "barcode": "1234567890123",
        }
    ]

    with patch("cli.api_request", return_value=(200, products)):
        cli.list_inventory()

    assert "Oat Milk" in capsys.readouterr().out


def test_add_product():
    answers = iter(["Oat Milk", "", "", "", "2.50", "10"])

    with patch("builtins.input", side_effect=lambda _: next(answers)):
        with patch("cli.api_request") as mock_api:
            cli.add_product()

    mock_api.assert_called_once()
    assert mock_api.call_args.args[0] == "POST"
    assert mock_api.call_args.args[1] == "/inventory"


def test_view_product():
    with patch("builtins.input", return_value="1"):
        with patch("cli.api_request") as mock_api:
            cli.view_product()

    mock_api.assert_called_once_with("GET", "/inventory/1")


def test_delete_product():
    product = {"id": 1, "product_name": "Oat Milk"}

    with patch("builtins.input", side_effect=["1", "y"]):
        with patch(
            "cli.api_request",
            side_effect=[
                (200, product),
                (200, {"message": "Item 1 deleted"}),
            ],
        ) as mock_api:
            cli.delete_product()

    assert mock_api.call_count == 2
    mock_api.assert_any_call("DELETE", "/inventory/1")


def test_cli_exit():
    with patch("builtins.input", return_value="0"):
        with patch("builtins.print"):
            cli.main()