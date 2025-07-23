# CKAN Modernization - 7 Day Sprint Timeline

## Quick Start
1. Make the setup script executable: `chmod +x setup_ckan_project.sh`
2. Run it: `./setup_ckan_project.sh`
3. Follow this timeline!

---

## Day 1-2: Legacy System Mastery

### Day 1 Morning (4 hours) ✅ COMPLETE
- [x] Run setup script and verify 1M+ LOC ✅ (LINE_COUNT_PROOF_original.txt confirms 1,061,463 lines)
- [x] Set up development environment ✅ (Monorepo structure created)
- [x] Get CKAN running locally with Docker ✅ (DevContainer with all services running)

**Key AI Prompts:**
```
"Analyze CKAN's architecture: explain how Pylons routes work, where controllers live, how extensions hook in, and the database schema"
```

### Day 1 Afternoon (4 hours) ✅ COMPLETE  
- [x] Map core business logic flows ✅ (Package creation, auth, search flows documented)
- [x] Document extension system ✅ (25+ plugin interfaces, dual Pylons/Flask architecture)
- [x] Identify Pylons-specific pain points ✅ (Global state, deprecated routing, no async support)

**Key AI Prompts:**
```
"Create a visual diagram of CKAN's request flow from URL to response, highlighting Pylons-specific components"
```

**📋 Day 1 Deliverables Created:**
- `docs/Day1_CKAN_Business_Logic_Analysis.md` - Comprehensive architectural analysis
- Mermaid flow diagram showing CKAN's dual routing architecture
- Updated AI prompts log with 4 archaeological dig prompts
- Technical debt assessment and modernization roadmap

### Day 2 Morning (4 hours)
- [x] Define target user: **Small City Open Data Portals** ✅ (Documented in brainlift files)
- [ ] Document current pain points
- [ ] Test existing features as baseline

### Day 2 Afternoon (4 hours)
- [ ] Create architecture modernization plan
- [ ] Set up Git branches for features
- [ ] Document "before" state with screenshots

---

## Day 3-4: Modernization Design & Foundation

### Day 3 Morning (4 hours)
- [ ] **Feature 1**: Docker/Kubernetes setup
- [ ] Create multi-stage Dockerfile
- [ ] Write docker-compose.yml

**Key AI Prompts:**
```
"Create a production-ready Dockerfile for CKAN with Python 3.11, including all dependencies and optimizations"
```

### Day 3 Afternoon (4 hours)
- [ ] **Feature 2**: OAuth2 Authentication foundation
- [ ] Research CKAN's current auth system
- [ ] Plan OAuth2 integration approach

### Day 4 Morning (4 hours)
- [ ] **Feature 3**: API modernization planning
- [ ] Design RESTful/GraphQL endpoints
- [ ] Set up FastAPI alongside Pylons

**Key AI Prompts:**
```
"Show how to run FastAPI alongside Pylons in CKAN, sharing the same database models and authentication"
```

### Day 4 Afternoon (4 hours)
- [ ] Create base modern UI components
- [ ] Set up Tailwind CSS
- [ ] Plan responsive design approach

---

## Day 5-6: Feature Implementation & Integration

### Day 5 Morning (4 hours)
- [ ] **Feature 4**: Async task processing
- [ ] Convert harvest jobs to Celery
- [ ] Add progress tracking

**Key AI Prompts:**
```
"Convert CKAN's synchronous harvest.gather_stage to an async Celery task with progress updates"
```

### Day 5 Afternoon (4 hours)
- [ ] **Feature 5**: Mobile-responsive UI
- [ ] Replace key templates with Tailwind
- [ ] Ensure mobile-first design

### Day 6 Morning (4 hours)
- [ ] **Feature 6**: Real-time notifications
- [ ] Add WebSocket support
- [ ] Create activity stream updates

**Key AI Prompts:**
```
"Add Socket.IO to CKAN for real-time dataset update notifications"
```

### Day 6 Afternoon (4 hours)
- [ ] Integration testing
- [ ] Fix critical bugs
- [ ] Performance optimization

---

## Day 7: Polish & Launch

### Morning (4 hours)
- [ ] Final bug fixes
- [ ] Create deployment documentation
- [ ] Prepare migration guide

### Afternoon (4 hours)
- [ ] Create demo video (before/after)
- [ ] Document all AI prompts used
- [ ] Write final project report
- [ ] Submit! 💕

---

## Daily Checklist
- [ ] Commit code changes regularly
- [ ] Document AI prompts in `ai_prompts_log.md`
- [ ] Take screenshots of progress
- [ ] Test each feature as completed
- [ ] Update project board

## Success Metrics
- ✅ 1M+ LOC verified
- ✅ 6 features implemented
- ✅ Working deployment
- ✅ AI utilization documented
- ✅ Clear value for target users 