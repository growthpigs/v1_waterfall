# Brand BOS Design System

## 🚨 CRITICAL: Read This First

This file MUST be created before any UI development begins. All developers and AI assistants MUST follow these exact specifications.

## Core Design Tokens

### Spacing (Never deviate from these)
```css
/* Card Internal Padding */
--card-padding: p-6           /* Standard card internal spacing */
--card-padding-small: p-4     /* Compact cards only */
--card-padding-large: p-8     /* Feature cards only */

/* Gaps Between Elements */
--card-gap: gap-6             /* Standard gap between ALL cards */
--section-gap: gap-8          /* Gap between major sections */
--element-gap: gap-4          /* Gap between related elements */

/* Layout Margins */
--page-margin: m-6            /* Standard page margins */
--section-margin: mb-8        /* Between major sections */
```

### Grid Layouts (Use these exact patterns)
```css
/* Dashboard Grid - 3 columns on desktop */
--dashboard-grid: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"

/* Two Column Layout */
--two-column: "grid grid-cols-1 lg:grid-cols-2 gap-6"

/* Content Container */
--page-container: "max-w-7xl mx-auto m-6"
```

### Card Standards (Every card MUST use these)
```css
/* Standard Card Background */
--card-base: "bg-white/10 backdrop-blur-md border border-white/20 rounded-xl"

/* Standard Card with Padding */
--standard-card: "bg-white/10 backdrop-blur-md border border-white/20 p-6 rounded-xl"

/* Metric Card (Dashboard) */
--metric-card: "bg-white/10 backdrop-blur-md border border-white/20 p-6 rounded-xl min-h-[120px] flex flex-col justify-between"

/* Progress Card (CIA Analysis) */
--progress-card: "bg-white/10 backdrop-blur-md border border-white/20 p-6 rounded-xl h-[200px]"
```

### Typography Hierarchy (Consistent text sizing)
```css
/* Page Titles */
--page-title: "text-3xl font-bold text-white mb-8"

/* Section Titles */
--section-title: "text-xl font-semibold text-white mb-6"

/* Card Titles */
--card-title: "text-lg font-medium text-white mb-4"

/* Body Text */
--body-text: "text-gray-300"
--body-text-small: "text-sm text-gray-400"

/* Metric Values */
--metric-value: "text-2xl font-bold text-white"
--metric-label: "text-sm text-gray-400"
```

### Brand Colors (Purple + Fire theme)
```css
/* Primary Purple */
--primary-bg: "bg-gradient-to-r from-purple-600 to-purple-700"
--primary-text: "text-purple-600"
--primary-border: "border-purple-200"

/* Fire Accents */
--accent-bg: "bg-gradient-to-r from-orange-500 to-red-500"
--accent-text: "text-orange-500"

/* Status Colors */
--success: "text-green-500"
--warning: "text-yellow-500"
--error: "text-red-500"
--info: "text-blue-500"
```

## Component Templates

### Dashboard Metric Card
```jsx
<div className="bg-white/10 backdrop-blur-md border border-white/20 p-6 rounded-xl min-h-[120px] flex flex-col justify-between">
  <div>
    <h3 className="text-lg font-medium text-white mb-4">{title}</h3>
    <div className="text-2xl font-bold text-white">{value}</div>
  </div>
  <div className="text-sm text-gray-400">{status}</div>
</div>
```

### CIA Progress Card
```jsx
<div className="bg-white/10 backdrop-blur-md border border-white/20 p-6 rounded-xl h-[200px]">
  <h3 className="text-lg font-medium text-white mb-4">CIA Analysis Progress</h3>
  <div className="space-y-4">
    {/* Progress content */}
  </div>
</div>
```

### Dashboard Grid Layout
```jsx
<div className="max-w-7xl mx-auto m-6">
  <h1 className="text-3xl font-bold text-white mb-8">Brand BOS Dashboard</h1>
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {/* Cards go here */}
  </div>
</div>
```

## Implementation Rules

### ✅ ALWAYS DO:
- Use exact classes from this document
- Copy/paste component templates exactly
- Maintain consistent card heights and spacing
- Use the standard grid patterns

### ❌ NEVER DO:
- Use random padding values (p-4, p-8, p-12)
- Use inconsistent gaps (gap-4, gap-8, gap-12)
- Create custom card backgrounds
- Deviate from typography hierarchy
- Use manual margin/padding combinations

## Claude Code Instructions

When working with Claude Code, always include this prompt:

```
BRAND BOS STYLING REQUIREMENTS:

Use these EXACT classes (from DESIGN_SYSTEM.md):

CARDS: "bg-white/10 backdrop-blur-md border border-white/20 p-6 rounded-xl"
GRIDS: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
TITLES: "text-lg font-medium text-white mb-4"
LAYOUT: "max-w-7xl mx-auto m-6"

Do NOT use any other padding, gap, or margin values.
Follow the component templates exactly.
```

## File Structure

This design system should be implemented as:

```
src/
├── lib/
│   └── design-tokens.ts      # TypeScript constants
├── styles/
│   └── globals.css           # CSS custom properties
└── components/
    └── ui/                   # Reusable components
```

## Validation Checklist

Before any code review, verify:
- [ ] All cards use identical background/border/padding
- [ ] Grid layouts use consistent gap-6 spacing
- [ ] Typography follows the hierarchy exactly
- [ ] No manual p-4, gap-8, or custom spacing values
- [ ] Component templates match this document exactly

---

**This document is the single source of truth for Brand BOS styling. Any deviations must be approved and updated here first.**