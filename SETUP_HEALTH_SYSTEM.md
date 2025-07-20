# 🚀 Health Check System Setup

## Quick Start

Run this command to set up the entire health check system:

```bash
npm run setup:health-system
```

## What This Sets Up

1. **Root Dependencies**: Installs monorepo management tools
2. **App Dependencies**: Installs testing and development dependencies
3. **Husky Hooks**: Sets up pre-commit health checks
4. **Configuration Files**: Creates vitest, prettier, and other configs
5. **Sample Tests**: Creates basic test infrastructure
6. **Documentation**: Generates comprehensive docs

## Manual Setup Steps

If you need to set up manually:

### 1. Install Root Dependencies
```bash
npm install --legacy-peer-deps
```

### 2. Install App Dependencies
```bash
cd dashboard
npm install --legacy-peer-deps
```

### 3. Setup Husky
```bash
npx husky install
chmod +x .husky/pre-commit
```

### 4. Run Initial Health Check
```bash
npm run health:all
```

## Verification

After setup, verify everything works:

```bash
# Test the health check system
npm run health:all

# Test pre-commit hooks
git add .
git commit -m "test commit"
```

## Next Steps

1. Review the generated documentation
2. Run your first health check
3. Make a test commit to verify pre-commit hooks
4. Start developing with confidence!
