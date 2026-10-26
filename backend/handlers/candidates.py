"""Lambda handler for listing candidate records from DynamoDB."""

import datetime
import json
import logging
import os
import sys
from typing import Any, Dict, List

import boto3

# Support local shared package imports when invoked in Lambda
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from shared.response import error_response, success_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle GET /api/candidates requests.

    Scans DynamoDB table for all candidate records, truncates resumeText
    for lightweight listing, and sorts by createdAt descending.

    Args:
        event: API Gateway invocation event dict.
        context: Lambda context object.

    Returns:
        dict: API Gateway proxy response with list of candidates.
    """
    logger.info("Received candidates listing request: %s", json.dumps(event))

    try:
        table_name = os.environ["TABLE_NAME"]
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(table_name)

        items: List[Dict[str, Any]] = []
        scan_kwargs: Dict[str, Any] = {}

        # Paginate scan across table
        while True:
            response = table.scan(**scan_kwargs)
            items.extend(response.get("Items", []))
            last_evaluated_key = response.get("LastEvaluatedKey")
            if not last_evaluated_key:
                break
            scan_kwargs["ExclusiveStartKey"] = last_evaluated_key

        # Format candidates and truncate resumeText for listing overview
        candidates: List[Dict[str, Any]] = []
        now_dt = datetime.datetime.now(datetime.timezone.utc)

        for item in items:
            raw_text = item.get("resumeText", "")
            # Truncate resumeText to 200 characters for listing summary
            truncated_text = (raw_text[:200] + "...") if len(raw_text) > 200 else raw_text

            status = item.get("status", "UNKNOWN")
            error_message = item.get("errorMessage")

            # Check if an UPLOADING record has timed out (> 5 minutes old)
            if status == "UPLOADING":
                created_at_str = item.get("createdAt")
                is_expired = False
                if created_at_str:
                    try:
                        created_dt = datetime.datetime.fromisoformat(created_at_str)
                        if (now_dt - created_dt).total_seconds() > 300:  # 5 minutes
                            is_expired = True
                    except Exception:
                        is_expired = True
                else:
                    is_expired = True

                if is_expired:
                    status = "FAILED"
                    error_message = error_message or "Upload timed out or was interrupted."
                    try:
                        table.update_item(
                            Key={"candidateId": item["candidateId"]},
                            UpdateExpression="SET #s = :status, errorMessage = :err",
                            ExpressionAttributeNames={"#s": "status"},
                            ExpressionAttributeValues={
                                ":status": "FAILED",
                                ":err": error_message,
                            },
                        )
                    except Exception as ddb_err:
                        logger.warning("Failed to update expired uploading status: %s", str(ddb_err))

            candidate_record: Dict[str, Any] = {
                "candidateId": item.get("candidateId"),
                "filename": item.get("filename"),
                "status": status,
                "createdAt": item.get("createdAt"),
                "resumeText": truncated_text,
            }

            if "candidateName" in item:
                candidate_record["candidateName"] = item.get("candidateName")
            if "processedAt" in item:
                candidate_record["processedAt"] = item.get("processedAt")
            if "matchResult" in item:
                candidate_record["matchResult"] = item.get("matchResult")
            if error_message:
                candidate_record["errorMessage"] = error_message

            candidates.append(candidate_record)

        # Sort candidates descending by createdAt (ISO timestamps sort lexicographically)
        candidates.sort(key=lambda x: x.get("createdAt") or "", reverse=True)

        return success_response(candidates, 200)

    except KeyError as ke:
        logger.error("Missing environment variable: %s", str(ke))
        return error_response(f"Server configuration error: missing {str(ke)}", 500)
    except Exception as e:
        logger.exception("Unexpected error in candidates handler: %s", str(e))
        return error_response(f"Internal server error: {str(e)}", 500)
