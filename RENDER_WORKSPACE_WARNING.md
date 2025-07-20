# ⚠️ CRITICAL: Workspace Selection for Render Deployment

## WORKSPACE INFORMATION

### ✅ CORRECT Workspace: **RA Perso**
This is where Brand BOS should be deployed.

### ❌ WRONG Workspace: **Think Big Media**  
DO NOT deploy here - this is for a different project.

## Agent Instructions Summary

The browser agent MUST:

1. **FIRST ACTION**: Switch to "RA Perso" workspace
   - Click workspace selector (top-left corner)
   - Select "RA Perso" from dropdown
   - Verify it shows "RA Perso" before proceeding

2. **VERIFY**: Never proceed if workspace shows "Think Big Media"

3. **THEN**: Follow the rest of the deployment instructions

## Why This Matters

- Deploying in wrong workspace will mix up projects
- Billing goes to wrong account
- Resources get confused between projects
- Hard to untangle later

## Quick Check for Agent

Before creating any resources:
```
Current Workspace: RA Perso ✅
NOT: Think Big Media ❌
```

Only proceed when workspace is confirmed correct!