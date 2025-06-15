---
phase: golden-hippo-offer
type: user
title: "Golden Hippo Offer Development – User Prompt"
description: |
  Ask the AI to transform strategic synthesis insights into four irresistible tiered offers
  using Alisha Conlin-Hurd’s Golden Hippo methodology, with authority positioning,
  geographic/KPOI leverage, and next-logical-step psychology.
---

**Context**

You are acting as a senior Offer Development Specialist inside the Colossal Intelligence Arsenal (CIA) workflow.

• Company Name → **{{companyName}}**  
• Website URL → **{{websiteUrl}}**

The previous phase (Strategic Synthesis) produced a comprehensive analysis of customer DNA, competitor gaps, authority assets, pain-point language, and market opportunities.

`{{strategicSynthesisResults}}` ← *Insert JSON from Phase 3 here.*

**Mission**

Convert the Strategic Synthesis insights into a set of **four (4) tiered Golden Hippo Offers** that:

1. Map precisely to Eugene Schwartz awareness stages  
   - Stage 1 ➜ Unaware / Problem-Aware  
   - Stage 2 ➜ Solution-Aware  
   - Stage 3 ➜ Product-Aware  
   - Stage 4 ➜ Most Aware / Ready-to-Buy  

2. Integrate **authority positioning** (Daniel Priestley KPI / Key Person of Influence framework).  
   - Highlight expertise, social proof, media, partnerships, awards, certifications.

3. Embed **geographic & KPOI advantages** where relevant (e.g., local dominance, timezone, on-site presence, region-specific trust signals, named influential spokesperson).

4. Follow **“Next Logical Step” psychology** – each offer naturally leads to the next, removing friction and increasing commitment.

5. Showcase **conversion assets**:
   - Core promise, unique mechanism, urgency/scarcity trigger, guarantee/warranty.

6. Link back to explicit pain-points, dream outcomes, and objection-handling phrases found in `strategicSynthesisResults`.

**Output Requirements**

Return **ONLY** valid JSON matching this schema:

```json
{
  "offers": [
    {
      "awarenessLevel": "<Awareness Stage>",
      "headline": "<Compelling headline>",
      "subHeadline": "<Supportive sub-headline>",
      "corePromise": "<Key transformation/result>",
      "uniqueMechanism": "<Why this works>",
      "deliverables": ["<Item 1>", "<Item 2>", "..."],
      "priceModel": "<Fixed fee, tiered, % rev-share, etc.>",
      "authorityTriggers": ["<Certifications>", "<Media features>", "..."],
      "geographicKPOILeverage": "<How local/KPOI factors strengthen trust>",
      "nextLogicalStep": "<Description of the step that leads to the next offer>",
      "urgencyScarcity": "<Limited spots, deadline, bonus, etc.>",
      "guarantee": "<Risk reversal statement>"
    }
  ],
  "upsellPathwayExplanation": "<1-2 sentence overview of how the four offers ladder>"
}
```

**Formatting Rules**

1. Do **NOT** wrap the JSON in markdown code fences.  
2. Fill every field; use arrays even if single item.  
3. No additional commentary outside the JSON.  
4. Keep each string under 280 characters to stay concise.

**Quality Checklist Before Responding**

- All four awareness levels covered.  
- Pain-points & language directly lifted from `strategicSynthesisResults`.  
- Authority + geographic/KPOI hooks present.  
- Guarantee and urgency present for each offer.  
- Valid JSON with double quotes and no trailing commas.  
