# GitHub Organization Secret Automation

Automate the distribution of secrets (like DockerHub credentials) to your GitHub organization with fine-grained control over which repositories can access each secret.

## Overview

This project provides a flexible way to manage organization-level secrets with repository-specific access control using a YAML configuration file (`repos1.yaml`). Secrets are fetched from organization secrets and distributed to selected repositories.

## Features

- Add secrets at the organization level (accessible by all repos)
- Secure encryption using NaCl/libsodium
- Support for different visibility levels (all, private, selected)
- Easy to configure and run

## Prerequisites

- GitHub organization admin access
- Personal Access Token (PAT) with `admin:org` scope
- DockerHub credentials (or any other secrets you want to distribute)

## Configuration

### 1. Create Organization Secrets First

Go to your organization Settings → Secrets and variables → Actions → Secrets and create:

- `ORG_ADMIN_TOKEN` - GitHub PAT with `admin:org` scope (for this workflow)
- `DOCKERHUB_USERNAME` - Your DockerHub username
- `DOCKERHUB_PASSWORD` - Your DockerHub password/token
- Any other secrets you want to distribute

**Important**: When creating these secrets, set visibility to **"Selected repositories"** (you can select any repo initially, the workflow will update it)

### 2. Configure `repos1.yaml`

Define which repositories should have access to each secret:

```yaml
secrets:
  - name: DOCKERHUB_USERNAME
    org_secret_name: DOCKERHUB_USERNAME
    repositories:
      - secret-test
      - secret-test-2
      - secret-test-3
  
  - name: DOCKERHUB_PASSWORD
    org_secret_name: DOCKERHUB_PASSWORD
    repositories:
      - secret-test
      - secret-test-2
      - secret-test-3
  
  # Add more secrets as needed
  - name: NPM_TOKEN
    org_secret_name: NPM_TOKEN
    repositories:
      - frontend-app
      - backend-api
```

**Fields:**
- `name`: Display name (can be same as org_secret_name)
- `org_secret_name`: The exact name of the organization secret
- `repositories`: List of repository names (without org prefix) that can access this secret

## Usage

### Automatic Distribution

The workflow automatically runs when you:
- Push changes to `repos1.yaml`
- Push changes to the workflow file
- Manually trigger via Actions tab

### Manual Trigger

1. Go to **Actions** tab in your repository
2. Select **"Distribute Secrets to Repositories"** workflow
3. Click **"Run workflow"**
4. Select branch and click **"Run workflow"**

### Adding New Secrets

1. Create the secret in your organization (Settings → Secrets → New organization secret)
2. Set visibility to **"Selected repositories"**
3. Update `repos1.yaml` with the new secret configuration:

```yaml
secrets:
  - name: NPM_TOKEN
    org_secret_name: NPM_TOKEN
    repositories:
      - frontend-app
      - backend-api
```

4. Commit and push - the workflow will automatically update repository access

## Files

- `repos1.yaml` - Configuration file defining secrets and repository access
- `.github/workflows/distribute-secrets.yml` - Main workflow using GitHub CLI
- `.github/workflows/distribute-org-secrets.yml` - Alternative Python-based workflow
- `distribute_org_secrets.py` - Python script for local execution
- `repos.txt` - Legacy repository list (kept for reference)

## Secret Visibility Options

When adding secrets to an organization, you can set visibility:

- `all` - Available to all repositories (public and private) - **Default**
- `private` - Only available to private repositories
- `selected` - Available to specific repositories only

## How It Works

1. **Read Configuration**: Parses `repos1.yaml` to get secret-to-repository mappings
2. **Fetch Repository IDs**: Uses GitHub API to get repository IDs for each repo name
3. **Update Secret Access**: Uses GitHub API to update which repositories can access each organization secret
4. **Maintain Secrets**: The actual secret values remain in organization secrets (never exposed)
5. **Access in Workflows**: Only the specified repositories can use these secrets in their workflows

**Note**: This workflow manages repository access for existing organization secrets. It does NOT create or update secret values.

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