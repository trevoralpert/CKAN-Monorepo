# CKAN Feature Implementation Checklist

**Implementation Order:** Optimized for dependencies, value delivery, and technical flow

---

## ✅ Phase 1: Usage Analytics Pipeline (Feature 6)
**Timeline:** Week 1-2  
**Why First:** Establish baseline metrics before any improvements

### Prerequisites
- [ ] Docker development environment running
- [ ] Access to CKAN database
- [ ] Understanding of CKAN's IActions interface

### Implementation Steps

#### 1.1 Event Tracking Infrastructure
- [ ] Create new extension: `ckanext-analytics`
  ```bash
  cd /usr/src/ckanext
  ckan generate extension analytics
  ```
- [ ] Define event schema in `ckanext-analytics/ckanext/analytics/models.py`
  - event_id (UUID)
  - event_type (view, download, api_call, search)
  - resource_id (optional)
  - dataset_id (optional)
  - user_id (optional, respect privacy)
  - timestamp
  - metadata (JSON)

#### 1.2 Implement Event Capture
- [ ] Create IActions implementation to hook into:
  - `package_show` (dataset views)
  - `resource_download` (file downloads)
  - `package_search` (search queries)
  - API calls via middleware
- [ ] Add database migration for analytics tables
- [ ] Implement privacy-respecting user tracking (hash IPs, honor DNT)

#### 1.3 Analytics Dashboard
- [ ] Create admin-only blueprint at `/dashboard/analytics`
- [ ] Build summary views:
  - Top 10 datasets (last 30 days)
  - Download trends chart
  - Search terms word cloud
  - API usage by endpoint
- [ ] Add CSV export functionality
- [ ] Implement caching layer (Redis) for dashboard queries

#### 1.4 Testing & Deployment
- [ ] Unit tests for event capture
- [ ] Integration tests for dashboard
- [ ] Performance test: ensure < 50ms overhead
- [ ] Document configuration options
- [ ] Deploy and verify baseline metrics capture

### Success Criteria
- [ ] 100% of key user actions logged
- [ ] Dashboard loads in < 2 seconds
- [ ] No performance degradation on main site
- [ ] First weekly metrics report generated

---

## ✅ Phase 2: Metadata Quality & Schema Enforcement (Feature 5)
**Timeline:** Week 3-4  
**Why Second:** Clean data is foundation for search and visualization

### Prerequisites
- [ ] Analytics showing current metadata quality issues
- [ ] Identified target metadata schema/standard
- [ ] ckanext-scheming installed

### Implementation Steps

#### 2.1 Schema Definition
- [ ] Create schema YAML for core dataset types:
  ```yaml
  dataset_type: city-dataset
  fields:
    - field_name: department
      label: Department
      validators: not_empty unicode
      form_snippet: select.html
      choices: [Public Works, Finance, Police, Fire, ...]
  ```
- [ ] Define controlled vocabularies for:
  - Departments/organizations
  - Update frequencies
  - Geographic coverage
  - Data categories

#### 2.2 Validation Layer
- [ ] Implement custom validators:
  - Email format validation
  - Date range validation
  - Geographic boundary validation
  - File size limits
- [ ] Create friendly error messages
- [ ] Add inline help text and examples

#### 2.3 Migration Tools
- [ ] Build audit script to identify non-compliant datasets
- [ ] Create bulk update interface for admins
- [ ] Implement gradual enforcement:
  - Phase 1: Warnings only
  - Phase 2: Block new datasets
  - Phase 3: Require updates to existing

#### 2.4 AI-Assisted Metadata (Bonus)
- [ ] Integrate OpenAI/local LLM for:
  - Tag suggestions based on description
  - Auto-categorization
  - Title improvement suggestions
- [ ] Add "Suggest improvements" button
- [ ] Track suggestion acceptance rate

### Success Criteria
- [ ] 95% of new datasets pass validation
- [ ] 80% of existing datasets updated
- [ ] 50% reduction in "Contact for info" datasets
- [ ] Positive user feedback on form UX

---

## ✅ Phase 3: Advanced Search & Discovery (Feature 3)
**Timeline:** Week 5-6  
**Why Third:** Leverages clean metadata, provides immediate user value

### Prerequisites
- [ ] Metadata schemas implemented
- [ ] Analytics showing search patterns
- [ ] Solr/Elasticsearch decision made

### Implementation Steps

#### 3.1 Search Backend Enhancement
- [ ] If keeping Solr:
  - Update schema.xml with new fields
  - Add synonyms.txt (transit=transportation=bus)
  - Configure field boosting (title > description)
  - Enable spell checking and suggestions
- [ ] If moving to Elasticsearch:
  - Set up ES cluster
  - Implement custom analyzer
  - Build migration scripts
  - Create fallback to Solr

#### 3.2 Faceted Search Implementation
- [ ] Add facets for:
  - Organization/Department
  - Update frequency
  - File format
  - Time range (last week/month/year)
  - Geographic area
- [ ] Implement facet counts and filters
- [ ] Add "Clear all filters" functionality

#### 3.3 Related Datasets Feature
- [ ] Implement similarity scoring based on:
  - Shared tags
  - Same department
  - Related keywords
  - User behavior (users who viewed X also viewed Y)
- [ ] Add "Related Datasets" section to dataset page
- [ ] Track click-through rates

#### 3.4 Search UI Improvements
- [ ] Implement autocomplete/typeahead
- [ ] Add search suggestions ("Did you mean...")
- [ ] Create saved search functionality
- [ ] Add search result previews

### Success Criteria
- [ ] 40% improvement in search success rate
- [ ] 60% reduction in "no results" searches
- [ ] 25% increase in datasets discovered via related
- [ ] Search response time < 200ms

---

## ✅ Phase 4: Mobile-First UX & React Widgets (Feature 1)
**Timeline:** Week 7-9  
**Why Fourth:** Can now showcase clean data with good search

### Prerequisites
- [ ] Search and metadata features working
- [ ] Identified top 2-3 painful UI workflows
- [ ] React/Vue decision made (recommend React for ecosystem)

### Implementation Steps

#### 4.1 Development Setup
- [ ] Create `ckanext-modernui` extension
- [ ] Set up Webpack/Vite build pipeline
- [ ] Configure React with TypeScript
- [ ] Implement CSS framework (Tailwind recommended)
- [ ] Set up component library structure

#### 4.2 Dataset Upload Wizard
- [ ] Build multi-step React component:
  - Step 1: Basic metadata
  - Step 2: Upload files (with progress)
  - Step 3: Additional metadata
  - Step 4: Review & submit
- [ ] Implement:
  - Auto-save to localStorage
  - Validation at each step
  - File type detection
  - Preview capability
- [ ] Progressive enhancement fallback

#### 4.3 Advanced Search Filters
- [ ] Create React component for search page
- [ ] Implement:
  - Interactive facet selection
  - Date range picker
  - Map-based geographic filter
  - Real-time result count
- [ ] Mobile-optimized filter drawer
- [ ] Save filter combinations

#### 4.4 Responsive Design Overhaul
- [ ] Audit all pages for mobile issues
- [ ] Implement responsive tables
- [ ] Optimize touch targets (48px minimum)
- [ ] Add mobile navigation menu
- [ ] Test on real devices

### Success Criteria
- [ ] 90% mobile usability score (Google Lighthouse)
- [ ] 50% reduction in form abandonment
- [ ] 20% reduction in mobile bounce rate
- [ ] Works without JavaScript enabled

---

## ✅ Phase 5: Interactive Data Visualizations (Feature 4)
**Timeline:** Week 10-11  
**Why Fifth:** Builds on React infrastructure, showcases clean data

### Prerequisites
- [ ] React infrastructure from Phase 4
- [ ] Datastore enabled and populated
- [ ] Analytics showing most-downloaded datasets

### Implementation Steps

#### 5.1 Visualization Plugin Setup
- [ ] Create `ckanext-visualize` extension
- [ ] Integrate charting library (Chart.js or Plotly)
- [ ] Set up resource view plugin interface
- [ ] Configure supported file types (CSV, JSON, Excel)

#### 5.2 Chart Type Implementation
- [ ] Implement chart types:
  - Line chart (time series data)
  - Bar chart (categorical comparisons)
  - Pie chart (proportions)
  - Scatter plot (correlations)
  - Basic map (if geographic data)
- [ ] Auto-detect appropriate chart type
- [ ] Allow user to switch chart types

#### 5.3 Admin Dashboard
- [ ] Build analytics dashboard using Phase 1 data:
  - Portal usage trends
  - Popular datasets
  - User activity heatmap
  - API usage patterns
- [ ] Implement dashboard widgets:
  - Real-time activity feed
  - Download counter
  - Search trends
  - System health indicators
- [ ] Add export to PDF functionality

#### 5.4 Performance & Caching
- [ ] Implement smart data sampling for large datasets
- [ ] Cache generated visualizations
- [ ] Add loading states and progress indicators
- [ ] Optimize for mobile rendering

### Success Criteria
- [ ] 80% of tabular datasets have visualizations
- [ ] < 3 second load time for visualizations
- [ ] 150% increase in time spent on dataset pages
- [ ] Admin dashboard used weekly

---

## ✅ Phase 6: Async/Await for Heavy I/O (Feature 2)
**Timeline:** Week 12-13  
**Why Last:** Performance optimization of existing features

### Prerequisites
- [ ] All features implemented and working
- [ ] Performance bottlenecks identified via analytics
- [ ] Load testing environment set up

### Implementation Steps

#### 6.1 Async Infrastructure
- [ ] Upgrade to Python 3.10+ if needed
- [ ] Add async dependencies:
  - httpx (async HTTP)
  - databases (async SQL)
  - aioredis (async Redis)
- [ ] Configure gunicorn with uvicorn workers
- [ ] Set up async middleware layer

#### 6.2 API Endpoint Migration
- [ ] Prioritize endpoints by impact:
  1. `/api/3/action/package_search`
  2. `/api/3/action/resource_create`
  3. `/api/3/action/datastore_search`
- [ ] For each endpoint:
  - Convert to `async def`
  - Replace blocking calls
  - Add connection pooling
  - Implement timeouts
- [ ] Maintain backward compatibility

#### 6.3 File Upload Optimization
- [ ] Implement streaming multipart uploads
- [ ] Add resumable upload support
- [ ] Background processing for large files
- [ ] Progress reporting via WebSocket/SSE
- [ ] Chunk-based virus scanning

#### 6.4 Database Optimization
- [ ] Implement read replicas for search
- [ ] Add connection pooling
- [ ] Optimize slow queries identified by analytics
- [ ] Implement query result caching
- [ ] Add database query monitoring

### Success Criteria
- [ ] 50% reduction in p95 response time
- [ ] 5x increase in concurrent request handling
- [ ] 90% reduction in timeout errors
- [ ] No increase in error rates

---

## 🎯 Post-Implementation

### Documentation & Training
- [ ] Create user guides for each feature
- [ ] Record video tutorials
- [ ] Build admin documentation
- [ ] Conduct staff training sessions

### Monitoring & Optimization
- [ ] Set up alerting for errors
- [ ] Create performance dashboards
- [ ] Schedule monthly review meetings
- [ ] Plan iterative improvements

### Success Metrics Review
- [ ] Month 1: Baseline vs current comparison
- [ ] Month 3: User satisfaction survey
- [ ] Month 6: ROI analysis presentation
- [ ] Year 1: Feature expansion planning

---

## 📊 Overall Success Criteria

By the end of the implementation:

1. **User Metrics**
   - 50% reduction in support tickets
   - 75% user satisfaction score
   - 40% increase in data usage

2. **Technical Metrics**
   - < 3 second page load (mobile)
   - 99.9% uptime
   - < 200ms API response time

3. **Business Metrics**
   - 3+ success stories published
   - 25% reduction in IT time spent on portal
   - Positive ROI within 6 months 