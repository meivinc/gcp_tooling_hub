# Create a Cloud Scheduler job for daily execution
resource "google_cloud_scheduler_job" "tags_scheduler" {
  name             = "trigger-cfu-tags-to-bigquery"
  region           = var.default_region
  schedule         = var.schedule         # Daily at 1 AM by default
  time_zone        = var.timezone         # Europe/Paris by default
  attempt_deadline = "1800s"              # 30 minutes timeout
  description      = "Daily trigger for GCP project tags collection"

  retry_config {
    retry_count = 3
  }

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions2_function.tags_function.url

    oidc_token {
      service_account_email = local.sa_functions
      audience             = google_cloudfunctions2_function.tags_function.url
    }
  }

  project = local.tooling_project
}