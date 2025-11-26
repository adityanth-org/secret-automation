#!/usr/bin/env python3
import os
import sys
import requests
from github import Github, Auth
from base64 import b64encode
from nacl import encoding, public

def encrypt_secret(public_key: str, secret_value: str) -> str:
    """Encrypt a secret using the repository's public key."""
    public_key_obj = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key_obj)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")

def get_org_secret(org_name: str, token: str, secret_name: str):
    """Fetch a secret value from organization secrets.
    Note: GitHub API doesn't allow reading secret values directly.
    Secrets must be passed as environment variables from the workflow.
    """
    # This is a placeholder - GitHub doesn't allow reading secret values via API
    # Secrets must be passed through environment variables
    return os.getenv(secret_name)

def add_repo_secret(repo_full_name: str, token: str, secret_name: str, secret_value: str):
    """Add a secret to a specific repository using GitHub REST API.
    
    Args:
        repo_full_name: Full repository name (owner/repo)
        token: GitHub token
        secret_name: Name of the secret
        secret_value: Value of the secret
    """
    try:
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Get the repository's public key for Actions
        public_key_url = f'https://api.github.com/repos/{repo_full_name}/actions/secrets/public-key'
        response = requests.get(public_key_url, headers=headers)
        response.raise_for_status()
        public_key_data = response.json()
        
        # Encrypt the secret
        encrypted_value = encrypt_secret(public_key_data['key'], secret_value)
        
        # Create or update the repository secret
        secret_url = f'https://api.github.com/repos/{repo_full_name}/actions/secrets/{secret_name}'
        payload = {
            'encrypted_value': encrypted_value,
            'key_id': public_key_data['key_id']
        }
        
        response = requests.put(secret_url, headers=headers, json=payload)
        response.raise_for_status()
        
        print(f"✓ Added {secret_name} to {repo_full_name}")
        return True
    except Exception as e:
        print(f"✗ Failed to add {secret_name} to {repo_full_name}: {str(e)}")
        return False

def read_repos_file(filename: str = 'repos.txt'):
    """Read repository list from file."""
    try:
        with open(filename, 'r') as f:
            repos = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return repos
    except FileNotFoundError:
        print(f"Error: {filename} not found")
        sys.exit(1)

def main():
    # Get environment variables
    github_token = os.getenv('GITHUB_TOKEN')
    org_name = os.getenv('ORG_NAME')
    
    # Secrets to distribute (fetched from org secrets via workflow env vars)
    secrets_to_distribute = {
        'DOCKERHUB_USERNAME': os.getenv('DOCKERHUB_USERNAME'),
        'DOCKERHUB_PASSWORD': os.getenv('DOCKERHUB_PASSWORD')
    }
    
    if not github_token or not org_name:
        print("Error: Missing required environment variables")
        print("Required: GITHUB_TOKEN, ORG_NAME")
        sys.exit(1)
    
    # Check if all secrets are available
    missing_secrets = [name for name, value in secrets_to_distribute.items() if not value]
    if missing_secrets:
        print(f"Error: Missing secrets: {', '.join(missing_secrets)}")
        print("These must be set as organization secrets and passed via workflow")
        sys.exit(1)
    
    # Read repository list
    repos = read_repos_file()
    
    if not repos:
        print("Error: No repositories found in repos.txt")
        sys.exit(1)
    
    print(f"Distributing secrets to {len(repos)} repositories from organization: {org_name}\n")
    
    success_count = 0
    fail_count = 0
    
    # Distribute secrets to each repository
    for repo in repos:
        print(f"\nProcessing repository: {repo}")
        repo_success = True
        
        for secret_name, secret_value in secrets_to_distribute.items():
            if not add_repo_secret(repo, github_token, secret_name, secret_value):
                repo_success = False
                fail_count += 1
            else:
                success_count += 1
        
        if repo_success:
            print(f"✓ All secrets added to {repo}")
    
    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"  Repositories processed: {len(repos)}")
    print(f"  Secrets distributed successfully: {success_count}")
    print(f"  Failed operations: {fail_count}")
    print(f"{'='*50}")
    
    if fail_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
