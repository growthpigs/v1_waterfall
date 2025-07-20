#!/usr/bin/env node

import { execa } from 'execa'
import chalk from 'chalk'
import ora from 'ora'
import { readFileSync, existsSync } from 'fs'
import { join } from 'path'

const APPS = ['dashboard']

class ModifiedAppsChecker {
  constructor() {
    this.results = new Map()
    this.startTime = Date.now()
  }

  async getModifiedApps() {
    try {
      // Get staged files
      const stagedResult = await execa('git', ['diff', '--cached', '--name-only'])
      const stagedFiles = stagedResult.stdout.split('\n').filter(Boolean)
      
      // Get unstaged files
      const unstagedResult = await execa('git', ['diff', '--name-only'])
      const unstagedFiles = unstagedResult.stdout.split('\n').filter(Boolean)
      
      // Combine all modified files
      const allModifiedFiles = [...new Set([...stagedFiles, ...unstagedFiles])]
      
      // Determine which apps are affected
      const modifiedApps = new Set()
      
      for (const file of allModifiedFiles) {
        for (const app of APPS) {
          if (file.startsWith(`${app}/`)) {
            modifiedApps.add(app)
          }
        }
        
        // Root level changes affect all apps
        if (!file.includes('/') || file.startsWith('package.json') || file.startsWith('scripts/')) {
          APPS.forEach(app => modifiedApps.add(app))
        }
      }
      
      return Array.from(modifiedApps)
    } catch (error) {
      console.warn(chalk.yellow('⚠️  Could not determine modified apps, checking all apps'))
      return APPS
    }
  }

  async checkApp(appName, command = 'health:check') {
    const appPath = join(process.cwd(), appName)
    const packageJsonPath = join(appPath, 'package.json')
    
    if (!existsSync(packageJsonPath)) {
      return {
        success: false,
        error: `Package.json not found in ${appName}`,
        duration: 0
      }
    }

    const packageJson = JSON.parse(readFileSync(packageJsonPath, 'utf8'))
    const appDisplayName = packageJson.name || appName

    const spinner = ora(`🏥 Running health check for ${chalk.cyan(appDisplayName)}`).start()
    const startTime = Date.now()

    try {
      const result = await execa('npm', ['run', command], {
        cwd: appPath,
        stdio: 'pipe'
      })

      const duration = Date.now() - startTime
      spinner.succeed(`✅ ${chalk.green(appDisplayName)} - Health check passed ${chalk.gray(`(${duration}ms)`)}`)
      
      return {
        success: true,
        stdout: result.stdout,
        stderr: result.stderr,
        duration
      }
    } catch (error) {
      const duration = Date.now() - startTime
      spinner.fail(`❌ ${chalk.red(appDisplayName)} - Health check failed ${chalk.gray(`(${duration}ms)`)}`)
      
      if (error.stdout) {
        console.log(chalk.gray('STDOUT:'))
        console.log(error.stdout)
      }
      
      if (error.stderr) {
        console.log(chalk.gray('STDERR:'))
        console.log(error.stderr)
      }
      
      return {
        success: false,
        error: error.message,
        stdout: error.stdout,
        stderr: error.stderr,
        duration
      }
    }
  }

  async checkModifiedApps(command = 'health:check') {
    const modifiedApps = await this.getModifiedApps()
    
    if (modifiedApps.length === 0) {
      console.log(chalk.green('✅ No modified apps detected, skipping health checks'))
      return true
    }
    
    console.log(chalk.bold.blue(`\n🏥 Running health checks for modified apps: ${modifiedApps.join(', ')}\n`))
    
    const results = new Map()
    let allPassed = true

    for (const app of modifiedApps) {
      const result = await this.checkApp(app, command)
      results.set(app, result)
      
      if (!result.success) {
        allPassed = false
      }
    }

    this.printSummary(results, allPassed, modifiedApps)
    return allPassed
  }

  printSummary(results, allPassed, modifiedApps) {
    const totalDuration = Date.now() - this.startTime
    
    console.log(chalk.bold('\n📊 Modified Apps Health Check Summary'))
    console.log('━'.repeat(50))
    
    let passedCount = 0
    let failedCount = 0
    
    for (const [app, result] of results) {
      const status = result.success ? '✅ PASS' : '❌ FAIL'
      const duration = `${result.duration}ms`
      
      console.log(`📦 ${app.padEnd(20)} ${status} ${chalk.gray(duration)}`)
      
      if (result.success) {
        passedCount++
      } else {
        failedCount++
      }
    }
    
    console.log('━'.repeat(50))
    console.log(`📈 Checked: ${modifiedApps.length} | ✅ Passed: ${passedCount} | ❌ Failed: ${failedCount}`)
    console.log(`⏱️  Total time: ${totalDuration}ms`)
    console.log(`🚀 Performance: Checked ${modifiedApps.length}/${APPS.length} apps`)
    
    if (allPassed) {
      console.log(chalk.green.bold('\n🎉 All modified apps passed health checks!'))
    } else {
      console.log(chalk.red.bold('\n💥 Some modified apps failed health checks!'))
      console.log(chalk.yellow('💡 Fix the issues above before committing'))
    }
  }
}

async function main() {
  const args = process.argv.slice(2)
  const command = args[0] || 'health:check'
  
  const checker = new ModifiedAppsChecker()
  const success = await checker.checkModifiedApps(command)
  
  process.exit(success ? 0 : 1)
}

main().catch(error => {
  console.error(chalk.red('💥 Modified apps health check error:'), error)
  process.exit(1)
}) 