"""Unit tests for handlers.upload Lambda handler."""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add backend root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestUploadHandler(unittest.TestCase):
    """Tests for the upload handler."""

    def setUp(self):
        """Set up environment variables for each test."""
        os.environ["BUCKET_NAME"] = "test-bucket"
        os.environ["TABLE_NAME"] = "test-table"

    def tearDown(self):
        """Clean up environment variables."""
        os.environ.pop("BUCKET_NAME", None)
        os.environ.pop("TABLE_NAME", None)

    @patch("handlers.upload.boto3")
    def test_successful_upload(self, mock_boto3):
        """Test successful presigned URL generation."""
        # Mock S3 client
        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.return_value = "https://s3.example.com/presigned"
        mock_boto3.client.return_value = mock_s3

        # Mock DynamoDB
        mock_table = MagicMock()
        mock_dynamodb = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3.resource.return_value = mock_dynamodb

        from handlers.upload import handler

        event = {
            "queryStringParameters": {"filename": "resume.pdf"},
        }

        response = handler(event, None)
        body = json.loads(response["body"])

        assert response["statusCode"] == 200
        assert "candidateId" in body
        assert "uploadUrl" in body
        assert "s3Key" in body
        assert body["uploadUrl"] == "https://s3.example.com/presigned"
        assert body["s3Key"].startswith("resumes/")
        assert body["s3Key"].endswith("/resume.pdf")

    @patch("handlers.upload.boto3")
    def test_missing_filename(self, mock_boto3):
        """Test error when filename is missing."""
        from handlers.upload import handler

        event = {"queryStringParameters": {}}

        response = handler(event, None)
        body = json.loads(response["body"])

        assert response["statusCode"] == 400
        assert "error" in body

    @patch("handlers.upload.boto3")
    def test_non_pdf_file(self, mock_boto3):
        """Test error when file is not a PDF."""
        from handlers.upload import handler

        event = {"queryStringParameters": {"filename": "resume.docx"}}

        response = handler(event, None)
        body = json.loads(response["body"])

        assert response["statusCode"] == 400
        assert "pdf" in body["error"].lower()

    @patch("handlers.upload.boto3")
    def test_no_query_params(self, mock_boto3):
        """Test error when no query parameters provided."""
        from handlers.upload import handler

        event = {"queryStringParameters": None}

        response = handler(event, None)
        body = json.loads(response["body"])

        assert response["statusCode"] == 400

    @patch("handlers.upload.boto3")
    def test_post_upload_failure(self, mock_boto3):
        """Test reporting upload failure via POST."""
        mock_table = MagicMock()
        mock_dynamodb = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3.resource.return_value = mock_dynamodb

        from handlers.upload import handler

        event = {
            "httpMethod": "POST",
            "body": json.dumps({
                "candidateId": "cand-123",
                "status": "FAILED",
                "errorMessage": "Network error during upload",
            }),
        }

        response = handler(event, None)
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["candidateId"] == "cand-123"
        assert body["status"] == "FAILED"
        mock_table.update_item.assert_called_once()

    def test_missing_env_vars(self):
        """Test error when environment variables are missing."""
        os.environ.pop("BUCKET_NAME", None)
        os.environ.pop("TABLE_NAME", None)

        from handlers.upload import handler

        event = {"queryStringParameters": {"filename": "resume.pdf"}}

        response = handler(event, None)

        assert response["statusCode"] == 500


class TestUploadHandlerCORS(unittest.TestCase):
    """Tests for CORS headers in upload responses."""

    def setUp(self):
        os.environ["BUCKET_NAME"] = "test-bucket"
        os.environ["TABLE_NAME"] = "test-table"

    def tearDown(self):
        os.environ.pop("BUCKET_NAME", None)
        os.environ.pop("TABLE_NAME", None)

    @patch("handlers.upload.boto3")
    def test_cors_headers_present(self, mock_boto3):
        """Test that CORS headers are included in all responses."""
        from handlers.upload import handler

        event = {"queryStringParameters": {"filename": "resume.pdf"}}

        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.return_value = "https://example.com"
        mock_boto3.client.return_value = mock_s3

        mock_table = MagicMock()
        mock_dynamodb = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3.resource.return_value = mock_dynamodb

        response = handler(event, None)

        assert "Access-Control-Allow-Origin" in response["headers"]
        assert response["headers"]["Access-Control-Allow-Origin"] == "*"


if __name__ == "__main__":
    unittest.main()
