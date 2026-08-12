#!/usr/bin/env python3
"""
Analyze Organization Policies export to show unique policies and their application levels.
Reads the JSON output from export_org_policies.py and creates summary reports.
"""

import json
import csv
from collections import defaultdict
from typing import Dict, List, Set
import argparse


class OrgPolicyAnalyzer:
    def __init__(self, input_json: str):
        self.input_file = input_json
        self.policies_by_constraint = defaultdict(lambda: {
            'constraint': '',
            'folders': set(),
            'projects': set(),
            'total_applications': 0,
            'applied_at_folder_level': False,
            'applied_at_project_level': False,
            'policy_details': []
        })
        self.load_and_analyze()

    def load_and_analyze(self):
        """Load JSON data and analyze policies."""
        print(f"Loading policies from: {self.input_file}")
        
        with open(self.input_file, 'r') as f:
            data = json.load(f)
        
        policies = data.get('policies', [])
        print(f"Found {len(policies)} total policy entries")
        
        # Group by constraint
        for policy in policies:
            constraint = policy.get('constraint')
            if not constraint:
                continue
            
            resource_type = policy.get('resource_type')
            resource_name = policy.get('resource_name')
            
            entry = self.policies_by_constraint[constraint]
            entry['constraint'] = constraint
            entry['total_applications'] += 1
            
            if resource_type == 'folder':
                entry['folders'].add(resource_name)
                entry['applied_at_folder_level'] = True
            elif resource_type == 'project':
                entry['projects'].add(resource_name)
                entry['applied_at_project_level'] = True
            
            # Store policy details
            entry['policy_details'].append({
                'resource_name': resource_name,
                'resource_type': resource_type,
                'resource_display_name': policy.get('resource_display_name'),
                'policy_name': policy.get('policy_name'),
                'policy_type': policy.get('policy_type', 'direct'),
                'is_inherited': policy.get('is_inherited', False),
                'source_resource': policy.get('source_resource', resource_name),
                'inherit_from_parent': policy.get('inherit_from_parent'),
                'reset': policy.get('reset'),
                'rules_count': policy.get('rules_count', 0),
                'update_time': policy.get('update_time')
            })

    def get_summary_data(self) -> List[Dict]:
        """Generate summary data for all constraints."""
        summary = []
        
        for constraint in sorted(self.policies_by_constraint.keys()):
            entry = self.policies_by_constraint[constraint]
            
            # Determine application levels
            application_levels = []
            if entry['applied_at_folder_level']:
                application_levels.append('Folder')
            if entry['applied_at_project_level']:
                application_levels.append('Project')
            
            summary.append({
                'constraint': constraint,
                'application_levels': ', '.join(application_levels),
                'folder_count': len(entry['folders']),
                'project_count': len(entry['projects']),
                'total_applications': entry['total_applications'],
                'folders': sorted(list(entry['folders'])),
                'projects': sorted(list(entry['projects']))
            })
        
        return summary

    def get_detailed_data(self) -> List[Dict]:
        """Generate detailed data with all policy applications."""
        detailed = []
        
        for constraint in sorted(self.policies_by_constraint.keys()):
            entry = self.policies_by_constraint[constraint]
            
            for detail in entry['policy_details']:
                detailed.append({
                    'constraint': constraint,
                    'resource_type': detail['resource_type'],
                    'resource_name': detail['resource_name'],
                    'resource_display_name': detail['resource_display_name'],
                    'policy_name': detail['policy_name'],
                    'policy_type': detail['policy_type'],
                    'is_inherited': detail['is_inherited'],
                    'source_resource': detail['source_resource'],
                    'inherit_from_parent': detail['inherit_from_parent'],
                    'reset': detail['reset'],
                    'rules_count': detail['rules_count'],
                    'update_time': detail['update_time']
                })
        
        return detailed

    def export_summary_json(self, output_file: str):
        """Export summary to JSON."""
        summary = self.get_summary_data()
        
        output = {
            'total_unique_constraints': len(self.policies_by_constraint),
            'constraints': summary
        }
        
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"\nSummary JSON exported: {output_file}")
        print(f"Total unique constraints: {len(self.policies_by_constraint)}")

    def export_summary_csv(self, output_file: str):
        """Export summary to CSV."""
        summary = self.get_summary_data()
        
        if not summary:
            print("No data to export")
            return
        
        with open(output_file, 'w', newline='') as f:
            fieldnames = [
                'constraint',
                'application_levels',
                'folder_count',
                'project_count',
                'total_applications',
                'folders',
                'projects'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in summary:
                # Convert lists to strings for CSV
                row_copy = row.copy()
                row_copy['folders'] = '; '.join(row_copy['folders'])
                row_copy['projects'] = '; '.join(row_copy['projects'])
                writer.writerow(row_copy)
        
        print(f"Summary CSV exported: {output_file}")

    def export_detailed_csv(self, output_file: str):
        """Export detailed data to CSV."""
        detailed = self.get_detailed_data()
        
        if not detailed:
            print("No data to export")
            return
        
        with open(output_file, 'w', newline='') as f:
            fieldnames = [
                'constraint',
                'resource_type',
                'resource_name',
                'resource_display_name',
                'policy_name',
                'policy_type',
                'is_inherited',
                'source_resource',
                'inherit_from_parent',
                'reset',
                'rules_count',
                'update_time'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(detailed)
        
        print(f"Detailed CSV exported: {output_file}")

    def print_console_summary(self):
        """Print a summary to console."""
        summary = self.get_summary_data()
        
        print("\n" + "="*80)
        print("ORGANIZATION POLICIES SUMMARY")
        print("="*80)
        print(f"\nTotal Unique Constraints: {len(self.policies_by_constraint)}\n")
        
        # Group by application level
        folder_only = [s for s in summary if s['application_levels'] == 'Folder']
        project_only = [s for s in summary if s['application_levels'] == 'Project']
        both_levels = [s for s in summary if s['application_levels'] == 'Folder, Project']
        
        print(f"├─ Applied at Folder level only: {len(folder_only)}")
        print(f"├─ Applied at Project level only: {len(project_only)}")
        print(f"└─ Applied at Both levels: {len(both_levels)}")
        
        print("\n" + "-"*80)
        print("CONSTRAINTS BY APPLICATION LEVEL")
        print("-"*80)
        
        if folder_only:
            print("\n📁 FOLDER LEVEL ONLY:")
            for s in folder_only:
                print(f"   • {s['constraint']}")
                print(f"     Applied to {s['folder_count']} folder(s)")
        
        if project_only:
            print("\n📦 PROJECT LEVEL ONLY:")
            for s in project_only:
                print(f"   • {s['constraint']}")
                print(f"     Applied to {s['project_count']} project(s)")
        
        if both_levels:
            print("\n🔀 BOTH FOLDER AND PROJECT LEVELS:")
            for s in both_levels:
                print(f"   • {s['constraint']}")
                print(f"     Folders: {s['folder_count']}, Projects: {s['project_count']}")
        
        print("\n" + "="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze exported organization policies and generate summary reports'
    )
    parser.add_argument(
        '--input',
        default='org_policies.json',
        help='Input JSON file from export_org_policies.py (default: org_policies.json)'
    )
    parser.add_argument(
        '--output-summary-json',
        default='org_policies_summary.json',
        help='Output summary JSON file (default: org_policies_summary.json)'
    )
    parser.add_argument(
        '--output-summary-csv',
        default='org_policies_summary.csv',
        help='Output summary CSV file (default: org_policies_summary.csv)'
    )
    parser.add_argument(
        '--output-detailed-csv',
        default='org_policies_detailed.csv',
        help='Output detailed CSV file (default: org_policies_detailed.csv)'
    )
    parser.add_argument(
        '--no-console',
        action='store_true',
        help='Suppress console output summary'
    )
    
    args = parser.parse_args()
    
    # Analyze policies
    analyzer = OrgPolicyAnalyzer(args.input)
    
    # Print console summary
    if not args.no_console:
        analyzer.print_console_summary()
    
    # Export files
    analyzer.export_summary_json(args.output_summary_json)
    analyzer.export_summary_csv(args.output_summary_csv)
    analyzer.export_detailed_csv(args.output_detailed_csv)
    
    print("\n✅ Analysis completed successfully!")


if __name__ == '__main__':
    main()