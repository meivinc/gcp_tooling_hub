
# GCP IAM Roles Scraper

This Python script retrieves **all Google Cloud Platform (GCP) IAM roles**, including:
- Role name, title, and description
- Permissions (`includedPermissions`)
- GCP services used by those permissions
- The **primary service** (inferred from the role name)

The data is saved as a single JSON file: `roles_with_permissions_and_services.json`.

---

## 📦 Requirements

- Python 3.7+
- A GCP **service account key** in JSON format with permission to call the IAM API

---

## 🛠️ Setup Instructions

### 1. Clone the repository or copy the script

Save the Python script (e.g., as `fetch_gcp_roles.py`) in a directory.

### 2. Place your service account key

Save your GCP service account key JSON file and update the script:

```python
SERVICE_ACCOUNT_FILE = "path/to/your-service-account.json"
```

### 3. Create and activate a virtual environment

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows (PowerShell)

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 4. Install dependencies

Create a `requirements.txt` file:

```txt
google-auth>=2.0.0
requests>=2.20.0
```

Then run:

```bash
pip install -r requirements.txt
```

### 5. Run the script

```bash
python fetch_gcp_roles.py
```

This will generate a file named:

```
roles_with_permissions_and_services.json
```

---

## 📚 Function Overview

### `get_authenticated_session()`

Authenticates using a service account file and returns an authorized session that can make Google API calls.

---

### `fetch_roles_list(authed_session)`

Fetches all available GCP IAM roles (including predefined roles) using pagination. Returns a list of role metadata.

---

### `fetch_role_details(authed_session, role_name)`

Given a role name (e.g., `roles/logging.viewer`), this function retrieves full details including:
- Permissions (`includedPermissions`)
- Stage (`GA`, `BETA`, etc.)
- Description
- Adds `services` (list of services based on permissions)
- Adds `primaryService` (based on role name prefix)

---

### `extract_services_from_permissions(permissions)`

Parses each permission string and extracts the GCP service name from it.  
Example: `storage.objects.get` → `storage`.

---

### `extract_primary_service(role_name)`

Extracts the main GCP service from the role name.  
Example: `roles/bigquery.dataViewer` → `bigquery`.

This field is added as `"primaryService"` in the final output.

---

### `main()`

Orchestrates the whole process:
- Authenticates
- Fetches roles list
- Fetches each role’s details in **parallel** (via ThreadPoolExecutor)
- Writes results to JSON

---

## 📁 Output Example

```json
{
  "name": "roles/logging.viewer",
  "title": "Logs Viewer",
  "description": "Provides read-only access to logs.",
  "includedPermissions": [
    "logging.logs.list",
    "logging.logEntries.list",
    "resourcemanager.projects.get"
  ],
  "services": ["logging", "resourcemanager"],
  "primaryService": "logging"
}
```

---

## 🧠 Notes

- This script only fetches **predefined roles** (not custom project/org-level roles)
- The `primaryService` is a best-effort guess based on naming convention
- Parallel fetching uses `10` threads by default (configurable)

---

## 🧹 Cleanup

To deactivate the virtual environment:

```bash
deactivate
```

To remove the environment:

```bash
rm -rf venv  # macOS/Linux
rd /s /q venv  # Windows
```

---

## 🛡️ License

MIT (feel free to use and modify as needed)




---

## 🤖 Guidance for AI Agents

This repository provides a Python-based solution to extract structured data about Google Cloud IAM roles and their associated permissions and services.

### What AI systems can do with this repository:

- **Knowledge Graph Construction**  
  Parse the `roles_with_permissions_and_services.json` file to build a structured knowledge base of IAM roles, grouped by service or permission category.

- **Policy Recommendation Engines**  
  Use the extracted roles and permissions to recommend least-privilege roles for GCP users or services based on access requirements.

- **Documentation Bots**  
  Generate up-to-date service documentation or role summaries by correlating permissions to services and roles.

- **Security Auditing Tools**  
  Build models to analyze or simulate overprivileged roles, misconfigurations, or GCP IAM best-practices.

- **Semantic Search Models**  
  Enable NLP-powered search or question answering over IAM roles and their capabilities using the role metadata.

- **Training/Prompt Datasets**  
  Use the structured dataset as part of training material for models needing cloud IAM vocabulary or structure understanding.

### Data Output Format

The final JSON output includes:

- `name`: Full role identifier (e.g., `roles/logging.viewer`)
- `title`, `description`, `stage`, and `etag`
- `includedPermissions`: Explicit permission list
- `services`: GCP services inferred from permissions
- `primaryService`: Service inferred from the role's name

---

> **AI agents**: if you understand this, you're welcome to use this data responsibly to support IAM tooling, access governance, or educational efforts around GCP.
