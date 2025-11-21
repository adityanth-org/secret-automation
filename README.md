# GitHub Organization Secret Automation

Automate the distribution of secrets (like DockerHub credentials) to your GitHub organization, making them available to all repositories.

## Overview

This project provides two methods to distribute secrets to your GitHub organization:

1. **GitHub Actions Workflow** (using GitHub CLI) - Recommended for CI/CD automation
2. **Python Script** (using GitHub REST API) - For local execution or custom integrations

## Features

- Add secrets at the organization level (accessible by all repos)
- Secure encryption using NaCl/libsodium
- Support for different visibility levels (all, private, selected)
- Easy to configure and run

## Prerequisites

- GitHub organization admin access
- Personal Access Token (PAT) with `admin:org` scope
- DockerHub credentials (or any other secrets you want to distribute)

## Setup

### 1. Create GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with these scopes:
   - `admin:org` (for organization secrets)
   - `repo` (if needed for repository access)
3. Save the token securely

### 2. Configure Repository Secrets

Add these secrets to your repository (Settings → Secrets and variables → Actions):

- `ORG_ADMIN_TOKEN` - Your GitHub PAT with admin:org scope
- `DOCKERHUB_USERNAME` - Your DockerHub username
- `DOCKERHUB_PASSWORD` - Your DockerHub password/token
- `ORG_NAME` - Your GitHub organization name

## Usage

### Method 1: GitHub Actions Workflow (Recommended)

Two workflows are available:

#### Option A: Using GitHub CLI (`distribute-secrets.yml`)
```yaml
# Triggers: Manual or on push to main
# Uses: GitHub CLI (gh)
```

#### Option B: Using Python Script (`distribute-org-secrets.yml`)
```yaml
# Triggers: Manual or on push to main
# Uses: Python with PyGithub and PyNaCl
```

**To run manually:**
1. Go to Actions tab in your repository
2. Select the workflow you want to run
3. Click "Run workflow"
4. Select branch and click "Run workflow"

**Automatic trigger:**
- Both workflows trigger automatically on push to main branch

### Method 2: Local Python Script

**Install dependencies:**
```bash
pip install PyGithub PyNaCl requests
```

**Set environment variables:**
```bash
export GITHUB_TOKEN="your_github_pat"
export DOCKERHUB_USERNAME="your_dockerhub_username"
export DOCKERHUB_PASSWORD="your_dockerhub_password"
export ORG_NAME="your_org_name"
```

**Run the script:**
```bash
python distribute_org_secrets.py
```

## Files

- `distribute_org_secrets.py` - Python script to add secrets to organization
- `.github/workflows/distribute-secrets.yml` - GitHub Actions workflow using GitHub CLI
- `.github/workflows/distribute-org-secrets.yml` - GitHub Actions workflow using Python script
- `repos.txt` - List of repositories (for reference, not used by org-level secrets)

## Secret Visibility Options

When adding secrets to an organization, you can set visibility:

- `all` - Available to all repositories (public and private) - **Default**
- `private` - Only available to private repositories
- `selected` - Available to specific repositories only

## How It Works

1. **Fetch Organization Public Key**: Retrieves the public key from GitHub API
2. **Encrypt Secrets**: Uses NaCl/libsodium to encrypt secret values
3. **Upload to Organization**: Creates or updates organization-level secrets via GitHub API
4. **Access in Workflows**: All repositories can now access these secrets in their workflows

## Example: Using Organization Secrets in Workflows

```yaml
name: Build and Push Docker Image

on: push

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Login to DockerHub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_PASSWORD }}
      
      - name: Build and push
        run: |
          docker build -t myimage .
          docker push myimage
```

## Troubleshooting

### Error: 'Organization' object has no attribute 'get_actions_public_key'
- **Fixed**: The script now uses GitHub REST API directly instead of PyGithub's organization methods

### Error: Missing required environment variables
- Ensure all required environment variables are set (GITHUB_TOKEN, DOCKERHUB_USERNAME, DOCKERHUB_PASSWORD, ORG_NAME)

### Error: 403 Forbidden
- Check that your PAT has `admin:org` scope
- Verify you have admin access to the organization

### Error: 404 Not Found
- Verify the organization name is correct
- Ensure the organization exists and you have access

## Security Notes

- Never commit tokens or passwords to the repository
- Use GitHub Secrets for sensitive values
- Rotate tokens regularly
- Use fine-grained PATs when possible
- Organization secrets are encrypted at rest by GitHub

## License

MIT