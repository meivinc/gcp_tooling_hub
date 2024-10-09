import json
from google.cloud import storage


def export_to_json(data, filename):
    """Exports the given data to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def upload_json_to_gcs(bucket_name, source_file_name, destination_blob_name, project_id=None):
    """Uploads a JSON file to a Google Cloud Storage bucket.

    Args:
        bucket_name (str): Name of the GCS bucket.
        source_file_name (str): Path to the local JSON file to upload.
        destination_blob_name (str): Name of the blob (file) in GCS.
        project_id (str, optional): The ID of the GCP project. If not specified,
            the default project will be used. 
    """

    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        f"File {source_file_name} uploaded to {bucket_name}/{destination_blob_name}."
    )