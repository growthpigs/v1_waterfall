# 🚀 Brand BOS Quick Start Deployment Guide

**Time to Deploy: ~30 minutes**

## ✅ Pre-Deployment Checklist

Run this command to verify everything is ready:
```bash
./scripts/check-deployment-ready.sh
```

## 📝 Step-by-Step Deployment

### 1️⃣ Create Your Environment File (2 min)
```bash
cp .env.example .env
# Edit .env with your actual values
```

**Minimum Required Values:**
- `SUPABASE_URL` - From your Supabase project
- `SUPABASE_ANON_KEY` - From Supabase API settings
- `ANTHROPIC_API_KEY` - From console.anthropic.com
- `SECRET_KEY` - Generate with: `openssl rand -hex 32`

### 2️⃣ Push to GitHub (2 min)
```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### 3️⃣ Deploy Backend to Render (10 min)

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub account
4. Select your repository
5. Render will auto-detect `render.yaml`
6. Click **"Apply"**
7. Wait for deployment (~5-7 minutes)

### 4️⃣ Configure Environment Variables in Render (5 min)

In your Render service dashboard:
1. Go to **"Environment"** tab
2. Add these variables:

```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJ...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJ...
ANTHROPIC_API_KEY=sk-ant-api03-...
ALLOWED_ORIGINS=https://your-app.vercel.app
```

3. Click **"Save Changes"**
4. Service will auto-redeploy

### 5️⃣ Deploy Frontend to Vercel (10 min)

```bash
# Install Vercel CLI if needed
npm install -g vercel

# Deploy frontend
cd frontend
vercel

# Follow prompts:
# - Link to existing project? No
# - What's your project name? brand-bos
# - In which directory? ./
# - Override settings? No
```

Add environment variable in Vercel:
```
VITE_API_URL=https://brand-bos-api.onrender.com
```

### 6️⃣ Setup Database (5 min)

#### Option A: Supabase (Recommended)
1. Create project at [supabase.com](https://supabase.com)
2. Get connection details from Settings → API
3. Run migrations:
```bash
# From your local machine
psql $SUPABASE_CONNECTION_STRING < src/database/migrations/001_initial_schema.sql
```

#### Option B: Use Render PostgreSQL
1. Add database in Render dashboard
2. Update `DATABASE_URL` in environment variables

## 🎉 Verify Deployment

### Backend Health Check:
```bash
curl https://brand-bos-api.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-20T...",
  "version": "1.0.0"
}
```

### Frontend Check:
Visit your Vercel URL: `https://brand-bos.vercel.app`

## 🔧 Troubleshooting

### Common Issues:

**502 Bad Gateway**
- Check Render logs for startup errors
- Verify all required env vars are set
- Ensure PORT is not hardcoded

**Database Connection Failed**
- Verify Supabase credentials
- Check if IP is whitelisted
- Ensure SSL mode is enabled

**Frontend API Errors**
- Verify `VITE_API_URL` is correct
- Check CORS settings in backend
- Ensure `ALLOWED_ORIGINS` includes frontend URL

## 📱 Post-Deployment

1. **Monitor Logs**: Check Render dashboard logs tab
2. **Set Up Alerts**: Configure Slack webhook for notifications
3. **Custom Domain**: Add your domain in Render settings
4. **Enable Analytics**: Add tracking codes to frontend

## 🆘 Need Help?

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Deployment Logs**: Check the Render dashboard
- **API Docs**: Visit `/docs` on your deployed backend

---

**Congratulations! Your Brand BOS platform is now live! 🎊**

Next steps:
- Test all features thoroughly
- Set up monitoring and alerts
- Configure custom domains
- Plan your first Authority Avalanche campaign