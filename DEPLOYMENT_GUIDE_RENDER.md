# Brand BOS Deployment Guide - Render.com

This guide walks you through deploying Brand BOS on Render.com with a free tier setup.

## 📋 Prerequisites

1. **GitHub Account** - Your code must be in a GitHub repository
2. **Render Account** - Sign up at [render.com](https://render.com)
3. **Supabase Account** - For database (or use Render PostgreSQL)
4. **API Keys Ready**:
   - Anthropic API Key
   - Google Ads credentials (if using Adsby)
   - SMTP credentials for email

## 🚀 Quick Start Deployment

### Step 1: Prepare Your Repository

1. Push your code to GitHub:
```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

2. Update `render.yaml`:
   - Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username
   - Update the repository URL

### Step 2: Deploy to Render

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Select your repository and branch
5. Render will detect the `render.yaml` file automatically

### Step 3: Configure Environment Variables

In Render Dashboard, add these environment variables:

#### Required Variables:
```bash
# Supabase
SUPABASE_URL=your-supabase-project-url
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-key

# AI Services
ANTHROPIC_API_KEY=your-anthropic-api-key

# Security (Render generates SECRET_KEY automatically)
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
```

#### Optional Variables:
```bash
# Google Ads (for Adsby module)
GOOGLE_ADS_CLIENT_ID=your-client-id
GOOGLE_ADS_CLIENT_SECRET=your-client-secret
GOOGLE_ADS_DEVELOPER_TOKEN=your-dev-token

# Notifications
SLACK_WEBHOOK_URL=your-slack-webhook
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Step 4: Database Setup

#### Option A: Use Supabase (Recommended)
1. Create a project at [supabase.com](https://supabase.com)
2. Run migrations:
```bash
# Install Supabase CLI
npm install -g supabase

# Link to your project
supabase link --project-ref your-project-ref

# Run migrations
supabase db push
```

#### Option B: Use Render PostgreSQL
1. Add to `render.yaml`:
```yaml
databases:
  - name: brand-bos-db
    plan: free
```

2. Update environment variables to use Render's DATABASE_URL

### Step 5: Deploy Frontend to Vercel

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy frontend:
```bash
cd frontend
vercel --prod
```

3. Configure environment variable:
```bash
VITE_API_URL=https://brand-bos-api.onrender.com
```

## 🔧 Local Development

### Using Docker Compose:
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values
nano .env

# Start services
docker-compose up

# Frontend runs on http://localhost:5173
# Backend runs on http://localhost:8080
```

### Without Docker:
```bash
# Backend
cd /
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8080

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## 📊 Monitoring & Logs

### View Logs in Render:
1. Go to your service in Render Dashboard
2. Click "Logs" tab
3. Use filters for specific log levels

### Health Checks:
- Backend: `https://your-app.onrender.com/health`
- Metrics: `https://your-app.onrender.com/metrics`

## 🚨 Troubleshooting

### Common Issues:

1. **502 Bad Gateway**
   - Check logs for startup errors
   - Verify all required environment variables are set
   - Ensure PORT is not hardcoded (use `$PORT`)

2. **Database Connection Failed**
   - Verify Supabase credentials
   - Check if migrations have been run
   - Ensure network access is allowed

3. **Slow Cold Starts (Free Tier)**
   - Normal for free tier (spins down after 15 min)
   - Consider upgrading for always-on service

### Debug Commands:
```bash
# Test locally with production settings
docker build -t brand-bos .
docker run -p 8080:8080 --env-file .env brand-bos

# Check Docker image size
docker images brand-bos

# Test health endpoint
curl http://localhost:8080/health
```

## 🔄 Updating Your Deployment

### Automatic Deploys:
- Render automatically deploys when you push to main branch
- Takes 3-5 minutes for new deployment

### Manual Deploy:
1. Go to Render Dashboard
2. Click "Manual Deploy" → "Deploy latest commit"

### Rolling Back:
1. Go to "Deploys" tab in Render
2. Find previous successful deploy
3. Click "Rollback to this deploy"

## 📈 Scaling & Performance

### Free Tier Limitations:
- Spins down after 15 minutes of inactivity
- 512MB RAM, 0.5 CPU
- Limited to 750 hours/month

### Upgrade Options:
- **Starter**: $7/month - Always on, 512MB RAM
- **Standard**: $25/month - 2GB RAM, better CPU
- **Pro**: Custom resources for high traffic

### Performance Tips:
1. Use Redis caching (included in deployment)
2. Enable CDN for static assets
3. Optimize Docker image size
4. Use connection pooling for database

## 🔐 Security Checklist

- [ ] All secrets in environment variables
- [ ] HTTPS enforced (automatic on Render)
- [ ] CORS configured correctly
- [ ] Database using SSL
- [ ] API rate limiting enabled
- [ ] Security headers configured

## 📞 Support Resources

- **Render Status**: [status.render.com](https://status.render.com)
- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Community**: [community.render.com](https://community.render.com)

---

**Note**: This deployment is optimized for Render's infrastructure and avoids the proxy issues you experienced with Railway. The configuration ensures proper port binding and health checks that work with Render's routing layer.