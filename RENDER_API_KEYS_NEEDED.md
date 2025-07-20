# 🔑 API Keys Needed for Brand BOS Deployment

Before your agent deploys to Render, you'll need these API keys ready:

## 🎯 Render API Key (For Deployment)

**Your Render API Key**: `rnd_BypZpLEwf1wqzDjJutPdSrDHP9Iy`
- ✅ Configured for "RA Perso" workspace only
- ❌ Will not access "Think Big Media" workspace
- Use this for API-based deployment automation

## 1️⃣ Supabase (Database) - REQUIRED

**Get from**: https://app.supabase.com/project/YOUR_PROJECT/settings/api

You need:
- `SUPABASE_URL`: Looks like `https://xxxxx.supabase.co`
- `SUPABASE_ANON_KEY`: Starts with `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- `SUPABASE_SERVICE_ROLE_KEY`: Also starts with `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

**Don't have Supabase?**
1. Sign up free at [supabase.com](https://supabase.com)
2. Create new project
3. Wait 2 minutes for setup
4. Go to Settings → API

## 2️⃣ Anthropic (Claude AI) - REQUIRED

**Get from**: https://console.anthropic.com/settings/keys

You need:
- `ANTHROPIC_API_KEY`: Looks like `sk-ant-api03-xxxxx...`

**Don't have one?**
1. Sign up at [anthropic.com](https://anthropic.com)
2. Add billing (pay-as-you-go)
3. Create API key

## 3️⃣ Secret Key - REQUIRED

**Generate one**:
```bash
# Run this command in terminal:
openssl rand -hex 32

# Or use this online generator:
# https://randomkeygen.com/
# (Use the "CodeIgniter Encryption Keys" section)
```

You need:
- `SECRET_KEY`: Any random 32+ character string

## 4️⃣ Optional Keys (Can Add Later)

### Google Ads (for Adsby module):
- `GOOGLE_ADS_CLIENT_ID`
- `GOOGLE_ADS_CLIENT_SECRET`
- `GOOGLE_ADS_DEVELOPER_TOKEN`

### Email Notifications:
- `SMTP_HOST`: e.g., `smtp.gmail.com`
- `SMTP_USERNAME`: Your email
- `SMTP_PASSWORD`: App-specific password

### Slack Notifications:
- `SLACK_WEBHOOK_URL`: From Slack app settings

## 📋 Quick Checklist for Agent

Before running the browser agent, have ready:

```
☐ SUPABASE_URL=https://xxxxx.supabase.co
☐ SUPABASE_ANON_KEY=eyJhbGciOiJ...
☐ SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJ...
☐ ANTHROPIC_API_KEY=sk-ant-api03-...
☐ SECRET_KEY=(generate random 32+ chars)
```

## 🚀 Ready to Deploy?

Once you have these keys, your agent can follow the instructions in:
`RENDER_BROWSER_AGENT_INSTRUCTIONS.md`

The agent will input these values during Step 4 of the deployment process.