### Python part 

1. **Project Retrieval and Filtering:**
   - Fetches all active Google Cloud projects using the Resource Manager API.
   - Filters projects based on the presence of an "owner" label.

2. **Data Processing and Categorization:**
   - Extracts relevant project information, including name, ID, number, and labels.
   - Categorizes projects into two lists: those with the "owner" label and those without.

3. **JSON Export:**
   - Exports the categorized project data into two separate JSON files:
     - `projects_with_owner.json`: Contains details of projects with the "owner" label.
     - `projects_without_owner.json`: Contains details of projects without the "owner" label.

4. **Cloud Storage Upload:**
   - Uploads the generated JSON files to a specified Google Cloud Storage bucket.

5. **Cloud Monitoring Metrics:**
   - For each project, writes a custom metric named "project_labels_counter" to Cloud Monitoring.
   - The metric value is currently set to 1 but can be customized based on specific requirements.

## Code Structure

- **`main.py`:** Contains the main Cloud Function code, including project processing, JSON export, and Cloud Monitoring integration.
- **`global_func.py`:** Contains helper functions for exporting data to JSON and uploading files to Google Cloud Storage.

## Configuration

- **`BUCKET_NAME`:** The name of the Google Cloud Storage bucket to upload the JSON files to.
- **`BUCKET_PROJECT`:** The ID of the Google Cloud project that owns the storage bucket.
- **`PROJECT_ID`:** The ID of the Google Cloud project for Cloud Monitoring metrics.
- **`OWNER_LABEL`:** The name of the label used to categorize projects (default: "owner").

## Deployment

This Cloud Function is designed to be deployed using Google Cloud Functions. Ensure you have set up Google Cloud authentication and have the necessary permissions.

## Usage

Once deployed, the Cloud Function can be triggered via HTTP. The function will execute the project processing, JSON export, and Cloud Monitoring metric writing logic.




### Preparing and Deploying Your Python Code to Google Cloud Functions

1. **Set up Your Environment**
  **Create a Virtual Environment:**

```bash 
    python3 -m venv pyprojlist
    source pyprojlist/bin/activate
    This creates an isolated environment to manage your project's dependencies.

```

    **Install Dependencies:**
```bash 
pip freeze > requirements.txt
pip install -r requirements.txt
This records your project's dependencies and installs them within the virtual environment.
```


2. **Package Your Code**
Zip the python_code folder: Compress the entire python_code folder, including the requirements.txt file, into a single ZIP archive.

3. **Deploy to Cloud Functions**

Push to Cloud Function: Use the Google Cloud SDK or the Cloud Console to deploy the ZIP archive as a Cloud Function.
You'll need to configure settings like the function's name, region, trigger (e.g., HTTP trigger), and memory allocation.

1. **Test Your Deployed Function**
Test it: Once deployed, you can test your Cloud Function using curl:

```bash 
curl "https://<urlCloudFunction>.net/cfu-org-info-parsing/process_projects_http" \
-H "Authorization: bearer $(gcloud auth print-identity-token)"
# Replace <urlCloudFunction> with your function's URL.

```
This command sends an authenticated HTTP request to your function.
This process ensures your Python code is properly packaged with its dependencies and deployed as a functional Cloud Function.
