#!/usr/bin/env node

import { execa } from 'execa'
import chalk from 'chalk'
import ora from 'ora'
import { readFileSync, existsSync } from 'fs'
import { join } from 'path'

const APPS = ['dashboard']
const HEALTH_COMMANDS = ['health:check', 'health:full', 'health:ci']

class HealthChecker {
  constructor() {
    this.results = new Map()
    this.startTime = Date.now()
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

  async checkAllApps(command = 'health:check') {
    console.log(chalk.bold.blue(`\n🏥 Starting health check for all apps with command: ${command}\n`))
    
    const results = new Map()
    let allPassed = true

    for (const app of APPS) {
      const result = await this.checkApp(app, command)
      results.set(app, result)
      
      if (!result.success) {
        allPassed = false
      }
    }

    this.printSummary(results, allPassed)
    return allPassed
  }

  printSummary(results, allPassed) {
    const totalDuration = Date.now() - this.startTime
    
    console.log(chalk.bold('\n📊 Health Check Summary'))
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
    console.log(`📈 Total: ${passedCount + failedCount} | ✅ Passed: ${passedCount} | ❌ Failed: ${failedCount}`)
    console.log(`⏱️  Total time: ${totalDuration}ms`)
    
    if (allPassed) {
      console.log(chalk.green.bold('\n🎉 All health checks passed!'))
    } else {
      console.log(chalk.red.bold('\n💥 Some health checks failed!'))
    }
  }
}

async function main() {
  const args = process.argv.slice(2)
  const command = args[0] || 'health:check'
  
  if (!HEALTH_COMMANDS.includes(command)) {
    console.error(chalk.red(`❌ Invalid command: ${command}`))
    console.error(chalk.yellow(`Available commands: ${HEALTH_COMMANDS.join(', ')}`))
    process.exit(1)
  }

  const checker = new HealthChecker()
  const success = await checker.checkAllApps(command)
  
  process.exit(success ? 0 : 1)
}

main().catch(error => {
  console.error(chalk.red('💥 Health check system error:'), error)
  process.exit(1)
}) 