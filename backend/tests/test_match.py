"""Unit tests for handlers.match Lambda handler."""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from decimal import Decimal

# Add backend root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestMatchHandler(unittest.TestCase):
    """Tests for the match handler."""

    def setUp(self):
        """Set up environment variables for each test."""
        os.environ["TABLE_NAME"] = "test-table"

    def tearDown(self):
        """Clean up environment variables."""
        os.environ.pop("TABLE_NAME", None)

    @patch("handlers.match.boto3")
    def test_successful_match(self, mock_boto3):
        """Test successful skill matching with candidates."""
        # Mock DynamoDB scan for completed candidates
        mock_table = MagicMock()
        mock_table.scan.return_value = {
            "Items": [
                {
                    "candidateId": "test-id-1",
                    "candidateName": "John Doe",
                    "filename": "john_doe.pdf",
                    "status": "COMPLETED",
                    "createdAt": "2024-01-01T00:00:00Z",
                    "resumeText": "Experienced in Python, Django, and PostgreSQL development.",
                },
                {
                    "candidateId": "test-id-2",
                    "candidateName": "Jane Smith",
                    "filename": "jane_smith.pdf",
                    "status": "COMPLETED",
                    "createdAt": "2024-01-02T00:00:00Z",
                    "resumeText": "React and JavaScript frontend developer with Node.js experience.",
                },
            ],
        }
        mock_dynamodb = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3.resource.return_value = mock_dynamodb

        from handlers.match import handler

        event = {
            "body": json.dumps({
                "jobTitle": "Backend Developer",
                "requirements": "Python, Django, PostgreSQL, Docker",
            }),
        }

        response = handler(event, None)
        body = json.loads(response["body"])

        assert response["statusCode"] == 200
        assert isinstance(body, list)
        assert len(body) == 2

        # First result should have higher match percentage (Python/Django/PostgreSQL match)
        assert body[0]["matchResult"]["match_percentage"] >= body[1]["matchResult"]["match_percentage"]

    @patch("handlers.match.boto3")
    def test_missing_requirements(self, mock_boto3):
        """Test error when requirements field is missing."""
        from handlers.match import handler

        event = {
            "body": json.dumps({
                "jobTitle": "Developer",
            }),
        }

        response = handler(event, None)
        body = json.loads(response["body"])

        assert response["statusCode"] == 400
        assert "error" in body

    @patch("handlers.match.boto3")
    def test_empty_requirements(self, mock_boto3):
        """Test error when requirements is empty string."""
        from handlers.match import handler

        event = {
            "body": json.dumps({
                "jobTitle": "Developer",
                "requirements": "   ",
            }),
        }

        response = handler(event, None)
        body = json.loads(response["body"])

        assert response["statusCode"] == 400

    @patch("handlers.match.boto3")
    def test_no_body(self, mock_boto3):
        """Test error when request body is missing."""
        from handlers.match import handler

        event = {}

        response = handler(event, None)
        body = json.loads(response["body"])

        assert response["statusCode"] == 400

    @patch("handlers.match.boto3")
    def test_results_sorted_by_percentage(self, mock_boto3):
        """Test that results are sorted by match percentage descending."""
        mock_table = MagicMock()
        mock_table.scan.return_value = {
            "Items": [
                {
                    "candidateId": "low-match",
                    "candidateName": "Low Match",
                    "filename": "low.pdf",
                    "status": "COMPLETED",
                    "resumeText": "I enjoy cooking and gardening.",
                },
                {
                    "candidateId": "high-match",
                    "candidateName": "High Match",
                    "filename": "high.pdf",
                    "status": "COMPLETED",
                    "resumeText": "Expert in Python, Django, React, Docker, Kubernetes, PostgreSQL.",
                },
            ],
        }
        mock_dynamodb = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3.resource.return_value = mock_dynamodb

        from handlers.match import handler

        event = {
            "body": json.dumps({
                "requirements": "Python, Django, React, Docker",
            }),
        }

        response = handler(event, None)
        body = json.loads(response["body"])

        assert response["statusCode"] == 200
        # High match should come first
        if len(body) >= 2:
            assert body[0]["matchResult"]["match_percentage"] >= body[1]["matchResult"]["match_percentage"]

    @patch("handlers.match.boto3")
    def test_base64_encoded_body(self, mock_boto3):
        """Test that base64-encoded body is handled correctly."""
        import base64

        mock_table = MagicMock()
        mock_table.scan.return_value = {"Items": []}
        mock_dynamodb = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3.resource.return_value = mock_dynamodb

        from handlers.match import handler

        payload = json.dumps({"requirements": "Python"})
        encoded = base64.b64encode(payload.encode()).decode()

        event = {
            "body": encoded,
            "isBase64Encoded": True,
        }

        response = handler(event, None)
        body = json.loads(response["body"])

        assert response["statusCode"] == 200
        assert isinstance(body, list)

    @patch("handlers.match.boto3")
    def test_cors_headers(self, mock_boto3):
        """Test CORS headers in response."""
        mock_table = MagicMock()
        mock_table.scan.return_value = {"Items": []}
        mock_dynamodb = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3.resource.return_value = mock_dynamodb

        from handlers.match import handler

        event = {
            "body": json.dumps({"requirements": "Python"}),
        }

        response = handler(event, None)

        assert "Access-Control-Allow-Origin" in response["headers"]
        assert response["headers"]["Access-Control-Allow-Origin"] == "*"

    def test_missing_env_var(self):
        """Test error when TABLE_NAME environment variable is missing."""
        os.environ.pop("TABLE_NAME", None)

        from handlers.match import handler

        event = {
            "body": json.dumps({"requirements": "Python"}),
        }

        response = handler(event, None)
        assert response["statusCode"] == 500


if __name__ == "__main__":
    unittest.main()
