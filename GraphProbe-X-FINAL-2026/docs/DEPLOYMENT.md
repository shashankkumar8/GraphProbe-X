# GraphProbe-X Deployment Guide

## Static Interactive Console Deployment (GitHub Pages)

The interactive research console in `site/` is designed for zero-backend static deployment.

### Automated GitHub Actions Deployment
1. Push commits to `main` branch.
2. The GitHub Action `.github/workflows/deploy-pages.yml` will automatically build and publish `site/` to GitHub Pages.
3. Access at `https://<username>.github.io/GraphProbe-X/`.

### Manual / Local Testing
Run the lightweight python web server:
```bash
python -m scripts.serve
```
Navigate to `http://localhost:8000/site/index.html`.
