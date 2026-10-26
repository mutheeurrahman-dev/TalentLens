# 🚀 AWS Setup & Deployment Guide for TalentLens

This guide walks you through deploying the complete TalentLens serverless stack to your AWS account using AWS SAM and configuring the frontend client.

---

## 📋 Prerequisites

Before starting the deployment, verify that you have the following tools installed and configured:

1. **AWS Account**: Active account with administrative privileges.
2. **AWS CLI v2**:
   - Check installation: `aws --version`
   - Configure credentials:
     ```bash
     aws configure
     ```
     Provide your AWS Access Key ID, Secret Access Key, default region (e.g. `us-east-1`), and default output format (`json`).
3. **AWS SAM CLI**:
   - Check installation: `sam --version`
   - [AWS SAM CLI Installation Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
4. **Python 3.12**:
   - Check installation: `python --version` (or `python3 --version`)
5. **Node.js 18+ & npm**:
   - Check installation: `node -v` and `npm -v`

---

## 🛠️ Step 1: Deploy Backend with SAM

Open your terminal, navigate to the `backend/` directory, and run `sam build` followed by guided deployment:

```bash
cd backend
sam build
sam deploy --guided
```

### Guided Prompts Explanation

During `sam deploy --guided`, SAM will prompt you with the following configuration questions:

1. **Stack Name [talentlens]**: Press <kbd>Enter</kbd> to accept the default `talentlens` (or enter a custom name).
2. **AWS Region [us-east-1]**: Choose your preferred region, e.g., `us-east-1`, `us-west-2`, or `ap-south-1`.
3. **Confirm changes before deploy [Y/n]**:
   - Enter `Y` to review the CloudFormation changeset before resources are provisioned.
4. **Allow SAM CLI IAM role creation [Y/n]**:
   - Enter `Y`. SAM will generate the required IAM execution roles for Lambda functions, DynamoDB, Textract, S3, and SQS.
5. **Disable rollback for deployments [y/N]**:
   - Enter `N` so that CloudFormation automatically rolls back changes if an error occurs.
6. **UploadFunction has no authentication. Is this okay? [y/N]**:
   - Enter `y` (allows public access for demo/evaluation API endpoints).
7. **CandidatesFunction has no authentication. Is this okay? [y/N]**:
   - Enter `y`.
8. **MatchFunction has no authentication. Is this okay? [y/N]**:
   - Enter `y`.
9. **Save arguments to configuration file [Y/n]**:
   - Enter `Y` (this updates `samconfig.toml` so future deployments can be run with just `sam deploy`).
10. **SAM configuration file [samconfig.toml]**: Press <kbd>Enter</kbd>.
11. **SAM configuration environment [default]**: Press <kbd>Enter</kbd>.

SAM will create the S3 deployment bucket (if not already existing), upload the Lambda packages, and trigger the CloudFormation deployment.

---

## 📌 Step 2: Note the Stack Outputs

Once CloudFormation successfully deploys all resources, SAM will print the **Outputs** table:

```text
-------------------------------------------------------------------------------------------------
Outputs
-------------------------------------------------------------------------------------------------
Key                 TalentLensApiUrl
Description         HTTP API Gateway endpoint URL
Value               https://a1b2c3d4e5.execute-api.us-east-1.amazonaws.com

Key                 TalentLensBucketName
Description         S3 bucket for storing resumes
Value               talentlens-resumes-123456789012-us-east-1

Key                 TalentLensTableName
Description         DynamoDB table name for candidate metadata
Value               TalentLensCandidates

Key                 TalentLensQueueUrl
Description         SQS processing queue URL
Value               https://sqs.us-east-1.amazonaws.com/123456789012/talentlens-processing-queue
-------------------------------------------------------------------------------------------------
```

> [!IMPORTANT]
> Save the `TalentLensApiUrl` value. You will need it in Step 3.
>
> **Note**: The API routes are `/api/upload`, `/api/candidates`, and `/api/match`. When setting `VITE_API_URL` in Step 3, you must append `/api` to the ApiUrl output value.

You can also retrieve these outputs at any time using the AWS CLI:
```bash
aws cloudformation describe-stacks --stack-name talentlens --query "Stacks[0].Outputs" --output table
```

---

## 💻 Step 3: Configure Frontend

1. Navigate to the `frontend/` directory.
2. Create a `.env` file. Take the `TalentLensApiUrl` value from Step 2 and **append `/api`**:

```bash
cd ../frontend
```

On Windows PowerShell:
```powershell
# Example: if TalentLensApiUrl = https://a1b2c3d4e5.execute-api.us-east-1.amazonaws.com
# Then VITE_API_URL = https://a1b2c3d4e5.execute-api.us-east-1.amazonaws.com/api
Set-Content -Path .env -Value "VITE_API_URL=https://<your-api-id>.execute-api.<region>.amazonaws.com/api"
```

On Linux/macOS:
```bash
echo "VITE_API_URL=https://<your-api-id>.execute-api.<region>.amazonaws.com/api" > .env
```

> [!WARNING]
> The `/api` suffix is required. Without it, API calls will return 404 errors because the Lambda routes are `/api/upload`, `/api/candidates`, and `/api/match`.

3. Build the production assets to verify everything compiles:
```bash
npm run build
```

---

## 🌐 Step 4: Host Frontend

### Option A: Local Development (Demo & Testing)
Run the Vite development server on your machine:
```bash
npm run dev
```
Visit `http://localhost:5173` to use the application.

### Option B: S3 + CloudFront (Production Deployment)
1. **Create an S3 bucket for web hosting**:
   ```bash
   aws s3 mb s3://talentlens-web-<your-account-id> --region us-east-1
   ```
2. **Build and upload static assets**:
   ```bash
   npm run build
   aws s3 sync dist/ s3://talentlens-web-<your-account-id> --delete
   ```
3. **Distribute via CloudFront**:
   - Create a CloudFront distribution pointing to the S3 bucket with an Origin Access Control (OAC).
   - Configure default root object to `index.html` and redirect 404/403 errors to `/index.html` for single-page routing.

---

## 🔬 Step 5: Test the Deployment

1. **Upload Resume**:
   - Open the frontend application in your browser.
   - Navigate to the **Upload** view and select a sample resume PDF.
   - Click **Upload**. The browser requests a presigned URL from `GET /api/upload` and uploads directly to S3.
2. **Verify Background Processing**:
   - S3 triggers an event to `talentlens-processing-queue`.
   - `ProcessResumeFunction` picks up the message, invokes Amazon Textract, extracts contact details and skill sets, and persists the record into DynamoDB.
   - Inspect DynamoDB to confirm the record:
     ```bash
     aws dynamodb scan --table-name TalentLensCandidates --max-items 5
     ```
3. **Evaluate Job Matching**:
   - In the frontend, navigate to **Job Match**.
   - Enter required skills (e.g., `Python, AWS, Docker`) and minimum experience years.
   - Click **Run Match** and verify the ranked candidate scores returned by `POST /api/match`.

---

## 📊 Monitoring & Debugging

### 1. Lambda CloudWatch Logs
To stream logs live from any of the Lambda handlers:
```bash
# ProcessResumeFunction logs
sam logs -n ProcessResumeFunction --stack-name talentlens --tail

# UploadFunction logs
sam logs -n UploadFunction --stack-name talentlens --tail

# MatchFunction logs
sam logs -n MatchFunction --stack-name talentlens --tail
```

### 2. DynamoDB Candidate Records
View items stored in the candidate table:
```bash
aws dynamodb scan --table-name TalentLensCandidates
```

### 3. SQS Dead-Letter Queue (DLQ)
Check if any documents failed processing and landed in the DLQ:
```bash
aws sqs get-queue-attributes \
  --queue-url $(aws sqs get-queue-url --queue-name talentlens-processing-dlq --query "QueueUrl" --output text) \
  --attribute-names ApproximateNumberOfMessages
```

---

## 🧹 Cleanup & Teardown

To avoid incurring ongoing charges when you are finished using TalentLens, delete all AWS resources:

```bash
# 1. Empty the S3 Resume bucket (CloudFormation cannot delete non-empty buckets)
BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name talentlens --query "Stacks[0].Outputs[?OutputKey=='BucketName'].OutputValue" --output text)
aws s3 rm s3://$BUCKET_NAME --recursive

# 2. Delete the CloudFormation stack via SAM
cd backend
sam delete --stack-name talentlens --no-prompts
```

### What `sam delete` Removes:
- S3 Resume Bucket
- DynamoDB Table (`TalentLensCandidates`)
- SQS Queues (`talentlens-processing-queue` & `talentlens-processing-dlq`)
- Queue Policies and IAM execution roles
- HTTP API Gateway (`TalentLensApi`) and all routes
- All 4 AWS Lambda functions

---

## 💰 Cost Estimation

TalentLens is built entirely on serverless, pay-as-you-go AWS services:

| Service | Free Tier Allowance | Standard Cost After Free Tier |
| :--- | :--- | :--- |
| **AWS Lambda** | 1,000,000 requests/month & 3.2M seconds compute | $0.20 per 1M requests |
| **Amazon API Gateway** | 1,000,000 HTTP API calls/month (first 12 mos) | $1.00 per 1M requests |
| **Amazon S3** | 5 GB standard storage & 20,000 GET requests | $0.023 per GB-month |
| **Amazon DynamoDB** | 25 GB storage & 25 WCU / 25 RCU | On-Demand: $0.25 per 1M WRU, $0.125 per 1M RRU |
| **Amazon SQS** | 1,000,000 requests/month | $0.40 per 1M requests |
| **Amazon Textract** | 1,000 pages/month (first 3 mos with `DetectDocumentText`) | $1.50 per 1,000 pages processed |

> [!NOTE]
> For demo, evaluation, and moderate testing workloads, the overall operational cost is effectively **$0.00** under AWS Free Tier.

---

## 🛠️ Troubleshooting

### 1. CORS Errors in Browser
- **Symptom**: Browser reports `No 'Access-Control-Allow-Origin' header is present on the requested resource`.
- **Solution**:
  - Verify that `TalentLensApi` in `backend/template.yaml` includes `AllowOrigins: ['*']` and `AllowMethods: ['GET', 'POST', 'OPTIONS']`.
  - Check that the `ResumeBucket` CORS configuration includes `AllowedMethods: [GET, PUT, HEAD]` for presigned PUT uploads.

### 2. Amazon Textract Timeout
- **Symptom**: `ProcessResumeFunction` reports `Task timed out after 30.00 seconds`.
- **Solution**:
  - The `ProcessResumeFunction` is configured with a timeout of `180` seconds and `512 MB` memory. Large multi-page documents may take up to 60-90 seconds to extract. Ensure the SQS visibility timeout (`VisibilityTimeout: 300`) remains greater than the Lambda function timeout.

### 3. SQS Queue Not Receiving S3 Events
- **Symptom**: Files are uploaded to S3, but `talentlens-processing-queue` receives no messages.
- **Solution**:
  - Ensure the uploaded file path starts with `resumes/` (the S3 prefix filter configured in `template.yaml`).
  - Verify that `ProcessingQueuePolicy` grants `sqs:SendMessage` to `s3.amazonaws.com` matching the S3 bucket ARN.
  - Confirm the S3 bucket has `DependsOn: ProcessingQueuePolicy` to avoid race conditions during stack provisioning.

### 4. IAM Permission Denied Errors
- **Symptom**: Lambda logs indicate `AccessDeniedException` when calling DynamoDB or Textract.
- **Solution**:
  - Check the SAM policy templates on the respective functions (`S3CrudPolicy`, `DynamoDBCrudPolicy`, `DynamoDBReadPolicy`, and the inline Statement for `textract:StartDocumentTextDetection` and `textract:GetDocumentTextDetection`).
  - If custom roles were specified, redeploy with `sam deploy --guided` and ensure IAM role creation is permitted.
