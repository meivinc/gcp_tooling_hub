import json
import concurrent.futures
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

# Path to your service account key file
SERVICE_ACCOUNT_FILE = "path/to/your-service-account.json"
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

def get_authenticated_session():
    """Authenticate with Google Cloud using a service account."""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return AuthorizedSession(credentials)

def fetch_roles_list(authed_session):
    """Fetch the list of all IAM roles (paginated)."""
    url = "https://iam.googleapis.com/v1/roles"
    roles = []
    next_token = None

    while True:
        full_url = url
        if next_token:
            full_url += f"?pageToken={next_token}"

        response = authed_session.get(full_url)
        response.raise_for_status()
        data = response.json()
        print(f"Fetched {len(data.get('roles', []))} roles from current page")
        roles.extend(data.get("roles", []))
        next_token = data.get("nextPageToken")
        if not next_token:
            break
    return roles

def extract_services_from_permissions(permissions):
    """Extract a set of GCP services from a list of permissions."""
    services = set()
    for perm in permissions:
        if "." in perm:
            service = perm.split(".")[0]
            services.add(service)
    return sorted(services)

def extract_primary_service(role_name):
    """
    Extract the primary service from a role name.
    Example: 'roles/logging.viewer' → 'logging'
    """
    if role_name.startswith("roles/") and "." in role_name:
        return role_name.split("/")[1].split(".")[0]
    elif "/" in role_name:
        return role_name.split("/")[1].split(".")[0]
    return "unknown"

def fetch_role_details(authed_session, role_name):
    """Fetch detailed information for a single role."""
    url = f"https://iam.googleapis.com/v1/{role_name}"
    try:
        response = authed_session.get(url)
        response.raise_for_status()
        data = response.json()

        # Extract services from permissions
        permissions = data.get("includedPermissions", [])
        data["services"] = extract_services_from_permissions(permissions)

        # Add primary service from role name
        data["primaryService"] = extract_primary_service(role_name)

        print(f"Fetched {len(permissions)} permissions for role {role_name}")
        return data
    except Exception as e:
        print(f"Error fetching role {role_name}: {e}")
        return None

def main():
    authed_session = get_authenticated_session()

    print("Fetching list of all roles...")
    roles = fetch_roles_list(authed_session)
    print(f"Total roles found: {len(roles)}")

    detailed_roles = []

    print("Fetching role details in parallel...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(fetch_role_details, authed_session, role['name']): role
            for role in roles
        }
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            role_name = futures[future]['name']
            data = future.result()
            if data:
                detailed_roles.append(data)
            print(f"[{i}/{len(roles)}] Processed role {role_name}")

    # Save the output JSON
    with open("roles_with_permissions_and_services.json", "w") as f:
        json.dump(detailed_roles, f, indent=2)

    print(f"✅ Saved {len(detailed_roles)} roles with permissions and services to roles_with_permissions_and_services.json")

if __name__ == "__main__":
    main()
