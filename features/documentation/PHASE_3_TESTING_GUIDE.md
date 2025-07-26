# Phase 3 Testing Guide: Advanced Search & Discovery

**Status:** Phase 3 Complete - Testing Required  
**Features:** City-specific faceted search, related datasets, enhanced search UI, API endpoints  
**Test Duration:** ~20 minutes  

---

## 🎯 **What We're Testing**

**Phase 3 implements:**
- ✅ **Enhanced Search Backend**: Solr schema enhancement with city metadata fields
- ✅ **City-Specific Faceting**: 6 new facets based on Phase 2 schema + enhanced UI  
- ✅ **Related Datasets Intelligence**: Multi-factor similarity with analytics integration
- ✅ **Search UI Enhancements**: Modern responsive interface with suggestions API
- ✅ **API Infrastructure**: RESTful endpoints for suggestions and related datasets

---

## 🔧 **Pre-Test Setup**

### **1. Verify Services and Data**
```bash
# Ensure you're in the main CKAN-Fork directory
cd /Users/trevoralpert/Desktop/GAUNTLET_AI/Project_6/CKAN-Fork

# Services should be running from Phase 2 testing
docker-compose -f docker-compose.arm64.yml ps

# Verify search_enhanced plugin is active
docker-compose -f docker-compose.arm64.yml exec ckan bash
ckan --config=/usr/src/CKAN-Modernization-20250721/ckan-monorepo/ckan/demo.ini plugins list | grep search_enhanced
```

### **2. Create Test Datasets (If Needed)**
```bash
# You need at least 3-5 datasets with city schema for proper testing
# Create via web interface or CLI if none exist
```

---

## 🔍 **Test 1: City-Specific Faceted Search**

### **Objective:** Verify enhanced search facets appear and function correctly

### **Steps:**
1. **Navigate to dataset search:** `http://localhost:5000/dataset`
2. **Examine left sidebar for facets**

### **Expected Facets (Must Appear):**

#### **✅ City-Specific Facets:**
- 🏛️ **Department**
  - Should show: Fire, Police, Public Works, Finance, etc.
  - Each with dataset count: "Fire Department (3)"
- 📅 **Update Frequency**  
  - Should show: Real-time, Daily, Weekly, Monthly, etc.
  - With counts: "Daily (5)", "Weekly (2)"
- 🗺️ **Geographic Coverage**
  - Should show: City-wide, Ward/District, Neighborhood, etc.
  - With counts: "City-wide (8)", "Neighborhood (2)"
- 📊 **Data Quality**
  - Should show: High, Medium, Low, Unknown
  - With counts: "High (4)", "Medium (3)"
- 🔒 **Access Level**
  - Should show: Public, Restricted, Confidential  
  - With counts: "Public (10)", "Restricted (1)"

#### **✅ Enhanced Standard Facets:**
- 🏢 **Organization** (enhanced display)
- 🏷️ **Tags** (with improved UI)
- 📄 **Format** (CSV, JSON, etc.)
- ⚖️ **License** (with icons)

### **Facet Functionality Testing:**
1. **Single facet selection:**
   - Click "Fire Department" → Should filter to fire datasets only
   - URL should update: `/dataset?extras_department=fire`
   - Result count should decrease appropriately

2. **Multiple facet combination:**
   - Select "Fire Department" + "Daily" update frequency
   - Should show intersection of both filters
   - Results should match both criteria

3. **Facet UI features:**
   - Look for collapsible sections with icons
   - "Clear all filters" button should appear when filters active
   - Mobile-responsive behavior (resize window)

### **✅ Pass Criteria:**
- [ ] All 6 city-specific facets appear
- [ ] Facets show accurate dataset counts
- [ ] Single facet filtering works correctly
- [ ] Multiple facets combine properly
- [ ] "Clear all filters" functionality works
- [ ] Mobile-responsive design functions
- [ ] URL updates reflect filter state

---

## 🔗 **Test 2: Related Datasets Recommendations**

### **Objective:** Verify intelligent dataset recommendations based on similarity

### **Steps:**
1. **Navigate to any dataset detail page**
2. **Look for "Related Datasets" section** (usually bottom or right sidebar)

### **Expected Related Datasets Display:**

#### **✅ Similarity Indicators:**
- 🟢 **High Similarity** (same department + shared tags)
- 🟡 **Medium Similarity** (same department OR shared tags)  
- 🔴 **Low Similarity** (same organization or co-viewed)

#### **✅ Analytics Integration:**
- 🔥 **Popular** badge (datasets with high view counts)
- ⚡ **Active** badge (recently updated datasets)
- 👥 **"Users who viewed this also viewed..."** recommendations

#### **✅ Department Quick Links:**
- 🏛️ **"See all from Fire Department"** links
- Direct navigation to department-filtered search results

### **Related Datasets Algorithm Testing:**
1. **Department similarity (40% weight):**
   - View a Fire Department dataset
   - Related should prioritize other Fire datasets

2. **Tag similarity (30% weight):**
   - View dataset tagged "emergency", "response"  
   - Related should show datasets with similar tags

3. **Analytics co-viewing (20% weight):**
   - Requires analytics data from Phase 1
   - Popular combinations should appear higher

4. **Organization similarity (10% weight):**
   - Same organization datasets should appear

### **✅ Pass Criteria:**
- [ ] Related datasets section appears on dataset pages
- [ ] Shows 3-5 related datasets with similarity scores
- [ ] Color-coded similarity levels work correctly
- [ ] Analytics-based popularity badges appear
- [ ] Department quick links function properly
- [ ] Click tracking works (check analytics)

---

## 🚀 **Test 3: Search Suggestions & Enhanced UI**

### **Objective:** Verify search experience improvements and API functionality

### **Search Suggestions API Testing:**
```bash
# Test search suggestions endpoint
curl "http://localhost:5000/api/search/suggestions?q=fire" -H "Accept: application/json"

# Expected response:
{
  "suggestions": [
    {"title": "Fire Department Response Times", "score": 0.95},
    {"title": "Fire Safety Inspections", "score": 0.87},
    {"title": "Emergency Fire Incidents", "score": 0.83}
  ],
  "total": 3
}

# Test related datasets API
curl "http://localhost:5000/api/dataset/{dataset-id}/related" -H "Accept: application/json"

# Expected response:
{
  "related": [
    {
      "id": "dataset-id-2",
      "title": "Related Dataset",
      "similarity_score": 0.85,
      "similarity_level": "high",
      "badges": ["popular"],
      "department": "fire"
    }
  ],
  "total": 5
}
```

### **Search UI Enhancement Testing:**
1. **Search suggestions (if implemented):**
   - Start typing in search box
   - Should show dropdown with suggestions
   - Click suggestion should execute search

2. **Zero-result search handling:**
   - Search for nonsense term: "xyzabc123"
   - Should show "No results found" with suggestions
   - Should offer alternative search terms

3. **Enhanced search results:**
   - Search results should show popularity indicators
   - Department badges should appear
   - Enhanced result snippets with metadata

4. **Mobile-responsive search:**
   - Test on mobile viewport
   - Touch-optimized filter controls
   - Collapsible facet sections

### **Search Backend Testing:**
```bash
# Inside CKAN container, test search enhancements
ckan --config=demo.ini search-enhanced status

# Test field boosting (should prioritize title matches)
ckan --config=demo.ini search-enhanced test-boosting "fire department"

# Verify analytics integration in search
ckan --config=demo.ini analytics stats --search-terms
```

### **✅ Pass Criteria:**
- [ ] Search suggestions API returns JSON responses
- [ ] Related datasets API functions correctly
- [ ] Zero-result searches show helpful suggestions
- [ ] Search results include popularity indicators
- [ ] Mobile search interface works properly
- [ ] Field boosting prioritizes relevant results

---

## 📊 **Test 4: Search Analytics Integration**

### **Objective:** Verify Phase 1 analytics data enhances search experience

### **Analytics-Driven Features Testing:**
1. **Popular dataset boosting:**
   - Datasets with high view counts should rank higher
   - Search for general terms, popular datasets should appear first

2. **Search term suggestions:**
   - Common search terms should appear in suggestions
   - Based on analytics data from Phase 1

3. **Related datasets co-viewing:**
   - "Users who viewed X also viewed Y" recommendations
   - Based on session analytics data

### **Analytics Integration Commands:**
```bash
# Check search analytics data
ckan --config=demo.ini analytics stats --search-terms --days 30

# Expected output showing popular search terms:
# Top Search Terms (Last 30 Days):
# 1. "fire department" - 45 searches
# 2. "police reports" - 32 searches  
# 3. "budget data" - 28 searches

# Test analytics-driven search ranking
ckan --config=demo.ini search-enhanced analytics-boost --query "emergency"
```

### **✅ Pass Criteria:**
- [ ] Popular datasets appear higher in search results
- [ ] Search suggestions based on analytics data
- [ ] Co-viewing recommendations work correctly
- [ ] Analytics data properly influences search ranking

---

## 🌐 **Test 5: API Infrastructure & Performance**

### **Objective:** Verify API endpoints and performance requirements

### **API Endpoint Testing:**
```bash
# Test all Phase 3 API endpoints
echo "Testing Search Suggestions API..."
curl -w "%{time_total}s\n" "http://localhost:5000/api/search/suggestions?q=fire"

echo "Testing Related Datasets API..."
curl -w "%{time_total}s\n" "http://localhost:5000/api/dataset/sample-dataset/related"

echo "Testing Enhanced Search API..."
curl -w "%{time_total}s\n" "http://localhost:5000/api/3/action/package_search?q=fire&facet.field=extras_department"

# All responses should be < 200ms (Phase 3 requirement)
```

### **Performance Testing:**
```bash
# Test search response times
echo "Performance testing search endpoints..."
for i in {1..10}; do
  curl -w "%{time_total}s " -s -o /dev/null "http://localhost:5000/dataset?q=fire"
done
echo ""

# Average should be under 200ms
```

### **Load Testing (Optional):**
```bash
# Test concurrent search requests
echo "Testing concurrent search performance..."
ab -n 100 -c 10 "http://localhost:5000/dataset?q=fire"

# Check for errors and response times
```

### **✅ Pass Criteria:**
- [ ] All API endpoints respond within 200ms
- [ ] JSON responses are well-formed
- [ ] No errors under normal load
- [ ] Concurrent requests handled properly

---

## 🚨 **Troubleshooting Common Issues**

### **Facets Not Appearing:**
```bash
# Check Solr indexing
curl "http://localhost:8983/solr/ckan/select?q=*:*&rows=0&facet=true&facet.field=extras_department"

# Reindex datasets if needed
ckan --config=demo.ini search-index rebuild

# Check plugin loading
ckan --config=demo.ini plugins list | grep search_enhanced
```

### **Related Datasets Not Showing:**
```bash
# Need minimum dataset count for recommendations
ckan --config=demo.ini dataset list | wc -l

# Check similarity calculation
ckan --config=demo.ini search-enhanced test-similarity [dataset-id]

# Verify analytics data exists
ckan --config=demo.ini analytics stats --datasets
```

### **API Endpoints Not Working:**
```bash
# Check blueprint registration
ckan --config=demo.ini routes list | grep api

# Verify plugin configuration
ckan --config=demo.ini config-tool dump | grep search_enhanced

# Test plugin activation
ckan --config=demo.ini search-enhanced health-check
```

### **Search Performance Issues:**
```bash
# Check Solr performance
curl "http://localhost:8983/solr/admin/cores?action=STATUS"

# Optimize Solr index
curl "http://localhost:8983/solr/ckan/update?optimize=true"

# Check database query performance
ckan --config=demo.ini db analyze
```

---

## 📝 **Test Results Documentation**

### **Create Detailed Test Report:**
```bash
# Generate comprehensive Phase 3 test report
cat > phase3_test_results.md << EOF
# Phase 3 Test Results - $(date)

## Faceted Search Test
- [ ] City-specific facets displayed: ✅/❌
- [ ] Facet filtering functional: ✅/❌
- [ ] Multiple facets combine properly: ✅/❌
- [ ] Mobile-responsive design: ✅/❌

## Related Datasets Test
- [ ] Related section appears: ✅/❌
- [ ] Similarity scoring works: ✅/❌
- [ ] Analytics integration active: ✅/❌
- [ ] Department quick links functional: ✅/❌

## Search Enhancement Test
- [ ] Search suggestions API working: ✅/❌
- [ ] Zero-result handling functional: ✅/❌
- [ ] Enhanced result display: ✅/❌
- [ ] Mobile search optimized: ✅/❌

## Analytics Integration Test
- [ ] Popular dataset boosting: ✅/❌
- [ ] Search term suggestions: ✅/❌
- [ ] Co-viewing recommendations: ✅/❌

## API & Performance Test
- [ ] All endpoints respond < 200ms: ✅/❌
- [ ] JSON responses well-formed: ✅/❌
- [ ] Concurrent requests handled: ✅/❌

## Overall Phase 3 Status: ✅ PASS / ❌ FAIL

### Performance Metrics:
- Average search response time: ___ms
- Facet filter response time: ___ms
- Related datasets load time: ___ms
- API endpoint response time: ___ms

### Issues Found:
[List any problems encountered]

### Integration Status:
- [ ] Phase 1 analytics feeding Phase 3: ✅/❌
- [ ] Phase 2 schema powering Phase 3 facets: ✅/❌
- [ ] All three phases working harmoniously: ✅/❌

### Next Steps:
[Actions needed before Phase 4 development]
EOF
```

---

## ✅ **Success Criteria Summary**

**Phase 3 PASSES if:**
- [x] City-specific facets appear and filter correctly (6 new facets)
- [x] Related datasets show with intelligent similarity scoring
- [x] Search suggestions API responds within 200ms
- [x] Analytics data enhances search experience
- [x] Mobile-responsive search interface functions properly
- [x] All API endpoints return well-formed JSON responses
- [x] Search performance meets < 200ms requirement
- [x] Integration with Phase 1 analytics and Phase 2 schema confirmed

**Ready for Phase 4 development when all criteria are met!**

---

## 🚀 **Next Phase Preview**

Once Phase 3 testing passes, **Phase 4: Mobile-First UX & React Widgets** will build upon:
- ✅ **API Infrastructure** (from Phase 3 testing)
- ✅ **Clean Metadata** (from Phase 2 schema)  
- ✅ **Analytics Foundation** (from Phase 1 tracking)

The solid search and metadata foundation enables rich React component development! 