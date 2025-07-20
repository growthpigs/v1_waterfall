# 🏥 Health Check System

## Overview
Enterprise-grade health check system for the Brand BOS Waterfall monorepo.

## Available Commands

### Root Level Commands
- `npm run health:all` - Check all apps
- `npm run health:modified` - Check only modified apps (used in pre-commit)
- `npm run setup:health-system` - Setup the entire health check system

### App Level Commands (run from app directory)
- `npm run health:check` - Quick health check (format, lint, type-check, test)
- `npm run health:full` - Complete check including build and coverage
- `npm run health:ci` - CI/CD version with verbose output

## Features

### 🚀 Performance Optimizations
- Smart pre-commit hooks that only check modified apps
- Parallel execution where possible
- Efficient caching and incremental checks

### 📊 Comprehensive Testing
- Vitest for modern testing
- React Testing Library for component tests
- Coverage reporting with v8 provider
- Bundle analysis with rollup-plugin-visualizer

### 🎨 Developer Experience
- Emoji indicators for clear status
- Colored output with chalk
- Spinner animations with ora
- Detailed error reporting

### 🔧 Enterprise Features
- Pre-commit hooks with Husky
- Consistent formatting with Prettier
- TypeScript type checking
- ESLint code quality checks
- Automated dependency management

## Usage Examples

```bash
# Check all apps
npm run health:all

# Check only modified apps (faster)
npm run health:modified

# Run full health check with coverage
npm run health:all health:full

# Run CI version
npm run health:all health:ci
```

## Configuration

### Vitest Configuration
Each app has a `vitest.config.ts` with:
- React support
- JSDOM environment
- Path aliases
- Coverage thresholds

### Pre-commit Hooks
Automatically runs health checks on modified apps before commit.

## Troubleshooting

### Common Issues
1. **Dependencies not installed**: Run `npm run setup:health-system`
2. **Pre-commit hooks not working**: Check `.husky/pre-commit` permissions
3. **Tests failing**: Check `src/test/setup.ts` for proper mocking

### Debug Commands
```bash
# Check specific app
cd dashboard && npm run health:check

# Run with verbose output
npm run health:all health:ci

# Check coverage
cd dashboard && npm run test:coverage
```
