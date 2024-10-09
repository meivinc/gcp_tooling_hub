from google.cloud import resourcemanager_v3
from google.cloud import monitoring_v3
from global_func import export_to_json 
from global_func import upload_json_to_gcs 

import time
import functions_framework # Import for HTTP triggering
# Authenticate (ensure you have set up Google Cloud authentication)
# See https://cloud.google.com/docs/authentication/getting-started

@functions_framework.http
def process_projects_http(request):
    """HTTP Cloud Function entry point. 

    Args:
        request (flask.Request): The request object.

    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    process_projects()  # Call your main processing logic
    return "Project processing complete!"

    
# Create a client
client = resourcemanager_v3.ProjectsClient()

# Create a Cloud Monitoring client (can be global or passed as argument)
monitoring_client = monitoring_v3.MetricServiceClient()

# Define the filter expression
filter_expression = 'state:ACTIVE'
# Create the request with the filter
request = resourcemanager_v3.SearchProjectsRequest(
    query=filter_expression
)

# Constants (consider using uppercase for constants)
OWNER_LABEL = "owner" # Label to filter on 
PROJECTS_WITH_OWNER_FILE = "projects_with_owner.json"
PROJECTS_WITHOUT_OWNER_FILE = "projects_without_owner.json"
BUCKET_NAME = "gcp-bucket-name" # Google Bucket Name
BUCKET_PROJECT = "project-id-exemple" # Google Project ID 

# Monitoring 
PROJECT_ID = "project-id-exemple" # Google Project ID 




def process_project_parse(project, projects_with_owner, projects_without_owner):
    """Processes a single project and appends its details to the appropriate list."""
    project_info = {
        "Project Name": project.name.split("/")[-1],
        "Project ID": project.project_id,
        "Project Number": project.name,
        "Labels": dict(project.labels)  # Convert to regular dictionary
    }
    if "owner" in project.labels:
        projects_with_owner.append(project_info)
    else:
        projects_without_owner.append(project_info)


def write_metric_for_each_project(project_name, metric_name, metric_value):
    """Writes a metric for a single project with a specified value.

    Args:
        project_name: The name of the project.
        metric_name: The name of the custom metric.
        metric_value: The value to write for this project's metric.
    """
    # Aggregate labels into a string
    aggregated_labels = ','.join(project_name.labels.keys()) 

    project_id = f"projects/{PROJECT_ID}" 
    time_series_list = []

    now = time.time()
    seconds = int(now)
    nanos = int((now - seconds) * 10**9)
    interval = monitoring_v3.TimeInterval(
        {"end_time": {"seconds": seconds, "nanos": nanos}}
    )

    series = monitoring_v3.TimeSeries()
    series.metric.type = f"custom.googleapis.com/{metric_name}" 
    series.resource.type = "global"

    # Correctly initialize labels as an empty dictionary
    # series.metric.labels = {} 

    # Add project_name and project_id as metric labels
    series.metric.labels["project_name"] = project_name.display_name
    series.metric.labels["project_id"] = project_name.project_id
    series.metric.labels["labels"] = aggregated_labels

    point = monitoring_v3.Point({"interval": interval, "value": {"int64_value": metric_value}})
    series.points = [point]
    time_series_list.append(series)

    monitoring_client = monitoring_v3.MetricServiceClient()
    monitoring_client.create_time_series(name=project_id, time_series=time_series_list)
    print(f"Successfully wrote '{metric_name}' metric for project: {project_name.display_name}")


# Process each project initially
def process_projects():
    """Fetches projects, categorizes them, and exports to JSON."""
    # Process projects
    projects_with_owner = []
    projects_without_owner = []

    projects = list(client.search_projects(request=request))
    for project in projects:
        process_project_parse(project, projects_with_owner, projects_without_owner)  # Pass the lists here
        # Write the metric to Cloud Monitoring
        # Calculate metric_value for this project (customize as needed)
        metric_value = 1  # Replace with your logic
        # Call the function for each project individually
        write_metric_for_each_project(project, "project_labels_counter", metric_value)

    # Print the count of projects with the "owner" label
    print(f"Number of projects with '{OWNER_LABEL}' label: {len(projects_with_owner)}")
    print(f"Number of projects without '{OWNER_LABEL}' label: {len(projects_without_owner)}")
    print(f"Total number of projects {len(projects)}")

    
    export_to_json(projects_with_owner, PROJECTS_WITH_OWNER_FILE)
    export_to_json(projects_without_owner, PROJECTS_WITHOUT_OWNER_FILE)

    upload_json_to_gcs(BUCKET_NAME, PROJECTS_WITH_OWNER_FILE, f"label-parsing/{PROJECTS_WITH_OWNER_FILE}", project_id=BUCKET_PROJECT)
    upload_json_to_gcs(BUCKET_NAME, PROJECTS_WITHOUT_OWNER_FILE, f"label-parsing/{PROJECTS_WITHOUT_OWNER_FILE}", project_id=BUCKET_PROJECT)
