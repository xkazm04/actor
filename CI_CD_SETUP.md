# CI/CD Setup Guide

This repository uses GitHub Actions to automatically build and deploy the Apify Actor when changes are pushed to the `master` branch.

## Setup Instructions

### 1. Configure GitHub Secrets

You need to add the following secrets to your GitHub repository:

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add:

   - **`APIFY_TOKEN`**: Your Apify API token
     - Get it from: https://console.apify.com/account/integrations
     - This token authenticates the deployment
   
   - **`APIFY_ACTOR_ID`** (optional): Your Actor ID
     - Only needed if you don't have an `apify.json` file
     - Format: `qk4NvJzPrddjBCEqs` (your Actor ID)
     - Find it in your Actor settings on Apify Console

### 2. Workflow Behavior

The workflow (`.github/workflows/deploy.yml`) will:

- ✅ Trigger automatically on every push to `master` branch
- ✅ Can be manually triggered via GitHub Actions UI (`workflow_dispatch`)
- ✅ Install Apify CLI
- ✅ Build and push your Actor to Apify
- ✅ Show deployment summary in GitHub Actions

### 3. Workflow Steps

1. **Checkout**: Gets the latest code from the repository
2. **Setup Node.js**: Installs Node.js (required for Apify CLI)
3. **Install Apify CLI**: Installs the Apify command-line tool
4. **Login**: Authenticates with Apify using your token
5. **Push**: Builds and deploys the Actor
6. **Info**: Shows Actor information after deployment

### 4. Alternative: Using apify.json

If you prefer to use an `apify.json` configuration file instead of secrets:

1. Create `apify.json` in the root directory:
```json
{
  "actorSpecification": 1,
  "name": "your-actor-name",
  "version": "1.0.0",
  "buildTag": "latest",
  "environmentVariables": {}
}
```

2. The workflow will automatically detect and use it

### 5. Monitoring Deployments

- View deployment status: Go to **Actions** tab in your GitHub repository
- Check logs: Click on any workflow run to see detailed logs
- Deployment summary: Available in the workflow run summary

### 6. Troubleshooting

**Error: "APIFY_TOKEN not found"**
- Make sure you've added `APIFY_TOKEN` to GitHub Secrets
- Check that the secret name matches exactly (case-sensitive)

**Error: "Actor ID not found"**
- Add `APIFY_ACTOR_ID` to GitHub Secrets, OR
- Create an `apify.json` file with your Actor configuration

**Error: "Docker build failed"**
- Check your `DockerFile` (note the capitalization)
- Verify all dependencies in `rquirements.txt` are valid
- Check GitHub Actions logs for specific error messages

**Error: "Permission denied"**
- Verify your Apify token has the correct permissions
- Ensure the token is for the correct Apify account

## Manual Deployment

You can also deploy manually using Apify CLI:

```bash
# Install Apify CLI
npm install -g apify-cli

# Login
apify login --token YOUR_APIFY_TOKEN

# Push Actor
apify push
```

## Security Notes

- ⚠️ Never commit API tokens or secrets to the repository
- ✅ Always use GitHub Secrets for sensitive information
- ✅ The workflow uses `${{ secrets.APIFY_TOKEN }}` which is secure
- ✅ Tokens are masked in GitHub Actions logs

## Next Steps

After setting up the secrets, push to `master` branch and the workflow will automatically deploy your Actor!

