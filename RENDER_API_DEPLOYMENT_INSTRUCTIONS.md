# 🚀 Render API Deployment Instructions (Using API Key)

Since you have a Render API key that's locked to "RA Perso" workspace, we can use the Render API for deployment instead of browser automation!

## 🔑 Your API Key
```
rnd_BypZpLEwf1wqzDjJutPdSrDHP9Iy
```
✅ This key only works with "RA Perso" workspace
❌ Cannot access "Think Big Media" workspace

## 📡 API Deployment Commands

### 1️⃣ Create Web Service via API

```bash
curl --request POST \
  --url https://api.render.com/v1/services \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer rnd_BypZpLEwf1wqzDjJutPdSrDHP9Iy' \
  --header 'Content-Type: application/json' \
  --data '{
    "type": "web_service",
    "name": "brand-bos-api",
    "ownerId": "YOUR_OWNER_ID",
    "repo": "https://github.com/YOUR_GITHUB_USERNAME/V1_Waterfall",
    "branch": "main",
    "buildFilter": {
      "paths": ["**"],
      "ignoredPaths": []
    },
    "runtime": "docker",
    "dockerfilePath": "./Dockerfile",
    "dockerContext": ".",
    "envVars": [
      {"key": "PORT", "value": "8080"},
      {"key": "ENVIRONMENT", "value": "production"},
      {"key": "LOG_LEVEL", "value": "INFO"},
      {"key": "SUPABASE_URL", "value": "YOUR_SUPABASE_URL"},
      {"key": "SUPABASE_ANON_KEY", "value": "YOUR_SUPABASE_ANON_KEY"},
      {"key": "SUPABASE_SERVICE_ROLE_KEY", "value": "YOUR_SUPABASE_SERVICE_KEY"},
      {"key": "ANTHROPIC_API_KEY", "value": "YOUR_ANTHROPIC_KEY"},
      {"key": "SECRET_KEY", "value": "YOUR_SECRET_KEY"},
      {"key": "ALLOWED_ORIGINS", "value": "http://localhost:5173,http://localhost:3000"}
    ],
    "plan": "free",
    "region": "oregon",
    "healthCheckPath": "/health"
  }'
```

### 2️⃣ Get Owner ID First

Before creating the service, get your owner ID:

```bash
curl --request GET \
  --url https://api.render.com/v1/owners \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer rnd_BypZpLEwf1wqzDjJutPdSrDHP9Iy'
```

This will return your owner information. Look for the `id` field in the "RA Perso" workspace entry.

### 3️⃣ Create Redis Instance

```bash
curl --request POST \
  --url https://api.render.com/v1/services \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer rnd_BypZpLEwf1wqzDjJutPdSrDHP9Iy' \
  --header 'Content-Type: application/json' \
  --data '{
    "type": "redis",
    "name": "brand-bos-redis",
    "ownerId": "YOUR_OWNER_ID",
    "plan": "free",
    "region": "oregon",
    "maxmemoryPolicy": "allkeys-lru"
  }'
```

### 4️⃣ Link Redis to Web Service

After both services are created, update the web service with Redis URL:

```bash
# First, get the Redis connection string from the Redis service details
# Then update the web service environment variables

curl --request PATCH \
  --url https://api.render.com/v1/services/YOUR_SERVICE_ID/env-vars \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer rnd_BypZpLEwf1wqzDjJutPdSrDHP9Iy' \
  --header 'Content-Type: application/json' \
  --data '[
    {"key": "REDIS_URL", "value": "YOUR_REDIS_CONNECTION_STRING"}
  ]'
```

## 🐍 Python Script for Easier Deployment

Save this as `deploy_to_render.py`:

```python
import requests
import json
import os
from typing import Dict, Any

# Your Render API key (locked to RA Perso workspace)
API_KEY = "rnd_BypZpLEwf1wqzDjJutPdSrDHP9Iy"
BASE_URL = "https://api.render.com/v1"

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def get_owner_id() -> str:
    """Get the owner ID for RA Perso workspace"""
    response = requests.get(f"{BASE_URL}/owners", headers=headers)
    owners = response.json()
    
    for owner in owners:
        if owner["name"] == "RA Perso":
            return owner["id"]
    
    raise ValueError("RA Perso workspace not found!")

def create_web_service(owner_id: str, env_vars: Dict[str, str]) -> Dict[str, Any]:
    """Create the Brand BOS web service"""
    
    service_config = {
        "type": "web_service",
        "name": "brand-bos-api",
        "ownerId": owner_id,
        "repo": "https://github.com/YOUR_GITHUB_USERNAME/V1_Waterfall",
        "branch": "main",
        "runtime": "docker",
        "dockerfilePath": "./Dockerfile",
        "dockerContext": ".",
        "envVars": [{"key": k, "value": v} for k, v in env_vars.items()],
        "plan": "free",
        "region": "oregon",
        "healthCheckPath": "/health"
    }
    
    response = requests.post(
        f"{BASE_URL}/services",
        headers=headers,
        json=service_config
    )
    
    return response.json()

def create_redis_service(owner_id: str) -> Dict[str, Any]:
    """Create the Redis service"""
    
    redis_config = {
        "type": "redis",
        "name": "brand-bos-redis",
        "ownerId": owner_id,
        "plan": "free",
        "region": "oregon",
        "maxmemoryPolicy": "allkeys-lru"
    }
    
    response = requests.post(
        f"{BASE_URL}/services",
        headers=headers,
        json=redis_config
    )
    
    return response.json()

def main():
    print("🚀 Deploying Brand BOS to Render (RA Perso workspace)...")
    
    # Get owner ID
    print("Getting workspace ID...")
    owner_id = get_owner_id()
    print(f"✅ Found RA Perso workspace: {owner_id}")
    
    # Environment variables
    env_vars = {
        "PORT": "8080",
        "ENVIRONMENT": "production",
        "LOG_LEVEL": "INFO",
        "SUPABASE_URL": input("Enter SUPABASE_URL: "),
        "SUPABASE_ANON_KEY": input("Enter SUPABASE_ANON_KEY: "),
        "SUPABASE_SERVICE_ROLE_KEY": input("Enter SUPABASE_SERVICE_ROLE_KEY: "),
        "ANTHROPIC_API_KEY": input("Enter ANTHROPIC_API_KEY: "),
        "SECRET_KEY": input("Enter SECRET_KEY (or press Enter to generate): ") or os.urandom(32).hex(),
        "ALLOWED_ORIGINS": "http://localhost:5173,http://localhost:3000"
    }
    
    # Create Redis
    print("\nCreating Redis service...")
    redis = create_redis_service(owner_id)
    print(f"✅ Redis created: {redis['service']['name']}")
    
    # Add Redis URL to env vars
    env_vars["REDIS_URL"] = redis["service"]["connectionString"]
    
    # Create web service
    print("\nCreating web service...")
    web_service = create_web_service(owner_id, env_vars)
    print(f"✅ Web service created: {web_service['service']['name']}")
    print(f"🌐 URL: https://{web_service['service']['name']}.onrender.com")
    
    print("\n✨ Deployment initiated! Check Render dashboard for build progress.")

if __name__ == "__main__":
    main()
```

## 🎯 Quick Deployment Steps

1. **Save the Python script** above as `deploy_to_render.py`

2. **Update GitHub username** in the script

3. **Run the script**:
   ```bash
   python deploy_to_render.py
   ```

4. **Enter your API keys** when prompted

5. **Monitor deployment** at https://dashboard.render.com

## 📝 Notes

- The API key `rnd_BypZpLEwf1wqzDjJutPdSrDHP9Iy` is workspace-locked to "RA Perso"
- Services will automatically deploy when you push to GitHub
- Free tier services spin down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds

## 🔍 Verify Deployment

Check deployment status:
```bash
curl --request GET \
  --url https://api.render.com/v1/services \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer rnd_BypZpLEwf1wqzDjJutPdSrDHP9Iy'
```

This will list all services in your "RA Perso" workspace.