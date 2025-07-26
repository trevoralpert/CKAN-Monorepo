# Phase 2 Testing Guide: Metadata Quality & Schema Enforcement

**Status:** Phase 2 Complete - Testing Required  
**Features:** City dataset schema, validation system, audit tools, AI assistance  
**Test Duration:** ~15 minutes  

---

## 🎯 **What We're Testing**

**Phase 2 implements:**
- ✅ **City Dataset Schema**: 26 custom fields for municipal data
- ✅ **Validation System**: 7 custom validators with friendly error messages  
- ✅ **Metadata Audit**: Quality scoring and improvement recommendations
- ✅ **AI Assistance**: Automated metadata enhancement suggestions

---

## 🔧 **Pre-Test Setup**

### **1. Verify Docker Services**
```bash
# Ensure you're in the main CKAN-Fork directory
cd /Users/trevoralpert/Desktop/GAUNTLET_AI/Project_6/CKAN-Fork

# Start all services
docker-compose -f docker-compose.arm64.yml up -d

# Wait 30 seconds for services to initialize
# Check services are running
docker-compose -f docker-compose.arm64.yml ps
```

### **2. Check Plugin Configuration**
```bash
# Access CKAN container
docker-compose -f docker-compose.arm64.yml exec ckan bash

# Verify plugins are loaded
ckan --config=/usr/src/CKAN-Modernization-20250721/ckan-monorepo/ckan/demo.ini plugins list

# Expected: analytics, search_enhanced, scheming_datasets
```

---

## 📋 **Test 1: City Dataset Schema Interface**

### **Objective:** Verify city-specific form fields appear correctly

### **Steps:**
1. **Open CKAN in browser:** `http://localhost:5000`
2. **Create admin account** (if not exists):
   - Click "Register" 
   - Create account with admin privileges
3. **Navigate to:** "Datasets" → "Add Dataset"

### **Expected Results - Form Fields:**

#### **✅ Core City Fields (Must Appear):**
- 🏛️ **City Department** (Required dropdown)
  - Options: Fire, Police, Public Works, Finance, Parks & Recreation, etc.
- 👤 **Department Contact Person** (Required text)
- 📧 **Contact Email** (Required, email validation)
- 📅 **Update Frequency** (Required dropdown)
  - Options: Real-time, Daily, Weekly, Monthly, etc.
- 🗺️ **Geographic Coverage** (Required dropdown)  
  - Options: City-wide, Ward/District, Neighborhood, etc.

#### **✅ Data Quality Fields:**
- 📊 **Data Quality Assessment** (Dropdown)
  - Options: High, Medium, Low, Unknown
- 🗓️ **Last Updated Date** (Required date picker)
- 🗓️ **Next Scheduled Update** (Optional date picker)

#### **✅ Legal/Access Fields:**
- 🔒 **Public Access Level** (Required dropdown)
  - Options: Public, Restricted, Confidential
- 📝 **Privacy/Sensitivity Notes** (Markdown text area)
- ⚖️ **Legal/Compliance Requirements** (Markdown text area)

#### **✅ Additional City Fields:**
- 🔄 **Collection Method** (Dropdown)
  - Options: Automated, Manual Entry, Survey, etc.
- 💡 **Public Value/Use Cases** (Markdown text area)
- 🕐 **Time Period Start/End** (Date pickers)

### **Validation Testing:**
1. **Try to submit empty form** → Should show required field errors
2. **Enter invalid email** → Should show email format error  
3. **Leave department blank** → Should require selection
4. **Test help text** → Hover/click should show guidance

### **✅ Pass Criteria:**
- [ ] All 26+ city-specific fields appear
- [ ] Required field validation works
- [ ] Email validation functions
- [ ] Help text displays correctly
- [ ] Form submissions work with valid data

---

## 🔍 **Test 2: Metadata Audit System**

### **Objective:** Verify data quality analysis functionality

### **Steps:**
1. **Access CKAN container:**
   ```bash
   docker-compose -f docker-compose.arm64.yml exec ckan bash
   cd /usr/src/CKAN-Modernization-20250721/ckan-monorepo/ckan
   ```

2. **Run metadata audit:**
   ```bash
   # Full audit command
   ckan --config=demo.ini analytics audit-metadata
   ```

### **Expected Output:**
```
🔍 Starting Metadata Quality Audit...
==================================================
📊 Found X datasets to analyze

🔎 Auditing dataset 1/X: [Dataset Title]...
🔎 Auditing dataset 2/X: [Dataset Title]...

📋 AUDIT SUMMARY:
- Total datasets: X
- Average quality score: XX.X/100
- Total issues found: XX
- Issue breakdown:
  * Missing required fields: X
  * Invalid email formats: X  
  * Incomplete descriptions: X
  * Missing contact info: X

💡 TOP RECOMMENDATIONS:
1. Add department contact for X datasets
2. Improve descriptions for X datasets  
3. Add geographic coverage for X datasets
```

### **CLI Audit Features to Test:**
```bash
# Test specific audit functions
ckan --config=demo.ini analytics audit-metadata --format=json > audit_results.json
ckan --config=demo.ini analytics audit-metadata --department=fire
ckan --config=demo.ini analytics audit-metadata --export-csv
```

### **✅ Pass Criteria:**
- [ ] Audit runs without errors
- [ ] Shows dataset count and quality scores
- [ ] Identifies specific metadata issues
- [ ] Provides actionable recommendations
- [ ] Supports JSON export and filtering

---

## 🤖 **Test 3: AI-Assisted Metadata Enhancement**

### **Objective:** Verify AI suggestion system functionality

### **Steps:**
1. **Test AI suggestion API:**
   ```bash
   # Inside CKAN container
   ckan --config=demo.ini analytics suggest-metadata [dataset-id]
   ```

2. **Test AI endpoints via curl:**
   ```bash
   # Test tag suggestions
   curl -X POST "http://localhost:5000/api/ai/suggest-tags" \
        -H "Content-Type: application/json" \
        -d '{"description": "Fire department response times for emergency calls"}'

   # Test department classification  
   curl -X POST "http://localhost:5000/api/ai/classify-department" \
        -H "Content-Type: application/json" \
        -d '{"title": "Police Incident Reports", "description": "Daily crime statistics"}'
   ```

### **Expected Results:**
- **Tag Suggestions:** Returns relevant tags based on content
- **Department Classification:** Correctly identifies city department
- **Quality Assessment:** Provides improvement recommendations

### **✅ Pass Criteria:**
- [ ] AI suggestion commands execute successfully  
- [ ] API endpoints return JSON responses
- [ ] Suggestions are relevant and accurate
- [ ] Multiple AI providers configured (Mock/OpenAI)

---

## 📊 **Test 4: Schema Integration Verification**

### **Objective:** Confirm schema is properly integrated with CKAN

### **Steps:**
1. **Check schema registration:**
   ```bash
   # Inside CKAN container
   ckan --config=demo.ini scheming dataset-types
   # Should show: city-dataset
   
   ckan --config=demo.ini scheming dataset-schema city-dataset
   # Should display full schema definition
   ```

2. **Test dataset creation with city schema:**
   - Create dataset via web interface
   - Select "city-dataset" type if prompted
   - Fill in all city-specific fields  
   - Save and verify data persists

3. **Verify database storage:**
   ```bash
   # Check that custom fields are stored
   ckan --config=demo.ini dataset show [dataset-name]
   # Should show city-specific fields in extras
   ```

### **✅ Pass Criteria:**
- [ ] Schema properly registered with CKAN
- [ ] City dataset type available
- [ ] Custom fields save to database correctly
- [ ] Field data displays on dataset pages

---

## 🚨 **Troubleshooting Common Issues**

### **Schema Fields Not Showing:**
```bash
# Check plugin loading
ckan --config=demo.ini plugins list | grep scheming

# Verify schema file path
ls -la /usr/src/CKAN-Modernization-20250721/ckan-monorepo/ckan/extensions/ckanext-scheming/ckanext/scheming/city_dataset_schema.yaml

# Restart CKAN after changes
docker-compose -f docker-compose.arm64.yml restart ckan
```

### **Validation Errors Not Working:**
```bash
# Check validator registration
ckan --config=demo.ini config-tool dump | grep validator

# Test email validator directly
python -c "
from ckan.plugins.toolkit import Invalid
from ckan.lib.navl.validators import email_validator
try:
    email_validator('invalid-email')
except Invalid as e:
    print('Validation working:', e)
"
```

### **Audit System Issues:**
```bash
# Check analytics plugin status
ckan --config=demo.ini analytics health-check

# Verify database tables exist
ckan --config=demo.ini analytics init-db --help

# Test with verbose output
ckan --config=demo.ini analytics audit-metadata --verbose
```

---

## 📝 **Test Results Documentation**

### **Create Test Report:**
```bash
# Generate comprehensive test report
cat > phase2_test_results.md << EOF
# Phase 2 Test Results - $(date)

## Schema Interface Test
- [ ] City fields displayed: ✅/❌
- [ ] Validation working: ✅/❌  
- [ ] Help text showing: ✅/❌

## Audit System Test  
- [ ] Audit runs successfully: ✅/❌
- [ ] Quality scores generated: ✅/❌
- [ ] Recommendations provided: ✅/❌

## AI Enhancement Test
- [ ] AI suggestions working: ✅/❌
- [ ] API endpoints responding: ✅/❌  
- [ ] Multiple providers configured: ✅/❌

## Integration Test
- [ ] Schema registered: ✅/❌
- [ ] Data saves correctly: ✅/❌
- [ ] Fields display properly: ✅/❌

## Overall Phase 2 Status: ✅ PASS / ❌ FAIL

### Issues Found:
[List any problems encountered]

### Next Steps:
[Actions needed before Phase 3 testing]
EOF
```

---

## ✅ **Success Criteria Summary**

**Phase 2 PASSES if:**
- [x] City dataset form shows 26+ custom fields with proper validation
- [x] Metadata audit system runs and provides quality scores  
- [x] AI suggestion system responds with relevant recommendations
- [x] Schema integration allows proper data storage and retrieval
- [x] All CLI commands execute without errors
- [x] Web interface displays city-specific fields correctly

**Ready for Phase 3 testing when all criteria are met!** 