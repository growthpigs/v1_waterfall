---
phase: convergence-blender
type: user
title: "Convergence Blender – User Prompt"
description: |
  Ask the AI to translate Golden Hippo Offer outputs into a 12-week omni-channel
  content blueprint, including silos, themes, weekly schedule and a practical
  implementation timeline.
---

**Context**

• Company → **{{companyName}}**  
• Website → **{{websiteUrl}}**

The previous phase produced the four-tier Golden Hippo Offer including authority hooks,
objection handling and pricing structure:

`{{goldenHippoOfferResults}}`

---

**Mission for the AI (Convergence Blender)**

1. Create a **12-week content calendar** that converges traffic, trust and conversions
   on the Golden Hippo Offer ladder.  
2. Group the calendar into **content silos / themes** that map to the awareness
   stages and value propositions defined above.  
3. Provide a **weekly distribution plan** (channels, content types, hero/hub/help ratio).  
4. Supply an **implementation roadmap** that details production owners,
   deadlines, and KPI checkpoints.

---

**Deliverables – return ONLY valid JSON**

```json
{
  "contentSilos": [
    {
      "siloName": "",
      "coreTheme": "",
      "targetAwarenessStage": "",
      "primaryObjective": "",
      "weeklyCadence": 0,
      "exampleTopics": [""]
    }
  ],
  "weeklySchedule": [
    {
      "week": 1,
      "theme": "",
      "goal": "",
      "pieces": [
        {
          "day": "",
          "channel": "",
          "format": "",
          "workingTitle": "",
          "callToAction": "",
          "repurposeInto": [""]
        }
      ]
    }
  ],
  "implementationTimeline": [
    {
      "milestone": "",
      "ownerRole": "",
      "startDate": "",
      "endDate": "",
      "dependencies": [""]
    }
  ],
  "kpis": ["", ""]
}
```

**Formatting rules**

1. Do **NOT** wrap the JSON in code fences.  
2. Fill every array even if single element.  
3. Dates in ISO-8601 (`YYYY-MM-DD`).  
4. Keep any string ≤ 280 characters.  
5. No commentary outside JSON.
