# Project Waterfall – Implementation Roadmap  
_Updated: 2025-06-13_

---

## 1. Executive Snapshot

| Status | Item | Notes | Owner |
| ------ | ---- | ----- | ----- |
| ✅ Done | Local project scaffold (`waterfall-app/`) | React & Node workspaces, core folder tree | CTO |
| ✅ Done | `.gitignore`, `README.md`, root `package.json` | Monorepo scripts (`install-all`, `dev`, etc.) | CTO |
| ✅ Done | Git initialised, first commit | `main` branch | CTO |
| ✅ Done | Backend foundation<br/>• Express server entry<br/>• Global config loader<br/>• JWT auth middleware<br/>• Error middleware | Compiles & boots (requires `.env`) | CTO |
| ✅ Done | Core Mongoose models<br/>• `User` with subscription/usage<br/>• `CIAReport` full schema<br/>• `ContentItem` military classes | Schemas validated | CTO |
| ✅ Done | Primary API routes<br/>`/api/auth`, `/api/users`, `/api/cia`, `/api/cartwheel`, `/api/dataforseo` | Unit tests pending | CTO |
| 🟡 In-Progress | Phase 1 backlog (see §2) | Target completion **Jun 30 ’25** | CTO + FE Lead |
| ⏭ Next | CI pipeline, React bootstrap, Unit tests, Docker baseline | See §3 | —

---

## 2. Phase 1 – Foundation _(Month 1-2)_  

| Milestone | Tasks | ETA | Owner | Dependencies |
| --------- | ----- | --- | ----- | ------------ |
| 1.1 Environment Baseline | • `.env.example` verified<br/>• dotenv validation helper<br/>• Secure secrets vault (local: direnv / Doppler) | Jun 15 | DevOps | — |
| 1.2 CI/CD Skeleton | • GitHub Actions: lint, test matrix<br/>• auto-tag on `main` merge | Jun 18 | DevOps | 1.1 |
| 1.3 API Test Harness | • Jest + Supertest setup<br/>• Smoke tests for each route | Jun 19 | Backend Lead | 1.2 |
| 1.4 React Boot | • `create-react-app` eject → Vite/CRA? (decision)<br/>• Global theme, routing skeleton<br/>• Storybook scaffold | Jun 21 | FE Lead | 1.1 |
| 1.5 Auth Flow E2E | • Signup / login REST ↔ React<br/>• Token storage & refresh hooks | Jun 24 | FE + BE | 1.3,1.4 |
| 1.6 Initial CIA Wizard MVP | • Stepper UI (company, site URL)<br/>• Trigger backend placeholder | Jun 28 | Full-stack | 1.5 |
| 1.7 Docs & ADRs | • Architecture decision records<br/>• Contributing guide | Jun 30 | PM/CTO | rolling |

---

## 3. Phase 2 – Core Functionality _(Month 3-4)_  

| Milestone | Highlights |
| --------- | ---------- |
| 2.1 Full CIA pipeline modules (website, competitor, SEO) |
| 2.2 Clarity Board (limited CIA) with usage caps |
| 2.3 Convergence Blender service & scoring algorithm |
| 2.4 Advanced UI dashboards, progress rings |
| 2.5 Security & performance pass |

_Target window:_ **Jul 01 – Aug 31 ’25**

---

## 4. Phase 3 – Cartwheel Bundle _(Month 5-6)_  

* Prompt Library CRUD  
* Multi-format generators (Blog, Social, Email)  
* Notion / PDF / G-Sheets exporters  
* Content Calendar UX  

_Target window:_ **Sep 01 – Oct 31 ’25**

---

## 5. Phase 4 – Tools & Payments _(Month 7-8)_  

* Individual micro-tools (LeadGen, Hashtag miner, etc.)  
* Stripe / Paddle billing integration  
* Usage credits + metering  
* Admin dashboard & analytics

---

## 6. Phase 5 – Launch & Iteration _(Month 9+)_

* Public beta, onboarding flows  
* Feedback loop, A/B infra  
* Desktop (Mac) feasibility spike  
* Roadmap 2.0 planning

---

## 7. Immediate Action Items (Sprint 0 / Week 2)

- [ ] **Finish Env Validation:** add `config/validateEnv.js`, call before server boot  
- [ ] **GitHub Actions Lint/Test:** ESLint + Jest workflow (`.github/workflows/ci.yml`)  
- [ ] **React Scaffold:** initialise Vite + TS, commit baseline UI  
- [ ] **Jest + Supertest:** write at least 3 passing tests per route group  
- [ ] **Docker Compose:** Mongo + Redis + API for local dev  
- [ ] **ADR-0001:** choose CRA vs Vite and document decision  
- [ ] **README Quick-start Update:** add Docker instructions  

_Assignees: CTO (oversee), Backend-Lead (tests), FE-Lead (React), DevOps (CI/CD)_  

---

## 8. RACI Matrix (Phase 1)

| Area | CTO | PM | FE Lead | BE Lead | DevOps |
| ---- | --- | -- | ------- | ------- | ------ |
| Architecture decisions | R | C | I | I | I |
| CI/CD setup | A | I | I | I | R |
| React bootstrap | I | C | R | I | I |
| API test harness | I | C | I | R | I |
| Documentation | A | R | C | C | C |

_R = Responsible, A = Accountable, C = Consulted, I = Informed_

---

## 9. Communication & Review Cadence

| Ritual | Schedule | Participants |
| ------ | -------- | ------------ |
| Stand-up (15 min) | Mon-Fri 09:00 PT | Whole dev team |
| Sprint Planning | Bi-weekly Mon | PM, Leads, CTO |
| Demo / Review | Bi-weekly Fri | All stakeholders |
| Architecture Sync | Wed 14:00 PT | CTO + Leads |
| Retrospective | End of sprint | Team |

Minutes & action logs stored in `/docs/meetings/`.

---

_This roadmap is living documentation – update after each sprint or major decision. Pull requests modifying this file must use label **roadmap**._
