resource "google_project_iam_member" "monitoring_binding_writer" {
  project = local.monitoring_project
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${local.sa_functions}"
}

resource "google_project_iam_member" "tooling_function_invoker" {
  project = local.tooling_project
  role    = "roles/cloudfunctions.serviceAgent"
  member  = "serviceAccount:${local.sa_functions}"
}


resource "google_project_iam_member" "cloud_build_allow" {
  project = local.tooling_project
  role    = "roles/cloudbuild.builds.builder"
  member  = "serviceAccount:${local.cloud_build_sa}" 
}