# Project Waterfall

A full-stack marketing intelligence platform that helps marketers, founders, and content teams turn raw data into actionable insights and channel-ready content.

---

## Table of Contents
1. Project Overview  
2. Core Features  
3. High-Level Architecture  
4. Tech Stack  
5. Repository Structure  
6. Quick Start  
7. Environment Variables  
8. NPM Scripts Reference  
9. Roadmap & Milestones  
10. Contributing  
11. License  

---

## 1. Project Overview
Project Waterfall unifies SEO intelligence, market research, trend data and AI-assisted copy generation behind a CleanMyMac-inspired UI.  
The platform centres around three pillars:

| Pillar | Purpose |
| ------ | ------- |
| **CIA – Colossal Intelligence Arsenal** | End-to-end data ingestion & analysis pipeline that outputs the _Master Content Bible_. |
| **Cartwheel Bundle** | Always-on generator that converts CIA insights into blogs, social posts, video scripts and more (military-themed classifications). |
| **Clarity Board** | Free, lightweight taste of CIA to drive sign-ups. |

Key differentiators:  
• Convergence Blender (long-/mid-/short-term data fusion)  
• Cost-efficient DataForSEO MCP integration (3.5 B keywords non-live cache)  
• Proprietary prompt library (Hormozi, Kern, etc.)  
• Seamless Notion export for BuildFast workflows  

---

## 2. Core Features
- Wizard-driven onboarding & data collection  
- Automated website / competitor / SEO / social proof analysis  
- Master Content Bible generation (brand, keyword & content strategy)  
- Military classification for 60+ content types (SNIPER, VIPER, …)  
- One-click export to PDF, DOCX, Notion, Google Sheets  
- Role & subscription tiers with usage limits  
- Micro-service ready Node API + React client with Redux  

---

## 3. High-Level Architecture
```
Client (React) ──▶ API Gateway (Express)
                       │
                       ▼
               ┌──────────────┐
               │ Service Layer│
               │  • CIA Engine│
               │  • Cartwheel │
               │  • Auth/Users│
               └──────────────┘
                       │
           ┌───────────┴───────────┐
           │ External Integrations │
           │  • DataForSEO MCP     │
           │  • Google Trends      │
           │  • Twitter, TikTok    │
           │  • Notion API         │
           └───────────┬───────────┘
                       ▼
                MongoDB + Redis
```
Infra: Docker → Kubernetes (future), CI/CD via GitHub Actions, metrics with Prometheus/Grafana.

---

## 4. Tech Stack
| Layer      | Technology |
| ---------- | ---------- |
| Frontend   | React 18, Redux Toolkit, Styled-Components, D3, Chart.js |
| Backend    | Node 18, Express 4, MongoDB 8 (Mongoose), Redis, JWT |
| DevOps     | Docker, GitHub Actions, (future) K8s, Terraform |
| Integrations | DataForSEO, Google Trends, X/Twitter, TikTok, Notion |
| Tooling    | ESLint + Prettier, Jest, Supertest, Nodemon |

---

## 5. Repository Structure
```
waterfall-app/
  client/                # React application
    src/
      components/
      pages/
      redux/
      styles/
  server/                # Node / Express API
    src/
      api/               # Route definitions
      models/            # Mongoose schemas
      services/          # Business logic (CIA, Cartwheel …)
      middlewares/
      config/
    .env.example
  .gitignore
  package.json           # Monorepo root scripts
  README.md
```

---

## 6. Quick Start

### Prerequisites
- Node 18+
- npm 9+ or pnpm/yarn  
- MongoDB instance (local or Atlas)
- Optional: Redis for caching

### Installation
```bash
# clone repo
git clone https://github.com/your-org/waterfall.git
cd waterfall-app

# install all workspaces
npm run install-all
```

### Environment
1. Copy `server/.env.example` → `server/.env`  
2. Fill in Mongo, JWT secrets and any API keys you own.

### Development Mode
```bash
npm run dev   # concurrently starts backend on :5000 and frontend on :3000
```
Visit `http://localhost:3000`.

### Production Build
```bash
npm run build     # builds React app
npm run server    # serves API + static client
```

Docker/Kubernetes manifests will be added in Phase 2.

---

## 7. Environment Variables (server)
| Variable | Description |
| -------- | ----------- |
| `PORT` | API port *(default 5000)* |
| `MONGODB_URI` | Mongo connection string |
| `JWT_SECRET` | Access token secret |
| `DATAFORSEO_LOGIN` / `DATAFORSEO_PASSWORD` | API creds |
| `NOTION_API_KEY` | Notion integration |
| … | See `server/.env.example` for full list |

---

## 8. NPM Scripts Reference
Root:
- `npm run dev` – concurrent frontend & backend
- `npm run build` – production client build
- `npm test` – run all Jest tests

Client:
- `npm start` – React dev server
- `npm run lint[:fix]`

Server:
- `npm run dev` – Nodemon watch
- `npm run test` – Jest + Supertest API tests
- `npm run lint[:fix]`

---

## 9. Roadmap & Milestones
| Phase | Timeline | Highlights |
| ----- | -------- | ---------- |
| 1. Foundation | M1-M2 | Auth, DB schema, CIA wizard MVP, base UI |
| 2. Core Function | M3-M4 | Complete CIA, Clarity Board, Convergence Blender |
| 3. Cartwheel | M5-M6 | Prompt Library, multi-format content generator, Notion export |
| 4. Tools & Payments | M7-M8 | Individual tools, subscription billing, optimisation |
| 5. Launch & Iterate | M9+ | Public launch, feedback loop, desktop app exploration |

Progress tracked via GitHub Projects.

---

## 10. Contributing
1. Fork & clone repo  
2. Create feature branch: `git checkout -b feat/your-feature`  
3. Follow ESLint/Prettier rules (`npm run lint:fix`)  
4. Commit with [Conventional Commits](https://www.conventionalcommits.org)  
5. Push & open PR against `main`  
CI will run lint + tests.

---

## 11. License
Project Waterfall © 2025 San Francisco AI Factory.  
Licensed under the MIT License – see `LICENSE` for details.

For questions or partnership inquiries, open an issue or email team@factory.ai.
