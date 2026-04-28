# Private GitHub Packages Setup Guide

## Overview
This guide sets up private GitHub Packages for the `pheno-sdk` package, allowing secure distribution of proprietary code across your projects.

## Prerequisites

### 1. GitHub Token Setup
Create a Personal Access Token (PAT) with the following scopes:
- `read:packages` - To install private packages
- `write:packages` - To publish private packages  
- `repo` - For private repository access

**Steps:**
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `read:packages`, `write:packages`, `repo`
4. Copy the token (starts with `ghp_`)

### 2. Create Private Repository
1. Go to: https://github.com/new
2. Repository name: `pheno-sdk`
3. Owner: `KooshaPari`
4. Make it **PRIVATE** (required for private packages)
5. Don't initialize with README, .gitignore, or license

## Publishing the Package

### Step 1: Build the Package
```bash
cd pheno-sdk
python -m build
```

### Step 2: Publish to Private GitHub Packages
```bash
export GITHUB_TOKEN=ghp_your_token_here
./publish-to-private-github-packages.sh
```

## Installing Private Packages

### Method 1: Using pip config (Recommended)
```bash
# Configure pip globally
pip config set global.index-url https://pypi.pkg.github.com/KooshaPari/simple
pip config set global.extra-index-url https://pypi.org/simple

# Set up authentication
export GITHUB_TOKEN=ghp_your_token_here
```

### Method 2: Using environment variables
```bash
export GITHUB_TOKEN=ghp_your_token_here
pip install --index-url "https://__token__:${GITHUB_TOKEN}@pypi.pkg.github.com/KooshaPari/simple" --extra-index-url https://pypi.org/simple pheno-sdk
```

### Method 3: Using .pip/pip.conf (Already configured)
The projects already have `.pip/pip.conf` files configured for private packages.

## Docker Build with Private Packages

All Dockerfiles are configured to use BuildKit secrets for private package authentication:

```bash
# Build with GitHub token
export GITHUB_TOKEN=ghp_your_token_here
docker build --secret id=github_token,src=<(echo "$GITHUB_TOKEN") -t your-image .
```

Or use the provided build scripts:
```bash
# For router
cd router && ./build-with-github-packages.sh

# For morph  
cd morph && ./build-with-github-packages.sh

# For zen-mcp-server
cd zen-mcp-server && make build-docker

# For atoms_mcp-old
cd atoms_mcp-old && make build-docker
```

## Project-Specific Setup

### Router
- **Dockerfile**: ✅ Configured for private packages
- **pip.conf**: ✅ Configured for private packages
- **Build script**: ✅ Uses BuildKit secrets

### Morph
- **Dockerfile**: ✅ Configured for private packages
- **pip.conf**: ✅ Configured for private packages
- **Build script**: ✅ Uses BuildKit secrets

### Zen-MCP-Server
- **Dockerfile**: ✅ Configured for private packages
- **pip.conf**: ✅ Configured for private packages
- **Makefile**: ✅ Uses Python entry points
- **Dev setup**: ✅ Configures local environment

### Atoms-MCP-Old
- **Dockerfile**: ✅ Configured for private packages
- **pip.conf**: ✅ Configured for private packages
- **Makefile**: ✅ Uses Python entry points
- **Dev setup**: ✅ Configures local environment

## Testing the Setup

### 1. Test Package Availability
```bash
export GITHUB_TOKEN=ghp_your_token_here
pip index versions pheno-sdk --index-url "https://__token__:${GITHUB_TOKEN}@pypi.pkg.github.com/KooshaPari/simple" --extra-index-url https://pypi.org/simple
```

### 2. Test Local Installation
```bash
export GITHUB_TOKEN=ghp_your_token_here
pip install pheno-sdk
```

### 3. Test Docker Builds
```bash
# Test router
cd router && ./build-with-github-packages.sh

# Test morph
cd morph && ./build-with-github-packages.sh
```

## Troubleshooting

### Common Issues

1. **404 Not Found**: Repository doesn't exist or is public
   - Solution: Create private repository first

2. **Authentication Failed**: Invalid or expired token
   - Solution: Generate new token with correct scopes

3. **Package Not Found**: Package not published yet
   - Solution: Run `./publish-to-private-github-packages.sh`

4. **Permission Denied**: Token lacks required scopes
   - Solution: Regenerate token with `read:packages`, `write:packages`, `repo`

### Verification Commands

```bash
# Check token permissions
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# Check package availability
pip index versions pheno-sdk --index-url "https://__token__:${GITHUB_TOKEN}@pypi.pkg.github.com/KooshaPari/simple" --extra-index-url https://pypi.org/simple

# Test installation
pip install --dry-run pheno-sdk
```

## Security Notes

- **Never commit tokens** to version control
- **Use environment variables** for token storage
- **Rotate tokens regularly** for security
- **Use least privilege** - only grant necessary scopes
- **Monitor token usage** in GitHub settings

## Next Steps

1. **Create the private repository** on GitHub
2. **Publish the package** using the provided script
3. **Test the Docker builds** to ensure everything works
4. **Set up CI/CD** with GitHub Actions using `GITHUB_TOKEN` secret
5. **Document the process** for your team

## CI/CD Integration

For GitHub Actions, use the built-in `GITHUB_TOKEN`:

```yaml
- name: Build Docker image
  run: |
    docker build --secret id=github_token,src=<(echo "${{ secrets.GITHUB_TOKEN }}") -t your-image .
```

For other CI systems, set the `GITHUB_TOKEN` environment variable in your CI configuration.
