variable "default_region" {
  description = "Default region to create resources where applicable."
  type        = string
  default     = "europe-west1"
}

variable "tooling_project_id" {
  description = "Project ID where the Cloud Function will be deployed"
  type        = string
}

variable "bigquery_project_id" {
  description = "Project ID where Bigquery will be used"
  type        = string
}

variable "tooling_bucket" {
  description = "GCS bucket name for storing Cloud Function source code"
  type        = string
}

variable "sa_functions_email" {
  description = "Service account email for Cloud Function execution"
  type        = string
}

variable "monitoring_project_id" {
  description = "Project ID for monitoring and logging (optional)"
  type        = string
  default     = ""
}

variable "cloud_build_sa_email" {
  description = "Service account email for Cloud Build"
  type        = string
}

variable "org_id" {
  description = "GCP Organization ID for tag collection"
  type        = string
}

variable "bq_dataset" {
  description = "BigQuery dataset name for project tags"
  type        = string
  default     = "billing_data"
}

variable "schedule" {
  description = "Cron schedule for Cloud Scheduler (daily at 1 AM)"
  type        = string
  default     = "0 1 * * *"
}

variable "timezone" {
  description = "Timezone for Cloud Scheduler"
  type        = string
  default     = "Europe/Paris"
}

variable "python_code_name" {
  description = "Name of Zip file used to push python code to cloud function"
  type        = string
}