from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from bot.client import get_client
from bot.orders import place_order
from bot.settings import get_public_config_status
from bot.validators import validate_order

templates = Jinja2Templates(directory="templates")


def create_app():
    app = FastAPI(title="Binance Demo Dashboard")

    @app.get("/health")
    def health():
        status = get_public_config_status()
        return {
            "status": "ok",
            "binance": {
                "api_key_configured": status["has_api_key"],
                "api_secret_configured": status["has_api_secret"],
                "base_url_configured": status["has_base_url"],
            },
        }

    @app.get("/", response_class=HTMLResponse)
    def dashboard(request: Request):
        return render_dashboard(request)

    @app.post("/orders/validate", response_class=HTMLResponse)
    def validate_order_request(
        request: Request,
        symbol: str = Form(...),
        side: str = Form(...),
        order_type: str = Form(...),
        quantity: float = Form(...),
        price: str = Form(""),
    ):
        try:
            normalized = normalize_order_form(symbol, side, order_type, quantity, price)
            validate_normalized_order(normalized)
            success_message = "Order request is valid. Next we can wire this form to real execution."
            error_message = None
        except ValueError as exc:
            normalized = normalize_order_form(symbol, side, order_type, quantity, price, coerce_price=False)
            error_message = str(exc)
            success_message = None

        return render_dashboard(
            request,
            form_data=normalized,
            success_message=success_message,
            error_message=error_message,
        )

    @app.post("/orders/execute", response_class=HTMLResponse)
    def execute_order_request(
        request: Request,
        symbol: str = Form(...),
        side: str = Form(...),
        order_type: str = Form(...),
        quantity: float = Form(...),
        price: str = Form(""),
        confirm_execution: str = Form(""),
    ):
        try:
            normalized = normalize_order_form(symbol, side, order_type, quantity, price)
            validate_normalized_order(normalized)

            if confirm_execution != "yes":
                raise ValueError("Please confirm demo execution before submitting")

            client = get_client()
            order_response = place_order(
                client,
                normalized["symbol"],
                normalized["side"],
                normalized["order_type"],
                normalized["quantity"],
                normalized["price"],
            )

            return render_dashboard(
                request,
                form_data=normalized,
                success_message="Demo order submitted successfully.",
                execution_result=build_execution_result(order_response),
            )
        except Exception as exc:
            normalized = normalize_order_form(symbol, side, order_type, quantity, price, coerce_price=False)
            return render_dashboard(
                request,
                form_data=normalized,
                error_message=str(exc),
            )

    return app


def normalize_order_form(symbol, side, order_type, quantity, price, coerce_price=True):
    normalized_price = price
    if coerce_price:
        normalized_price = float(price) if price else None
    return {
        "symbol": symbol.upper(),
        "side": side.upper(),
        "order_type": order_type.upper(),
        "quantity": quantity,
        "price": normalized_price,
    }


def validate_normalized_order(normalized):
    validate_order(
        normalized["symbol"],
        normalized["side"],
        normalized["order_type"],
        normalized["quantity"],
        normalized["price"],
    )


def build_execution_result(order_response):
    return {
        "order_id": order_response.get("orderId", "N/A"),
        "status": order_response.get("status", "N/A"),
        "executed_qty": order_response.get("executedQty", "N/A"),
        "avg_price": order_response.get("avgPrice") or order_response.get("price") or "N/A",
    }


def render_dashboard(
    request,
    form_data=None,
    success_message=None,
    error_message=None,
    execution_result=None,
):
    status = get_public_config_status()
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "config": status,
            "form_data": form_data
            or {
                "symbol": "BTCUSDT",
                "side": "BUY",
                "order_type": "MARKET",
                "quantity": 0.002,
                "price": "",
            },
            "success_message": success_message,
            "error_message": error_message,
            "execution_result": execution_result,
        },
    )


app = create_app()
