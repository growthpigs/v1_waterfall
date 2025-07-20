# CLAUDE.md - Brand BOS Project Rules and Context

## Project Overview - Brand BOS
**Brand BOS** is a professional services authority platform implementing the Authority Avalanche methodology for financial advisors and professional service firms. The platform transforms client testimonials into narrative-driven content across multiple channels to establish thought leadership and generate qualified leads.

## Technology Stack - Brand BOS
- **Frontend**: React + Next.js + TypeScript + Tailwind CSS
- **Content Management**: Automated testimonial transformation workflows
- **Distribution**: Multi-channel content automation (LinkedIn, email, blog)
- **Analytics**: Content performance and engagement tracking
- **Authentication**: Professional client portal access
- **Deployment**: Vercel with CDN optimization

## CRITICAL: SuperClaude Integration for Brand BOS

### Always Use SuperClaude Commands for Development
- **NEVER use traditional prompts** - Always use SuperClaude commands
- **ALWAYS apply appropriate personas** for specialized expertise
- **INCLUDE Brand BOS context flags** in every command
- **USE MCP servers** for enhanced development capabilities

### SuperClaude Command Priority for Brand BOS
1. **`/load`** - Always start with project context loading
2. **`/analyze`** - Analyze issues before fixing
3. **`/improve`** - Fix identified problems
4. **`/build`** - Rebuild components when needed

## CRITICAL: Notification System

You MUST use the notification system to alert the user BEFORE asking questions or when tasks complete:

### When to Send Notifications

1. **BEFORE asking ANY yes/no question**:
   ```bash
   /Users/rodericandrews/WarRoom_Development/1.0-war-room/scripts/claude-notify-unified.sh approval "Your question here" "What will happen next"
   ```
   Then display the question.

2. **After completing a task**:
   ```bash
   /Users/rodericandrews/WarRoom_Development/1.0-war-room/scripts/claude-notify-unified.sh complete "What was accomplished" "Next steps available"
   ```
   Always provide next options.

3. **When asking what to do next**:
   ```bash
   /Users/rodericandrews/WarRoom_Development/1.0-war-room/scripts/claude-notify-unified.sh next "Current status" "1. Option 1\n2. Option 2\n3. Option 3"
   ```
   Never leave user without clear next steps.

4. **When errors occur**:
   ```bash
   /Users/rodericandrews/WarRoom_Development/1.0-war-room/scripts/claude-notify-unified.sh error "What went wrong" "How to fix it"
   ```

### How It Works
- Displays the full message text first
- Sends notification to Apple Watch (shows as 🚨 APPROVAL, ✅ COMPLETE, etc.)
- Plays distinct sound on Mac (Frog, Glass, Pop, or Sosumi)
- User arrives to see completed text, ready to respond

### Example Usage
```bash
# About to run a command that needs approval
/Users/rodericandrews/WarRoom_Development/1.0-war-room/scripts/claude-notify-unified.sh approval "Run database migration?" "This will update the schema"

# Task completed
/Users/rodericandrews/WarRoom_Development/1.0-war-room/scripts/claude-notify-unified.sh complete "Monitoring system implemented" "Ready to test or move to next task"
```

IMPORTANT: The script path must be exact. Notifications won't work without calling this script.

## Brand BOS Specific Development Rules

### Layout Issues (CURRENT PRIORITY)
**ALWAYS use these commands for layout problems:**
```bash
/analyze --layout --sidebar --spacing --persona-frontend --professional-services --evidence
/improve --layout --sidebar-spacing --persona-frontend --professional-services --magic
/build --component "ComponentName" --layout-fix --persona-frontend --professional-services
```

### Professional Services UI Standards
- **Clean, trustworthy design** that builds authority and credibility
- **Consistent spacing** between sidebar and content (24px standard)
- **Background differentiation** between sidebar and main content areas
- **Theme-independent layout** - structure stays same regardless of color
- **Mobile-responsive** design for professional audiences

### Authority Avalanche Methodology Integration
- **Testimonial transformation** workflows using Frank Kern narrative approach
- **Multi-channel content distribution** automation
- **Authority measurement** and analytics integration
- **Professional services workflow** optimization

## Mandatory SuperClaude Usage Patterns

### For Layout Issues (Your Current Problem)
```bash
# ALWAYS start with context loading
/load --full --analyze --persona-frontend --professional-services --c7

# Analyze the specific issue
/analyze --layout --sidebar --spacing --persona-frontend --professional-services --evidence

# Fix the identified problems
/improve --layout --sidebar-spacing --theme-consistency --persona-frontend --professional-services --magic
```

### For Component Problems
```bash
# Component analysis
/analyze --components --consistency --persona-frontend --authority-content --c7

# Component improvement
/improve --components --cross-page-consistency --persona-frontend --professional-services --magic

# Component rebuilding if needed
/build --component "ComponentName" --professional-services --persona-frontend --magic
```

### For Authority Content Features
```bash
# Authority content development
/build --component "TestimonialCard" --authority-content --persona-mentor --magic

# Content workflow automation  
/build --workflow "authority-avalanche" --content-automation --persona-architect --seq
```

## Required Personas for Brand BOS

### Primary Personas (Use Most Often)
- **`--persona-frontend`** - React/Next.js UI expertise (CRITICAL for layout issues)
- **`--persona-mentor`** - Authority Avalanche content strategy
- **`--persona-architect`** - System and workflow design

### Secondary Personas (Use When Needed)
- **`--persona-performance`** - Content delivery optimization
- **`--persona-security`** - Professional services compliance
- **`--persona-qa`** - Quality assurance and testing

## Required MCP Integration

### Essential MCP Servers for Brand BOS
- **`--c7`** - React/Next.js and CSS documentation (ALWAYS use for frontend work)
- **`--magic`** - Professional services UI components (ALWAYS use for UI building)
- **`--evidence`** - Detailed explanations (ALWAYS use for learning)

### MCP Usage Rules
- **Layout work** → `--c7` + `--evidence` + `--magic`
- **Component building** → `--magic` + `--c7` + `--professional-services`
- **Problem analysis** → `--evidence` + `--c7`

## Brand BOS Specific Flags (MANDATORY)

### Always Include These Context Flags
- **`--professional-services`** - Professional services UI patterns and standards
- **`--authority-content`** - Authority Avalanche content workflows (when applicable)

### Layout Specific Flags
- **`--layout`** - Layout structure and spacing issues
- **`--sidebar-spacing`** - Sidebar layout problems (current priority)
- **`--theme`** - Theme color consistency issues
- **`--spacing`** - Spacing standardization

## Code Standards for Brand BOS

### CSS Architecture Requirements
- **CSS custom properties** for consistent spacing across themes
- **Background contrast system** for all color variations
- **Professional services design tokens** implementation
- **Responsive layout** that works with all themes

### React Component Standards
- **Consistent component structure** across all pages
- **Professional services appropriate** styling and behavior
- **Theme-independent** component architecture
- **Authority content optimized** display patterns

## Testing Requirements for Brand BOS

### Layout Testing (CRITICAL)
```bash
/test --layout --themes --persona-frontend --professional-services --evidence
```
- Test layout consistency across all theme colors
- Validate professional services design standards
- Ensure responsive behavior on all devices

### Component Testing
```bash
/test --components --consistency --persona-frontend --authority-content --evidence
```
- Test component behavior across different pages
- Validate styling consistency and inheritance
- Ensure professional services compliance

## RESOLVED Issues (Session 2025-01-14)

### 1. Sidebar Layout Inconsistency (RESOLVED ✅)
**Problem**: Orange theme missing background differentiation, excessive spacing
**Solution Applied**: Fixed Content Calendar orange theme gradient inconsistency
- Fixed `from-[#a05a2c] via-[#d2691e] to-[#7c3f14]` → `from-orange-600 via-orange-700 to-orange-800`
- Fixed cluster colors to match theme constants
- Created theme-independent CSS variables system

### 2. Cross-Theme Layout Standardization (RESOLVED ✅)
**Problem**: Different layouts for different theme colors
**Solution Applied**: Built comprehensive professional services component system
- Created `/shared/styles/theme-variables.css` with theme-independent variables
- Built `ProfessionalLayout`, `ProfessionalSidebar`, `ProfessionalCard`, `ProfessionalButton` components
- Implemented glassmorphic design system with consistent spacing

### 3. Component Navigation Difficulty (IMPROVED ✅)
**Problem**: Hard to maneuver and switch between components
**Solution Applied**: Created professional services component library
- Built reusable professional components with consistent API
- Implemented responsive sidebar with mobile support
- Created professional button and card systems

## NEW Implementation Details (Session 2025-01-14)

### Professional Services Component System
**Location**: `/shared/components/`
**Files Created**:
- `ProfessionalLayout.tsx` - Theme-independent layout wrapper
- `ProfessionalSidebar.tsx` - Consistent sidebar with glassmorphic effects
- `ProfessionalCard.tsx` - Authority-building card component
- `ProfessionalButton.tsx` - Professional services button system
- `index.ts` - Component export management

### Theme Variables System
**Location**: `/shared/styles/theme-variables.css`
**Features**:
- CSS custom properties for consistent spacing
- Glassmorphic background system
- Theme-independent layout variables
- Professional services design tokens
- Mobile-responsive spacing system

### Orange Theme Fixes Applied
**Files Fixed**:
- `Content Calendar/src/components/generated/ContentCalendarPage.tsx`
- Standardized gradient values to match THEME_CONSTANTS.md
- Fixed cluster color consistency
- Eliminated hardcoded hex values

## Current Status (Session 2025-01-14)

### COMPLETED WORK ✅
- Orange theme gradient standardization
- Professional services component library
- Theme-independent CSS variables system
- Glassmorphic design system implementation
- Mobile-responsive professional components
- Dashboard build testing successful

### NEXT PRIORITIES
1. **Implement Professional Components Across All Applications**
   - Replace generated components with professional equivalents
   - Migrate all apps to use new component system
   - Ensure consistent professional services compliance

2. **Advanced Authority Avalanche Integration**
   - Build testimonial transformation components
   - Create authority measurement dashboard
   - Implement multi-channel content distribution UI

3. **Performance Optimization**
   - Optimize glassmorphic effects for mobile
   - Implement lazy loading for professional components
   - Add performance monitoring for authority content

## SuperClaude Quality Standards

### Development Velocity Requirements
- **Use SuperClaude commands** for 10x faster development
- **Apply appropriate personas** for specialized expertise
- **Include evidence flags** for learning and understanding
- **Use MCP servers** for enhanced capabilities

### Professional Services Compliance
- **Authority demonstration** through design quality
- **Consistent visual hierarchy** and spacing
- **Mobile-optimized** professional interfaces
- **Clean, trustworthy** professional appearance

## Session Learning (2025-01-14)

### Key Insights from Layout Fix Session
1. **Theme Consistency Critical**: Hardcoded hex values in orange theme caused visual inconsistencies
2. **Professional Components Essential**: Reusable component library dramatically improves development speed
3. **CSS Variables System**: Theme-independent variables enable consistent spacing across all themes
4. **Glassmorphic Effects**: Professional services require sophisticated visual hierarchy
5. **Mobile-First Approach**: Professional audiences access platforms on mobile devices

### Successful SuperClaude Methodology Applied
- **Analysis Phase**: Comprehensive codebase analysis identified root causes
- **Build Phase**: Created systematic component library with professional standards
- **Testing Phase**: Validated build success and development server functionality
- **Documentation Phase**: Updated project knowledge base with new insights

### Development Patterns That Work
1. **Start with Analysis**: Always understand the problem before building
2. **Build Systematically**: Create reusable components vs. one-off fixes
3. **Test Incrementally**: Validate each component as it's built
4. **Document Everything**: Update CLAUDE.md with new insights

### Files to Reference for Future Sessions
- `/shared/styles/theme-variables.css` - Theme-independent variables
- `/shared/components/` - Professional services component library
- `/dashboard/src/constants/layout.ts` - Layout constants and standards
- `Content Calendar/src/components/generated/ContentCalendarPage.tsx` - Fixed orange theme implementation

## Forbidden Practices for Brand BOS

### NEVER Do These Things
- ❌ Use traditional prompts instead of SuperClaude commands
- ❌ Skip persona flags when using commands
- ❌ Ignore professional services context flags
- ❌ Work on layout issues without frontend persona
- ❌ Build components without magic and c7 MCP servers

### ALWAYS Do These Things
- ✅ Start every session with `/load` command
- ✅ Use `--persona-frontend` for all UI work
- ✅ Include `--professional-services` context
- ✅ Apply `--evidence` flag for explanations
- ✅ Use `--c7` and `--magic` MCP servers for development

## Success Metrics for Brand BOS

### Layout Consistency Targets
- All themes have identical layout structure
- Consistent 24px spacing between sidebar and content
- Proper background differentiation across all theme colors
- Professional services design standards compliance

### Development Efficiency Targets
- 10x faster development using SuperClaude methodology
- Evidence-based development with detailed explanations
- Professional services appropriate component generation
- Authority Avalanche methodology integration

---

**REMEMBER**: This is a SuperClaude enhanced project. ALWAYS use SuperClaude commands with appropriate personas and MCP integration. Traditional prompting is not allowed for Brand BOS development.

**# ACTIVE CONTRIBUTORS
- **User (Human)**: Works in Cursor IDE, directs the project, makes
high-level decisions, has the best taste & judgement.
- **Cursor Agent**: AI copilot activated by User, lives in the Cursor
IDE, medium level of autonomy, can edit multiple files at once, can run
terminal commands, can access the whole codebase; the User uses it to
vibe-code the app.
- **Claude Code**: Terminal-based AI agent with high autonomy, can edit
multiple files simultaneously, understands entire codebase automatically,
runs tests/Git operations, handles large-scale refactoring and complex
debugging independently