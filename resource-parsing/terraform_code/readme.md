
# Terraform Code for Resource Parsing

This directory contains Terraform code for configuring the infrastructure required for the resource parsing Cloud Function. It includes resources for:

- **Cloud Storage Bucket:** Creates a bucket to store the generated JSON files.
- **Cloud Monitoring Workspace:** Creates a workspace to store the custom metrics.
- **Cloud Function:** Deploys the Cloud Function itself, including its configuration and dependencies.

## Functionality

The Terraform code automates the following tasks:

1. **Cloud Storage Bucket Creation:**
   - Creates a new Cloud Storage bucket with the specified name and location.
   - Configures access control to allow the Cloud Function to write to the bucket.

2. **Cloud Monitoring Workspace Creation:**
   - Creates a new Cloud Monitoring workspace for the specified project.
   - Configures the workspace to allow the Cloud Function to write custom metrics.

3. **Cloud Function Deployment:**
   - Deploys the Cloud Function using the provided source code and configuration.
   - Sets up the function's trigger (e.g., HTTP trigger).
   - Configures the function's environment variables, including the bucket name, project ID, and owner label.
   - Specifies the function's runtime environment and memory allocation.

## Code Structure

- **`main.tf`:** Contains the main Terraform configuration, including the resource definitions and dependencies.
- **`variables.tf`:** Defines the variables used in the configuration, allowing for customization.
- **`outputs.tf`:** Defines the outputs of the Terraform code, providing access to important values like the function's URL.

## Configuration

- **`bucket_name`:** The name of the Cloud Storage bucket.
- **`bucket_location`:** The location of the Cloud Storage bucket.
- **`project_id`:** The ID of the Google Cloud project.
- **`function_name`:** The name of the Cloud Function.
- **`function_region`:** The region where the Cloud Function will be deployed.
- **`owner_label`:** The name of the label used to categorize projects.

## Deployment

1. **Initialize Terraform:**
   ```bash
   terraform init
