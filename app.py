from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from bot.client import get_client
from bot.orders import place_order
from bot.settings import get_public_config_status
from bot.validators import validate_order

templates = Jinja2Templates(directory="templates")
order_activity = []


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
            append_activity("Validation passed", normalized)
        except ValueError as exc:
            normalized = normalize_order_form(symbol, side, order_type, quantity, price, coerce_price=False)
            error_message = str(exc)
            success_message = None
            append_activity("Validation failed", normalized, details=error_message)

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
                success_message=build_success_message(client),
                execution_result=build_execution_result(order_response),
                activity_title="Execution succeeded",
            )
        except Exception as exc:
            normalized = normalize_order_form(symbol, side, order_type, quantity, price, coerce_price=False)
            failure_message = str(exc)
            activity_title = "Execution blocked"
            if confirm_execution == "yes":
                activity_title = "Execution failed"
            append_activity(activity_title, normalized, details=failure_message)
            return render_dashboard(
                request,
                form_data=normalized,
                error_message=failure_message,
                activity_title=activity_title,
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
    result = {
        "order_id": order_response.get("orderId", "N/A"),
        "status": order_response.get("status", "N/A"),
        "executed_qty": order_response.get("executedQty", "N/A"),
        "avg_price": order_response.get("avgPrice") or order_response.get("price") or "N/A",
    }
    append_activity("Execution succeeded", result)
    return result


def build_success_message(client):
    if getattr(client, "last_retry_reason", "") == "timestamp_sync":
        return "Demo order submitted successfully after syncing time with Binance."
    return "Demo order submitted successfully."


def append_activity(title, payload, details=None):
    order_activity.insert(
        0,
        {
            "title": title,
            "payload": format_activity_payload(payload),
            "details": details,
        },
    )
    del order_activity[8:]


def format_activity_payload(payload):
    if "symbol" in payload:
        bits = [
            payload.get("symbol", "N/A"),
            payload.get("side", "N/A"),
            payload.get("order_type", "N/A"),
            f"qty {payload.get('quantity', 'N/A')}",
        ]
        if payload.get("price") not in (None, ""):
            bits.append(f"price {payload['price']}")
        return " | ".join(str(bit) for bit in bits)
    return (
        f"orderId {payload.get('order_id', 'N/A')} | "
        f"status {payload.get('status', 'N/A')} | "
        f"qty {payload.get('executed_qty', 'N/A')} | "
        f"avg {payload.get('avg_price', 'N/A')}"
    )


def render_dashboard(
    request,
    form_data=None,
    success_message=None,
    error_message=None,
    execution_result=None,
    activity_title=None,
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
            "activity_title": activity_title,
            "order_activity": order_activity,
        },
    )


app = create_app()
