# GCP Project Tags to BigQuery - Terraform Deployment

This Terraform configuration deploys a Cloud Function that automatically collects GCP project tags and uploads them to BigQuery for billing analysis. The function is triggered daily by Cloud Scheduler.

## Architecture Overview

- **Cloud Function (Gen 2)**: Executes the tags collection and BigQuery upload (HTTP trigger)
- **Cloud Scheduler**: Triggers the function daily at 1 AM via direct HTTP call (configurable)
- **Service Accounts**: Dedicated SAs with minimal required permissions
- **BigQuery Dataset**: Auto-created dataset for storing project tags data

## File Structure

```
terraform_code/
├── main.tf              # Main configuration and locals
├── variables.tf         # Variable definitions
├── functions.tf         # Cloud Function resources
├── scheduler.tf         # Cloud Scheduler configuration
├── binding.tf           # IAM bindings and permissions
├── terraform.tfvars.example  # Example configuration
└── README.md           # This file
```

## Prerequisites

### 1. Terraform Setup
- Terraform >= 1.0 installed
- Google Cloud SDK installed and authenticated
- Access to a GCP project for deployment

### 2. Required Resources
- **GCS Bucket**: For storing Cloud Function source code
- **Service Accounts**: Function execution and Cloud Build
- **Organization Permissions**: Tag viewing and resource listing

### 3. Pre-created Resources
You need to create these resources before running Terraform:

```bash
# Create GCS bucket for function source
gsutil mb gs://your-bucket-name

# Create service account for Cloud Function
gcloud iam service-accounts create sa-tags \
  --display-name="Tags to BigQuery Function SA"

# Create service account for Cloud Build (if needed)
gcloud iam service-accounts create sa-cloudbuild \
  --display-name="Cloud Build SA"
```

## Deployment Steps

### 1. Configure Variables
```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your actual values
```

**Required variables to update:**
- `tooling_project_id`: Your GCP project ID (where Cloud Function is deployed)
- `bigquery_project_id`: Your BigQuery project ID (can be same or different)
- `tooling_bucket`: Your GCS bucket name
- `sa_functions_email`: Service account email for function execution
- `cloud_build_sa_email`: Service account email for Cloud Build
- `org_id`: Your GCP organization ID

### 2. Initialize and Deploy
```bash
terraform init
terraform plan
terraform apply
```

### 3. Verify Deployment
```bash
# Check function deployment
gcloud functions list --filter="name:cfu-tags-to-bigquery"

# Check scheduler job
gcloud scheduler jobs list --filter="name:trigger-cfu-tags-to-bigquery"

# Trigger manually for testing
gcloud scheduler jobs run trigger-cfu-tags-to-bigquery --location=europe-west1

# Test function directly via HTTP
curl -X POST "https://REGION-PROJECT-ID.cloudfunctions.net/cfu-tags-to-bigquery" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)"
```

## Configuration Options

### Function Settings
- **Memory**: 256MB (configurable in functions.tf)
- **Timeout**: 30 minutes (maximum allowed for Cloud Functions)
- **Runtime**: Python 3.11
- **Max Instances**: 1 (prevents parallel executions)

### Scheduler Settings
- **Default Schedule**: `0 1 * * *` (daily at 1 AM)
- **Timezone**: Europe/Paris
- **Retry**: 3 attempts on failure
- **Timeout**: 30 minutes

### BigQuery Tables Created
The function automatically creates:
1. `projects_with_tags` - Main project information
2. `project_tags` - Normalized tags for filtering

## Permissions

### Organization-level Permissions
The function service account gets these org-level roles:
- `roles/viewer` - View all GCP resources (includes project access)
- `roles/resourcemanager.folderViewer` - View folder hierarchy
- `roles/resourcemanager.organizationViewer` - View organization
- `roles/resourcemanager.tagViewer` - Read tags and tag bindings

### Project-level Permissions

**BigQuery Project (`bigquery_project_id`):**
- `roles/bigquery.dataEditor` - Write to BigQuery tables
- `roles/bigquery.jobUser` - Execute BigQuery jobs

**Tooling Project (`tooling_project_id`):**
- `roles/cloudfunctions.serviceAgent` - Cloud Function execution
- `roles/logging.logWriter` - Write function logs
- `roles/cloudbuild.builds.builder` - Deploy function via Cloud Build

## Monitoring

### View Function Logs
```bash
gcloud functions logs read cfu-tags-to-bigquery --region=europe-west1
```

### Check Scheduler Status
```bash
gcloud scheduler jobs describe trigger-cfu-tags-to-bigquery --location=europe-west1
```

### Monitor BigQuery Tables
```sql
-- Check recent data uploads (replace PROJECT-ID with your BigQuery project)
SELECT export_date, COUNT(*) as project_count
FROM `PROJECT-ID.billing_data.projects_with_tags`
GROUP BY export_date
ORDER BY export_date DESC
LIMIT 7;
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
   - Verify service account has organization-level permissions
   - Check that the SA is enabled and active

2. **Function Timeout**
   - Maximum timeout is 30 minutes (Cloud Functions limit)
   - Consider optimizing for very large organizations (1000+ projects)
   - Break down processing if needed

3. **BigQuery Errors**
   - Verify dataset exists and SA has access
   - Check BigQuery quotas and limits

4. **Scheduler Not Triggering**
   - Verify function URL is accessible
   - Check scheduler job status and logs
   - Ensure OIDC token authentication is working

### Debug Function Locally
```bash
cd ../python_code/dev
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_local.txt
python test_dry_run.py
```

## Cost Optimization

- **Function execution**: ~2-10 minutes daily
- **Estimated cost**: $1-5/month for typical organizations
- **Storage**: BigQuery storage with 1-year retention
- **Network**: Minimal API calls

## Maintenance

### Updates
To update the function code:
1. Modify code in `../python_code/dev/`
2. Run `terraform apply` to redeploy

### Monitoring
- Set up BigQuery monitoring for data freshness
- Monitor function execution logs for errors
- Review organization changes that might affect permissions

## Cleanup

```bash
terraform destroy
```

**Note**: This removes the function and scheduler but preserves:
- BigQuery dataset and tables (data retention)
- Service accounts (reusable)  
- GCS bucket (reusable)

## Manual Testing

### Test Function Directly
```bash
# Get function URL
FUNCTION_URL=$(gcloud functions describe cfu-tags-to-bigquery --region=europe-west1 --format="value(serviceConfig.uri)")

# Test with authentication
curl -X POST "$FUNCTION_URL" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{"test": "manual-trigger"}'
```

### Monitor Execution
```bash
# Watch logs in real-time
gcloud functions logs tail cfu-tags-to-bigquery --region=europe-west1

# Check BigQuery for new data (replace PROJECT-ID with your BigQuery project)
bq query --use_legacy_sql=false 'SELECT export_date, COUNT(*) FROM `PROJECT-ID.billing_data.projects_with_tags` GROUP BY export_date ORDER BY export_date DESC LIMIT 5'
```