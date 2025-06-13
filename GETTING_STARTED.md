# Getting Started – Project Waterfall (local development)

Welcome to the **Project Waterfall** code-base!  
Follow this guide to spin up the full stack (Node API + React UI) on your machine in minutes.

---

## 1. Prerequisites

| Tool | Minimum Version | Notes |
| ---- | --------------- | ----- |
| Node.js | **18.x** | Use nvm or volta for painless switching |
| npm / pnpm / yarn | npm 9+ (default scripts assume **npm**) | |
| Git | latest | |
| MongoDB | **6+** | Local instance or Atlas connection string |
| Redis *(optional)* | 6+ | For caching – app runs without it |
| Docker *(optional)* | 24+ | One-command spin-up via `docker compose` |

> ⚠️  If you do not want to install MongoDB/Redis locally, use Docker or free cloud services (MongoDB Atlas, Upstash Redis).

---

## 2. Clone the repo

```bash
git clone https://github.com/growthpigs/v1_waterfall.git
cd v1_waterfall/waterfall-app
```

Repository layout (abridged):

```
waterfall-app/
  client/   # React 18 + Redux Toolkit
  server/   # Node 18, Express, Mongoose
  README.md
  GETTING_STARTED.md  <-- you are here
```

---

## 3. Install dependencies

Monorepo helper script installs root, client **and** server:

```bash
npm run install-all
```

---

## 4. Configure environment variables

1. Copy the server template:
   ```bash
   cp server/.env.example server/.env
   ```
2. Fill in:
   - `MONGODB_URI` – `mongodb://localhost:27017/waterfall` **or** Atlas string  
   - `JWT_SECRET` / `JWT_REFRESH_SECRET`
   - 3rd-party API keys (DataForSEO, Twitter → optional)

> Keep secrets **out of version control**.

---

## 5. Fire it up (dev mode)

```bash
npm run dev
```

Script launches:

| Service | Port | Live-reload |
| ------- | ---- | ---------- |
| API (Express) | `http://localhost:5000` | nodemon |
| UI  (React)   | `http://localhost:3000` | vite/CRA |

Verify:

```bash
curl http://localhost:5000/api/health
# → {"status":"ok","message":"Project Waterfall API is running"}
```

Open `http://localhost:3000` to view the UI (placeholder during Phase 1).

---

## 6. Alternative: Docker Compose

Quick spin-up (Mongo + Redis + API) – requires Docker Desktop:

```bash
docker compose up -d
```

The compose file lives in `devops/docker-compose.yml` (added in Phase 1 milestone 1.5).

---

## 7. Useful scripts

| Command | Description |
| ------- | ----------- |
| `npm test` | Run **Jest + Supertest** suite (server & client) |
| `npm run lint` / `lint:fix` | ESLint + Prettier |
| `npm run build` | Production React build |
| `npm run server` | API only |
| `npm run client` | React only |

---

## 8. Troubleshooting

| Symptom | Fix |
| ------- | ---- |
| `ECONNREFUSED localhost:27017` | MongoDB not running – start service or update `MONGODB_URI`. |
| `Token expired` API errors | Delete `token` / `refreshToken` from browser localStorage & log in again. |
| `EADDRINUSE 3000/5000` | Ports busy – change via `.env` (`PORT`) or `client/.env` (`PORT=3001`). |
| CORS blocked calls | Ensure API runs on **5000** or adjust `client/src/setupProxy.js`. |

---

## 9. Next steps

* Read the high-level **[README](../README.md)** for architecture & tech stack.  
* Track progress & current sprint in **[IMPLEMENTATION_ROADMAP.md](../IMPLEMENTATION_ROADMAP.md)**.  
* Want to contribute? Check `CONTRIBUTING.md` (coming in Phase 1).

Happy building!  
— The Waterfall Engineering Team
