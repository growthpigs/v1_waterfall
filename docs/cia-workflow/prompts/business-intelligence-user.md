---
phase: business-intelligence
type: user
version: 1.0
last_updated: 2025-06-13
description: >
  User prompt for Phase 1 — Business Intelligence.
  Supplies dynamic company data that the system prompt (“Cerberus-BI”) will analyse.
---

Below is the **source dossier** for Phase 1 of Operation Waterfall’s Colossal Intelligence Arsenal (CIA).

Use this information to populate every field of the JSON schema described by the system instructions.

Company Details
• **Company Name:** {{companyName}}
• **Website URL:** {{websiteUrl}}
• **Industry / Niche:** {{industry}}
• **Target Audience / ICP(s):** {{targetAudience}}
• **Key Person of Influence (KPOI):** {{keyPersonOfInfluence}}
• **Business Goals:** {{businessGoals}}
• **Content Goals:** {{contentGoals}}
• **Brand Voice:** {{brandVoice}}
• **Known Challenges / Pain Points:** {{painPoints}}
• **Differentiators / Unique Selling Proposition:** {{uniqueSellingProposition}}
• **Additional Notes:** {{additionalNotes}}

Contextual Reminders
1. If a field is marked “null” it means the client has no data; infer cautiously.
2. Preserve verbatim customer language whenever present (surrounding quotes already removed).
3. Output must comply with the system prompt’s *JSON-only* protocol.

Begin when ready.