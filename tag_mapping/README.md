# GCP Project Tags Mapping for Billing Analysis

This project automatically collects GCP project tags across your entire organization and uploads them to BigQuery for billing analysis and cost allocation. It provides both development tools and production-ready Cloud Function deployment.

## 🎯 **Objective**

Enable **tag-based cost allocation** and **billing analysis** by:
- 🏷️ **Collecting all project tags** from your GCP organization hierarchy
- 📊 **Normalizing tag data** for easy filtering and joining
- 💰 **Integrating with billing data** for cost allocation by business units, environments, or cost centers
- 📈 **Enabling Looker dashboards** with tag-based filtering and grouping

## 🏗️ **Architecture Overview**

```
GCP Organization
├── Projects (with tags)
├── Folders (with inherited tags)
└── Organization (with inherited tags)
            ↓
    Cloud Function (daily 1 AM)
            ↓
    BigQuery Tables
    ├── projects_with_tags (main project info)
    └── project_tags (normalized for filtering)
            ↓
    Looker/BI Tools
    └── Cost allocation dashboards
```

## 📁 **Project Structure**

```
tag_mapping/
├── python_code/dev/          # 🐍 Cloud Function source code
│   ├── main.py               # Main function logic
│   ├── requirements.txt      # Python dependencies
│   ├── config.py.example     # Configuration template
│   ├── test_*.py             # Local testing scripts
│   └── README_LOCAL_TESTING.md
│
├── terraform_code/           # 🏗️ Infrastructure as Code
│   ├── main.tf               # Main Terraform configuration
│   ├── functions.tf          # Cloud Function deployment
│   ├── scheduler.tf          # Daily scheduler setup
│   ├── binding.tf            # IAM permissions
│   ├── variables.tf          # Variable definitions
│   ├── terraform.tfvars.example  # Configuration template
│   └── README.md             # Deployment guide
│
├── .gitignore               # 🔒 Security - excludes sensitive files
└── README.md                # 📖 This file
```

## 🚀 **Quick Start**

### **For Local Development & Testing:**
```bash
cd python_code/dev
cp config.py.example config.py
# Edit config.py with your values
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_local.txt
python test_dry_run.py
```

### **For Production Deployment:**
```bash
cd terraform_code
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
terraform init
terraform apply
```

## 📊 **Data Output**

### **BigQuery Tables Created:**

#### `projects_with_tags` - Main project information
```sql
project_id          | project_number | project_name | lifecycle_state | create_time | export_date | tag_count
prj-billing-export  | 774405888519   | Billing Exp  | ACTIVE         | 2025-08-05  | 2025-08-20  | 3
```

#### `project_tags` - Normalized tags for filtering
```sql
project_id          | project_number | tag_key    | tag_value      | tag_full              | export_date
prj-billing-export  | 774405888519   | Environment| Production     | Environment:Production| 2025-08-20
prj-billing-export  | 774405888519   | Team       | Data-Platform  | Team:Data-Platform    | 2025-08-20
```

## 💡 **Use Cases**

### **Cost Allocation by Business Unit:**
```sql
SELECT 
  t.tag_value as business_unit,
  SUM(b.cost) as total_cost
FROM billing_export b
JOIN projects_with_tags p ON b.project.id = p.project_number
JOIN project_tags t ON p.project_id = t.project_id
WHERE t.tag_key = 'BusinessUnit'
GROUP BY t.tag_value
```

### **Environment-based Cost Analysis:**
```sql
SELECT 
  t.tag_value as environment,
  COUNT(DISTINCT p.project_id) as project_count,
  SUM(b.cost) as total_cost
FROM billing_export b
JOIN projects_with_tags p ON b.project.id = p.project_number
JOIN project_tags t ON p.project_id = t.project_id
WHERE t.tag_key = 'Environment'
GROUP BY t.tag_value
```

### **Untagged Projects (Cost Governance):**
```sql
SELECT 
  p.project_id,
  p.project_name,
  SUM(b.cost) as cost_without_tags
FROM billing_export b
JOIN projects_with_tags p ON b.project.id = p.project_number
WHERE p.tag_count = 0
GROUP BY p.project_id, p.project_name
ORDER BY cost_without_tags DESC
```

## 🔧 **Features**

### **Production Ready:**
- ✅ **Automated daily execution** via Cloud Scheduler
- ✅ **Error handling and retries** for resilient operation
- ✅ **1-year data retention** with automatic cleanup
- ✅ **Minimal IAM permissions** for security
- ✅ **Comprehensive logging** and monitoring

### **Development Friendly:**
- ✅ **Local testing** without cloud deployment
- ✅ **Dry run mode** for safe development
- ✅ **Configuration templates** with examples
- ✅ **Security by default** - sensitive data in gitignore

### **Enterprise Features:**
- ✅ **Organization-level tag collection** including inherited tags
- ✅ **Separate project support** for tooling vs BigQuery
- ✅ **Normalized data structure** for efficient querying
- ✅ **BigQuery partitioning** for performance
- ✅ **Looker/BI integration ready**

## 🔒 **Security**

- **Sensitive data protection** - All credentials and IDs in gitignored config files
- **Minimal IAM roles** - Only required permissions granted
- **Service account isolation** - Dedicated SAs for each function
- **Organization-level permissions** - Read-only access to tags and projects

## 📈 **Scalability**

- **Large organizations** - Handles 1000+ projects efficiently
- **30-minute timeout** - Maximum Cloud Function execution time
- **Daily processing** - Fresh data for daily business decisions
- **Incremental costs** - ~$1-5/month for typical organizations

## 🛠️ **Maintenance**

### **Regular Tasks:**
- Monitor function execution logs monthly
- Review BigQuery storage costs quarterly
- Update IAM permissions as organization changes
- Test disaster recovery procedures annually

### **Updates:**
- Code changes: Modify `python_code/dev/` and run `terraform apply`
- Configuration: Update `terraform.tfvars` and redeploy
- Permissions: Adjust `binding.tf` as needed

## 📚 **Documentation**

- **[Local Testing Guide](python_code/dev/README_LOCAL_TESTING.md)** - Development and debugging
- **[Terraform Deployment Guide](terraform_code/README.md)** - Production deployment
- **[Configuration Examples](terraform_code/terraform.tfvars.example)** - Setup templates

## 🤝 **Contributing**

1. **Development:** Test locally with `test_dry_run.py`
2. **Deployment:** Use separate dev/staging environments
3. **Security:** Never commit `config.py` or `terraform.tfvars`
4. **Documentation:** Update READMEs for any architectural changes

## 📞 **Support**

For issues or questions:
1. Check the troubleshooting sections in individual READMEs
2. Review Cloud Function logs: `gcloud functions logs read cfu-tags-to-bigquery`
3. Verify BigQuery data freshness with the provided SQL queries
4. Test locally to isolate issues between local and cloud environments

---

**💰 Ready to optimize your GCP costs with tag-based allocation? Start with the Quick Start guide above!**