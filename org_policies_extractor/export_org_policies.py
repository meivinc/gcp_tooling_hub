#!/usr/bin/env python3
"""
Export Organization Policies for a GCP folder and all its recursive resources.
Outputs results in both JSON and CSV formats.
"""

import json
import csv
from google.cloud import orgpolicy_v2
from google.cloud import resourcemanager_v3
from typing import List, Dict, Any, Optional
import argparse
from datetime import datetime


class OrgPolicyExporter:
    def __init__(self, include_ancestors: bool = True, include_effective: bool = False):
        self.policy_client = orgpolicy_v2.OrgPolicyClient()
        self.folder_client = resourcemanager_v3.FoldersClient()
        self.project_client = resourcemanager_v3.ProjectsClient()
        self.organization_client = resourcemanager_v3.OrganizationsClient()
        self.policies_data = []
        self.resource_display_names = {}  # Cache for resource display names
        self.processed_resources = set()  # Track processed resources to avoid duplicate exports
        self.include_ancestors = include_ancestors
        self.include_effective = include_effective

    def get_display_name(self, resource_name: str, resource_type: str) -> str:
        """Get display name for a resource (organization, folder or project)."""
        # Check cache first
        if resource_name in self.resource_display_names:
            return self.resource_display_names[resource_name]

        display_name = None
        try:
            if resource_type == 'organization':
                request = resourcemanager_v3.GetOrganizationRequest(name=resource_name)
                organization = self.organization_client.get_organization(request=request)
                display_name = organization.display_name
            elif resource_type == 'folder':
                request = resourcemanager_v3.GetFolderRequest(name=resource_name)
                folder = self.folder_client.get_folder(request=request)
                display_name = folder.display_name
            elif resource_type == 'project':
                request = resourcemanager_v3.GetProjectRequest(name=resource_name)
                project = self.project_client.get_project(request=request)
                display_name = project.display_name
        except Exception as e:
            print(f"  Warning: Could not fetch display name for {resource_name}: {str(e)}")
            display_name = resource_name  # Fallback to resource name

        # Cache it
        self.resource_display_names[resource_name] = display_name
        return display_name

    def get_ancestors(self, folder_name: str) -> List[Dict[str, str]]:
        """Traverse upwards from a folder to find all ancestor folders and the parent organization."""
        ancestors = []
        current_name = folder_name

        while current_name and (current_name.startswith('folders/') or current_name.startswith('projects/')):
            try:
                if current_name.startswith('folders/'):
                    request = resourcemanager_v3.GetFolderRequest(name=current_name)
                    folder = self.folder_client.get_folder(request=request)
                    self.resource_display_names[current_name] = folder.display_name
                    parent = folder.parent
                elif current_name.startswith('projects/'):
                    request = resourcemanager_v3.GetProjectRequest(name=current_name)
                    project = self.project_client.get_project(request=request)
                    self.resource_display_names[current_name] = project.display_name
                    parent = project.parent
                else:
                    break

                if not parent:
                    break

                if parent.startswith('organizations/'):
                    org_display = self.get_display_name(parent, 'organization')
                    ancestors.append({'resource_name': parent, 'resource_type': 'organization', 'display_name': org_display})
                    break
                elif parent.startswith('folders/'):
                    folder_display = self.get_display_name(parent, 'folder')
                    ancestors.append({'resource_name': parent, 'resource_type': 'folder', 'display_name': folder_display})
                    current_name = parent
                else:
                    break
            except Exception as e:
                print(f"  Warning: Failed to fetch ancestor for {current_name}: {str(e)}")
                break

        # Return ancestors ordered from top-most (Organization) down to direct parent
        ancestors.reverse()
        return ancestors

    def list_policies_for_resource(self, resource_name: str, resource_type: str, policy_type: str = 'direct') -> List[Dict[str, Any]]:
        """List all policies explicitly set on a given resource."""
        policies = []

        # Get display name for this resource
        display_name = self.get_display_name(resource_name, resource_type)

        try:
            request = orgpolicy_v2.ListPoliciesRequest(parent=resource_name)

            for policy in self.policy_client.list_policies(request=request):
                policy_data = {
                    'resource_name': resource_name,
                    'resource_type': resource_type,
                    'resource_display_name': display_name,
                    'policy_name': policy.name,
                    'constraint': policy.name.split('/')[-1] if policy.name else None,
                    'etag': policy.spec.etag if policy.spec else None,
                    'update_time': policy.spec.update_time.isoformat() if policy.spec and policy.spec.update_time else None,
                    'inherit_from_parent': policy.spec.inherit_from_parent if policy.spec else None,
                    'reset': policy.spec.reset if policy.spec else None,
                    'policy_type': policy_type,  # 'direct', 'ancestor', or 'effective'
                    'is_inherited': (policy_type == 'ancestor'),
                }
                
                # Add rules information
                if policy.spec and policy.spec.rules:
                    rules_summary = []
                    for idx, rule in enumerate(policy.spec.rules):
                        rule_info = {
                            'rule_index': idx,
                            'allow_all': rule.allow_all if hasattr(rule, 'allow_all') else None,
                            'deny_all': rule.deny_all if hasattr(rule, 'deny_all') else None,
                            'enforce': rule.enforce if hasattr(rule, 'enforce') else None,
                        }
                        
                        # Add values
                        if rule.values:
                            rule_info['allowed_values'] = list(rule.values.allowed_values) if rule.values.allowed_values else []
                            rule_info['denied_values'] = list(rule.values.denied_values) if rule.values.denied_values else []
                        
                        # Add condition
                        if rule.condition:
                            rule_info['condition_expression'] = rule.condition.expression
                            rule_info['condition_title'] = rule.condition.title
                            rule_info['condition_description'] = rule.condition.description
                        
                        rules_summary.append(rule_info)
                    
                    policy_data['rules'] = rules_summary
                    policy_data['rules_count'] = len(rules_summary)
                else:
                    policy_data['rules'] = []
                    policy_data['rules_count'] = 0
                
                policies.append(policy_data)
                
        except Exception as e:
            print(f"Error listing policies for {resource_name}: {str(e)}")
            if "PermissionDenied" in str(type(e).__name__) or "403" in str(e):
                print(f"  --> Hint: Ensure your account has 'roles/orgpolicy.policyViewer' or 'orgpolicy.policies.list' permission on {resource_name}.")
        
        return policies

    def get_effective_policy_for_resource(self, resource_name: str, resource_type: str, constraint: str) -> Optional[Dict[str, Any]]:
        """Fetch the effective evaluated policy for a specific constraint on a resource."""
        display_name = self.get_display_name(resource_name, resource_type)
        policy_resource_name = f"{resource_name}/policies/{constraint}"

        try:
            request = orgpolicy_v2.GetEffectivePolicyRequest(name=policy_resource_name)
            policy = self.policy_client.get_effective_policy(request=request)

            policy_data = {
                'resource_name': resource_name,
                'resource_type': resource_type,
                'resource_display_name': display_name,
                'policy_name': policy.name if hasattr(policy, 'name') else policy_resource_name,
                'constraint': constraint,
                'etag': policy.spec.etag if policy.spec else None,
                'update_time': policy.spec.update_time.isoformat() if policy.spec and policy.spec.update_time else None,
                'inherit_from_parent': True,
                'reset': False,
                'policy_type': 'effective',
                'is_inherited': True,
            }

            if policy.spec and policy.spec.rules:
                rules_summary = []
                for idx, rule in enumerate(policy.spec.rules):
                    rule_info = {
                        'rule_index': idx,
                        'allow_all': rule.allow_all if hasattr(rule, 'allow_all') else None,
                        'deny_all': rule.deny_all if hasattr(rule, 'deny_all') else None,
                        'enforce': rule.enforce if hasattr(rule, 'enforce') else None,
                    }
                    if rule.values:
                        rule_info['allowed_values'] = list(rule.values.allowed_values) if rule.values.allowed_values else []
                        rule_info['denied_values'] = list(rule.values.denied_values) if rule.values.denied_values else []
                    if rule.condition:
                        rule_info['condition_expression'] = rule.condition.expression
                        rule_info['condition_title'] = rule.condition.title
                        rule_info['condition_description'] = rule.condition.description
                    rules_summary.append(rule_info)
                policy_data['rules'] = rules_summary
                policy_data['rules_count'] = len(rules_summary)
            else:
                policy_data['rules'] = []
                policy_data['rules_count'] = 0

            return policy_data
        except Exception as e:
            # Effective policy might fail if constraint doesn't apply or lacks permission
            return None

    def fetch_effective_policies(self, resource_name: str, resource_type: str, constraints: List[str]):
        """Fetch effective policies for a list of constraints on a resource."""
        effective_policies = []
        for constraint in set(constraints):
            eff_pol = self.get_effective_policy_for_resource(resource_name, resource_type, constraint)
            if eff_pol:
                effective_policies.append(eff_pol)
        return effective_policies

    def list_root_folders(self, organization_name: str) -> List[str]:
        """List all root folders under an organization."""
        folders = []

        try:
            request = resourcemanager_v3.ListFoldersRequest(parent=organization_name)

            for folder in self.folder_client.list_folders(request=request):
                folders.append(folder.name)
                # Cache the display name while we have it
                self.resource_display_names[folder.name] = folder.display_name

        except Exception as e:
            print(f"Error listing root folders for {organization_name}: {str(e)}")

        return folders

    def list_subfolders(self, parent_folder: str) -> List[str]:
        """List all subfolders under a parent folder."""
        subfolders = []

        try:
            request = resourcemanager_v3.ListFoldersRequest(parent=parent_folder)

            for folder in self.folder_client.list_folders(request=request):
                subfolders.append(folder.name)
                # Cache the display name while we have it
                self.resource_display_names[folder.name] = folder.display_name

        except Exception as e:
            print(f"Error listing subfolders for {parent_folder}: {str(e)}")

        return subfolders

    def list_projects(self, parent_folder: str) -> List[str]:
        """List all projects under a folder."""
        projects = []

        try:
            request = resourcemanager_v3.ListProjectsRequest(parent=parent_folder)

            for project in self.project_client.list_projects(request=request):
                projects.append(project.name)
                # Cache the display name while we have it
                self.resource_display_names[project.name] = project.display_name

        except Exception as e:
            print(f"Error listing projects for {parent_folder}: {str(e)}")

        return projects

    def process_ancestors_if_needed(self, resource_name: str):
        """Discover and process ancestor folders and organization policies."""
        if not self.include_ancestors:
            return

        ancestors = self.get_ancestors(resource_name)
        if ancestors:
            print(f"\n--- Ancestor Hierarchy for {resource_name} ---")
            for anc in ancestors:
                anc_name = anc['resource_name']
                anc_type = anc['resource_type']
                anc_display = anc['display_name']

                if anc_name in self.processed_resources:
                    continue

                print(f"Processing ancestor {anc_type}: {anc_name} ({anc_display})")
                anc_policies = self.list_policies_for_resource(anc_name, anc_type, policy_type='ancestor')
                self.policies_data.extend(anc_policies)
                self.processed_resources.add(anc_name)
                print(f"  Found {len(anc_policies)} policies for ancestor {anc_type}")

    def process_organization_recursive(self, organization_name: str):
        """Recursively process an organization and all its children."""
        if organization_name in self.processed_resources:
            return
        self.processed_resources.add(organization_name)

        # Get and cache display name for this organization
        display_name = self.get_display_name(organization_name, 'organization')
        print(f"Processing organization: {organization_name} ({display_name})")

        # Get policies for the organization itself
        org_policies = self.list_policies_for_resource(organization_name, 'organization', policy_type='direct')
        self.policies_data.extend(org_policies)
        print(f"  Found {len(org_policies)} policies for organization")

        # Collect constraints for effective policies if enabled
        discovered_constraints = [p['constraint'] for p in org_policies if p.get('constraint')]

        if self.include_effective and discovered_constraints:
            eff_policies = self.fetch_effective_policies(organization_name, 'organization', discovered_constraints)
            self.policies_data.extend(eff_policies)
            print(f"  Fetched {len(eff_policies)} effective policies for organization")

        # Get and process all root folders
        root_folders = self.list_root_folders(organization_name)
        print(f"  Found {len(root_folders)} root folders")
        for folder in root_folders:
            self.process_folder_recursive(folder, is_root_target=False)

        # Get and process all projects directly under the organization
        projects = self.list_projects(organization_name)
        print(f"  Found {len(projects)} projects directly under organization")
        for project in projects:
            self.process_project(project, 'organization', discovered_constraints)

    def process_project(self, project_name: str, parent_type: str, known_constraints: List[str] = None):
        """Process a single project."""
        if project_name in self.processed_resources:
            return
        self.processed_resources.add(project_name)

        project_display_name = self.get_display_name(project_name, 'project')
        print(f"    Processing project: {project_name} ({project_display_name})")
        project_policies = self.list_policies_for_resource(project_name, 'project', policy_type='direct')
        self.policies_data.extend(project_policies)
        print(f"      Found {len(project_policies)} direct policies for project")

        if self.include_effective:
            constraints_to_check = list(set([p['constraint'] for p in project_policies if p.get('constraint')] + (known_constraints or [])))
            if constraints_to_check:
                eff_policies = self.fetch_effective_policies(project_name, 'project', constraints_to_check)
                self.policies_data.extend(eff_policies)
                print(f"      Fetched {len(eff_policies)} effective policies for project")

    def process_folder_recursive(self, folder_name: str, is_root_target: bool = True):
        """Recursively process a folder and all its children."""
        # Process ancestors first if requested
        if is_root_target:
            self.process_ancestors_if_needed(folder_name)

        if folder_name in self.processed_resources:
            return
        self.processed_resources.add(folder_name)

        # Get and cache display name for this folder
        display_name = self.get_display_name(folder_name, 'folder')
        print(f"\nProcessing folder: {folder_name} ({display_name})")

        # Get policies for the folder itself
        folder_policies = self.list_policies_for_resource(folder_name, 'folder', policy_type='direct')
        self.policies_data.extend(folder_policies)
        print(f"  Found {len(folder_policies)} direct policies for folder")

        discovered_constraints = [p['constraint'] for p in self.policies_data if p.get('constraint')]

        if self.include_effective and discovered_constraints:
            eff_policies = self.fetch_effective_policies(folder_name, 'folder', discovered_constraints)
            self.policies_data.extend(eff_policies)
            print(f"  Fetched {len(eff_policies)} effective policies for folder")

        # Get and process all subfolders
        subfolders = self.list_subfolders(folder_name)
        print(f"  Found {len(subfolders)} subfolders")
        for subfolder in subfolders:
            self.process_folder_recursive(subfolder, is_root_target=False)

        # Get and process all projects
        projects = self.list_projects(folder_name)
        print(f"  Found {len(projects)} projects")
        for project in projects:
            self.process_project(project, 'folder', discovered_constraints)

    def export_to_json(self, output_file: str):
        """Export policies data to JSON file."""
        with open(output_file, 'w') as f:
            json.dump({
                'export_timestamp': datetime.now().isoformat(),
                'total_policies': len(self.policies_data),
                'policies': self.policies_data
            }, f, indent=2, default=str)
        
        print(f"\nJSON export completed: {output_file}")
        print(f"Total policies exported: {len(self.policies_data)}")

    def export_to_csv(self, output_file: str):
        """Export policies data to CSV file."""
        if not self.policies_data:
            print("No policies to export")
            return
        
        # Flatten the data for CSV
        csv_rows = []
        for policy in self.policies_data:
            base_row = {
                'resource_name': policy['resource_name'],
                'resource_display_name': policy['resource_display_name'],
                'resource_type': policy['resource_type'],
                'policy_type': policy.get('policy_type', 'direct'),
                'is_inherited': policy.get('is_inherited', False),
                'policy_name': policy['policy_name'],
                'constraint': policy['constraint'],
                'etag': policy['etag'],
                'update_time': policy['update_time'],
                'inherit_from_parent': policy['inherit_from_parent'],
                'reset': policy['reset'],
                'rules_count': policy['rules_count'],
            }
            
            # If there are rules, create a row for each rule
            if policy['rules']:
                for rule in policy['rules']:
                    row = base_row.copy()
                    row['rule_index'] = rule['rule_index']
                    row['allow_all'] = rule.get('allow_all')
                    row['deny_all'] = rule.get('deny_all')
                    row['enforce'] = rule.get('enforce')
                    row['allowed_values'] = json.dumps(rule.get('allowed_values', []))
                    row['denied_values'] = json.dumps(rule.get('denied_values', []))
                    row['condition_expression'] = rule.get('condition_expression')
                    row['condition_title'] = rule.get('condition_title')
                    row['condition_description'] = rule.get('condition_description')
                    csv_rows.append(row)
            else:
                # No rules, just add the base row
                csv_rows.append(base_row)
        
        # Write to CSV
        if csv_rows:
            fieldnames = csv_rows[0].keys()
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_rows)
            
            print(f"CSV export completed: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Export GCP Organization Policies for an organization, folder(s), and their recursive resources'
    )

    # Create mutually exclusive group for org-id and folder-id
    resource_group = parser.add_mutually_exclusive_group(required=True)
    resource_group.add_argument(
        '--org-id',
        help='Organization ID (numeric) or full organization name (organizations/123456789)'
    )
    resource_group.add_argument(
        '--folder-id',
        nargs='+',
        help='One or more Folder IDs (numeric) or full folder names (folders/123456789). Separate multiple IDs with spaces.'
    )

    parser.add_argument(
        '--include-ancestors',
        action=argparse.BooleanOptionalAction,
        default=True,
        help='Automatically fetch policies from ancestor folders and organization when using --folder-id (default: True)'
    )
    parser.add_argument(
        '--include-effective',
        action='store_true',
        default=False,
        help='Fetch evaluated effective policies for resources in addition to explicit policy definitions'
    )

    parser.add_argument(
        '--output-json',
        default=None,
        help='Output JSON file path (default: org_policies_YYYYMMDD_HHMMSS.json)'
    )
    parser.add_argument(
        '--output-csv',
        default=None,
        help='Output CSV file path (default: org_policies_YYYYMMDD_HHMMSS.csv)'
    )

    args = parser.parse_args()

    # Generate timestamp for filenames if not provided
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_json = args.output_json if args.output_json else f'org_policies_{timestamp}.json'
    output_csv = args.output_csv if args.output_csv else f'org_policies_{timestamp}.csv'

    # Create exporter
    exporter = OrgPolicyExporter(
        include_ancestors=args.include_ancestors,
        include_effective=args.include_effective
    )

    # Process organization or folder(s)
    if args.org_id:
        # Format organization name
        org_name = args.org_id
        if not org_name.startswith('organizations/'):
            org_name = f'organizations/{org_name}'

        print(f"Starting organization policy export for: {org_name}")
        print(f"Output files: {output_json}, {output_csv}\n")
        exporter.process_organization_recursive(org_name)
    else:
        # Format folder names
        folder_names = []
        for folder_id in args.folder_id:
            folder_name = folder_id if folder_id.startswith('folders/') else f'folders/{folder_id}'
            folder_names.append(folder_name)

        print(f"Starting organization policy export for {len(folder_names)} folder(s):")
        for folder in folder_names:
            print(f"  - {folder}")
        print(f"Include Ancestors: {args.include_ancestors}")
        print(f"Include Effective Policies: {args.include_effective}")
        print(f"\nOutput files: {output_json}, {output_csv}\n")

        for folder_name in folder_names:
            print(f"\n{'='*80}")
            print(f"Processing folder hierarchy: {folder_name}")
            print(f"{'='*80}")
            exporter.process_folder_recursive(folder_name, is_root_target=True)

    # Export to both formats
    print(f"\n{'='*80}")
    print("Exporting consolidated results")
    print(f"{'='*80}")
    exporter.export_to_json(output_json)
    exporter.export_to_csv(output_csv)

    print("\nExport completed successfully!")
    if args.folder_id:
        print(f"Total folders processed: {len(folder_names)}")
    print(f"Total policies exported: {len(exporter.policies_data)}")


if __name__ == '__main__':
    main()

