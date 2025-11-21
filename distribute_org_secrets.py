#!/usr/bin/env python3
import os
import sys
from github import Github, Auth
from base64 import b64encode
from nacl import encoding, public

def encrypt_secret(public_key: str, secret_value: str) -> str:
    """Encrypt a secret using the organization's public key."""
    public_key_obj = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key_obj)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")

def add_org_secret(org, secret_name: str, secret_value: str, visibility: str = "all"):
    """Add a secret to an organization.
    
    Args:
        org: GitHub organization object
        secret_name: Name of the secret
        secret_value: Value of the secret
        visibility: 'all', 'private', or 'selected' (default: 'all')
    """
    try:
        # Get the organization's public key for Actions
        public_key = org.get_actions_public_key()
        
        # Encrypt the secret
        encrypted_value = encrypt_secret(public_key.key, secret_value)
        
        # Create or update the organization secret
        org.create_secret(secret_name, encrypted_value, public_key.key_id, visibility=visibility)
        print(f"✓ Added {secret_name} to organization {org.login} (visibility: {visibility})")
        return True
    except Exception as e:
        print(f"✗ Failed to add {secret_name} to organization {org.login}: {str(e)}")
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
    
    try:
        org = g.get_organization(org_name)
        
        success_count = 0
        fail_count = 0
        
        # Add secrets to organization
        # visibility options: 'all', 'private', or 'selected'
        if add_org_secret(org, 'DOCKERHUB_USERNAME', dockerhub_username, visibility='all'):
            success_count += 1
        else:
            fail_count += 1
            
        if add_org_secret(org, 'DOCKERHUB_PASSWORD', dockerhub_password, visibility='all'):
            success_count += 1
        else:
            fail_count += 1
        
        print(f"\nSummary:")
        print(f"  Successful: {success_count}")
        print(f"  Failed: {fail_count}")
        
        if fail_count > 0:
            sys.exit(1)
            
    except Exception as e:
        print(f"✗ Error accessing organization {org_name}: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
