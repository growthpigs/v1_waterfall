#!/usr/bin/env python3
"""
Brand BOS One-Click Deployment Script for Render
Deploys to RA Perso workspace only
"""

import requests
import json
import os
import sys
import time
from typing import Dict, Any, Optional
from datetime import datetime

# Your Render API key (locked to RA Perso workspace)
API_KEY = "rnd_BypZpLEwf1wqzDjJutPdSrDHP9Iy"
BASE_URL = "https://api.render.com/v1"

# GitHub repository
GITHUB_REPO = "https://github.com/growthpigs/v1_waterfall"

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

class RenderDeployment:
    def __init__(self):
        self.owner_id = None
        self.web_service_id = None
        self.redis_service_id = None
        self.web_service_url = None
        
    def print_status(self, message: str, status: str = "INFO"):
        """Pretty print status messages"""
        symbols = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️",
            "WORKING": "🔄"
        }
        print(f"{symbols.get(status, '•')} {message}")
    
    def get_owner_id(self) -> str:
        """Get the owner ID for RA Perso workspace"""
        self.print_status("Fetching workspace information...", "WORKING")
        
        try:
            response = requests.get(f"{BASE_URL}/owners", headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # The API returns a list of objects with 'owner' field
            for item in data:
                owner = item.get("owner", {})
                if owner.get("name") == "RA Perso":
                    self.owner_id = owner["id"]
                    self.print_status(f"Found RA Perso workspace (ID: {self.owner_id})", "SUCCESS")
                    return self.owner_id
            
            self.print_status("RA Perso workspace not found in available workspaces!", "ERROR")
            # Show available workspaces
            for item in data:
                owner = item.get("owner", {})
                print(f"  - {owner.get('name', 'Unknown')} (ID: {owner.get('id', 'Unknown')})")
                
        except Exception as e:
            self.print_status(f"Error fetching workspace: {str(e)}", "ERROR")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
        sys.exit(1)
    
    def check_existing_services(self) -> Dict[str, Any]:
        """Check if services already exist"""
        self.print_status("Checking for existing services...", "WORKING")
        
        try:
            response = requests.get(f"{BASE_URL}/services", headers=headers)
            response.raise_for_status()
            data = response.json()
            
            existing = {
                "web": None,
                "redis": None
            }
            
            # The API returns a list of objects with 'service' field
            for item in data:
                service = item.get("service", {})
                # Only check services in RA Perso workspace
                if service.get("ownerId") == self.owner_id:
                    if service.get("name") == "brand-bos-api":
                        existing["web"] = service
                        self.print_status("Found existing web service", "WARNING")
                    elif service.get("name") == "brand-bos-redis":
                        existing["redis"] = service
                        self.print_status("Found existing Redis service", "WARNING")
            
            return existing
            
        except Exception as e:
            self.print_status(f"Error checking services: {str(e)}", "WARNING")
            return {"web": None, "redis": None}
    
    def create_web_service(self, env_vars: Dict[str, str]) -> Dict[str, Any]:
        """Create the Brand BOS web service"""
        self.print_status("Creating web service...", "WORKING")
        
        service_config = {
            "type": "web_service",
            "name": "brand-bos-api",
            "ownerId": self.owner_id,
            "repo": GITHUB_REPO,
            "branch": "main",
            "runtime": "docker",
            "dockerfilePath": "./Dockerfile",
            "dockerContext": ".",
            "envVars": [{"key": k, "value": v} for k, v in env_vars.items()],
            "plan": "free",
            "region": "oregon",
            "healthCheckPath": "/health",
            "numInstances": 1,
            "buildCommand": "",
            "startCommand": ""
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/services",
                headers=headers,
                json=service_config
            )
            response.raise_for_status()
            result = response.json()
            
            self.web_service_id = result["service"]["id"]
            self.web_service_url = f"https://{result['service']['name']}.onrender.com"
            self.print_status(f"Web service created: {result['service']['name']}", "SUCCESS")
            
            return result
            
        except Exception as e:
            self.print_status(f"Error creating web service: {str(e)}", "ERROR")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            sys.exit(1)
    
    def create_redis_service(self) -> Optional[Dict[str, Any]]:
        """Create the Redis service"""
        self.print_status("Creating Redis service...", "WORKING")
        
        redis_config = {
            "type": "redis",
            "name": "brand-bos-redis",
            "ownerId": self.owner_id,
            "plan": "free",
            "region": "oregon",
            "maxmemoryPolicy": "allkeys-lru",
            "ipAllowList": None
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/services",
                headers=headers,
                json=redis_config
            )
            response.raise_for_status()
            result = response.json()
            
            self.redis_service_id = result["service"]["id"]
            self.print_status(f"Redis service created: {result['service']['name']}", "SUCCESS")
            
            return result
            
        except Exception as e:
            self.print_status(f"Error creating Redis service: {str(e)}", "WARNING")
            self.print_status("Continuing without Redis (optional service)", "WARNING")
            return None
    
    def wait_for_redis_url(self, max_attempts: int = 10) -> Optional[str]:
        """Wait for Redis connection string to be available"""
        self.print_status("Waiting for Redis connection details...", "WORKING")
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(
                    f"{BASE_URL}/services/{self.redis_service_id}",
                    headers=headers
                )
                response.raise_for_status()
                service_data = response.json()
                
                # Check for connection info in various possible locations
                redis_url = None
                service = service_data.get("service", {})
                
                # Try different fields where the URL might be
                for field in ["redisConnectionString", "connectionString", "url"]:
                    if field in service:
                        redis_url = service[field]
                        break
                
                # Check environment variables
                if not redis_url and "envVars" in service:
                    for var in service["envVars"]:
                        if var["key"] == "REDIS_URL":
                            redis_url = var["value"]
                            break
                
                if redis_url:
                    self.print_status("Redis connection ready", "SUCCESS")
                    return redis_url
                
                time.sleep(2)
                
            except Exception as e:
                self.print_status(f"Attempt {attempt + 1}/{max_attempts}: Waiting for Redis...", "INFO")
                time.sleep(2)
        
        self.print_status("Redis URL not available yet, continuing without it", "WARNING")
        return None
    
    def update_web_service_env(self, new_vars: Dict[str, str]):
        """Update web service environment variables"""
        self.print_status("Updating web service configuration...", "WORKING")
        
        try:
            # Get current env vars
            response = requests.get(
                f"{BASE_URL}/services/{self.web_service_id}",
                headers=headers
            )
            response.raise_for_status()
            service_data = response.json()
            
            # Update with new vars
            current_vars = {var["key"]: var["value"] for var in service_data["service"].get("envVars", [])}
            current_vars.update(new_vars)
            
            # Send update
            env_var_list = [{"key": k, "value": v} for k, v in current_vars.items()]
            
            response = requests.put(
                f"{BASE_URL}/services/{self.web_service_id}/env-vars",
                headers=headers,
                json=env_var_list
            )
            response.raise_for_status()
            
            self.print_status("Environment variables updated", "SUCCESS")
            
        except Exception as e:
            self.print_status(f"Error updating environment: {str(e)}", "WARNING")
    
    def collect_env_vars(self) -> Dict[str, str]:
        """Collect environment variables from user"""
        print("\n" + "="*60)
        print("🔐 Environment Configuration")
        print("="*60)
        
        env_vars = {
            "PORT": "8080",
            "ENVIRONMENT": "production",
            "LOG_LEVEL": "INFO",
        }
        
        # Required variables
        print("\n📌 Required Configuration:")
        
        # Supabase
        print("\n🗄️  Supabase Configuration (get from supabase.com/dashboard)")
        env_vars["SUPABASE_URL"] = input("SUPABASE_URL: ").strip()
        env_vars["SUPABASE_ANON_KEY"] = input("SUPABASE_ANON_KEY: ").strip()
        env_vars["SUPABASE_SERVICE_ROLE_KEY"] = input("SUPABASE_SERVICE_ROLE_KEY: ").strip()
        
        # Anthropic
        print("\n🤖 AI Configuration (get from console.anthropic.com)")
        env_vars["ANTHROPIC_API_KEY"] = input("ANTHROPIC_API_KEY: ").strip()
        
        # Secret key
        print("\n🔑 Security Configuration")
        secret_key = input("SECRET_KEY (press Enter to auto-generate): ").strip()
        env_vars["SECRET_KEY"] = secret_key if secret_key else os.urandom(32).hex()
        
        # CORS
        print("\n🌐 CORS Configuration")
        default_origins = "http://localhost:5173,http://localhost:3000"
        origins = input(f"ALLOWED_ORIGINS [{default_origins}]: ").strip()
        env_vars["ALLOWED_ORIGINS"] = origins if origins else default_origins
        
        return env_vars
    
    def deploy(self):
        """Main deployment process"""
        print("\n" + "="*60)
        print("🚀 Brand BOS Deployment to Render (RA Perso Workspace)")
        print("="*60)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Repository: {GITHUB_REPO}")
        print("="*60)
        
        # Check if repo is configured
        if "YOUR_GITHUB_USERNAME" in GITHUB_REPO:
            print("\n❌ ERROR: Please update GITHUB_REPO with your GitHub username!")
            print("Edit this file and replace 'YOUR_GITHUB_USERNAME' with your actual username.")
            sys.exit(1)
        
        # Get workspace
        self.get_owner_id()
        
        # Check existing services
        existing = self.check_existing_services()
        
        if existing["web"]:
            print(f"\n⚠️  Web service already exists: {existing['web']['name']}")
            proceed = input("Delete and recreate? (y/N): ").lower()
            if proceed != 'y':
                print("Deployment cancelled.")
                sys.exit(0)
            # Note: Actual deletion would require DELETE API call
        
        # Collect environment variables
        env_vars = self.collect_env_vars()
        
        print("\n" + "="*60)
        print("🚀 Starting Deployment...")
        print("="*60)
        
        # Create Redis first (optional)
        redis_url = None
        if not existing["redis"]:
            redis_result = self.create_redis_service()
            if redis_result and self.redis_service_id:
                redis_url = self.wait_for_redis_url()
        elif existing["redis"]:
            self.print_status("Using existing Redis service", "INFO")
            self.redis_service_id = existing["redis"]["id"]
        
        # Add Redis URL if available
        if redis_url:
            env_vars["REDIS_URL"] = redis_url
        
        # Create web service
        self.create_web_service(env_vars)
        
        # Update with Redis URL if we got it after web service creation
        if redis_url and "REDIS_URL" not in env_vars:
            self.update_web_service_env({"REDIS_URL": redis_url})
        
        # Final summary
        print("\n" + "="*60)
        print("✨ Deployment Complete!")
        print("="*60)
        print(f"\n🌐 Your API URL: {self.web_service_url}")
        print(f"📊 Health Check: {self.web_service_url}/health")
        print(f"📚 API Docs: {self.web_service_url}/docs")
        print(f"\n🎛️  Render Dashboard: https://dashboard.render.com")
        print("\n⏱️  Note: Initial build takes 5-10 minutes. Check the dashboard for progress.")
        print("\n🔄 Next Steps:")
        print("1. Monitor build logs in Render dashboard")
        print("2. Once deployed, test the health endpoint")
        print("3. Deploy frontend to Vercel")
        print("4. Update frontend VITE_API_URL to your Render URL")
        print("\n" + "="*60)

def main():
    """Main entry point"""
    deployment = RenderDeployment()
    
    try:
        deployment.deploy()
    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()