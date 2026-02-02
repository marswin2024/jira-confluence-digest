#!/bin/bash

# Jira & Confluence Daily Digest - Google Cloud Run Deployment Script

set -e

echo "=========================================="
echo "Google Cloud Run Deployment"
echo "=========================================="

# Configuration
PROJECT_ID="your-gcp-project-id"
SERVICE_NAME="jira-confluence-digest"
REGION="europe-west1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "Project ID: ${PROJECT_ID}"
echo "Service Name: ${SERVICE_NAME}"
echo "Region: ${REGION}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed"
    echo "Install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Build and push Docker image
echo "Step 1: Building Docker image..."
gcloud builds submit --tag ${IMAGE_NAME} --project ${PROJECT_ID}

# Deploy to Cloud Run
echo "Step 2: Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --no-allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 900 \
  --set-env-vars "JIRA_URL=${JIRA_URL},JIRA_USERNAME=${JIRA_USERNAME},JIRA_API_TOKEN=${JIRA_API_TOKEN},CONFLUENCE_URL=${CONFLUENCE_URL},CONFLUENCE_USERNAME=${CONFLUENCE_USERNAME},CONFLUENCE_API_TOKEN=${CONFLUENCE_API_TOKEN},SMTP_HOST=${SMTP_HOST},SMTP_PORT=${SMTP_PORT},SMTP_USERNAME=${SMTP_USERNAME},SMTP_PASSWORD=${SMTP_PASSWORD},RECIPIENT_EMAIL=${RECIPIENT_EMAIL},TIMEZONE=Europe/Berlin" \
  --project ${PROJECT_ID}

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --platform managed --region ${REGION} --format 'value(status.url)' --project ${PROJECT_ID})

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo "Service URL: ${SERVICE_URL}"
echo ""
echo "Next steps:"
echo "1. Test the service: curl -X POST ${SERVICE_URL}/run-digest -H \"Authorization: Bearer \$(gcloud auth print-identity-token)\""
echo "2. Create Cloud Scheduler job to run daily at 7:00 AM"
echo ""
