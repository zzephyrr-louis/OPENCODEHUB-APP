"""
Test script for version upload API endpoints
Run this after starting the Django development server
"""

import requests
import json
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

# Test credentials (you'll need to create a test user first)
USERNAME = "testuser"
PASSWORD = "testpass123"

def test_api_endpoints():
    """Test the version upload API endpoints"""
    
    print("=" * 50)
    print("Testing OpenCodeHub Version Upload API")
    print("=" * 50)
    
    # Create a session for authentication
    session = requests.Session()
    
    # 1. Login first (using session authentication)
    print("\n1. Logging in...")
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    login_response = session.post(f"{BASE_URL}/login/", data=login_data)
    
    if login_response.status_code == 200:
        print("✓ Login successful")
    else:
        print(f"✗ Login failed: {login_response.status_code}")
        return
    
    # 2. Get CSRF token
    csrf_token = session.cookies.get('csrftoken')
    headers = {'X-CSRFToken': csrf_token}
    
    # 3. List projects
    print("\n2. Fetching projects...")
    projects_response = session.get(f"{API_URL}/projects/", headers=headers)
    
    if projects_response.status_code == 200:
        projects = projects_response.json()
        print(f"✓ Found {projects.get('count', 0)} projects")
        
        if projects.get('results'):
            project = projects['results'][0]
            project_id = project['id']
            print(f"   Using project: {project['title']} (ID: {project_id})")
            
            # 4. List versions for the project
            print(f"\n3. Fetching versions for project {project_id}...")
            versions_response = session.get(
                f"{API_URL}/projects/{project_id}/versions/",
                headers=headers
            )
            
            if versions_response.status_code == 200:
                versions = versions_response.json()
                print(f"✓ Found {versions.get('count', 0)} versions")
                
                # 5. Upload a new version
                print(f"\n4. Uploading new version...")
                
                # Create a test file
                test_file_content = b"# Test Version File\nThis is a test version upload."
                files = {
                    'version_file': ('test_v1.0.0.md', test_file_content, 'text/markdown')
                }
                
                version_data = {
                    'version_number': '1.0.0',
                    'description': 'Test version upload via API',
                    'is_latest': True
                }
                
                upload_response = session.post(
                    f"{API_URL}/projects/{project_id}/versions/upload/",
                    data=version_data,
                    files=files,
                    headers=headers
                )
                
                if upload_response.status_code == 201:
                    uploaded_version = upload_response.json()
                    print(f"✓ Version uploaded successfully!")
                    print(f"   Version ID: {uploaded_version['id']}")
                    print(f"   Version Number: {uploaded_version['version_number']}")
                    print(f"   File Size: {uploaded_version['file_size']} bytes")
                    print(f"   Is Latest: {uploaded_version['is_latest']}")
                    
                    # 6. Get latest version
                    print(f"\n5. Fetching latest version...")
                    latest_response = session.get(
                        f"{API_URL}/projects/{project_id}/versions/latest/",
                        headers=headers
                    )
                    
                    if latest_response.status_code == 200:
                        latest = latest_response.json()
                        print(f"✓ Latest version: v{latest['version_number']}")
                    
                    # 7. Download the version
                    version_id = uploaded_version['id']
                    print(f"\n6. Downloading version {version_id}...")
                    download_response = session.get(
                        f"{API_URL}/projects/{project_id}/versions/{version_id}/download/",
                        headers=headers
                    )
                    
                    if download_response.status_code == 200:
                        print(f"✓ Download successful!")
                        print(f"   Content length: {len(download_response.content)} bytes")
                    else:
                        print(f"✗ Download failed: {download_response.status_code}")
                        
                else:
                    print(f"✗ Upload failed: {upload_response.status_code}")
                    print(f"   Error: {upload_response.json()}")
                    
            else:
                print(f"✗ Failed to fetch versions: {versions_response.status_code}")
        else:
            print("   No projects found. Please create a project first.")
    else:
        print(f"✗ Failed to fetch projects: {projects_response.status_code}")
    
    print("\n" + "=" * 50)
    print("API Testing Complete!")
    print("=" * 50)


if __name__ == "__main__":
    print("\nNote: Make sure to:")
    print("1. Start the Django server: python manage.py runserver")
    print("2. Create a test user with username 'testuser' and password 'testpass123'")
    print("3. Create at least one project for the test user")
    print("\nPress Enter to continue with testing...")
    input()
    
    test_api_endpoints()
