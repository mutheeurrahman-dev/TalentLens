"""Lambda handler for generating presigned upload URLs and tracking candidates."""

import datetime
import json
import logging
import os
import sys
import uuid
from typing import Any, Dict

import boto3
import botocore.config

# Support local shared package imports when invoked in Lambda
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from shared.response import error_response, success_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _get_query_params(event: Dict[str, Any]) -> Dict[str, str]:
    """Extract query parameters supporting REST API v1 and HTTP API v2."""
    params = event.get("queryStringParameters")
    if params is None:
        return {}
    return params


def _get_http_method(event: Dict[str, Any]) -> str:
    """Extract HTTP method from event supporting REST API and HTTP API v2."""
    http_ctx = event.get("requestContext", {}).get("http", {})
    method = http_ctx.get("method") or event.get("httpMethod", "GET")
    return method.upper()


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle /api/upload requests.

    GET: Generates a presigned S3 PUT URL for uploading resume PDF files,
         creates an initial DynamoDB candidate record with 'UPLOADING' status.
    POST: Updates candidate status to 'FAILED' if client-side upload fails.

    Args:
        event: API Gateway invocation event dict.
        context: Lambda context object.

    Returns:
        dict: API Gateway proxy response.
    """
    logger.info("Received upload request: %s", json.dumps(event))

    try:
        bucket_name = os.environ["BUCKET_NAME"]
        table_name = os.environ["TABLE_NAME"]
        method = _get_http_method(event)
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(table_name)

        if method == "POST":
            # Handle client-reported upload failure
            body_str = event.get("body") or "{}"
            if event.get("isBase64Encoded", False):
                import base64
                body_str = base64.b64decode(body_str).decode("utf-8")
            try:
                body = json.loads(body_str) if isinstance(body_str, str) else body_str
            except Exception:
                return error_response("Invalid JSON in request body", 400)

            candidate_id = body.get("candidateId")
            if not candidate_id:
                return error_response("Field 'candidateId' is required.", 400)

            status = body.get("status", "FAILED")
            error_message = body.get("errorMessage", "Upload failed or interrupted.")

            table.update_item(
                Key={"candidateId": candidate_id},
                UpdateExpression="SET #s = :status, errorMessage = :err",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={
                    ":status": status,
                    ":err": error_message,
                },
            )
            logger.info("Updated candidate %s status to %s: %s", candidate_id, status, error_message)
            return success_response({"candidateId": candidate_id, "status": status}, 200)

        # Default GET handler: generate presigned upload URL
        query_params = _get_query_params(event)
        filename = query_params.get("filename")

        if not filename or not filename.strip():
            return error_response("Query parameter 'filename' is required.", 400)

        filename = filename.strip()
        if not filename.lower().endswith(".pdf"):
            return error_response("Invalid file type. Only .pdf files are supported.", 400)

        candidate_id = str(uuid.uuid4())
        s3_key = f"resumes/{candidate_id}/{filename}"

        # Initialize S3 client with regional endpoint and virtual addressing
        region_name = os.environ.get("AWS_REGION", "ap-south-1")
        s3_client = boto3.client(
            "s3",
            region_name=region_name,
            endpoint_url=f"https://s3.{region_name}.amazonaws.com",
            config=botocore.config.Config(
                signature_version="s3v4",
                s3={"addressing_style": "virtual"},
            ),
        )

        # Generate presigned PUT URL expiring in 300 seconds
        upload_url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": bucket_name,
                "Key": s3_key,
                "ContentType": "application/pdf",
            },
            ExpiresIn=300,
        )

        created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        item = {
            "candidateId": candidate_id,
            "filename": filename,
            "s3Key": s3_key,
            "status": "UPLOADING",
            "createdAt": created_at,
            "resumeText": "",
        }

        table.put_item(Item=item)

        response_data = {
            "candidateId": candidate_id,
            "uploadUrl": upload_url,
            "s3Key": s3_key,
        }
        return success_response(response_data, 200)

    except KeyError as ke:
        logger.error("Missing environment variable: %s", str(ke))
        return error_response(f"Server configuration error: missing {str(ke)}", 500)
    except Exception as e:
        logger.exception("Unexpected error in upload handler: %s", str(e))
        return error_response(f"Internal server error: {str(e)}", 500)
