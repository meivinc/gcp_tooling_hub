import json
import os
from datetime import datetime, timezone
import pytz
from google.cloud import resourcemanager_v3, bigquery
from google.cloud.exceptions import NotFound
from google.api_core import exceptions

# Import functions_framework only when running in Cloud Function
try:
    import functions_framework
    CLOUD_FUNCTION_MODE = True
except ImportError:
    CLOUD_FUNCTION_MODE = False
    print("Running in local mode (functions_framework not available)")

# Configuration from environment variables or local config file
def get_config(key, default=None):
    """Get configuration from environment variables or local config file."""
    # First try environment variables (for Cloud Function)
    env_value = os.environ.get(key)
    if env_value:
        return env_value
    
    # Then try local config file (for local development)
    try:
        import config
        return getattr(config, key, default)
    except ImportError:
        return default

ORG_ID = get_config('ORG_ID', 'your-org-id-here')
BQ_PROJECT_ID = get_config('BQ_PROJECT_ID', 'your-bigquery-project-id')
BQ_DATASET = get_config('BQ_DATASET', 'billing_data')
BQ_TABLE_PROJECTS = get_config('BQ_TABLE_PROJECTS', 'projects_with_tags')
BQ_TABLE_TAGS = get_config('BQ_TABLE_TAGS', 'project_tags')

# Initialize clients
projects_client = resourcemanager_v3.ProjectsClient()
folders_client = resourcemanager_v3.FoldersClient()
organizations_client = resourcemanager_v3.OrganizationsClient()
tag_keys_client = resourcemanager_v3.TagKeysClient()
tag_values_client = resourcemanager_v3.TagValuesClient()
tag_bindings_client = resourcemanager_v3.TagBindingsClient()
bq_client = bigquery.Client(project=BQ_PROJECT_ID)

# Cache for tag details
tag_details_cache = {}

def get_tag_details(tag_value_name):
    """Retrieve and cache formatted tag details (Key:Value)."""
    if tag_value_name in tag_details_cache:
        return tag_details_cache[tag_value_name]

    try:
        # Get tag value details
        request = resourcemanager_v3.GetTagValueRequest(name=tag_value_name)
        value_details = tag_values_client.get_tag_value(request=request)
        
        # Get tag key details
        key_request = resourcemanager_v3.GetTagKeyRequest(name=value_details.parent)
        key_details = tag_keys_client.get_tag_key(request=key_request)
        
        formatted_name = f"{key_details.short_name}:{value_details.short_name}"
        tag_details_cache[tag_value_name] = formatted_name
        return formatted_name
    except exceptions.GoogleAPICallError as e:
        print(f"Error getting tag details for {tag_value_name}: {e}")
        return None

def get_tags_for_resource(resource_name):
    """Retrieve formatted tags for a given resource."""
    try:
        request = resourcemanager_v3.ListTagBindingsRequest(parent=resource_name)
        bindings = tag_bindings_client.list_tag_bindings(request=request)
        
        tags = set()
        for binding in bindings:
            tag_value = binding.tag_value
            if tag_value:
                formatted_tag = get_tag_details(tag_value)
                if formatted_tag:
                    tags.add(formatted_tag)
        return tags
    except exceptions.GoogleAPICallError as e:
        print(f"Error getting tags for resource {resource_name}: {e}")
        return set()

def create_projects_table_schema():
    """Define BigQuery schema for projects table."""
    return [
        bigquery.SchemaField("project_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("project_number", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("project_name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("lifecycle_state", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("create_time", "DATE", mode="NULLABLE"),
        bigquery.SchemaField("export_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("export_time", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("tag_count", "INTEGER", mode="REQUIRED"),
    ]

def create_tags_table_schema():
    """Define BigQuery schema for normalized tags table."""
    return [
        bigquery.SchemaField("project_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("project_number", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("tag_key", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("tag_value", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("tag_full", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("export_date", "DATE", mode="REQUIRED"),
    ]

def create_table_if_not_exists(table_id, schema, partition_field=None):
    """Create BigQuery table if it doesn't exist."""
    table_ref = bq_client.dataset(BQ_DATASET).table(table_id)
    
    try:
        bq_client.get_table(table_ref)
        print(f"Table {BQ_DATASET}.{table_id} already exists")
    except NotFound:
        table = bigquery.Table(table_ref, schema=schema)
        
        if partition_field:
            table.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field=partition_field
            )
            table.clustering_fields = ["project_id"]
        
        table = bq_client.create_table(table)
        print(f"Created table {BQ_DATASET}.{table_id}")

def collect_project_data():
    """Collect all projects and their tags."""
    # Use Paris timezone to match scheduler timezone
    paris_tz = pytz.timezone('Europe/Paris')
    export_time = datetime.now(timezone.utc)
    export_time_paris = export_time.astimezone(paris_tz)
    export_date = export_time_paris.date()

    print("Retrieving all projects...")
    try:
        request = resourcemanager_v3.SearchProjectsRequest()
        projects_response = projects_client.search_projects(request=request)
        projects = list(projects_response)
        
        if not projects:
            print("ERROR: No projects found")
            return [], [], 0
    except exceptions.GoogleAPICallError as e:
        print(f"ERROR: {e}")
        return [], [], 0

    print(f"Processing {len(projects)} projects...")
    
    projects_data = []
    tags_data = []
    
    for i, project in enumerate(projects):
        project_id = project.project_id
        project_number = project.name.split('/')[-1]
        project_display_name = project.display_name
        print(f"Processing ({i+1}/{len(projects)}) {project_id}")

        if not project_number:
            continue

        effective_tags = set()
        
        # Get project ancestors and tags
        try:
            request = resourcemanager_v3.GetProjectRequest(name=project.name)
            project_details = projects_client.get_project(request=request)
            
            current_parent = project_details.parent
            ancestors = [{"type": "project", "id": project_number}]
            
            # Traverse up the hierarchy
            while current_parent:
                if current_parent.startswith('folders/'):
                    folder_id = current_parent.split('/')[-1]
                    ancestors.append({"type": "folder", "id": folder_id})
                    try:
                        folder_request = resourcemanager_v3.GetFolderRequest(name=current_parent)
                        folder = folders_client.get_folder(request=folder_request)
                        current_parent = folder.parent
                    except exceptions.GoogleAPICallError:
                        break
                elif current_parent.startswith('organizations/'):
                    org_id = current_parent.split('/')[-1]
                    ancestors.append({"type": "organization", "id": org_id})
                    break
                else:
                    break
            
            # Get tags for each ancestor
            for ancestor in ancestors:
                resource_type = ancestor.get('type')
                resource_id = ancestor.get('id')
                if resource_type == 'project':
                    resource_name = f"//cloudresourcemanager.googleapis.com/projects/{project_number}"
                else:
                    resource_name = f"//cloudresourcemanager.googleapis.com/{resource_type}s/{resource_id}"
                
                effective_tags.update(get_tags_for_resource(resource_name))
                
        except exceptions.GoogleAPICallError as e:
            print(f"Error processing project {project_id}: {e}")
            # If we can't get ancestors, still try to get direct project tags
            resource_name = f"//cloudresourcemanager.googleapis.com/projects/{project_number}"
            effective_tags.update(get_tags_for_resource(resource_name))

        # Convert lifecycle state enum to string
        lifecycle_state = project.state.name if hasattr(project.state, 'name') else str(project.state)
        
        # Format create time
        create_time = project.create_time.strftime('%Y-%m-%d') if project.create_time else ''

        # Only process ACTIVE projects for BigQuery
        if lifecycle_state == 'ACTIVE':
            # Process main project data
            projects_data.append({
                'project_id': project_id,
                'project_number': project_number,
                'project_name': project_display_name,
                'lifecycle_state': lifecycle_state,
                'create_time': create_time if create_time else None,
                'export_date': export_date.isoformat(),
                'export_time': export_time.isoformat(),
                'tag_count': len(effective_tags)
            })
            
            # Process tags data (normalized)
            for tag in effective_tags:
                if ':' in tag:
                    key, value = tag.split(':', 1)
                else:
                    key, value = tag, ''
                
                tags_data.append({
                    'project_id': project_id,
                    'project_number': project_number,
                    'tag_key': key,
                    'tag_value': value,
                    'tag_full': tag,
                    'export_date': export_date.isoformat()
                })

    return projects_data, tags_data, len(projects)

def upload_to_bigquery(projects_data, tags_data):
    """Upload data to BigQuery with 1-year retention."""
    # Use Paris timezone to match scheduler timezone  
    paris_tz = pytz.timezone('Europe/Paris')
    export_time = datetime.now(timezone.utc)
    export_time_paris = export_time.astimezone(paris_tz)
    export_date = export_time_paris.date()
    
    print("Creating BigQuery tables if needed...")
    
    # Create tables if they don't exist
    create_table_if_not_exists(
        BQ_TABLE_PROJECTS, 
        create_projects_table_schema(), 
        partition_field="export_date"
    )
    
    create_table_if_not_exists(
        BQ_TABLE_TAGS, 
        create_tags_table_schema(), 
        partition_field="export_date"
    )
    
    print(f"Found {len(projects_data)} active projects with {len(tags_data)} total tags")
    
    if not projects_data:
        print("WARNING: No active projects found!")
        return

    # Delete existing data for today (if re-running) and old data (>1 year)
    print("Cleaning existing data for today and data older than 1 year...")
    retention_date = export_date.replace(year=export_date.year - 1)
    
    for table_name in [BQ_TABLE_PROJECTS, BQ_TABLE_TAGS]:
        # Delete today's data (for re-runs)
        delete_today_query = f"""
        DELETE FROM `{BQ_PROJECT_ID}.{BQ_DATASET}.{table_name}`
        WHERE export_date = @export_date
        """
        
        # Delete data older than 1 year
        delete_old_query = f"""
        DELETE FROM `{BQ_PROJECT_ID}.{BQ_DATASET}.{table_name}`
        WHERE export_date < @retention_date
        """
        
        job_config_today = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("export_date", "DATE", export_date)
            ]
        )
        job_config_old = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("retention_date", "DATE", retention_date)
            ]
        )
        
        bq_client.query(delete_today_query, job_config=job_config_today).result()
        old_data_job = bq_client.query(delete_old_query, job_config=job_config_old)
        old_data_job.result()
        
        if old_data_job.num_dml_affected_rows > 0:
            print(f"Deleted {old_data_job.num_dml_affected_rows} old records from {table_name}")

    # Upload projects data
    print("Uploading to BigQuery...")
    projects_table_ref = bq_client.dataset(BQ_DATASET).table(BQ_TABLE_PROJECTS)
    projects_job = bq_client.load_table_from_json(
        projects_data, 
        projects_table_ref,
        job_config=bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            schema=create_projects_table_schema()
        )
    )
    projects_job.result()
    
    # Upload tags data
    if tags_data:
        tags_table_ref = bq_client.dataset(BQ_DATASET).table(BQ_TABLE_TAGS)
        tags_job = bq_client.load_table_from_json(
            tags_data,
            tags_table_ref,
            job_config=bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
                schema=create_tags_table_schema()
            )
        )
        tags_job.result()

def tags_to_bigquery_function(request):
    """Cloud Function entry point triggered by HTTP request from Cloud Scheduler."""
    print("Starting GCP tags collection and BigQuery upload...")
    
    try:
        # Collect project data
        projects_data, tags_data, total_projects = collect_project_data()
        
        # Upload to BigQuery
        upload_to_bigquery(projects_data, tags_data)
        
        result = {
            "status": "success",
            "total_projects": total_projects,
            "active_projects_uploaded": len(projects_data),
            "tag_records_uploaded": len(tags_data),
            "export_time": datetime.now(timezone.utc).isoformat()
        }
        
        print(f"Pipeline completed successfully!")
        print(f"- Processed {total_projects} total projects")
        print(f"- {len(projects_data)} active projects uploaded to {BQ_DATASET}.{BQ_TABLE_PROJECTS}")
        print(f"- {len(tags_data)} tag records uploaded to {BQ_DATASET}.{BQ_TABLE_TAGS}")
        
        return result
        
    except Exception as e:
        error_msg = f"Error in tags pipeline: {str(e)}"
        print(error_msg)
        return {"status": "error", "error": error_msg}

# Add decorator only when in Cloud Function mode
if CLOUD_FUNCTION_MODE:
    tags_to_bigquery_function = functions_framework.http(tags_to_bigquery_function)

# For local testing
if __name__ == "__main__":
    # Mock HTTP request for local testing
    class MockRequest:
        def __init__(self):
            self.method = 'POST'
            self.data = b'{}'
    
    result = tags_to_bigquery_function(MockRequest())
    print(json.dumps(result, indent=2))