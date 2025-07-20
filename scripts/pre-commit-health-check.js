#!/usr/bin/env node

import { execSync } from 'child_process';
import { existsSync } from 'fs';
import { join } from 'path';

console.log('🏥 Running pre-commit health checks...\n');

// Get list of changed files
let changedFiles = [];
try {
  const output = execSync('git diff --cached --name-only', { encoding: 'utf8' });
  changedFiles = output.trim().split('\n').filter(Boolean);
} catch (error) {
  console.log('❌ Failed to get changed files');
  process.exit(1);
}

// Determine which apps have changes
const appsToCheck = new Set();
for (const file of changedFiles) {
  if (file.startsWith('dashboard/')) {
    appsToCheck.add('dashboard');
  }
}

if (appsToCheck.size === 0) {
  console.log('✅ No app changes detected, skipping health checks');
  process.exit(0);
}

console.log(`📦 Apps with changes: ${Array.from(appsToCheck).join(', ')}\n`);

let allPassed = true;

for (const app of appsToCheck) {
  const appPath = join(process.cwd(), app);
  
  if (!existsSync(appPath)) {
    console.log(`❌ App ${app} not found`);
    allPassed = false;
    continue;
  }
  
  console.log(`🔍 Checking ${app}...`);
  
  try {
    execSync('npm run health:check', { 
      cwd: appPath, 
      stdio: 'inherit' 
    });
    console.log(`✅ ${app} passed health checks\n`);
  } catch (error) {
    console.log(`❌ ${app} failed health checks\n`);
    allPassed = false;
  }
}

if (allPassed) {
  console.log('🎉 All changed apps passed health checks!');
  process.exit(0);
} else {
  console.log('💥 Some apps failed health checks - commit blocked');
  process.exit(1);
} 