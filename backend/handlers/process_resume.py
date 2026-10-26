"""Lambda handler triggered by SQS to extract text from resume PDFs using AWS Textract."""

import datetime
import json
import logging
import os
import re
import time
import urllib.parse
from typing import Any, Dict, List, Optional

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _extract_name_heuristic(lines: List[str]) -> str:
    """Extract candidate name from the first few lines of text.

    Uses a heuristic looking for the first non-empty line formatted like a human name
    (2 to 4 words, letters only, excluding header words like Resume, CV, Curriculum Vitae).

    Args:
        lines: List of raw lines extracted from Textract.

    Returns:
        Extracted candidate name or 'Unknown Candidate'.
    """
    excluded_keywords = {
        "resume",
        "curriculum",
        "vitae",
        "cv",
        "profile",
        "summary",
        "page",
        "contact",
        "email",
        "phone",
        "address",
        "experience",
        "education",
        "skills",
    }

    for line in lines[:10]:
        cleaned = line.strip()
        if not cleaned:
            continue

        words = cleaned.split()
        if 2 <= len(words) <= 4:
            # Check if all words are alphabetic (allow dots/hyphens like St. or Anne-Marie)
            is_alphabetic = all(re.match(r"^[A-Za-z.\-]+$", w) for w in words)
            has_no_keywords = not any(w.lower() in excluded_keywords for w in words)
            if is_alphabetic and has_no_keywords:
                return " ".join(words)

    # Fallback to first non-empty line if reasonably short, otherwise Unknown
    for line in lines[:5]:
        cleaned = line.strip()
        if cleaned and len(cleaned) < 50:
            return cleaned

    return "Unknown Candidate"


def _extract_text_from_pdf_s3(bucket_name: str, s3_key: str) -> List[str]:
    """Fallback text extraction: downloads PDF from S3 and extracts text via pypdf."""
    logger.info("Extracting text directly from S3 PDF: bucket=%s, key=%s", bucket_name, s3_key)
    region = os.environ.get("AWS_REGION", "ap-south-1")
    s3_client = boto3.client("s3", region_name=region)
    obj = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
    pdf_bytes = obj["Body"].read()

    lines: List[str] = []
    try:
        import io
        import pypdf

        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages:
            page_text = page.extract_text() or ""
            for line in page_text.splitlines():
                cleaned = line.strip()
                if cleaned:
                    lines.append(cleaned)
    except Exception as pdf_err:
        logger.warning("pypdf parsing failed: %s; falling back to stream parsing", str(pdf_err))
        import zlib

        stream_pattern = re.compile(rb"stream[\r\n]+(.*?)[\r\n]+endstream", re.DOTALL)
        for match in stream_pattern.finditer(pdf_bytes):
            stream_data = match.group(1)
            try:
                decomp = zlib.decompress(stream_data)
            except Exception:
                decomp = stream_data
            for m in re.finditer(rb"\((.*?)\)", decomp):
                try:
                    cleaned = m.group(1).decode("utf-8", errors="ignore").strip()
                    if cleaned and len(cleaned) > 1:
                        lines.append(cleaned)
                except Exception:
                    pass

    return lines


def _process_single_record(record: Dict[str, Any], textract_client: Any, table: Any) -> None:
    """Process a single SQS message containing an S3 event.

    Args:
        record: SQS record dictionary.
        textract_client: Boto3 Textract client.
        table: DynamoDB Table resource.
    """
    body_str = record.get("body", "{}")
    body = json.loads(body_str)

    # Some configurations wrap S3 events in SNS before SQS
    if "Message" in body and isinstance(body["Message"], str):
        try:
            body = json.loads(body["Message"])
        except Exception:
            pass

    records = body.get("Records", [])
    if not records:
        logger.warning("No S3 records found in SQS message body.")
        return

    for s3_event in records:
        s3_info = s3_event.get("s3", {})
        bucket_name = s3_info.get("bucket", {}).get("name")
        raw_key = s3_info.get("object", {}).get("key")

        if not bucket_name or not raw_key:
            logger.warning("Missing bucket name or object key in S3 record: %s", s3_info)
            continue

        s3_key = urllib.parse.unquote_plus(raw_key)
        logger.info("Processing S3 object: bucket=%s, key=%s", bucket_name, s3_key)

        # Expected format: resumes/{candidateId}/{filename}
        key_parts = s3_key.split("/")
        if len(key_parts) < 3 or key_parts[0] != "resumes":
            logger.error("S3 key '%s' does not conform to resumes/{candidateId}/{filename}", s3_key)
            continue

        candidate_id = key_parts[1]
        filename = key_parts[2]

        try:
            # Update candidate status to PROCESSING
            table.update_item(
                Key={"candidateId": candidate_id},
                UpdateExpression="SET #s = :status",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={":status": "PROCESSING"},
            )

            text_lines: List[str] = []

            # Attempt asynchronous Textract document text detection
            try:
                start_response = textract_client.start_document_text_detection(
                    DocumentLocation={
                        "S3Object": {
                            "Bucket": bucket_name,
                            "Name": s3_key,
                        }
                    }
                )
                job_id = start_response["JobId"]
                logger.info("Started Textract JobId: %s for candidateId: %s", job_id, candidate_id)

                # Poll get_document_text_detection with exponential backoff
                poll_interval = 2.0
                max_poll_interval = 10.0
                elapsed = 0.0
                timeout = 120.0
                job_status = "IN_PROGRESS"

                while elapsed < timeout:
                    time.sleep(poll_interval)
                    elapsed += poll_interval

                    status_response = textract_client.get_document_text_detection(JobId=job_id)
                    job_status = status_response.get("JobStatus")

                    if job_status in ("SUCCEEDED", "FAILED"):
                        break

                    poll_interval = min(poll_interval * 1.5, max_poll_interval)

                if job_status == "SUCCEEDED":
                    next_token: Optional[str] = None
                    while True:
                        get_kwargs: Dict[str, Any] = {"JobId": job_id}
                        if next_token:
                            get_kwargs["NextToken"] = next_token

                        result = textract_client.get_document_text_detection(**get_kwargs)
                        blocks = result.get("Blocks", [])

                        for block in blocks:
                            if block.get("BlockType") == "LINE":
                                line_text = block.get("Text", "").strip()
                                if line_text:
                                    text_lines.append(line_text)

                        next_token = result.get("NextToken")
                        if not next_token:
                            break
                else:
                    logger.warning("Textract job did not succeed (status=%s), falling back to S3 PDF extraction", job_status)
                    text_lines = _extract_text_from_pdf_s3(bucket_name, s3_key)

            except Exception as textract_err:
                logger.warning(
                    "Textract invocation failed (%s). Falling back to direct PDF text extraction.",
                    str(textract_err),
                )
                text_lines = _extract_text_from_pdf_s3(bucket_name, s3_key)

            full_resume_text = "\n".join(text_lines)
            candidate_name = _extract_name_heuristic(text_lines)
            if candidate_name == "Unknown Candidate" and filename:
                candidate_name = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ")
            processed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

            # Update DynamoDB with completed status
            table.update_item(
                Key={"candidateId": candidate_id},
                UpdateExpression="SET #s = :status, resumeText = :text, candidateName = :name, processedAt = :ts",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={
                    ":status": "COMPLETED",
                    ":text": full_resume_text,
                    ":name": candidate_name,
                    ":ts": processed_at,
                },
            )
            logger.info("Successfully processed resume for candidate: %s", candidate_id)

        except Exception as proc_err:
            logger.exception("Error processing candidateId %s: %s", candidate_id, str(proc_err))
            try:
                table.update_item(
                    Key={"candidateId": candidate_id},
                    UpdateExpression="SET #s = :status, errorMessage = :err",
                    ExpressionAttributeNames={"#s": "status"},
                    ExpressionAttributeValues={":status": "FAILED", ":err": str(proc_err)},
                )
            except Exception as ddb_err:
                logger.exception("Failed to update status to FAILED in DynamoDB: %s", str(ddb_err))
            raise proc_err


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle SQS events triggering resume text extraction via AWS Textract.

    Args:
        event: SQS invocation event containing batch records.
        context: Lambda context object.

    Returns:
        dict: SQS batch item failures response structure.
    """
    logger.info("Received SQS batch event with %d records", len(event.get("Records", [])))

    table_name = os.environ["TABLE_NAME"]
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    textract_client = boto3.client("textract")

    batch_item_failures: List[Dict[str, str]] = []

    for record in event.get("Records", []):
        message_id = record.get("messageId", "")
        try:
            _process_single_record(record, textract_client, table)
        except Exception as e:
            logger.error("Failed processing SQS message %s: %s", message_id, str(e))
            batch_item_failures.append({"itemIdentifier": message_id})

    return {"batchItemFailures": batch_item_failures}
