---
phase: master-content-bible
type: user
title: "Master Content Bible – User Prompt"
description: |
  Final synthesis prompt. Convert all prior CIA phase outputs into a single, prescriptive
  Content Bible that the marketing team can execute immediately.
---

**Context**

• Company → **{{companyName}}**  
• Website → **{{websiteUrl}}**

Below are the structured JSON results from every preceding CIA phase:

```json
{
  "businessIntelligence": {{businessIntelligenceResults}},
  "seoSocialIntelligence": {{seoSocialIntelligenceResults}},
  "strategicSynthesis": {{strategicSynthesisResults}},
  "goldenHippoOffer": {{goldenHippoOfferResults}},
  "convergenceBlender": {{convergenceBlenderResults}}
}
```

*(The assistant should parse these objects for data references – they are NOT part of the final answer.)*

---

### Your Mission (Master Content Bible Architect)

Using all intelligence above, produce a **single Master Content Bible** that gives the company everything required to dominate its niche for the next 12 months.

**Required sections – return ONLY the JSON object defined below:**

1. **brandNarrative** – mission, vision, USP, company story.  
2. **brandGuidelines**  
   - *voice*: tone, vocabulary, “do say / don’t say”, sample paragraphs.  
   - *visualGuidelines*: color hex codes, primary/secondary fonts, imagery style.  
3. **targetAudiencePersonas** – 3–5 persona cards (name, demo/psycho, pains, goals, preferred channels, content triggers).  
4. **keywordStrategy** – primary & secondary keywords + semantic clusters.  
5. **contentStrategy**  
   - goals, KPIs, hero/hub/help channel mix.  
   - 12-week calendar themes referencing the Convergence Blender weekly schedule.  
6. **contentFormulas** – headline formulas, email subject lines, CTA templates, story frameworks.  
7. **competitiveInsights** – strengths to emphasise, weaknesses to fix, positioning angles vs. top 3 competitors.  
8. **implementationRoadmap** – Gantt-style milestones for 12 months (quarter, ownerRole, startDate, endDate, successMetric, dependencies).  
9. **governance** – meeting cadence, asset library structure, optimisation process.

---

### Output format  
Return *ONLY* valid JSON following this schema (no markdown fences, no commentary):

```json
{
  "brandNarrative": {
    "story": "",
    "mission": "",
    "vision": "",
    "uniqueSellingProposition": ""
  },
  "brandGuidelines": {
    "voice": {
      "tone": "",
      "vocabulary": ["", ""],
      "doSay": ["", ""],
      "dontSay": ["", ""],
      "examples": ["", ""]
    },
    "visualGuidelines": {
      "primaryColors": ["#FFFFFF"],
      "secondaryColors": ["#000000"],
      "fonts": ["", ""],
      "imageryStyle": ""
    }
  },
  "targetAudiencePersonas": [
    {
      "name": "",
      "description": "",
      "demographics": {
        "age": "",
        "gender": "",
        "location": "",
        "income": ""
      },
      "psychographics": {
        "interests": ["", ""],
        "values": ["", ""],
        "painPoints": ["", ""],
        "goals": ["", ""]
      },
      "preferredChannels": ["", ""],
      "contentTriggers": ["", ""]
    }
  ],
  "keywordStrategy": {
    "primaryKeywords": ["", ""],
    "secondaryKeywords": ["", ""],
    "semanticClusters": [
      {
        "mainKeyword": "",
        "relatedKeywords": ["", ""]
      }
    ]
  },
  "contentStrategy": {
    "goals": ["", ""],
    "kpis": ["", ""],
    "channels": [
      {
        "name": "",
        "purpose": "",
        "contentTypes": ["", ""],
        "frequency": "",
        "metrics": ["", ""]
      }
    ],
    "calendar12Week": [
      {
        "week": 1,
        "theme": "",
        "objective": "",
        "pieces": [
          {
            "day": "",
            "channel": "",
            "format": "",
            "workingTitle": "",
            "callToAction": ""
          }
        ]
      }
    ]
  },
  "contentFormulas": {
    "headlineFormulas": ["", ""],
    "emailSubjects": ["", ""],
    "ctaTemplates": ["", ""],
    "storyFrameworks": ["", ""]
  },
  "competitiveInsights": {
    "strengthsToEmphasize": ["", ""],
    "weaknessesToAddress": ["", ""],
    "opportunitiesToTarget": ["", ""],
    "threatsToMonitor": ["", ""]
  },
  "implementationRoadmap": [
    {
      "milestone": "",
      "ownerRole": "",
      "quarter": "Q1",
      "startDate": "YYYY-MM-DD",
      "endDate": "YYYY-MM-DD",
      "successMetric": "",
      "dependencies": ["", ""]
    }
  ],
  "governance": {
    "meetingCadence": "",
    "assetLibraryStructure": ["", ""],
    "optimisationProcess": ""
  }
}
```

**Rules**  
1. *No* markdown fences, only raw JSON.  
2. Every array must contain at least one element.  
3. Strings ≤ 280 chars, use smart line wrapping.  
4. Do not invent data; derive from the provided phase results.  
5. If information is missing, use intelligent placeholders clearly marked “TBD”.  
