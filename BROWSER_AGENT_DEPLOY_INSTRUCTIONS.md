# 🤖 Browser Agent Instructions for Brand BOS Deployment

**Agent Task**: Run the deployment script to deploy Brand BOS to Render.com

## Prerequisites
- Agent must have terminal/command line access
- Python must be installed on the system
- Agent needs the API credentials ready to input

## Step-by-Step Instructions for Browser Agent

### 1️⃣ Open Terminal/Command Line

**On Mac:**
- Press `Cmd + Space`
- Type "Terminal"
- Press Enter

**On Windows:**
- Press `Windows + R`
- Type "cmd"
- Press Enter

### 2️⃣ Navigate to Project Directory

**Execute this command:**
```bash
cd /Users/rodericandrews/App_Building/V1_Waterfall
```

**Verify you're in the right directory:**
```bash
pwd
```
Should show: `/Users/rodericandrews/App_Building/V1_Waterfall`

### 3️⃣ Run the Deployment Script

**Execute:**
```bash
python deploy.py
```

**If that doesn't work, try:**
```bash
python3 deploy.py
```

### 4️⃣ Follow the Script Prompts

The script will ask for several inputs. Here's exactly what to enter:

#### Workspace Selection
- The script will automatically find "RA Perso" workspace
- You'll see: `✅ Found RA Perso workspace (ID: xxx)`

#### Supabase Configuration
When prompted for **SUPABASE_URL**:
- Enter the Supabase project URL
- Format: `https://xxxxx.supabase.co`
- Press Enter

When prompted for **SUPABASE_ANON_KEY**:
- Enter the anon key from Supabase
- Starts with: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- Press Enter

When prompted for **SUPABASE_SERVICE_ROLE_KEY**:
- Enter the service role key from Supabase
- Also starts with: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- Press Enter

#### AI Configuration
When prompted for **ANTHROPIC_API_KEY**:
- Enter the Anthropic API key
- Format: `sk-ant-api03-xxxxx...`
- Press Enter

#### Security Configuration
When prompted for **SECRET_KEY**:
- Just press Enter (auto-generates a secure key)
- OR enter a custom 32+ character string

#### CORS Configuration
When prompted for **ALLOWED_ORIGINS**:
- Just press Enter to use defaults
- OR enter custom origins like: `https://yourdomain.com,https://app.yourdomain.com`

### 5️⃣ Wait for Deployment

The script will then:
1. Create Redis service (optional)
2. Create web service
3. Link them together
4. Show progress messages

**Expected output:**
```
✅ Found RA Perso workspace
✅ Redis service created: brand-bos-redis
✅ Web service created: brand-bos-api
✨ Deployment Complete!

🌐 Your API URL: https://brand-bos-api.onrender.com
📊 Health Check: https://brand-bos-api.onrender.com/health
📚 API Docs: https://brand-bos-api.onrender.com/docs
```

### 6️⃣ Save Important Information

**The agent should copy and save:**
1. The API URL (e.g., `https://brand-bos-api.onrender.com`)
2. Any error messages if deployment fails
3. The full output of the deployment

### 7️⃣ Verify Deployment (Optional)

**Open a web browser and navigate to:**
- Health check: `https://[your-api-url]/health`
- Should see: `{"status":"healthy","timestamp":"...","version":"1.0.0"}`

## 🚨 Troubleshooting

### If "python: command not found":
Try:
```bash
python3 deploy.py
```

### If "No such file or directory":
Make sure you're in the correct directory:
```bash
ls deploy.py
```
Should show the file exists

### If API key errors:
- Double-check the API key `rnd_BypZpLEwf1wqzDjJutPdSrDHP9Iy` is correct
- Ensure you're not in "Think Big Media" workspace

### If credential errors:
- Verify all keys are entered correctly
- No extra spaces before or after keys
- Keys are from the correct services

## 📝 Information to Report Back

After running the deployment, the agent should provide:
1. **Success/Failure status**
2. **The API URL** if successful
3. **Full error messages** if failed
4. **Screenshot of final output** (if possible)
5. **Time taken** for deployment

## ⏱️ Expected Timeline

- Script prompts: 2-3 minutes to enter all values
- Service creation: 1-2 minutes
- Total script time: ~5 minutes
- Build time on Render: 5-10 minutes additional

---

**Note**: The agent does NOT need to access Render.com website. Everything is handled through the terminal/command line using the API key.