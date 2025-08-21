# Upload function source code to GCS bucket
resource "google_storage_bucket_object" "object" {
  name   = var.python_code_name
  bucket = local.tooling_bucket
  source = data.archive_file.function_source.output_path
}

# Cloud Function for tags collection and BigQuery upload
resource "google_cloudfunctions2_function" "tags_function" {
  name        = "cfu-tags-to-bigquery"
  location    = var.default_region
  description = "Daily extraction of GCP project tags to BigQuery for billing analysis"

  build_config {
    runtime     = "python311"
    entry_point = "tags_to_bigquery_function"
    source {
      storage_source {
        bucket = local.tooling_bucket
        object = google_storage_bucket_object.object.name
      }
    }
  }

  service_config {
    max_instance_count    = 1
    min_instance_count    = 0
    available_memory      = "256M"
    timeout_seconds       = 3600  # 60 minutes
    service_account_email = local.sa_functions

    environment_variables = {
      ORG_ID            = var.org_id
      BQ_PROJECT_ID     = local.bigquery_project
      BQ_DATASET        = var.bq_dataset
      BQ_TABLE_PROJECTS = "projects_with_tags"
      BQ_TABLE_TAGS     = "project_tags"
    }
  }

  # No event trigger needed for HTTP functions

  project = local.tooling_project
}

# No Pub/Sub topic needed for HTTP trigger