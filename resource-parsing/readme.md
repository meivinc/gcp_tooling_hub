# Resource Parsing

This folder contains code for identifying and categorizing Google Cloud projects based on the presence of a specific label ("owner" by default). It utilizes both Python and Terraform to achieve this:

## Python Code ([`python_code`](./python_code/readme.md) folder)

The Python code defines a Cloud Function responsible for:

1. **Project Retrieval:** Fetches all active Google Cloud projects.
2. **Filtering:** Identifies projects with and without the specified "owner" label.
3. **Categorization:**  Organizes project details (name, ID, number, labels) into separate lists based on the label's presence.
4. **JSON Export:** Generates two JSON files:
   - `projects_with_owner.json`
   - `projects_without_owner.json`
5. **Cloud Storage Upload:** Uploads the JSON files to a designated Cloud Storage bucket.
6. **Cloud Monitoring Metrics:** Publishes a custom metric ("project_labels_counter") for each project to Cloud Monitoring.

**Key files:**

- `main.py`: Contains the core Cloud Function logic.
- `global_func.py`: Provides helper functions for JSON export and Cloud Storage interaction.

## Terraform Code ([`terraform_code`](./terraform_code/readme.md) folder)

The Terraform code automates the provisioning of the necessary infrastructure for the Python Cloud Function:

1. **Cloud Storage Bucket:** Creates the bucket where the categorized project JSON files will be stored.
2. **Cloud Monitoring Workspace:** Sets up the workspace to receive the custom metrics published by the function.
3. **Cloud Function Deployment:** Deploys the Python code as a Cloud Function, configuring its triggers, environment variables (bucket name, project ID, owner label), runtime, and memory allocation.

**Key files:**

- `main.tf`: Defines the core infrastructure resources.
- `variables.tf`: Allows for customization of deployment parameters.
- `outputs.tf`: Exposes important values like the deployed Cloud Function's URL.

## Workflow

1. The Terraform code is executed to create the required infrastructure (bucket, workspace, and deployed function).
2. The deployed Cloud Function is triggered (e.g., via HTTP).
3. The function retrieves, filters, and categorizes projects based on the "owner" label.
4. Categorized project data is exported to JSON files and uploaded to the designated Cloud Storage bucket.
5. Custom metrics for each project are published to Cloud Monitoring.

This setup provides a way to automatically track and analyze Google Cloud projects based on the presence or absence of a specific label, leveraging the power of both Python and Terraform for a streamlined and scalable solution. 
