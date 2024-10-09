# Create a Cloud Scheduler job
resource "google_cloud_scheduler_job" "main" {
  name             = "trigger-cfu-org-info-parsing"
  region           = var.default_region # Replace with your Cloud Function's region
  schedule         = "0 */4 * * *" # Run every 25 minutes
  time_zone        = "Europe/Paris" # Replace with your desired timezone
  attempt_deadline = "320s" # Adjust as needed

  http_target {
    http_method = "GET" # Use "POST" for Cloud Functions HTTP triggers
    uri         = "${google_cloudfunctions2_function.default.url}/${google_cloudfunctions2_function.default.build_config[0].entry_point}" # Replace with your Cloud Function's URL 

    # Optional: If your Cloud Function requires authentication, add headers here
    # headers = {
    #   Authorization = "Bearer ${data.google_iam_service_account_access_token.default.access_token}"
    # }
    oidc_token {
      service_account_email = local.sa_functions
      audience = "${google_cloudfunctions2_function.default.url}"
    }
  }
  project = local.tooling_project

}
