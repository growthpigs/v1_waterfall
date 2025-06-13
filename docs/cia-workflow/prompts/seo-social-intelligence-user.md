---
phase: seo-social-intelligence
type: user
version: 1.0
last_updated: 2025-06-13
description: >
  User prompt for Phase 2 — SEO & Social Intelligence.
  Supplies Phase 1 Business Intelligence output plus fresh keyword/SERP
  datasets and social-media insights for Oracle-SI analysis.
---

Below is the **combined intelligence dossier** for Phase 2 of Operation Waterfall’s
Colossal Intelligence Arsenal (CIA).

You will merge the foundational business insights from Phase 1 with the
latest SEO and social-media data to uncover high-leverage opportunities.

=====================================================================

PHASE 1 BUSINESS INTELLIGENCE
```json
{{businessIntelligenceJSON}}
```

LIVE/RECENT SEO DATA
• Keyword Suggestions (DataForSEO → keywords_for_keywords):  
```json
{{keywordSuggestionsJSON}}
```

• Organic Results for Primary Domain (DataForSEO → organic_searches):  
```json
{{organicResultsJSON}}
```

• Competitor Overlap (DataForSEO → domain_vs_domain):  
```json
{{competitorDataJSON}}
```

SOCIAL-MEDIA INTELLIGENCE
• Platform Sentiment & Engagement (Apify / native APIs):  
```json
{{socialSentimentJSON}}
```

• Trending Topics & Hashtags (Google Trends / BuzzSumo):  
```json
{{trendingTopicsJSON}}
```

=====================================================================

TASKS
1. Synthesise the above data to populate every field of the JSON schema
   defined in the system instructions (keyword_landscape, serp_competitor_overview,
   social_intelligence, viral_hook_hypotheses, risk_warnings, quick_win_recommendations).
2. Where numeric metrics are missing, infer reasonably or set to `null`.
3. Preserve any verbatim phrases contained in the inputs.
4. Honour all output constraints specified by the system prompt
   (JSON-only response, field order, token limits, etc.).

Begin when ready.  
Remember: **respond exclusively with the JSON object**. 