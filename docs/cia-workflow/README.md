# Colossal Intelligence Arsenal (CIA) Workflow  
_Repository Documentation Index_

Welcome to the CIA workflow docs. This folder is the **single source of truth** for the N8N-driven pipeline that powers Operation Waterfall’s “Colossal Intelligence Arsenal”.  
If you are building, maintaining, or consuming CIA features you should start here.

---

## 📂 Folder Layout

| Path | Purpose |
|------|---------|
| **phases/** | One markdown file per phase (e.g. `01-business-intel.md`). Each file explains the N8N nodes, inputs, outputs, and success criteria for that stage. |
| **prompts/** | Raw prompt templates used by the workflow (system, user, example-response). File naming: `{phaseId}-{slug}.md` |
| **examples/** | Reference JSON/CSV exports, screenshots, or Perplexity-Labs reports that illustrate a complete run. |

```
docs/cia-workflow/
├─ README.md  ← you are here
├─ phases/
│  ├─ 01-business-intel.md
│  ├─ 02-seo-social-intel.md
│  └─ …
├─ prompts/
│  ├─ 1A-foundational-business-intelligence.md
│  ├─ 1A-bis-response.md
│  └─ …
└─ examples/
   ├─ sample-report.json
   └─ phase-1-screenshots/
```

---

## 🗺️ High-Level Phase Map

| Phase | Description | Key Output |
|-------|-------------|------------|
| **1 — Business Intelligence** | Scrape company, ICP & competitor DNA | `business_intel.json` |
| **2 — SEO & Social Intelligence** | Keyword landscape + social sentiment | `seo_social_intel.json` |
| **3 — Strategic Synthesis** | X-trend merge + testimonial drama | `synthesis.json` |
| **4 — Golden Hippo Offer** | 90-day offer & value ladder | `offer.json` |
| **5 — Convergence Blender** | Weekly silo plan → funnel | `content_silos.json` |
| **6 — Master Content Bible** | Final deliverable pack | `master_bible.zip` |

Each `phases/*.md` file drills into the N8N nodes (HTTP Request, Function, IF, Merge etc.), environment variables, and webhooks required to reproduce that stage.

---

## 🛠️ Using These Docs

### Developers
1. Read the relevant `phases/*.md` when wiring backend services (`server/src/services/**`) or the CIA Wizard.
2. Import prompt files from `prompts/` instead of hard-coding strings.
3. Keep phase IDs in code in sync with filenames.

### Prompt Engineers / Ops Writers
- Edit prompt copy directly in `prompts/`.  
- Use markdown front-matter for metadata (`phase`, `role`, `credits_cost`, etc.).
- Submit a PR; CI will lint for broken front-matter and missing links.

### Contributors
1. Create a feature branch.
2. Add/modify docs.
3. Open a PR referencing the Jira / GitHub issue.
4. A reviewer must validate the workflow diagram & prompt test before merge.

---

## 🚦 Quality Checklist before Merging
- [ ] Phase markdown includes **node diagram** or bullet map.
- [ ] All input/output schemas documented.
- [ ] Prompt files have example responses.
- [ ] Linkbacks to upstream/downstream phases added.
- [ ] `docs/cia-workflow/README.md` index updated if new phase added.

---

### Next Steps
The core spec index is now in place.  
In follow-up commits we will populate:

- Detailed phase markdown files  
- Prompt templates for every phase + “bis” (response) variants  
- Example data exports

_Questions? Open an issue with the `documentation` label or ping `@growthpigs/cia-owners` in Slack._
