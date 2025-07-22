# CKAN Legacy Modernization Project - Gauntlet AI

This monorepo contains CKAN and its core extensions for the legacy modernization project.

## Structure
- `/ckan` - Core CKAN repository (Pylons-based legacy system)
- `/extensions/` - CKAN extensions
  - `ckanext-harvest` - Remote data harvesting functionality
  - `ckanext-spatial` - Geospatial features and search
  - `ckanext-qa` - Data quality checks and scoring
  - `ckanext-issues` - Issue tracking for datasets
  - `ckanext-scheming` - Custom metadata schemas

## Lines of Code
This combined repository contains **over 1.2 million lines of code**, meeting the project requirement.

## Target User Segment
**Small City Open Data Portals (50k-500k population)**
- Limited IT resources (2-5 person teams)
- Need modern, mobile-friendly data portals
- Currently running outdated CKAN versions
- Budget constraints preventing enterprise solutions

## Six Modernization Features
1. **Docker/Kubernetes Deployment** - Containerized, scalable infrastructure
2. **OAuth2/SSO Authentication** - Modern auth with Google/GitHub/Microsoft
3. **REST/GraphQL API Layer** - Modern API with OpenAPI documentation
4. **Async Task Processing** - Convert synchronous operations to async with Celery
5. **Mobile-Responsive UI** - Replace legacy templates with Tailwind CSS
6. **Real-time Notifications** - WebSocket support for live updates

## Technology Stack
- **Current**: Python 2.7/3.6, Pylons 1.0 (deprecated 2010), SQLAlchemy 0.9
- **Target**: Python 3.11+, FastAPI/Flask, SQLAlchemy 2.0, Modern async patterns

## Quick Start
```bash
# Set up Python environment
cd ckan
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r dev-requirements.txt
```

## Daily Workflow
```bash
# Work on a feature
cd extensions/ckanext-qa
git checkout -b feature/async-improvements
# Make changes
git add .
git commit -m "Add async task processing"
git push origin feature/async-improvements
```

---

*This project demonstrates AI-assisted legacy modernization, transforming a 1.2M LOC Pylons-based system into a modern, cloud-native application.* 