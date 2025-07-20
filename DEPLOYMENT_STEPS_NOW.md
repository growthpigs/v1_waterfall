# 🚀 Deploy Brand BOS Right Now!

Follow these steps in order to get your platform live.

## Step 1: Backend to Render.com (15 minutes)

### 1.1 Prepare Your Credentials
You need these ready:
- **Supabase URL**: From supabase.com dashboard
- **Supabase Anon Key**: From Supabase API settings  
- **Supabase Service Role Key**: From Supabase API settings
- **Anthropic API Key**: From console.anthropic.com

### 1.2 Run Deployment Script
```bash
cd /Users/rodericandrews/App_Building/V1_Waterfall
python3 deploy.py
```

### 1.3 Enter Credentials When Prompted
- Enter each credential as requested
- Press Enter for SECRET_KEY (auto-generates)
- Press Enter for ALLOWED_ORIGINS (uses defaults)

### 1.4 Wait for Deployment
- Script creates services in "RA Perso" workspace
- Takes 5-10 minutes to build and deploy
- You'll get a URL like: `https://brand-bos-api.onrender.com`

### 1.5 Save Your Backend URL!
**IMPORTANT**: Copy the API URL that's displayed. You'll need it for frontend deployment.

---

## Step 2: Frontend to Vercel (10 minutes)

### 2.1 Install Vercel CLI (if needed)
```bash
npm install -g vercel
```

### 2.2 Deploy Frontend
```bash
cd frontend
vercel
```

### 2.3 Follow Vercel Prompts
When asked:
- **Setup and deploy**: Y
- **Which scope**: Choose your account
- **Link to existing project**: N  
- **Project name**: brand-bos (or your choice)
- **Directory**: ./ (current directory)
- **Override settings**: N

### 2.4 Set Environment Variable
After deployment, in Vercel dashboard or CLI:
```bash
vercel env add VITE_API_URL
```
Enter: `https://brand-bos-api.onrender.com` (your Render URL)

### 2.5 Redeploy with Environment Variable
```bash
vercel --prod
```

---

## Step 3: Verify Everything Works (5 minutes)

### 3.1 Test Backend
Open in browser:
- Health: `https://brand-bos-api.onrender.com/health`
- Docs: `https://brand-bos-api.onrender.com/docs`

### 3.2 Test Frontend
- Visit your Vercel URL
- Check that it connects to backend
- Test login/features

### 3.3 Check Logs
- **Render**: Dashboard → Logs tab
- **Vercel**: Dashboard → Functions → Logs

---

## 🎉 You're Live!

Your Brand BOS platform is now deployed:
- **Backend API**: Running on Render.com
- **Frontend App**: Running on Vercel
- **Database**: Connected via Supabase
- **AI Features**: Powered by Anthropic

## What's Next?

1. **Custom Domain**: Add your domain in Vercel/Render settings
2. **SSL Certificates**: Automatic on both platforms
3. **Monitoring**: Set up alerts in Render dashboard
4. **Scaling**: Upgrade from free tier when needed

---

**Need Help?**
- Backend not responding? Check Render logs
- Frontend not connecting? Verify VITE_API_URL
- Database errors? Check Supabase credentials