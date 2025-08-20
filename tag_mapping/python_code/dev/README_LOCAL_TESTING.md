# Local Testing Guide

## 🧪 Testing Methods

### **Method 1: Direct Python Execution (Recommended)**

```bash
cd python_code/dev

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Test the function directly
python main.py
```

### **Method 2: Dry Run (Data Collection Only)**

```bash
# Test without uploading to BigQuery
python test_dry_run.py
```

This will:
- ✅ Collect all project data
- ✅ Process tags  
- ✅ Save results to JSON files
- ❌ Skip BigQuery upload

### **Method 3: Full Function Test**

```bash
# Test complete pipeline including BigQuery
python test_local.py
```

## 🔧 **Prerequisites**

### **1. Google Cloud Authentication**
```bash
# Authenticate with your user account
gcloud auth login
gcloud auth application-default login

# Or use service account key
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
```

### **2. Required Permissions**
Your account/service account needs:
- `roles/Viewer`
- `roles/resourcemanager.folderViewer` 
- `roles/resourcemanager.organizationViewer`
- `roles/resourcemanager.tagViewer`
- `roles/bigquery.dataEditor` (for full test)
- `roles/bigquery.jobUser` (for full test)

### **3. Configuration Setup**
Create your local configuration file:
```bash
cp config.py.example config.py
# Edit config.py with your actual values
```

**Alternatively**, use environment variables:
```bash
export ORG_ID='YOUR_ORG_ID'
export BQ_PROJECT_ID='YOUR_PROJECT_ID'
```

## 🛠️ **Functions Framework (Alternative)**

Test with the actual Cloud Functions runtime:

```bash
# Install Functions Framework
pip install functions-framework

# Start local server
functions-framework --target=tags_to_bigquery_function --debug

# In another terminal, trigger with curl (simple HTTP request)
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"trigger": "local-test"}'
```

## 🐛 **Debug Mode**

Add debug logging to main.py:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Add to functions for detailed logs
print(f"DEBUG: Processing project {project_id}")
```

## 📊 **Output Analysis**

After running tests, check:

1. **Console Output**: Progress and results
2. **JSON Files**: `dry_run_projects.json`, `dry_run_tags.json`
3. **BigQuery**: Tables created and populated (full test)
4. **Logs**: Any errors or warnings

## ⚡ **Quick Test Commands**

```bash
# Setup once
cd python_code/dev
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_local.txt

# Create config file
cp config.py.example config.py
# Edit config.py with your values

# Quick dry run test
python test_dry_run.py

# Full pipeline test
python test_local.py

# Direct execution
python main.py
```

## 🚨 **Common Issues**

### **Authentication Error**
```bash
gcloud auth application-default login
```

### **Permission Denied**
Check your account has org-level permissions

### **Module Import Error**
```bash
pip install -r requirements.txt
```

### **BigQuery Dataset Missing**
Create manually or run Terraform first

## 📝 **Test Results**

Successful test should show:
- ✅ Projects found and processed
- ✅ Tags collected from hierarchy
- ✅ BigQuery tables created/updated
- ✅ Data uploaded successfully

Example output:
```
🧪 Testing Cloud Function locally...
Processing 45 projects...
Found 12 active projects with 23 total tags
✅ Function completed!
```