# ckanext-search-enhanced

**Advanced Search & Discovery enhancements for CKAN Phase 3**

This extension provides enhanced search functionality that leverages Phase 2 metadata improvements and Phase 1 analytics data to deliver a superior search experience.

## ✨ Features

### 🏛️ City-Specific Faceted Search
- **Department Faceting**: Filter by city department (Fire, Police, Public Works, etc.)
- **Update Frequency**: Filter by how often data is updated (daily, weekly, monthly, etc.)
- **Geographic Coverage**: Filter by geographic scope (citywide, neighborhood, address-specific)
- **Data Quality**: Filter by data quality assessment levels
- **Public Access Level**: Filter by data accessibility levels

### 🔗 Related Datasets Recommendations
- **Smart Similarity**: Multi-factor scoring based on department, tags, and user behavior
- **Analytics Integration**: "Users who viewed this also viewed..." recommendations
- **Visual Similarity Indicators**: Color-coded similarity scores
- **Department-Based Suggestions**: Quick links to same-department datasets

### 📊 Analytics-Driven Search
- **Popularity Boosting**: Popular datasets rank higher in search results
- **Search Suggestions**: Auto-complete based on popular search terms
- **Zero-Result Help**: Suggestions when searches return no results
- **Click Tracking**: Track related dataset clicks for continuous improvement

### 🎨 Enhanced Search UI
- **Collapsible Facets**: Organized, toggleable facet sections with icons
- **Clear All Filters**: Easy filter management
- **Mobile Responsive**: Optimized for mobile devices
- **Visual Indicators**: Popularity and quality badges

## 🚀 Installation

1. **Install the extension**:
   ```bash
   cd /usr/src/ckanext
   pip install -e ./ckanext-search-enhanced
   ```

2. **Add to CKAN config**:
   ```ini
   # Add to ckan.plugins
   ckan.plugins = ... search_enhanced analytics
   
   # Optional: Configure facet limits
   search.facets.limit = 100
   search.facets.default = 15
   ```

3. **Update Solr schema** (optional for better performance):
   ```bash
   # Generate schema snippet
   ckan search-enhanced generate-schema >> /path/to/solr/schema.xml
   
   # Restart Solr and reindex
   ckan search-index rebuild
   ```

## 🔧 Configuration

### Basic Configuration

```ini
# Enable the extension
ckan.plugins = ... search_enhanced

# Facet configuration
search.facets.limit = 50
search.facets.default = 10

# Related datasets configuration
ckanext.search_enhanced.related_datasets.limit = 5
ckanext.search_enhanced.related_datasets.similarity_threshold = 0.2

# Analytics integration
ckanext.search_enhanced.analytics.enabled = true
ckanext.search_enhanced.analytics.boost_popular = true
```

### Advanced Configuration

```ini
# Similarity scoring weights (total should equal 1.0)
ckanext.search_enhanced.similarity.department_weight = 0.4
ckanext.search_enhanced.similarity.tags_weight = 0.3
ckanext.search_enhanced.similarity.analytics_weight = 0.2
ckanext.search_enhanced.similarity.organization_weight = 0.1

# Search suggestions
ckanext.search_enhanced.suggestions.enabled = true
ckanext.search_enhanced.suggestions.min_query_length = 2
ckanext.search_enhanced.suggestions.max_suggestions = 5

# Facet display order
ckanext.search_enhanced.facets.priority_order = department organization update_frequency tags
```

## 📚 API Endpoints

### Search Suggestions
```http
GET /api/search/suggestions?q=fire
```

**Response**:
```json
{
  "suggestions": [
    "fire department response times",
    "fire safety inspections"
  ],
  "autocomplete": [
    {
      "id": "fire-dept-stats",
      "name": "fire-dept-stats", 
      "title": "Fire Department Statistics",
      "url": "/dataset/fire-dept-stats"
    }
  ],
  "query": "fire"
}
```

### Related Datasets
```http
GET /api/dataset/{id}/related
```

**Response**:
```json
{
  "dataset_id": "fire-response-times",
  "related_datasets": [
    {
      "id": "fire-station-locations",
      "name": "fire-station-locations",
      "title": "Fire Station Locations",
      "notes": "Geographic locations of all fire stations...",
      "organization": "Fire Department",
      "similarity_score": 0.85,
      "url": "/dataset/fire-station-locations"
    }
  ],
  "count": 1
}
```

## 🎯 Usage Examples

### Template Integration

**Add related datasets to dataset pages**:
```html
<!-- In package/read.html -->
{% include 'package/snippets/related_datasets.html' %}
```

**Use enhanced facets**:
```html
<!-- In search/facets.html -->
{% ckan_extends %}
<!-- Enhanced facets are automatically applied -->
```

### JavaScript Integration

**Search suggestions**:
```javascript
// Auto-complete search box
$('#search-input').autocomplete({
  source: function(request, response) {
    $.get('/api/search/suggestions', {q: request.term})
      .done(function(data) {
        response(data.suggestions);
      });
  }
});
```

**Related datasets API**:
```javascript
// Load related datasets dynamically
fetch(`/api/dataset/${datasetId}/related`)
  .then(response => response.json())
  .then(data => {
    console.log(`Found ${data.count} related datasets`);
    // Render related datasets
  });
```

## 🏗️ Architecture

### Components

1. **SearchEnhancedPlugin**: Main plugin implementing IFacets and IPackageController
2. **SolrSchemaEnhancer**: Utilities for enhancing Solr schema with city metadata
3. **SearchEnhancedController**: API endpoints for suggestions and related datasets
4. **Templates**: Enhanced UI components for facets and related datasets

### Data Flow

```
1. Dataset Creation → Phase 2 Schema → City Metadata
2. Before Indexing → SolrSchemaEnhancer → Enhanced Solr Fields
3. Search Request → Enhanced Facets → Filtered Results
4. Dataset View → Related Datasets → Similarity Calculation
5. User Interaction → Analytics → Improved Recommendations
```

### Integration Points

- **Phase 1 Analytics**: Search patterns, view counts, co-viewing data
- **Phase 2 Schema**: City metadata fields for faceting and similarity
- **CKAN Core**: IFacets, IPackageController, search infrastructure

## 🧪 Testing

### Run Tests
```bash
cd /usr/src/ckanext-search-enhanced
pytest ckanext/search_enhanced/tests/
```

### Test Coverage
- Unit tests for similarity calculations
- Integration tests for faceting
- API endpoint tests
- Template rendering tests
- Analytics integration tests

### Manual Testing
```bash
# Test faceted search
curl "http://localhost:5000/dataset?extras_department=fire"

# Test search suggestions
curl "http://localhost:5000/api/search/suggestions?q=fire"

# Test related datasets
curl "http://localhost:5000/api/dataset/test-dataset/related"
```

## 🔍 Troubleshooting

### Common Issues

**Facets not appearing**:
- Ensure datasets have Phase 2 schema metadata
- Check that plugin is properly loaded
- Verify Solr indexing is working

**Related datasets empty**:
- Ensure analytics extension is installed and working
- Check that datasets have similarity factors (tags, department)
- Verify database connections

**Search suggestions not working**:
- Check analytics database has search query data
- Verify API endpoints are accessible
- Check JavaScript console for errors

### Debug Mode
```ini
# Enable debug logging
ckan.search_enhanced.debug = true

# Log all similarity calculations
ckan.search_enhanced.log_similarity = true
```

## 🚀 Performance

### Optimization Tips

1. **Solr Configuration**:
   - Add specific fields for better faceting performance
   - Use field boosting for relevance
   - Configure proper caching

2. **Analytics Integration**:
   - Use Redis caching for similarity calculations
   - Batch update popularity scores
   - Index view counts for faster queries

3. **Database Optimization**:
   - Add indexes on analytics tables
   - Use connection pooling
   - Cache related dataset calculations

### Benchmarks

With proper configuration:
- **Faceted search**: < 200ms response time
- **Related datasets**: < 500ms calculation time
- **Search suggestions**: < 100ms response time
- **Page load impact**: < 50ms additional overhead

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Run tests: `pytest`
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Create Pull Request

## 📜 License

This project is licensed under the AGPL License - see the LICENSE file for details.

## 🔗 Links

- [CKAN Documentation](https://docs.ckan.org/)
- [Phase 1 Analytics Extension](../ckanext-analytics/)
- [Phase 2 Schema Documentation](../city_dataset_schema.yaml)
- [Issue Tracker](https://github.com/ckan/ckanext-search-enhanced/issues) 