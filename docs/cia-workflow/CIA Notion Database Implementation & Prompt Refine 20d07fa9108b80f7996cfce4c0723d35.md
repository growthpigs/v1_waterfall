# CIA: Notion Database Implementation & Prompt Refinement Protocol

Prompt Type: ADMIN

# CIA: Notion Database Implementation & Prompt Refinement Protocol

## **CURRENT STATUS UPDATE**

**BREAKTHROUGH INTEGRATION:**

- **Notion Forms:** Ultra-minimal intake (Website URL + KPOI LinkedIn + Grok results)
- **N8N Automation:** DataForSEO API + Google Maps API automated
- **Manual Input Optimization:** Front-load Grok research, automate everything else
- **Form-to-Strategy Pipeline:** True "fill form, get complete strategy" system

---

## **NOTION DATABASE STRUCTURE (UPDATED)**

### **Database 1: "CIA System Prompts"**

**Properties:**

```
Name (Title) - Prompt identifier
Phase ID (Select) - Phase 1S, 1A, 1B, 1C, 1D, 1EB, Phase 2S, 2A, 2B, 2EB, etc.
Phase Number (Select) - Phase 1, Phase 2, Phase 3, Phase 4, Phase 5
Prompt Type (Select) - System Prompt, User Prompt, Example Response, Archive Export
Status (Select) - Not Started, In Progress, Complete, Tested
Prompt Text (Long text) - Actual prompt content
API Integration (Checkbox) - Uses external API data
Manual Input Required (Checkbox) - Needs user input
Quality Score (Number) - 1-10 based on Console testing
Last Updated (Date) - Auto-populate
Tags (Multi-select) - Analysis, Data Collection, Export, Strategy, Synthesis

```

### **Database 2: "CIA Client Projects"**

**Properties:**

```
Client Name (Title) - Auto-extracted from website
Project ID (Text) - Auto-generated unique ID
Website URL (URL) - From Notion form
KPOI LinkedIn (URL) - From Notion form
Grok Research (Long text) - From Notion form
Current Phase (Select) - Phase 1, 2, 3, 4, 5, Complete
Status (Select) - Queued, In Progress, Complete, Delivered
Form Submitted (Date) - Auto-populate
Analysis Started (Date) - N8N trigger
Completion Date (Date) - Final delivery
DataForSEO Results (Long text) - API response
Google Maps Reviews (Long text) - API response
Phase Results (Relation to Phase Outputs database)
Master Content Bible (Files) - Final deliverable

```

### **Database 3: "CIA Phase Outputs"**

**Properties:**

```
Output ID (Title) - Auto-generated
Client Project (Relation) - Links to client
Phase Number (Select) - Phase 1, 2, 3, 4, 5
Analysis Type (Select) - Business Intelligence, DNA Research, KPOI, Competitive, SEO, Social, etc.
Output Content (Long text) - Claude analysis results
Archive Data (Long text) - For Master Content Bible
Quality Check (Checkbox) - Human review complete
API Data Used (Long text) - External data sources
Created Date (Date) - Auto-populate

```

---

## **REFINED FORM STRUCTURE (ULTRA-MINIMAL)**

### **Notion Form: "CIA Strategic Intelligence Analysis"**

**Form Description:**
"Complete marketing intelligence analysis in 2 hours. Provide these 3 inputs to start:"

**Fields:**

**1. Company Website URL**

```
Field Type: URL
Required: Yes
Placeholder: "https://yourcompany.com"
Help Text: "We'll analyze everything from your website automatically"

```

**2. Key Person LinkedIn URL**

```
Field Type: URL
Required: Yes
Placeholder: "https://linkedin.com/in/founder-name"
Help Text: "Usually founder/CEO - we'll build their authority profile"

```

**3. X/Twitter Research Results**

```
Field Type: Long text
Required: Yes
Help Text: "First, copy this prompt to Grok X.com:"

GROK PROMPT:
"Analyze X/Twitter conversations about this industry. Search for problems, complaints, recommendations, and trending topics. Extract customer language patterns, pain points, viral content opportunities, and authority gaps. Focus on authentic customer voice and emotional triggers. Provide specific examples and exact phrases."

"Then paste the results here:"

```

**Submit Button:** "Start CIA Analysis"

---

## **PROMPT REFINEMENT PROTOCOL**

### **Phase 1: System Prompt Optimization**

**Current Focus:** Refining Phase 1S (Business Intelligence Analyst)

**Quality Criteria:**

- ✅ Integrates all strategic frameworks (Priestley, Alisha, Eugene Schwartz)
- ✅ References form inputs (Website URL, LinkedIn, Grok data)
- ✅ Sets up API data expectations (DataForSEO, Google Maps)
- ✅ Maintains customer language preservation
- ✅ Drama prioritization integration (1-10 scale)

**Testing Process:**

1. **Console Testing:** Use real websites for validation
2. **Output Comparison:** Manual vs. automated quality
3. **Framework Integration:** Ensure all methodologies applied
4. **API Data Integration:** Prepare for N8N automation
5. **Quality Scoring:** Rate 1-10 based on strategic depth

### **Example Response Requirements**

Each prompt needs **X-bis** example response showing:

- Strategic depth and framework integration
- Customer language pattern preservation
- Drama prioritization scoring
- Competitive intelligence insights
- Authority building opportunities
- Implementation-ready outputs

---

## **N8N AUTOMATION INTEGRATION POINTS**

### **API Calls Triggered by Form Submission:**

**Immediate N8N Actions:**

1. **Website Analysis:** Extract company data, meta information, content themes
2. **DataForSEO API:** Use Phase 1 keywords for comprehensive SEO intelligence
3. **Google Maps API:** Company reviews and testimonial data
4. **LinkedIn Analysis:** KPOI profile data and authority markers

**Sequential Phase Execution:**

1. **Phase 1:** Business intelligence + API data integration
2. **Phase 2:** SEO/Social intelligence (automated with API data)
3. **Phase 3:** Strategic synthesis + Grok trend integration
4. **Phase 4:** Golden Hippo offer development
5. **Phase 5:** Master Content Bible creation

### **Quality Control Integration:**

**Automated Checks:**

- Customer language pattern preservation
- Framework integration completeness
- Drama prioritization scoring consistency
- Competitive differentiation identification

**Human Review Points:**

- Final Master Content Bible quality
- Client-specific strategic recommendations
- Authority building opportunity prioritization

---

## **IMMEDIATE IMPLEMENTATION STEPS**

### **Week 1 Actions:**

**Day 1-2: Notion Setup**

- [ ]  Create all three databases with proper relationships
- [ ]  Build Notion form with ultra-minimal fields
- [ ]  Test form submission and data capture

**Day 3-4: Prompt Refinement**

- [ ]  Refine Phase 1S system prompt for N8N integration
- [ ]  Create Phase 1A-D user prompts with API data expectations
- [ ]  Generate example responses (1A-bis, 1B-bis, etc.)

**Day 5-7: N8N Blueprint**

- [ ]  Design complete workflow from form to deliverable
- [ ]  Test API integrations (DataForSEO, Google Maps)
- [ ]  Create error handling and quality control protocols

### **Success Criteria:**

**Form Functionality:**

- ✅ 3-field form captures all required inputs
- ✅ Grok prompt generates quality research data
- ✅ Form submission triggers N8N workflow

**Prompt Quality:**

- ✅ All prompts integrate strategic frameworks
- ✅ Example responses demonstrate expected quality
- ✅ API data integration points clearly defined

**Automation Readiness:**

- ✅ N8N workflow blueprint complete
- ✅ API credentials tested and operational
- ✅ Client deliverable format standardized

---

## **QUALITY ASSURANCE PROTOCOL**

### **Prompt Testing Standards:**

**Strategic Framework Integration:**

- Daniel Priestley's 5 P's methodology
- Alisha's DNA research and Golden Hippo offers
- Eugene Schwartz awareness sophistication
- VIRAL framework application
- Trust recession strategy implementation

**Customer Language Preservation:**

- Exact phrases maintained from research
- Drama prioritization scoring (1-10)
- Emotional trigger identification
- Authority gap analysis

**Competitive Intelligence:**

- Market positioning opportunities
- Differentiation strategy development
- Oversubscribed positioning potential
- KPOI authority building focus

### **Output Validation:**

**Business Impact Criteria:**

- Revenue attribution potential
- Authority building ROI
- Competitive advantage creation
- Implementation speed optimization
- Client satisfaction predictors

---

## **NEXT MILESTONE TARGETS**

### **Week 1 Completion:**

- Complete Notion database setup with refined prompts
- Ultra-minimal form operational and tested
- N8N workflow blueprint ready for development

### **Week 2 Target:**

- Full N8N automation operational
- End-to-end testing with real client data
- Quality control protocols validated

### **Week 3 Goal:**

- Production-ready CIA system
- Client onboarding process finalized
- First automated CIA analysis delivered

---

**CURRENT STATUS: Prompt Refinement & Notion Population PhaseNEXT ACTION: Refine Phase 1S system prompt for N8N integrationSUCCESS METRIC: Form-to-strategy pipeline operational within 7 days**