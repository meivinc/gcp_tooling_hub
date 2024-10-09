# gcp_tooling_hub: A Collection of GCP tools for Analysis

This GitHub repository, `gcp_tooling_hub`, serves as a hub for various small-scale Google Cloud Platform (GCP) tools. Each tool within this repository is designed to demonstrate a specific pattern or technique for analyzing and interacting with GCP resources using a combination of Python and Terraform.

## Purpose

The primary goal of this repository is to provide a collection of practical examples that can be used for:

- **Learning:** Explore different ways to leverage GCP services and APIs for data analysis and automation.
- **Inspiration:** Discover new approaches and patterns for building GCP-based solutions.
- **Rapid Prototyping:** Quickly create and deploy GCP projects for specific analysis tasks.

## Structure

The repository is organized into individual folders, each representing a distinct GCP project. Each project folder typically contains:

- **`python_code`:**  Python code for the Cloud Function or Cloud Run service. This code interacts with GCP APIs to perform the desired analysis or automation.
- **`terraform_code`:** Terraform code for provisioning the necessary infrastructure for the project. This includes resources like Cloud Storage buckets, Cloud Monitoring workspaces, and the deployment of the Cloud Function or Cloud Run service.
- **`readme.md`:** A README file that provides a detailed explanation of the project's purpose, functionality, code structure, configuration, and deployment instructions.

## List of Tools

- **[`resource-parsing`](./resource-parsing/readme.md)** : Retrieve labels on a project and inject it as a metric in Google Cloud monitoring


## Examples

The repository may contain projects covering a wide range of GCP analysis tasks, such as:

- **Resource Inventory:** Identifying and categorizing GCP resources based on specific criteria (e.g., labels, resource types).
- **Cost Analysis:** Analyzing GCP billing data to identify cost trends and potential optimization opportunities.
- **Security Auditing:**  Scanning GCP resources for security vulnerabilities and misconfigurations.
- **Data Processing:**  Using GCP services like BigQuery or Cloud Dataflow to process and analyze data from various sources.
- **Automation:** Automating routine GCP tasks using Cloud Functions or Cloud Run.


## Getting Started

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/meivinc/gcp_tooling_hub.git
