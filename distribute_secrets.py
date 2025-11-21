#!/usr/bin/env python3
import os
import sys
from github import Github, Auth
from base64 import b64encode
from nacl import encoding, public

def encrypt_secret(public_key: str, secret_value: str) -> str:
    """Encrypt a secret using the repository's public key."""
    public_key_obj = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key_obj)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")

def add_secret_to_repo(repo, secret_name: str, secret_value: str):
    """Add a secret to a repository."""
    try:
        # Get the repository's public key for Actions
        public_key = repo.get_actions_public_key()
        
        # Encrypt the secret
        encrypted_value = encrypt_secret(public_key.key, secret_value)
        
        # Create or update the secret for GitHub Actions
        repo.create_secret(secret_name, encrypted_value, public_key.key_id, secret_type="actions")
        print(f"✓ Added {secret_name} to {repo.full_name}")
        return True
    except Exception as e:
        print(f"✗ Failed to add {secret_name} to {repo.full_name}: {str(e)}")
        return False

def main():
    # Get environment variables
    github_token = os.getenv('GITHUB_TOKEN')
    dockerhub_username = os.getenv('DOCKERHUB_USERNAME')
    dockerhub_password = os.getenv('DOCKERHUB_PASSWORD')
    
    if not all([github_token, dockerhub_username, dockerhub_password]):
        print("Error: Missing required environment variables")
        sys.exit(1)
    
    # Initialize GitHub client with new auth method
    auth = Auth.Token(github_token)
    g = Github(auth=auth)
    
    # Read repository list
    try:
        with open('repos.txt', 'r') as f:
            repos = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print("Error: repos.txt not found")
        sys.exit(1)
    
    print(f"Processing {len(repos)} repositories...\n")
    
    success_count = 0
    fail_count = 0
    
    # Process each repository
    for repo_name in repos:
        print(f"Processing: {repo_name}")
        try:
            repo = g.get_repo(repo_name)
            
            # Add secrets
            if add_secret_to_repo(repo, 'DOCKERHUB_USERNAME', dockerhub_username):
                success_count += 1
            else:
                fail_count += 1
                
            if add_secret_to_repo(repo, 'DOCKERHUB_PASSWORD', dockerhub_password):
                success_count += 1
            else:
                fail_count += 1
                
            print("---")
        except Exception as e:
            print(f"✗ Error accessing {repo_name}: {str(e)}")
            fail_count += 2
            print("---")
    
    print(f"\nSummary:")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {fail_count}")
    
    if fail_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
