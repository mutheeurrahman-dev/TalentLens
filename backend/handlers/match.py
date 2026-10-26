"""Lambda handler for ranking candidate resumes against job description requirements."""

import base64
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

import boto3
from boto3.dynamodb.types import TypeDeserializer

# Support local shared package imports when invoked in Lambda
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from shared.response import error_response, success_response
from shared.skill_extractor import match_skills

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _parse_body(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Parse JSON body supporting REST API v1, HTTP API v2, and direct dicts."""
    body = event.get("body")
    if body is None:
        return None

    if isinstance(body, dict):
        return body

    if isinstance(body, str):
        if event.get("isBase64Encoded", False):
            body = base64.b64decode(body).decode("utf-8")
        try:
            return json.loads(body)
        except Exception:
            return None

    return None


def _get_candidates_by_ids(table_name: str, candidate_ids: List[str]) -> List[Dict[str, Any]]:
    """Fetch candidate items by IDs using DynamoDB batch_get_item.

    Args:
        table_name: DynamoDB table name.
        candidate_ids: List of candidateId strings.

    Returns:
        List of candidate item dicts.
    """
    dynamodb = boto3.resource("dynamodb")
    client = boto3.client("dynamodb")
    deserializer = TypeDeserializer()

    candidates: List[Dict[str, Any]] = []
    # DynamoDB BatchGetItem supports up to 100 keys per request
    chunk_size = 100
    for i in range(0, len(candidate_ids), chunk_size):
        chunk = candidate_ids[i : i + chunk_size]
        request_items = {
            table_name: {
                "Keys": [{"candidateId": {"S": cid}} for cid in chunk]
            }
        }
        response = client.batch_get_item(RequestItems=request_items)
        raw_items = response.get("Responses", {}).get(table_name, [])
        for raw in raw_items:
            deserialized = {k: deserializer.deserialize(v) for k, v in raw.items()}
            candidates.append(deserialized)

    return candidates


def _get_all_completed_candidates(table_name: str) -> List[Dict[str, Any]]:
    """Scan DynamoDB table for candidates with status 'COMPLETED'.

    Args:
        table_name: DynamoDB table name.

    Returns:
        List of COMPLETED candidate item dicts.
    """
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    items: List[Dict[str, Any]] = []
    scan_kwargs: Dict[str, Any] = {
        "FilterExpression": "#s = :completed",
        "ExpressionAttributeNames": {"#s": "status"},
        "ExpressionAttributeValues": {":completed": "COMPLETED"},
    }

    while True:
        response = table.scan(**scan_kwargs)
        items.extend(response.get("Items", []))
        last_evaluated_key = response.get("LastEvaluatedKey")
        if not last_evaluated_key:
            break
        scan_kwargs["ExclusiveStartKey"] = last_evaluated_key

    return items


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle POST /api/match requests.

    Matches resumes against requirements extracted from a job description,
    ranks candidates by match percentage descending, and returns results.

    Args:
        event: API Gateway invocation event dict.
        context: Lambda context object.

    Returns:
        dict: API Gateway proxy response with ranked candidates list.
    """
    logger.info("Received match request: %s", json.dumps(event))

    try:
        table_name = os.environ["TABLE_NAME"]
        payload = _parse_body(event)

        if not payload:
            return error_response("Invalid or missing request body.", 400)

        requirements = payload.get("requirements")
        if not requirements or not str(requirements).strip():
            return error_response("Field 'requirements' is required and must not be empty.", 400)

        requirements = str(requirements).strip()
        job_title = payload.get("jobTitle", "")
        candidate_ids = payload.get("candidateIds")

        if candidate_ids and isinstance(candidate_ids, list):
            candidates = _get_candidates_by_ids(table_name, candidate_ids)
        else:
            candidates = _get_all_completed_candidates(table_name)

        ranked_results: List[Dict[str, Any]] = []

        for candidate in candidates:
            resume_text = candidate.get("resumeText", "")
            if not resume_text:
                continue

            match_result = match_skills(resume_text, requirements)

            candidate_record = {
                "candidateId": candidate.get("candidateId"),
                "candidateName": candidate.get("candidateName", "Unknown Candidate"),
                "filename": candidate.get("filename"),
                "status": candidate.get("status"),
                "createdAt": candidate.get("createdAt"),
                "processedAt": candidate.get("processedAt"),
                "jobTitle": job_title,
                "matchResult": match_result,
            }
            ranked_results.append(candidate_record)

        # Sort candidates descending by match_percentage
        ranked_results.sort(
            key=lambda x: x.get("matchResult", {}).get("match_percentage", 0.0),
            reverse=True,
        )

        return success_response(ranked_results, 200)

    except KeyError as ke:
        logger.error("Missing environment variable: %s", str(ke))
        return error_response(f"Server configuration error: missing {str(ke)}", 500)
    except Exception as e:
        logger.exception("Unexpected error in match handler: %s", str(e))
        return error_response(f"Internal server error: {str(e)}", 500)
