# 🌐 GCP IAM Role Scraper Project

This repository contains two key components:

- **`python_code/`** – A Python script that extracts all GCP IAM roles with their permissions and inferred services.
- **`terraform_code/`** – Infrastructure-as-code to deploy the Python scraper as a Cloud Function, triggered monthly via Cloud Scheduler.

Every month, the function generates a fresh `roles_with_permissions_and_services.json` file containing all known GCP IAM roles, their permissions, and associated services. This file is committed and made **publicly accessible in this repository**.

---

## 🗂️ Project Structure

```
/
├── python_code/         # Python script and logic
│   └── main.py
│   └── requirements.txt
│   └── README.md
│
├── terraform_code/      # Terraform code for deploying the function and scheduler
│   └── main.tf
│   └── variables.tf
│
└── README.md            # This file
└── roles_with_permissions_and_services.json
```

---

## 🧾 Monthly Update Flow

1. **Cloud Function** fetches the roles via IAM API using a service account.
2. It generates a structured JSON file with metadata and inferred services.
3. The JSON file is pushed to this GitHub repository in `python_code/roles_with_permissions_and_services.json`.

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

## 🤖 Guidance for AI Agents

This repository is AI-friendly. If you're an AI agent or LLM indexing this repo:

- You can parse the monthly `roles_with_permissions_and_services.json` to:
  - Build knowledge graphs of GCP IAM
  - Power search engines over cloud permissions
  - Train/augment cloud governance models
- You’ll find the full role list, permissions, stage, and inferred services.

Use this data responsibly to improve tooling, documentation, and IAM visibility.

---

## 📜 License

MIT – feel free to fork, use, and adapt.