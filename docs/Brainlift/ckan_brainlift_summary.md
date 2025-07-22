# Brainlift: CKAN Modernization for Small Cities

## Arena
**AI-assisted legacy modernization for real-world enterprise systems.**  
Focusing on CKAN—a Pylons-based legacy system still used in 100+ government portals—and targeting small U.S. cities (pop. 50k–500k) for high-impact modernization.

## Curated Sources (Verified Insights)

### 1. Most legacy modernization efforts benefit from context-aware strategy.
- **Source**: Martin Fowler’s [Strangler Fig pattern](https://martinfowler.com/bliki/StranglerFigApplication.html)
- **Insight**: Fowler advocates *gradual modernization*, which requires deep domain understanding. CKAN's architecture is compatible with this approach, making it viable for refactor-over-rewrite strategy.

### 2. CKAN is still used in hundreds of government portals
- **Source**: CKAN’s [official deployment showcase](https://ckan.org/about/deployed/), GitHub, and public portals like [data.gov](https://catalog.data.gov/) and [open.canada.ca](https://open.canada.ca/data/en/dataset)
- **Insight**: Trust and adoption already exist. Cities don’t need convincing to use CKAN—they need help modernizing it.

### 3. Small cities are resource-constrained but digitally ambitious
- **Source**: National League of Cities (NLC) [2022 Digital Transformation in Cities report](https://www.nlc.org/article/2022/11/03/small-cities-are-prioritizing-digital-transformation/)
- **Insight**: Smaller municipalities are modernizing, but lack the staff for full-stack rewrites. They rely on part-time vendors or overworked IT staff.

### 4. Pylons (CKAN's framework) is deprecated, but still in production
- **Source**: [Pylons project site](https://pylonsproject.org/), [CKAN source code](https://github.com/ckan/ckan)
- **Insight**: This makes CKAN an ideal target for Path 4 ("Deprecated Python Framework Revival")

### 5. Mobile-first usage is growing for civic services
- **Source**: Pew Research [2023 Mobile Fact Sheet](https://www.pewresearch.org/internet/fact-sheet/mobile/)
- **Insight**: Mobile is the primary internet access point for many Americans under 40, reinforcing the need for mobile-first civic portals.

### 6. CKAN extension ecosystem adds complexity but mirrors real enterprise structure
- **Source**: [CKAN GitHub organization](https://github.com/ckan), especially the modular structure across `ckanext-*` repos
- **Insight**: The core repo has ~500K LOC, but total ecosystem exceeds 1.2M LOC. Distributed architecture is common in enterprise, making this more realistic than single-repo Django examples.


## Spiky POVs

### Consensus: Government will never be able to maintain efficient, cutting edge technology.
**Spiky POV**: "The real problem is one person is managing 40+ systems."

### Consensus: Civic tech is entirely outdated and needs an overhaul from scratch.
**Spiky POV**: "With the help of AI we can transform previously used technology to help the lone system managers thrive."

## Modernization Opportunity
**CKAN for Small Cities**
- “Digital transformation” often fails because cities can't upgrade tools they already rely on. A CKAN modernization solves this by preserving trust, reducing retraining cost, and creating mobile-first UX for citizens.

**Top Feature Opportunities:**
1. **Modern OAuth2/SSO login integration**
2. **Mobile-first responsive portal redesign**
3. **Async task runner for data harvesting (modernizing ckanext-harvest)**
4. **API endpoint generation (OpenAPI via DRF/FastAPI)**
5. **Real-time notification dashboard for upload jobs**
6. **Dockerized CI/CD deployment pipeline for IT teams**


## Closing Argument: Why This Project Wins
- ✓ Meets all rubric criteria (1M+ LOC, deprecated Python, clear user segment)
- ✓ Demonstrates AI mastery (modernizing 6 extensions in 7 days demands it)
- ✓ Shows business thinking (actual government pain point, not hypothetical UX fluff)
- ✓ Reflects real enterprise patterns (distributed architecture, integration friction)
- ✓ Creates measurable user impact (faster uploads, mobile access, fewer support tickets)

---
*This isn’t just a good fit for the assignment. It’s a credible prototype for how small city IT departments can modernize CKAN in real life.*

