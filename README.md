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

### 1. Configure `repos1.yaml`

Define your secrets and which repositories should have access:

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
- `name`: The secret name as it will appear in the organization
- `org_secret_name`: The name of the existing organization secret to fetch the value from
- `repositories`: List of repository names (without org prefix) that can access this secret

### 2. Setup Organization Secrets

Add these secrets to your **organization** (Settings → Secrets and variables → Actions → Secrets):

- `ORG_ADMIN_TOKEN` - GitHub PAT with `admin:org` scope
- `DOCKERHUB_USERNAME` - Your DockerHub username
- `DOCKERHUB_PASSWORD` - Your DockerHub password/token
- Any other secrets referenced in `repos1.yaml`

### 3. Setup Organization Variables

Add this variable to your **organization** (Settings → Variables → Actions):

- `ORG_NAME` - Your organization name (e.g., "adityanth-org")

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

1. Add the secret to your organization secrets
2. Update `repos1.yaml` with the new secret configuration
3. Add the secret to the workflow's `env` section:

```yaml
env:
  GH_TOKEN: ${{ secrets.ORG_ADMIN_TOKEN }}
  DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
  DOCKERHUB_PASSWORD: ${{ secrets.DOCKERHUB_PASSWORD }}
  NPM_TOKEN: ${{ secrets.NPM_TOKEN }}  # Add new secrets here
```

4. Commit and push - the workflow will automatically distribute the secrets

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

1. **Read Configuration**: Parses `repos1.yaml` to get secret definitions
2. **Fetch Secret Values**: Retrieves secret values from organization secrets (passed via workflow env)
3. **Set Organization Secrets**: Uses GitHub CLI to create/update organization secrets with `--visibility selected`
4. **Grant Repository Access**: Automatically grants access only to repositories listed in the configuration
5. **Access in Workflows**: Selected repositories can now use these secrets in their workflows

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