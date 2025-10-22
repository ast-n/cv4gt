# CV4GT Documentation

This directory contains the Sphinx documentation for CV4GT.

## Building Locally

```bash
# Build HTML documentation
make html

# View locally (opens at http://localhost:8080)
python -m http.server 8080 --directory _build/html
```

Then open http://localhost:8080 in your browser.

## Hosting Options

### Option 1: Read the Docs (Recommended)

Read the Docs provides free documentation hosting with automatic builds.

1. **Sign up** at https://readthedocs.org/ with your GitHub account

2. **Import** your repository:
   - Click "Import a Project"
   - Select `cv4gt` from your GitHub repos
   - Click "Next"

3. **Configure** (optional, defaults are usually fine):
   - Admin → Advanced Settings
   - Requirements file: `requirements.txt` (if needed)
   - Python interpreter: `CPython 3.x`

4. **Build**: Read the Docs will automatically build on every push to `main`

5. **Access**: Your docs will be at `https://cv4gt.readthedocs.io/`

### Option 2: GitHub Pages

Host directly from your GitHub repository.

1. **Create `.github/workflows/docs.yml`**:

```yaml
name: Build and Deploy Docs

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints

    - name: Build documentation
      run: |
        cd docs
        make html

    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./docs/_build/html
```

2. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Source: Deploy from a branch
   - Branch: `gh-pages` / `root`
   - Save

3. **Access**: Your docs will be at `https://ast-n.github.io/cv4gt/`

### Option 3: Self-Hosted

Host on your own server:

1. **Build documentation**:
   ```bash
   make html
   ```

2. **Copy to web server**:
   ```bash
   scp -r _build/html/* user@yourserver:/var/www/cv4gt-docs/
   ```

3. **Configure web server** (nginx example):
   ```nginx
   server {
       listen 80;
       server_name docs.cv4gt.com;
       root /var/www/cv4gt-docs;
       index index.html;
   }
   ```

## Updating Documentation

After making changes to docstrings or `.rst` files:

```bash
# Rebuild
make html

# Or clean and rebuild
make clean
make html
```

## Documentation Structure

- `index.rst` - Main page
- `getting_started.rst` - Installation and setup guide
- `configuration.rst` - Configuration reference
- `usage.rst` - Usage examples
- `contributing.rst` - Contribution guidelines
- `api/` - Auto-generated API documentation

## Adding New Pages

1. Create a new `.rst` file in `docs/`
2. Add it to the `toctree` in `index.rst`
3. Rebuild with `make html`

## Troubleshooting

**Import errors during build:**
- These are normal - mocked imports in `conf.py` handle this
- Your docstrings will still appear in the documentation

**Theme not applying:**
- Ensure `sphinx-rtd-theme` is installed: `pip install sphinx-rtd-theme`
- Check `html_theme = 'sphinx_rtd_theme'` in `conf.py`

**Documentation not updating:**
- Run `make clean && make html` to force rebuild
- Check for syntax errors in `.rst` files
