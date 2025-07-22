# Day 1: Architecture Archaeology Field Guide

*A systematic approach to excavating business logic from legacy codebases using AI as your archaeological toolkit*

## The Archaeologist's Mindset

Before touching any code, remember: You're not here to judge the ancient builders. You're here to understand why they built what they built, with the tools they had, under the constraints they faced.

Legacy code is organizational memory crystallized into syntax.

## Phase 1: Survey the Site (Hours 1-2)

### 1.1 Establish Timeline & Context
**First AI Prompt - The Historical Context:**
```
"I'm analyzing CKAN, a Python data portal system. Based on file headers, commit history, and framework choices, help me understand:
1. When was this system originally architected?
2. What were the popular patterns/frameworks of that era?
3. What problems were developers solving for in [2006-2010]?
4. What constraints did they face that we don't today?"
```

**What you're looking for:**
- Technology choices that seem "wrong" today but were best practices then
- Patterns that reveal organizational structure (who built this?)
- Comments that explain "why" not "what"

### 1.2 Map the Strata (Technology Layers)
**Second AI Prompt - The Stack Archaeology:**
```
"Analyze this requirements.txt/setup.py and help me identify:
1. Which dependencies are original vs added later?
2. Which versions suggest 'frozen in time' components?
3. What does Pylons==1.0.2 tell us about the architectural decisions?
4. Which dependencies are doing work that modern Python handles natively?"
```

**Create a timeline visualization:**
```
2006: Pylons 0.8 (cutting edge!)
2008: SQLAlchemy 0.4 (ORM was controversial)  
2010: Pylons 1.0 (peak framework)
2011: Pyramid announced (Pylons deprecated)
2012-2024: Maintenance mode (survival architecture)
```

## Phase 2: Excavate Core Patterns (Hours 2-4)

### 2.1 The Controller Archaeological Dig
**Third AI Prompt - Understanding Pylons MVC:**
```python
# Paste a typical controller like package.py
"This is a Pylons controller from CKAN. Help me understand:
1. How does Pylons routing work vs modern Flask/FastAPI?
2. What's the purpose of these class inheritance patterns?
3. Why are there so many decorators?
4. Map the request flow from URL to response"
```

**Document the artifacts:**
- Base controller patterns (what do all controllers inherit?)
- Authentication/authorization decorators
- Data validation approaches
- Template rendering logic

### 2.2 The Model Excavation
**Fourth AI Prompt - Data Architecture:**
```python
# Paste core models like package.py, user.py
"Analyze these SQLAlchemy 0.x models and explain:
1. What business rules are embedded in the model layer?
2. How does this old SQLAlchemy differ from modern versions?
3. What relationships reveal core business logic?
4. Which fields suggest evolutionary changes?"
```

**Create an entity relationship archaeology map:**
- Original entities (core business)
- Added entities (feature evolution)  
- Deprecated but present (organizational debt)

### 2.3 The Template Tomb
**Fifth AI Prompt - UI Logic Patterns:**
```
# Paste sample Genshi/Jinja templates
"These templates from CKAN show old-style patterns. Identify:
1. What business logic is hiding in templates? (Anti-pattern!)
2. Which templates are clearly 'bandaid' fixes?
3. How is mobile responsiveness handled? (Spoiler: it's not)
4. What JavaScript patterns reveal about the era?"
```

## Phase 3: Decode the Rituals (Hours 4-6)

### 3.1 The Configuration Ceremonies
**Sixth AI Prompt - Understanding Deployment:**
```ini
# Paste production.ini / development.ini
"This Pylons configuration reveals deployment patterns. Explain:
1. What does this tell us about the original deployment environment?
2. Which settings suggest organizational policies?
3. What security patterns were standard in 2010?
4. How would this map to modern 12-factor apps?"
```

### 3.2 The Extension Invocations  
**Seventh AI Prompt - Plugin Architecture:**
```python
# Paste IPlugin interfaces and sample extensions
"CKAN has a plugin system. Analyze:
1. Why did they build their own plugin architecture?
2. What were they optimizing for? (Flexibility vs performance)
3. How does this compare to modern plugin patterns?
4. What does this reveal about their users' needs?"
```

## Phase 4: Reconstruct the Civilization (Hours 6-8)

### 4.1 The Grand Synthesis
**Eighth AI Prompt - The Meta-Analysis:**
```
"Based on everything we've discovered about CKAN:
1. Create a 'day in the life' of a 2010 CKAN developer
2. What organizational structure does this codebase imply?
3. What were the top 3 design priorities?
4. What patterns would they do differently with hindsight?"
```

### 4.2 The Modernization Map
**Ninth AI Prompt - Bridge Building:**
```
"Given CKAN's architecture and my modernization goals:
1. What can be strangled vs what must be preserved?
2. Which patterns translate directly to FastAPI?
3. Where will the bodies be buried? (Hidden complexity)
4. What's the minimum viable modernization path?"
```

## The Archaeological Report Template

By end of Day 1, document:

### 1. Historical Context
- Original problem space (2006-2010 open data movement)
- Technology constraints of the era
- Organizational patterns revealed in code

### 2. Architecture Map
```
URL Route → Pylons Controller → Auth Decorator → 
Business Logic → SQLAlchemy 0.x → PostgreSQL
                     ↓
             Template Rendering → JSON/HTML Response
```

### 3. Critical Business Logic Locations
- `/ckan/controllers/` - Request handling patterns
- `/ckan/model/` - Core domain logic
- `/ckan/lib/` - Where the bodies are buried
- `/ckan/plugins/` - Extension points

### 4. Modernization Opportunities
- **Quick Wins**: Static assets, JavaScript, CSS
- **Medium Effort**: API endpoints, mobile templates
- **Deep Work**: Async conversion, framework migration

### 5. Organizational Insights
- Small team indicators (god objects, do-everything controllers)
- Government constraints (audit trails, permissions complexity)
- Academic origins (metadata overengineering)

## The AI Archaeology Toolkit

### Power Prompts for Legacy Analysis:
1. **The Time Machine**: "What would a 2010 developer have done differently with 2024 tools?"
2. **The Rosetta Stone**: "Translate this Pylons pattern to modern FastAPI"
3. **The X-Ray**: "What business logic is hidden in this spaghetti code?"
4. **The Carbon Dating**: "Based on code style, when was this section last meaningfully updated?"

### Anti-Patterns to Document:
- Business logic in templates
- God objects doing everything
- Permissions checks everywhere
- Manual SQL in controllers
- Global state mutations

## Day 1 Success Metrics

✅ You can explain CKAN's architecture to a new developer in 5 minutes
✅ You understand why every major design decision was made
✅ You've identified the 20% of code that does 80% of the work
✅ You know which corpses to not disturb
✅ You have a clear modernization attack plan

---

*Remember: Legacy systems aren't poorly designed - they're designed for constraints we no longer have. Your job isn't to judge the ancestors, but to honor their work while adapting it for modern needs.*

*The best modernization preserves accumulated business wisdom while shedding outdated technical constraints.* 