# 🤖 Browser Agent Instructions for Render.com Deployment

**Agent Task**: Deploy Brand BOS backend to Render.com using the web interface

## Prerequisites for Agent
- User must be logged into Render.com
- GitHub repository must be connected to Render account
- Repository URL: Check the git remote URL for exact path

## Step-by-Step Browser Instructions

### 0️⃣ Select Correct Workspace

**Navigate to**: https://dashboard.render.com/

**CRITICAL - Select the correct workspace**:
1. Look at top-left corner for workspace selector
2. If it shows "Think Big Media", click on it
3. Select **"RA Perso"** from the dropdown
4. **VERIFY**: Top-left should now show "RA Perso"
5. ⚠️ **DO NOT PROCEED** if workspace shows "Think Big Media"

### 1️⃣ Create New Web Service

**After confirming you're in "RA Perso" workspace**:
1. Click the **"New +"** button (top right, purple button)
2. Select **"Web Service"** from dropdown menu

### 2️⃣ Connect Repository

**On the "Create Web Service" page**:

1. **If repository not listed**:
   - Click **"Connect account"** under GitHub
   - Authorize Render to access the repository
   - Return to service creation

2. **Select repository**:
   - Search for: `V1_Waterfall` or the repository name
   - Click **"Connect"** button next to the repository

### 3️⃣ Configure Service Settings

**Fill in these exact values**:

| Field | Value |
|-------|-------|
| **Name** | `brand-bos-api` |
| **Region** | `Oregon (US West)` or closest to user |
| **Branch** | `main` |
| **Root Directory** | `.` (leave empty or single dot) |
| **Runtime** | `Docker` |
| **Instance Type** | `Free` |

**Advanced Settings** (click to expand):

| Field | Value |
|-------|-------|
| **Dockerfile Path** | `./Dockerfile` |
| **Docker Build Context Directory** | `.` |
| **Health Check Path** | `/health` |

### 4️⃣ Add Environment Variables

**Click** "Advanced" to expand settings, then find **"Environment Variables"** section.

**Add these variables** (click "Add Environment Variable" for each):

```
Key: SUPABASE_URL
Value: [User will provide]

Key: SUPABASE_ANON_KEY
Value: [User will provide]

Key: SUPABASE_SERVICE_ROLE_KEY
Value: [User will provide]

Key: ANTHROPIC_API_KEY
Value: [User will provide]

Key: SECRET_KEY
Value: [Generate random 32+ character string]

Key: ALLOWED_ORIGINS
Value: http://localhost:5173,http://localhost:3000

Key: ENVIRONMENT
Value: production

Key: LOG_LEVEL
Value: INFO

Key: PORT
Value: 8080
```

### 5️⃣ Create Service

1. Scroll to bottom
2. Click **"Create Web Service"** button (purple)
3. Wait for initial deployment (5-10 minutes)

### 6️⃣ Monitor Deployment

**On the service dashboard**:

1. Click on **"Logs"** tab to watch build progress
2. Look for: `Container started successfully`
3. Check **"Events"** tab for deployment status

**Expected Log Output**:
```
==> Building Docker image...
==> Pushing image to registry...
==> Deploying...
🚀 Starting Brand BOS Backend...
📋 Environment Information:
  - Port: 8080
  - Environment: production
✅ All required environment variables are set
🎯 Starting Uvicorn server on 0.0.0.0:8080
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 7️⃣ Verify Deployment

1. Find the service URL at top of dashboard (e.g., `https://brand-bos-api.onrender.com`)
2. Click the URL to open in new tab
3. Append `/health` to the URL
4. Should see: `{"status":"healthy","timestamp":"...","version":"1.0.0"}`

### 8️⃣ Create Redis Instance (Optional but Recommended)

**From main dashboard**:

1. Click **"New +"** → **"Redis"**
2. Configure:
   - **Name**: `brand-bos-redis`
   - **Region**: Same as web service
   - **Instance Type**: `Free`
   - **Maxmemory Policy**: `allkeys-lru`
3. Click **"Create Redis"**

**After Redis is created**:

1. Copy the **Internal Redis URL** from Redis dashboard
2. Go back to web service → **Environment** tab
3. Add new variable:
   - **Key**: `REDIS_URL`
   - **Value**: [Paste Internal Redis URL]
4. Click **"Save Changes"** (will trigger redeploy)

### 9️⃣ Set Up Auto-Deploy

**In service settings**:

1. Go to **"Settings"** tab
2. Under **"Build & Deploy"**:
   - **Auto-Deploy**: Toggle **ON**
   - **Branch**: Verify it says `main`
3. Click **"Save Changes"**

### 🎯 Success Criteria

The deployment is successful when:
- ✅ Service shows "Live" status
- ✅ Health check returns 200 OK
- ✅ No errors in logs
- ✅ Auto-deploy is enabled

### ⚠️ Common Issues to Check

1. **Build Failures**:
   - Check if Dockerfile path is correct
   - Verify repository has all required files

2. **Container Won't Start**:
   - Check environment variables are all set
   - Look for missing required variables in logs

3. **Health Check Failing**:
   - Ensure `/health` endpoint is accessible
   - Check PORT is set to 8080

### 📝 Information to Report Back

After deployment, agent should provide:
1. **Workspace used** (MUST be "RA Perso")
2. Service URL (e.g., `https://brand-bos-api.onrender.com`)
3. Deployment status (Live/Failed)
4. Any error messages from logs
5. Redis connection string (if created)

---

**⚠️ CRITICAL NOTE for Agent**: 
- **MUST deploy in "RA Perso" workspace**
- **DO NOT use "Think Big Media" workspace**
- Verify workspace selection before any other action
- If any step fails, capture the exact error message shown in the interface