#!/usr/bin/env python3
import os
import sys
import requests
from github import Github, Auth
from base64 import b64encode
from nacl import encoding, public

def encrypt_secret(public_key: str, secret_value: str) -> str:
    """Encrypt a secret using the organization's public key."""
    public_key_obj = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key_obj)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")

def add_org_secret(org_name: str, token: str, secret_name: str, secret_value: str, visibility: str = "all"):
    """Add a secret to an organization using GitHub REST API.
    
    Args:
        org_name: Organization name
        token: GitHub token
        secret_name: Name of the secret
        secret_value: Value of the secret
        visibility: 'all', 'private', or 'selected' (default: 'all')
    """
    try:
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Get the organization's public key for Actions
        public_key_url = f'https://api.github.com/orgs/{org_name}/actions/secrets/public-key'
        response = requests.get(public_key_url, headers=headers)
        response.raise_for_status()
        public_key_data = response.json()
        
        # Encrypt the secret
        encrypted_value = encrypt_secret(public_key_data['key'], secret_value)
        
        # Create or update the organization secret
        secret_url = f'https://api.github.com/orgs/{org_name}/actions/secrets/{secret_name}'
        payload = {
            'encrypted_value': encrypted_value,
            'key_id': public_key_data['key_id'],
            'visibility': visibility
        }
        
        response = requests.put(secret_url, headers=headers, json=payload)
        response.raise_for_status()
        
        print(f"✓ Added {secret_name} to organization {org_name} (visibility: {visibility})")
        return True
    except Exception as e:
        print(f"✗ Failed to add {secret_name} to organization {org_name}: {str(e)}")
        return False

def main():
    # Get environment variables
    github_token = os.getenv('GITHUB_TOKEN')
    dockerhub_username = os.getenv('DOCKERHUB_USERNAME')
    dockerhub_password = os.getenv('DOCKERHUB_PASSWORD')
    org_name = os.getenv('ORG_NAME')  # Organization name
    
    if not all([github_token, dockerhub_username, dockerhub_password, org_name]):
        print("Error: Missing required environment variables")
        print("Required: GITHUB_TOKEN, DOCKERHUB_USERNAME, DOCKERHUB_PASSWORD, ORG_NAME")
        sys.exit(1)
    
    # Initialize GitHub client with new auth method
    auth = Auth.Token(github_token)
    g = Github(auth=auth)
    
    print(f"Processing organization: {org_name}\n")
    
    success_count = 0
    fail_count = 0
    
    # Add secrets to organization
    # visibility options: 'all', 'private', or 'selected'
    if add_org_secret(org_name, github_token, 'DOCKERHUB_USERNAME', dockerhub_username, visibility='all'):
        success_count += 1
    else:
        fail_count += 1
        
    if add_org_secret(org_name, github_token, 'DOCKERHUB_PASSWORD', dockerhub_password, visibility='all'):
        success_count += 1
    else:
        fail_count += 1
    
    print(f"\nSummary:")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {fail_count}")
    
    if fail_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
