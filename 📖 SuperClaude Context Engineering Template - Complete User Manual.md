📖 SuperClaude Context Engineering Template - Complete User Manual
🚀 Getting Started
Step 1: Project Setup
For New Projects:
# Clone the template
git clone https://github.com/yourusername/context-engineering-template my-project
cd my-project

# Remove template git history and make it yours
rm -rf .git
git init
git add .
git commit -m "Initial commit from SuperClaude Context Engineering template"
For Existing Projects:
# Copy SuperClaude commands to your existing project
cp -r /path/to/template/.claude/commands/superclaude /your-project/.claude/commands/
cp /path/to/template/CLAUDE.md /your-project/CLAUDE.md
# Update your existing CLAUDE.md with SuperClaude methodology
Step 2: Configure MCP Servers
Open your Claude Desktop configuration file:
	•	Mac: ~/Library/Application Support/Claude/claude_desktop_config.json
	•	Windows: %APPDATA%/Claude/claude_desktop_config.json
Replace the content with:
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"],
      "autoApprove": ["resolve-library-id", "get-library-docs"]
    },
    "perplexity-ask": {
      "command": "npx",
      "args": ["-y", "server-perplexity-ask"],
      "env": {
        "PERPLEXITY_API_KEY": "YOUR_PERPLEXITY_API_KEY_HERE"
      },
      "autoApprove": ["search", "get_documentation"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "config": {
        "paths": ["./", "./src", "./docs"]
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_GITHUB_TOKEN_HERE"
      }
    }
  }
}
Get Your API Keys:
	•	Perplexity: Go to https://www.perplexity.ai/settings/api
	•	GitHub: Go to https://github.com/settings/tokens
Restart Claude Desktop completely (Cmd+Q on Mac, then reopen)
Step 3: Initialize Your Project
Open Claude Code in your project directory and run this exact prompt:
# Project Initialization Instructions - SuperClaude Enhanced

You are Claude Code with SuperClaude v2.0.1 framework integration. Please follow these steps:

1. **Load Project Context**
   Use: /load --full --analyze --persona-architect --c7 --summary
   This provides comprehensive project understanding

2. **Initialize Checkpoint System**
   - Create CHECKPOINTS directory if it doesn't exist
   - Copy checkpoint-template.md from the template
   - Create initial checkpoint: CHECKPOINTS/YYYY-MM-DD/00-00-initialization.md

3. **Generate Initial Assessment**
   Use: /analyze --architecture --persona-architect --seq --evidence
   Include:
   - Project understanding summary
   - Technology stack confirmation
   - Initial risks or concerns identified
   - Development strategy recommendations

4. **Create First Checkpoint**
   Document the initialization process and findings

Remember: 
- Always use SuperClaude commands for development tasks
- Apply appropriate personas for specialized expertise
- Create checkpoints every 3 hours OR at major milestones
- Use MCP servers for real-time research when needed
- Document all decisions in checkpoints with evidence
🧠 Understanding SuperClaude Commands
Core Commands (9)
/build - Build Projects, Features & Components
Purpose: Create new projects, features, or components with modern best practices
Basic Usage:
/build --react --ts --magic --persona-frontend --c7
/build --feature "user authentication" --tdd --persona-security
/build --api --openapi --validate --persona-backend --c7
Key Flags:
	•	--react, --vue, --angular - Frontend frameworks
	•	--api, --rest, --graphql - Backend types
	•	--feature "name" - Specific feature building
	•	--tdd - Test-driven development
	•	--magic - AI-generated UI components
	•	--openapi - Generate API documentation
/analyze - Comprehensive Analysis
Purpose: Analyze code, architecture, performance, or security
Basic Usage:
/analyze --code --persona-qa --think --evidence
/analyze --architecture --persona-architect --seq
/analyze --security --persona-security --c7
/analyze --performance --persona-performance --pup
Key Flags:
	•	--code - Code quality analysis
	•	--architecture - System design analysis
	•	--security - Security vulnerability analysis
	•	--performance - Performance bottleneck analysis
	•	--think, --think-hard, --ultrathink - Analysis depth
/test - Comprehensive Testing
Purpose: Create and run tests with full coverage
Basic Usage:
/test --unit --integration --coverage --persona-qa
/test --e2e --pup --persona-qa --strict
/test --security --owasp --persona-security
/test --performance --load --persona-performance --pup
Key Flags:
	•	--unit - Unit testing
	•	--integration - Integration testing
	•	--e2e - End-to-end testing
	•	--coverage - Code coverage analysis
	•	--strict - Strict testing standards
/scan - Security & Validation Scanning
Purpose: Security audits and code validation
Basic Usage:
/scan --security --owasp --deps --persona-security
/scan --validate --deps --persona-security --evidence
/scan --security --compliance --owasp --persona-security
Key Flags:
	•	--security - Security vulnerability scan
	•	--owasp - OWASP Top 10 compliance
	•	--deps - Dependency vulnerability scan
	•	--validate - Code validation
	•	--compliance - Regulatory compliance check
/troubleshoot - Advanced Debugging
Purpose: Debug issues with systematic root cause analysis
Basic Usage:
/troubleshoot --prod --five-whys --persona-analyzer --seq
/troubleshoot --performance --profile --persona-performance --pup
/troubleshoot --security --investigate --persona-security --timeline
/troubleshoot --debug --logs --persona-analyzer --seq
Key Flags:
	•	--prod - Production environment issues
	•	--five-whys - Root cause analysis methodology
	•	--investigate - Systematic investigation
	•	--debug - General debugging
	•	--logs - Log analysis approach
/deploy - Production Deployment
Purpose: Safe production deployment with validation
Basic Usage:
/deploy --env prod --plan --validate --persona-architect
/deploy --staging --smoke-test --persona-qa
/deploy --rollback --version v1.2.3 --persona-analyzer
/deploy --canary --percentage 10 --monitor --persona-architect
Key Flags:
	•	--env prod|staging|dev - Target environment
	•	--plan - Create deployment plan first
	•	--validate - Pre-deployment validation
	•	--rollback - Rollback to previous version
	•	--canary - Canary deployment strategy
/review - AI-Powered Code Review
Purpose: Comprehensive code review with evidence
Basic Usage:
/review --files src/ --quality --evidence --persona-qa
/review --pr --security --persona-security --c7
/review --architecture --persona-architect --seq
/review --performance --persona-performance --pup
Key Flags:
	•	--files path/ - Review specific files/directories
	•	--pr - Pull request review
	•	--quality - Code quality review
	•	--security - Security-focused review
	•	--evidence - Include evidence-based recommendations
/improve - Code & System Optimization
Purpose: Optimize performance, security, and code quality
Basic Usage:
/improve --performance --threshold 95% --persona-performance --pup
/improve --security --owasp --persona-security --evidence
/improve --quality --refactor --persona-refactorer --c7
/improve --architecture --scalability --persona-architect
Key Flags:
	•	--performance - Performance optimization
	•	--security - Security improvements
	•	--quality - Code quality enhancement
	•	--threshold X% - Set performance threshold
	•	--refactor - Code refactoring focus
/load - Project Context Loading
Purpose: Load and analyze comprehensive project context
Basic Usage:
/load --full --analyze --persona-architect --c7 --summary
/load --files src/ --persona-qa --metrics --health
/load --docs --examples --persona-mentor --summary
/load --fresh --rebuild-context --persona-architect
Key Flags:
	•	--full - Complete project context (default)
	•	--fresh - Rebuild context from scratch
	•	--analyze - Include context analysis
	•	--summary - Generate project summary
	•	--health - Include project health assessment
Template-Specific Commands (2)
/generate-prp - Generate Product Requirements Prompt
Purpose: Create comprehensive feature specifications
Usage:
/generate-prp INITIAL.md
What it does:
	1	Reads your INITIAL.md file
	2	Analyzes feature requirements
	3	Gathers context from examples and docs
	4	Creates comprehensive PRP in /PRPs/[feature-name].md
/execute-prp - Execute Product Requirements Prompt
Purpose: Implement features with validation and checkpoints
Usage:
/execute-prp PRPs/feature-name.md
What it does:
	1	Loads the PRP file
	2	Implements features step-by-step
	3	Creates checkpoints at milestones
	4	Runs validation after each step
	5	Generates implementation report
🎭 Using Cognitive Personas
When to Use Each Persona
--persona-architect - Systems Thinking
Use for:
	•	System design and architecture
	•	Database schema design
	•	API architecture planning
	•	Scalability planning
	•	Technology stack decisions
Example:
/build --api --microservices --persona-architect --seq
/analyze --architecture --persona-architect --evidence
/deploy --env prod --plan --persona-architect
--persona-security - Security-First Analysis
Use for:
	•	Security audits and scans
	•	Authentication/authorization systems
	•	OWASP compliance
	•	Vulnerability assessments
	•	Security-critical features
Example:
/build --auth --oauth2 --persona-security --c7
/scan --security --owasp --persona-security --evidence
/review --security --persona-security --evidence
--persona-qa - Quality Assurance
Use for:
	•	Testing strategies
	•	Code quality reviews
	•	QA processes
	•	Bug investigation
	•	Quality metrics
Example:
/test --coverage --e2e --persona-qa --pup --strict
/review --quality --evidence --persona-qa --c7
/analyze --code --persona-qa --evidence
--persona-performance - Optimization Focus
Use for:
	•	Performance optimization
	•	Bottleneck identification
	•	Load testing
	•	Resource optimization
	•	Performance monitoring
Example:
/improve --performance --threshold 95% --persona-performance --pup
/analyze --performance --persona-performance --evidence
/test --performance --load --persona-performance --pup
--persona-frontend - UX-Focused Development
Use for:
	•	UI/UX development
	•	Component creation
	•	Frontend architecture
	•	User experience optimization
	•	Accessibility
Example:
/build --react --components --persona-frontend --magic
/improve --ux --accessibility --persona-frontend --validate
/review --ui --persona-frontend --evidence
--persona-backend - Server Systems Expertise
Use for:
	•	API development
	•	Database operations
	•	Server architecture
	•	Backend optimization
	•	Integration development
Example:
/build --api --rest --openapi --persona-backend --c7
/analyze --database --persona-backend --seq
/troubleshoot --performance --database --persona-backend
--persona-analyzer - Problem-Solving Focus
Use for:
	•	Debugging complex issues
	•	Root cause analysis
	•	Investigation processes
	•	Problem-solving
	•	Systematic analysis
Example:
/troubleshoot --investigate --five-whys --persona-analyzer --seq
/analyze --issue --persona-analyzer --evidence
/review --bugs --persona-analyzer --systematic
--persona-refactorer - Code Quality Improvement
Use for:
	•	Code refactoring
	•	Technical debt reduction
	•	Code quality improvements
	•	Design pattern implementation
	•	Code organization
Example:
/improve --quality --refactor --persona-refactorer --c7
/analyze --code --persona-refactorer --evidence
/review --refactor --persona-refactorer --suggestions
--persona-mentor - Knowledge Sharing
Use for:
	•	Documentation creation
	•	Onboarding materials
	•	Knowledge transfer
	•	Educational content
	•	Training materials
Example:
/load --docs --examples --persona-mentor --summary
/review --documentation --persona-mentor --educational
/improve --documentation --persona-mentor --clarity
🌐 MCP Server Usage
Context7 (--c7) - Library Documentation
Best for:
	•	Library-specific implementation
	•	API documentation lookup
	•	Version-specific features
	•	Best practices for specific libraries
Usage Examples:
/build --react --hooks --persona-frontend --c7
/analyze --dependencies --persona-architect --c7
/improve --libraries --upgrade --persona-refactorer --c7
What it provides:
	•	Up-to-date documentation for 20,000+ libraries
	•	Version-specific API references
	•	Implementation examples
	•	Best practices
Sequential (--seq) - Multi-Step Reasoning
Best for:
	•	Complex problem-solving
	•	Systematic analysis
	•	Step-by-step planning
	•	Root cause analysis
Usage Examples:
/troubleshoot --investigate --five-whys --persona-analyzer --seq
/analyze --architecture --persona-architect --seq
/deploy --env prod --plan --persona-architect --seq
What it provides:
	•	Systematic thinking processes
	•	Step-by-step analysis
	•	Logical reasoning chains
	•	Complex problem breakdown
Magic (--magic) - AI-Generated UI Components
Best for:
	•	UI component generation
	•	Frontend development
	•	Design system creation
	•	Component optimization
Usage Examples:
/build --component "DataTable" --persona-frontend --magic
/improve --ui --components --persona-frontend --magic
/build --react --dashboard --persona-frontend --magic
What it provides:
	•	AI-generated React/Vue/Angular components
	•	Design system integration
	•	Responsive design patterns
	•	Accessibility compliance
Puppeteer (--pup) - Browser Automation
Best for:
	•	E2E testing
	•	Performance testing
	•	Browser automation
	•	UI testing
Usage Examples:
/test --e2e --persona-qa --pup
/improve --performance --frontend --persona-performance --pup
/test --visual --regression --persona-qa --pup
What it provides:
	•	Browser automation for testing
	•	Performance metrics collection
	•	Screenshot and visual testing
	•	User interaction simulation
📋 Complete Development Workflows
🚀 New Feature Development
Step 1: Define the Feature Create or update INITIAL.md:
## FEATURE
Build user authentication with JWT tokens and OAuth2 support

## TECHNICAL REQUIREMENTS
- JWT token-based authentication
- OAuth2 integration (Google, GitHub)
- Password reset functionality
- Multi-factor authentication support
- Session management

## SUPERCLAUDE APPROACH
- Use --persona-security for security-first implementation
- Use --persona-backend for API development
- Use --c7 for OAuth2 library documentation
- Include comprehensive testing with --persona-qa

## EXAMPLES
- /examples/auth/jwt-implementation.js
- /examples/oauth/google-integration.js
Step 2: Generate Comprehensive Specification
/generate-prp INITIAL.md
Step 3: Load Project Context
/load --full --analyze --persona-architect --c7 --summary
Step 4: Implement with Security Focus
/build --feature "user authentication" --tdd --persona-security --c7
Step 5: Comprehensive Testing
/test --integration --coverage --persona-qa --pup
/test --security --auth --persona-security --evidence
Step 6: Security Validation
/scan --security --owasp --auth --persona-security --evidence
Step 7: Code Review
/review --feature auth --quality --security --persona-qa --evidence
Step 8: Performance Optimization
/improve --performance --auth --persona-performance --validate
Step 9: Documentation & Deployment
/deploy --env staging --validate --smoke-test --persona-architect
🔍 Code Quality Improvement
Step 1: Comprehensive Analysis
/analyze --code --persona-refactorer --evidence --c7
Step 2: Security & Dependency Audit
/scan --validate --deps --security --persona-security --evidence
Step 3: Performance Analysis
/analyze --performance --persona-performance --pup --evidence
Step 4: Apply Improvements
/improve --quality --refactor --persona-refactorer --iterate
/improve --performance --threshold 95% --persona-performance --pup
/improve --security --owasp --persona-security --evidence
Step 5: Validation Testing
/test --coverage --strict --persona-qa --evidence
/test --performance --load --persona-performance --pup
Step 6: Final Review
/review --improvements --quality --persona-qa --evidence
🐛 Debugging & Troubleshooting
Step 1: Issue Investigation
/troubleshoot --investigate --five-whys --persona-analyzer --seq
Step 2: Code Analysis
/analyze --code --issue --persona-qa --evidence --c7
Step 3: Performance Investigation (if applicable)
/troubleshoot --performance --profile --persona-performance --pup
Step 4: Security Check (if applicable)
/troubleshoot --security --investigate --persona-security --timeline
Step 5: Validation Through Testing
/test --unit --coverage --persona-qa --evidence
/test --integration --affected-areas --persona-qa
Step 6: Root Cause Documentation
# The troubleshoot command automatically creates comprehensive reports
# Review the generated report in DAILY_REPORTS/
🚀 Production Deployment
Step 1: Pre-Deployment Security Check
/scan --security --owasp --deps --persona-security --evidence
Step 2: Comprehensive Testing
/test --coverage --e2e --strict --persona-qa --pup
/test --performance --load --persona-performance --pup
Step 3: Code Quality Review
/review --final --quality --security --persona-qa --evidence
Step 4: Deployment Planning
/deploy --env prod --plan --validate --persona-architect
Step 5: Staged Deployment
# First to staging
/deploy --env staging --validate --smoke-test --persona-architect

# Then to production with safety measures
/deploy --env prod --canary --percentage 10 --monitor --persona-architect
Step 6: Post-Deployment Validation
/test --smoke --production --persona-qa --pup
/analyze --performance --production --persona-performance --pup
📊 Checkpoint System Usage
Automatic Checkpoints
SuperClaude commands automatically create checkpoints:
	•	Before starting major operations
	•	After completing significant milestones
	•	When encountering errors
	•	At the end of successful operations
Manual Checkpoint Creation
# Create immediate checkpoint
./checkpoint-system/scripts/create-checkpoint.sh

# Or manually
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H-%M)
cp CHECKPOINTS/checkpoint-template.md "CHECKPOINTS/${DATE}/${TIME}-checkpoint.md"
Checkpoint Recovery
# List available checkpoints
git branch -a | grep checkpoint

# View checkpoint content
cat CHECKPOINTS/2025-01-15/14-30-checkpoint.md

# Recover from checkpoint
git checkout checkpoint/2025-01-15-1430
git checkout -b recovery-from-checkpoint

# Continue work from recovery point
What to Include in Checkpoints
	•	Commands executed and flags used
	•	Personas applied and reasoning
	•	MCP servers accessed and findings
	•	Decisions made and evidence
	•	Code changes and validation results
	•	Performance metrics
	•	Next steps and recommendations
🚨 Common Issues & Troubleshooting
SuperClaude Commands Not Working
Issue: Commands not recognized
# Solution 1: Verify you're in correct directory
ls .claude/commands/superclaude/
# Should show: build.md, analyze.md, test.md, etc.

# Solution 2: Restart Claude Code
# Exit and restart Claude Code completely

# Solution 3: Check file permissions
chmod +r .claude/commands/superclaude/*.md
Issue: Persona flags not working
# Verify correct syntax (note the double dashes)
/build --react --persona-frontend  # ✅ Correct
/build --react -persona-frontend   # ❌ Wrong
/build --react persona-frontend    # ❌ Wrong
MCP Server Issues
Issue: Context7 not working
# Check if Context7 is installed
npx @upstash/context7-mcp@latest --version

# Restart Claude Desktop
# Cmd+Q on Mac, then reopen

# Check MCP server status in Claude Code
/mcp
Issue: Perplexity API not working
# Verify API key in config
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Check API key validity at https://www.perplexity.ai/settings/api

# Restart Claude Desktop after config changes
Issue: "Permission denied" errors
# Fix file permissions
chmod -R 755 .claude/

# Ensure MCP config file is readable
chmod 644 ~/Library/Application\ Support/Claude/claude_desktop_config.json
Checkpoint Issues
Issue: Checkpoint creation fails
# Verify git is initialized
git status

# Create directories if missing
mkdir -p CHECKPOINTS/$(date +%Y-%m-%d)

# Check script permissions
chmod +x checkpoint-system/scripts/create-checkpoint.sh
Issue: Can't recover from checkpoint
# List all checkpoint branches
git branch -a | grep checkpoint

# If no checkpoint branches exist, check commit history
git log --oneline | grep CHECKPOINT

# Recover from commit instead
git checkout [commit-hash]
git checkout -b recovery-branch
Performance Issues
Issue: Commands run slowly
# Use ultra-compressed mode for large projects
/analyze --code --persona-qa --uc

# Limit scope to specific files
/review --files src/components/ --persona-qa

# Use lighter analysis modes
/analyze --code --think  # instead of --ultrathink
Issue: MCP timeouts
# Check internet connection
ping google.com

# Try without MCP servers first
/analyze --code --persona-qa --no-mcp

# Use only essential MCP servers
/build --react --persona-frontend --c7  # Only Context7
📈 Advanced Usage Tips
Combining Multiple Personas
# For complex features requiring multiple expertises
/build --feature "payment system" --tdd --persona-security --persona-backend --c7

# For comprehensive reviews
/review --pr --quality --security --persona-qa --persona-security --evidence
Optimizing MCP Usage
# Use Context7 for library-specific work
/build --react --hooks --persona-frontend --c7

# Use Sequential for complex problem-solving
/troubleshoot --investigate --complex-issue --persona-analyzer --seq

# Combine MCP servers for comprehensive analysis
/analyze --architecture --persona-architect --c7 --seq --evidence
Token Optimization
# Use ultra-compressed mode for large projects
/analyze --codebase --persona-architect --uc

# Focus on specific areas
/review --files src/critical/ --persona-qa --evidence

# Use lighter thinking modes for routine tasks
/analyze --code --think  # Instead of --ultrathink
Evidence-Based Development
# Always include evidence for decision-making
/analyze --architecture --persona-architect --evidence
/improve --performance --persona-performance --evidence
/scan --security --persona-security --evidence

# Use evidence to validate decisions
/review --decisions --evidence --persona-architect
🎯 Success Metrics to Track
Development Velocity
	•	Features per sprint: Track completed features
	•	Time to production: Measure feature delivery speed
	•	Code quality scores: Monitor improvement trends
	•	Bug reduction: Track defect rates
Quality Improvements
	•	Test coverage: Target 85%+ coverage
	•	Security scores: Monitor OWASP compliance
	•	Performance metrics: Track optimization gains
	•	Code review efficiency: Measure review completion time
Team Productivity
	•	Onboarding time: Track new developer productivity
	•	Knowledge transfer: Measure documentation effectiveness
	•	Deployment frequency: Track release velocity
	•	Rollback rates: Monitor deployment safety
🔄 Daily Workflow Recommendations
Morning (Start of Development)
# 1. Load fresh project context
/load --fresh --analyze --persona-architect --c7

# 2. Review any overnight changes
/analyze --changes --since yesterday --persona-qa

# 3. Create morning checkpoint
# (Automatic with SuperClaude commands)
During Development
# Use appropriate commands for each task
/build --feature "new-feature" --tdd --persona-[appropriate] --c7
/test --integration --coverage --persona-qa --pup
/review --code --persona-qa --evidence

# Create checkpoints every 3 hours or at major milestones
# (Automatic with SuperClaude commands)
End of Day
# 1. Final code review
/review --todays-work --quality --persona-qa --evidence

# 2. Create end-of-day checkpoint
/load --summary --todays-progress --persona-mentor

# 3. Plan tomorrow's work
# (Use checkpoint findings for next session planning)

This manual covers everything you need to effectively use your SuperClaude-enhanced Context Engineering template. Start with the basic workflows and gradually incorporate more advanced features as you become comfortable with the system.
Remember: Always use SuperClaude commands for development tasks and apply appropriate personas for specialized expertise. The system is designed to provide you with an AI development team with domain-specific knowledge!
