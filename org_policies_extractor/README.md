# GCP Organization Policies Exporter & Analyzer

Export and analyze organization policies applied on a GCP organization/folder and its recursive resources (subfolders and projects) to JSON and CSV formats.

## Features

### Export Tool (export_org_policies.py)
- Recursively traverses organization/folder hierarchy
- Exports policies from organizations, folders and projects
- Outputs both JSON and CSV formats
- Includes detailed policy rules and conditions
- Handles CEL conditions in policies
- Supports multiple folder exports in a single run

### Analysis Tool (analyze_org_policies.py)
- Analyzes exported policy data
- Groups policies by constraint
- Shows application levels (folder vs project)
- Generates summary and detailed reports
- Console output with statistics

## Prerequisites

1. **GCP Authentication**: Ensure you're authenticated with appropriate permissions:
   ```bash
   gcloud auth application-default login
   ```

2. **Required IAM Permissions**:
   - `orgpolicy.policies.list` on the folder and its descendants
   - `resourcemanager.folders.list` on the folder
   - `resourcemanager.projects.list` on the folder

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Exporting Policies (export_org_policies.py)

#### Basic Usage - Single Folder

```bash
python export_org_policies.py --folder-id 123456789
```

#### Export from Organization

```bash
python export_org_policies.py --org-id 123456789
```

#### Multiple Folders

```bash
python export_org_policies.py --folder-id 123456789 987654321 555555555
```

#### With Custom Output Files

```bash
python export_org_policies.py \
  --folder-id folders/123456789 \
  --output-json my_policies.json \
  --output-csv my_policies.csv
```

#### Export Arguments

- `--org-id`: Organization ID (numeric) or full organization name (organizations/123456789)
- `--folder-id`: One or more Folder IDs (numeric) or full folder names (folders/123456789)
- `--output-json`: Output JSON file path (default: org_policies_YYYYMMDD_HHMMSS.json)
- `--output-csv`: Output CSV file path (default: org_policies_YYYYMMDD_HHMMSS.csv)

**Note:** `--org-id` and `--folder-id` are mutually exclusive. Use one or the other.

### Analyzing Policies (analyze_org_policies.py)

After exporting policies, use the analyzer to generate summary reports:

#### Basic Usage

```bash
python analyze_org_policies.py --input org_policies.json
```

#### With Custom Output Files

```bash
python analyze_org_policies.py \
  --input org_policies.json \
  --output-summary-json summary.json \
  --output-summary-csv summary.csv \
  --output-detailed-csv detailed.csv
```

#### Suppress Console Output

```bash
python analyze_org_policies.py --input org_policies.json --no-console
```

#### Analysis Arguments

- `--input`: Input JSON file from export_org_policies.py (default: org_policies.json)
- `--output-summary-json`: Output summary JSON file (default: org_policies_summary.json)
- `--output-summary-csv`: Output summary CSV file (default: org_policies_summary.csv)
- `--output-detailed-csv`: Output detailed CSV file (default: org_policies_detailed.csv)
- `--no-console`: Suppress console output summary

## Output Formats

### Export Output (export_org_policies.py)

#### JSON Format
The JSON file contains:
- Export timestamp
- Total policy count
- Detailed policy information including:
  - Resource name and type
  - Policy constraint
  - Rules with conditions
  - Allowed/denied values
  - CEL expressions

#### CSV Format
The CSV file contains flattened data with one row per policy rule, including:
- Resource information
- Policy details
- Rule configuration
- Condition expressions

### Analysis Output (analyze_org_policies.py)

The analyzer generates three output files:

#### Summary JSON (org_policies_summary.json)
- Total unique constraints count
- For each constraint:
  - Application levels (Folder/Project)
  - Count of folders and projects where applied
  - List of all folders and projects

#### Summary CSV (org_policies_summary.csv)
- One row per unique constraint
- Columns: constraint, application_levels, folder_count, project_count, total_applications, folders, projects
- Easy to analyze in spreadsheet tools

#### Detailed CSV (org_policies_detailed.csv)
- One row per policy application
- Columns: constraint, resource_type, resource_name, resource_display_name, policy_name, inherit_from_parent, reset, rules_count, update_time
- Shows every instance where each policy is applied

## Example Output

### JSON Structure (org_policies.json)

The complete JSON structure:

```json
{
  "export_timestamp": "2025-12-12T10:30:00.123456",
  "total_policies": 15,
  "policies": [
    {
      "resource_name": "folders/123456789",
      "resource_type": "folder",
      "resource_display_name": "Production Environment",
      "policy_name": "folders/123456789/policies/iam.allowedPolicyMemberDomains",
      "constraint": "iam.allowedPolicyMemberDomains",
      "etag": "BwXYZ123ABC",
      "update_time": "2025-12-10T08:15:30.456789",
      "inherit_from_parent": false,
      "reset": false,
      "rules_count": 2,
      "rules": [
        {
          "rule_index": 0,
          "allow_all": null,
          "deny_all": null,
          "enforce": null,
          "allowed_values": ["C01234567"],
          "denied_values": [],
          "condition_expression": "resource.matchTag('123456789/environment', 'production')",
          "condition_title": "Production resources only",
          "condition_description": "Apply to production tagged resources"
        },
        {
          "rule_index": 1,
          "allow_all": null,
          "deny_all": true,
          "enforce": null,
          "allowed_values": [],
          "denied_values": [],
          "condition_expression": null,
          "condition_title": null,
          "condition_description": null
        }
      ]
    },
    {
      "resource_name": "projects/my-project-123",
      "resource_type": "project",
      "resource_display_name": "My Project",
      "policy_name": "projects/my-project-123/policies/compute.restrictSharedVpcSubnetworks",
      "constraint": "compute.restrictSharedVpcSubnetworks",
      "etag": "CwABC789XYZ",
      "update_time": "2025-12-11T14:20:15.789012",
      "inherit_from_parent": true,
      "reset": false,
      "rules_count": 1,
      "rules": [
        {
          "rule_index": 0,
          "allow_all": null,
          "deny_all": null,
          "enforce": true,
          "allowed_values": [],
          "denied_values": [],
          "condition_expression": null,
          "condition_title": null,
          "condition_description": null
        }
      ]
    }
  ]
}
```

### Field Descriptions

**Top Level:**
- `export_timestamp`: ISO 8601 timestamp when the export was created
- `total_policies`: Total number of policies exported
- `policies`: Array of policy objects

**Policy Object:**
- `resource_name`: Full GCP resource name (e.g., "folders/123" or "projects/my-project")
- `resource_type`: Type of resource ("organization", "folder", or "project")
- `resource_display_name`: Human-readable display name (only in analyze_org_policies.py)
- `policy_name`: Full policy resource name
- `constraint`: The organization policy constraint name
- `etag`: Entity tag for concurrency control
- `update_time`: ISO 8601 timestamp of last policy update
- `inherit_from_parent`: Boolean indicating if policy inherits from parent
- `reset`: Boolean indicating if policy is reset to default
- `rules_count`: Number of rules in the policy
- `rules`: Array of rule objects

**Rule Object:**
- `rule_index`: Zero-based index of the rule
- `allow_all`: Boolean - allows all values (list constraints only)
- `deny_all`: Boolean - denies all values (list constraints only)
- `enforce`: Boolean - enforces the constraint (boolean constraints only)
- `allowed_values`: Array of allowed values (list constraints)
- `denied_values`: Array of denied values (list constraints)
- `condition_expression`: CEL expression for conditional policy
- `condition_title`: Title of the condition
- `condition_description`: Description of the condition

## Workflow Example

```bash
# Step 1: Export policies from your organization
python export_org_policies.py --org-id 123456789

# Step 2: Analyze the exported data
python analyze_org_policies.py --input org_policies_20260211_153045.json

# The analyzer will generate:
# - org_policies_summary.json (summary of unique constraints)
# - org_policies_summary.csv (spreadsheet-friendly summary)
# - org_policies_detailed.csv (all policy applications)
```

## Notes

- The export script processes organizations, folders, subfolders, and projects recursively
- Large hierarchies may take several minutes to process
- Export generates both JSON and CSV files with timestamps in filenames
- The CSV format flattens nested rules for easier analysis in spreadsheet tools
- The analyzer reads the JSON export and creates summary reports for easier analysis
- Use the analyzer to quickly identify which policies are applied at folder vs project levels
