---
phase: strategic-synthesis
type: user
version: 1.0
last_updated: 2025-06-13
description: >
  User prompt for Phase 3 — Strategic Synthesis.
  Supplies validated JSON outputs from Phase 1 (Business Intelligence)
  and Phase 2 (SEO & Social Intelligence) that “Fusion-SS” will merge
  into a unified strategic blueprint.
---

Below is the **combined intelligence dossier** for Phase 3 of Operation Waterfall’s  
Colossal Intelligence Arsenal (CIA).

Your mission is to integrate these upstream datasets and generate the JSON object
specified in the system instructions (strategic_summary, priority_playbooks, etc.).

=====================================================================

PHASE 1 — BUSINESS INTELLIGENCE  
```json
{{businessIntelligenceJSON}}
```

PHASE 2 — SEO & SOCIAL INTELLIGENCE  
```json
{{seoSocialIntelligenceJSON}}
```

=====================================================================

TASKS  
1. Synthesise the two JSON payloads to populate every field of the Phase 3 schema.  
2. Preserve verbatim phrases when present; infer cautiously where data is `null`.  
3. Honour all constraints from the system prompt (JSON-only response, field order,
   token limit, numeric rules, etc.).

Begin when ready. **Respond exclusively with the JSON object.**
