# Manual GitHub Packages Setup

## The Issue
The 404 error occurs because GitHub Packages requires the repository to exist first before you can publish packages to it.

## Solution 1: Create Repository Manually (Recommended)

1. **Go to GitHub and create a new repository:**
   - Visit: https://github.com/new
   - Repository name: `pheno-sdk`
   - Owner: `KooshaPari`
   - Make it public (required for GitHub Packages)
   - Don't initialize with README, .gitignore, or license

2. **Publish the package:**
   ```bash
   cd pheno-sdk
   ./publish-to-github-packages-simple.sh
   ```

## Solution 2: Use Alternative Package Registry

If GitHub Packages continues to have issues, you can use an alternative approach:

### Option A: Use TestPyPI (Temporary)
```bash
cd pheno-sdk
python -m twine upload --repository testpypi dist/*
```

Then update all projects to use TestPyPI:
```bash
# Update .pip/pip.conf in all projects
[global]
index-url = https://test.pypi.org/simple
extra-index-url = https://pypi.org/simple
```

### Option B: Use Local Package Installation
Copy the wheel file to each project and modify Dockerfiles:

```bash
# Copy wheel to each project
cp pheno-sdk/dist/pheno_sdk-0.1.2-py3-none-any.whl router/
cp pheno-sdk/dist/pheno_sdk-0.1.2-py3-none-any.whl morph/
cp pheno-sdk/dist/pheno_sdk-0.1.2-py3-none-any.whl zen-mcp-server/
cp pheno-sdk/dist/pheno_sdk-0.1.2-py3-none-any.whl atoms_mcp-old/
```

Then update each Dockerfile to install the local package first:
```dockerfile
# Add this before the main dependency installation
COPY pheno_sdk-0.1.2-py3-none-any.whl ./
RUN pip install pheno_sdk-0.1.2-py3-none-any.whl
```

## Solution 3: Use Git Dependency (Fallback)

Temporarily revert to git dependency for testing:

1. **Update pyproject.toml in all projects:**
   ```toml
   dependencies = [
       "pheno-sdk @ git+https://github.com/KooshaPari/phenoSDK.git@main",
       # ... other dependencies
   ]
   ```

2. **Update Dockerfiles to use git:**
   ```dockerfile
   RUN pip install git+https://github.com/KooshaPari/phenoSDK.git@main
   ```

## Quick Test Commands

After setting up any solution:

```bash
# Test package availability
pip index versions pheno-sdk --index-url "https://__token__:${GITHUB_TOKEN}@pypi.pkg.github.com/KooshaPari/simple" --extra-index-url https://pypi.org/simple

# Test Docker builds
cd router && ./build-with-github-packages.sh
cd ../morph && ./build-with-github-packages.sh
```

## Recommended Next Steps

1. **Create the GitHub repository first** (Solution 1)
2. **Publish the package** using the simple script
3. **Test the Docker builds** to ensure everything works
4. **Update CI/CD pipelines** to use the new authentication method
