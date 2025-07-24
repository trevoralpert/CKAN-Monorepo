# CKAN Modernization: 6 Key Features Overview

**Target Audience:** Small City IT Teams (1-3 people) managing open data portals  
**Goal:** Enhance CKAN to be more user-friendly, performant, and measurable

---

## 📱 Feature 1: Mobile-First UX & React Widgets

### What it is
Replace clunky, desktop-first Jinja/jQuery components with responsive layouts and modern React (or Vue) components. Focus on high-impact areas like dataset upload wizards and advanced filter panels.

### Why it matters
- **Citizens are on phones**: 60%+ of government site traffic is mobile
- **Staff efficiency**: Better UX = fewer support tickets for small IT teams
- **Progressive enhancement**: Works without JavaScript for accessibility

### Implementation Approach
1. Identify 1-2 painful UI flows (dataset create/edit, search filters)
2. Add a CKAN plugin that injects bundled React widgets via IBlueprint + static assets
3. Use Tailwind/Bootstrap 5 for responsive CSS
4. Progressive enhancement: fall back to classic forms if JS fails

### Success Metrics
- Mobile bounce rate reduction: Target 20%
- Support ticket reduction: Target 30% for UI-related issues
- Page load time on mobile: < 3 seconds

---

## ⚡ Feature 2: Async/Await for Heavy I/O Paths

### What it is
Convert high-traffic or long-running endpoints (search, file upload, harvest jobs) to async to avoid blocking workers. Enables handling traffic spikes without scaling horizontally.

### Why it matters
- **Small-city servers can't scale horizontally**: Budget constraints
- **Handle spikes**: Census data releases, emergency info updates
- **Better user experience**: No more timeouts on large file uploads

### Implementation Approach
1. Pick one API route (e.g., `/api/3/action/package_search`) and refactor to `async def`
2. Swap blocking libs: `requests` → `httpx`, sync SQLAlchemy → async session for reads
3. Run under async-capable server (gunicorn + uvicorn workers)
4. Measure before/after latency

### Success Metrics
- 95th percentile response time: -50% reduction
- Concurrent request handling: 5x improvement
- Timeout errors: -90% reduction

---

## 🔍 Feature 3: Advanced Search & Discovery

### What it is
Upgrade from basic keyword search to faceted, semantic, or Elasticsearch-backed search with "related datasets" suggestions. Make data actually findable.

### Why it matters
- **Users can't find what they need**: Current search misses context
- **Reduces "where is that CSV?" emails**: Save IT team time
- **Increases data usage**: If people can find it, they'll use it

### Implementation Approach
1. Replace/augment Solr with Elasticsearch/OpenSearch, or tune Solr relevancy
2. Add facets (organization, tags, geography) and synonym/stopword lists
3. Optional: small embedding model to recommend similar datasets
4. Expose new search endpoints + UI widgets

### Success Metrics
- Search success rate: +40% (measured by clicks on results)
- "No results" searches: -60%
- Average time to find dataset: -50%

---

## 📊 Feature 4: Interactive Data Visualizations & Dashboards

### What it is
Resource view plugins (Chart.js/Plotly) for instant visualizations and an admin dashboard showing portal KPIs: downloads, API calls, top datasets.

### Why it matters
- **Stakeholders want quick insights**: Not raw CSV files
- **IT can show ROI**: "Look how many people used this dataset"
- **Builds trust**: Visual data is more accessible to citizens

### Implementation Approach
1. Build a `ckanext-visualize` plugin: pull datastore rows, render charts client-side
2. Add an admin-only dashboard page: query logs/analytics DB and render charts
3. Cache results to avoid heavy DB hits
4. Support common chart types: line, bar, pie, map

### Success Metrics
- Datasets with visualizations: 80% coverage
- User engagement time: +150% on datasets with charts
- Admin dashboard usage: Weekly by management

---

## 🎯 Feature 5: Metadata Quality & Schema Enforcement

### What it is
Enforce consistent metadata using ckanext-scheming, custom validators (Pydantic optional), and guided forms. No more "untitled_dataset_final_v2".

### Why it matters
- **Inconsistent metadata makes data useless**: Can't find or trust it
- **Clean schemas = trustable data**: Foundation for all other features
- **Compliance**: Many cities have data standards requirements

### Implementation Approach
1. Define JSON/YAML schemas for your target city (required fields, controlled vocab)
2. Add validators and friendly error messages in the form
3. Optional: AI prompt helper to suggest tags/descriptions
4. Run one-time audit script to flag bad legacy metadata

### Success Metrics
- Metadata completeness: 95%+ required fields filled
- Schema validation errors: -80% on submission
- Dataset discovery rate: +30% from better metadata

---

## 📈 Feature 6: Usage Analytics Pipeline

### What it is
Track downloads, API hits, search queries, and render them in a simple analytics view with export capabilities. Know what citizens actually use.

### Why it matters
- **IT needs evidence to justify upgrades**: Data-driven decisions
- **Product owners need usage insights**: What datasets to prioritize
- **Compliance reporting**: Many grants require usage metrics

### Implementation Approach
1. Add middleware or hook into IActions to log events (dataset_viewed, resource_downloaded)
2. Store events in lightweight table (or use Matomo/PostHog)
3. Build simple UI page and CSV export for monthly reports
4. Optional: email summary to admins weekly

### Success Metrics
- Event capture rate: 100% of key actions
- Report generation time: < 10 seconds
- Actionable insights identified: 3+ per month

---

## 🎯 Combined Impact

When all 6 features work together:

1. **Analytics** shows what people search for
2. **Metadata quality** ensures they find it
3. **Advanced search** connects them to data
4. **Visualizations** help them understand it
5. **Mobile UX** works wherever they are
6. **Async performance** handles the load

**Result**: A modern, measurable, maintainable open data portal that small city IT teams can actually manage. 