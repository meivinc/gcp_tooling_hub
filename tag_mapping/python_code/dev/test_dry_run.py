#!/usr/bin/env python3
"""
Dry run version - collects data but doesn't upload to BigQuery
"""
import os
import json
from main import collect_project_data

def dry_run_test():
    """Test data collection without uploading to BigQuery."""
    print("🔍 DRY RUN: Testing data collection only...")
    print("=" * 60)
    
    # Configuration will be loaded from config.py or environment variables
    # No need to set hardcoded values here
    
    try:
        print("Collecting project data...")
        projects_data, tags_data, total_projects = collect_project_data()
        
        print(f"\n📊 RESULTS:")
        print(f"  Total projects found: {total_projects}")
        print(f"  Active projects: {len(projects_data)}")
        print(f"  Total tag records: {len(tags_data)}")
        
        # Show sample data
        if projects_data:
            print(f"\n📝 SAMPLE PROJECT DATA:")
            print(json.dumps(projects_data[0], indent=2))
        
        if tags_data:
            print(f"\n🏷️  SAMPLE TAG DATA:")
            print(json.dumps(tags_data[0], indent=2))
            
        # Save to files for inspection
        with open('dry_run_projects.json', 'w') as f:
            json.dump(projects_data, f, indent=2)
            
        with open('dry_run_tags.json', 'w') as f:
            json.dump(tags_data, f, indent=2)
            
        print(f"\n💾 Data saved to:")
        print(f"  - dry_run_projects.json")
        print(f"  - dry_run_tags.json")
        
    except Exception as e:
        print(f"❌ Error during dry run: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    dry_run_test()