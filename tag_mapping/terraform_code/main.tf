locals {
  tooling_project   = var.tooling_project_id  # FORMAT = PROJECT-ID
  tooling_bucket    = var.tooling_bucket      # FORMAT = bucket_name
  bigquery_project = var.bigquery_project_id  # FORMAT = PROJECT-ID
  sa_functions      = var.sa_functions_email   # FORMAT = sa@<proj>.iam - Service account email
  monitoring_project = var.monitoring_project_id # FORMAT = PROJECT-ID (optional, for logging)
  cloud_build_sa    = var.cloud_build_sa_email # FORMAT = sa@<proj>.iam - Service account email
}

# Create zip file from source code
data "archive_file" "function_source" {
  type        = "zip"
  source_dir  = "../python_code/dev"
  output_path = "./tags-to-bigquery-v1.0.zip"
  excludes = [
    "venv",
    "__pycache__",
    "*.pyc",
    ".git",
    "test_*.py",
    "dry_run_*.json",
    "requirements_local.txt"
  ]
}