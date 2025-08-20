# BigQuery permissions for the function service account
resource "google_project_iam_member" "bigquery_data_editor" {
  project = local.bigquery_project
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${local.sa_functions}"
}

resource "google_project_iam_member" "bigquery_job_user" {
  project = local.bigquery_project
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${local.sa_functions}"
}

# Resource Manager permissions at organization level
resource "google_organization_iam_member" "resource_manager_project_viewer" {
  org_id = var.org_id
  role   = "roles/viewer"
  member = "serviceAccount:${local.sa_functions}"
}

resource "google_organization_iam_member" "resource_manager_folder_viewer" {
  org_id = var.org_id
  role   = "roles/resourcemanager.folderViewer"
  member = "serviceAccount:${local.sa_functions}"
}

resource "google_organization_iam_member" "resource_manager_organization_viewer" {
  org_id = var.org_id
  role   = "roles/resourcemanager.organizationViewer"
  member = "serviceAccount:${local.sa_functions}"
}

resource "google_organization_iam_member" "resource_manager_tag_viewer" {
  org_id = var.org_id
  role   = "roles/resourcemanager.tagViewer"
  member = "serviceAccount:${local.sa_functions}"
}

# Cloud Function invoker permission
resource "google_project_iam_member" "tooling_function_invoker" {
  project = local.tooling_project
  role    = "roles/cloudfunctions.serviceAgent"
  member  = "serviceAccount:${local.sa_functions}"
}

# Cloud Build permissions for deployment
resource "google_project_iam_member" "cloud_build_allow" {
  project = local.tooling_project
  role    = "roles/cloudbuild.builds.builder"
  member  = "serviceAccount:${local.cloud_build_sa}"
}

# Optional: Monitoring permissions if monitoring project is specified
resource "google_project_iam_member" "monitoring_binding_writer" {
  count   = var.monitoring_project_id != "" ? 1 : 0
  project = var.monitoring_project_id != "" ? var.monitoring_project_id : local.tooling_project
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${local.sa_functions}"
}

# Logging permissions
resource "google_project_iam_member" "logging_writer" {
  project = local.tooling_project
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${local.sa_functions}"
}