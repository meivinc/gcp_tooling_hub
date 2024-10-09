
resource "google_storage_bucket_object" "object" {
  name    = "label-parsing-v2.0.zip"
  bucket  = local.tooling_bucket
  source  = "./label-parsing-v2.0.zip" # Add path to the zipped function source code
}

resource "google_cloudfunctions2_function" "default" {
  name        = "cfu-org-info-parsing"
  location    = var.default_region
  description = "application relative to Label parsing"

  build_config {
    runtime     = "python312"
    entry_point = "process_projects_http" # Set the entry point
    source {
      storage_source {
        bucket = local.tooling_bucket
        object = google_storage_bucket_object.object.name
      }
    }
  }

  service_config {
    max_instance_count = 1
    available_memory   = "256M"
    service_account_email = local.sa_functions
  }
  project = local.tooling_project

}




