"""API Gateway response helper utilities."""

import json
from decimal import Decimal
from typing import Any, Dict


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder converting Decimal types to int or float."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            return float(obj)
        return super().default(obj)


CORS_HEADERS: Dict[str, str] = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
    "Content-Type": "application/json",
}


def success_response(data: Any, status_code: int = 200) -> Dict[str, Any]:
    """Return a successful API Gateway proxy response.

    Args:
        data: Payload data to serialize as JSON.
        status_code: HTTP status code (defaults to 200).

    Returns:
        dict: Standard API Gateway proxy response.
    """
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(data, cls=DecimalEncoder),
    }


def error_response(message: str, status_code: int = 500) -> Dict[str, Any]:
    """Return an error API Gateway proxy response.

    Args:
        message: Human-readable error description.
        status_code: HTTP error status code (defaults to 500).

    Returns:
        dict: Standard API Gateway proxy response with error payload.
    """
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps({"error": message}, cls=DecimalEncoder),
    }
