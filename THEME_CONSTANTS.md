# Brand BOS Theme Constants

## Module Color Schemes

Each module has a distinct color identity while maintaining visual cohesion:

### Dashboard
- **Primary**: Purple to Indigo
- **Gradient**: `from-purple-600 via-purple-700 to-indigo-800`
- **Usage**: Central hub, overview content

### Content Engine  
- **Primary**: Green to Emerald
- **Gradient**: `from-green-600 via-green-700 to-emerald-800`
- **Usage**: Content creation, writing tools

### Content Calendar
- **Primary**: Burnt Orange
- **Gradient**: `from-[#a05a2c] via-[#d2691e] to-[#7c3f14]`
- **Usage**: Scheduling, calendar views

### Performance
- **Primary**: Cyan to Blue
- **Gradient**: `from-cyan-600 via-cyan-700 to-blue-800`
- **Usage**: Analytics, metrics, data visualization

### CIA Analysis
- **Primary**: Blue spectrum
- **Gradient**: `from-blue-600 via-blue-700 to-blue-800`
- **Usage**: Intelligence, analysis, research

### Campaign Control
- **Primary**: Pink spectrum
- **Gradient**: `from-pink-600 via-pink-700 to-pink-800`
- **Usage**: Campaign management, marketing

### Settings
- **Primary**: Slate/Gray
- **Gradient**: `from-slate-600 via-slate-700 to-slate-800`
- **Usage**: Configuration, system settings

## Implementation Pattern

All modules follow this structure:
```tsx
<div className="min-h-screen w-full flex bg-gradient-to-br [MODULE_GRADIENT]">
  <div className="fixed inset-0 bg-gradient-to-br [MODULE_GRADIENT] -z-10" />
  // Content
</div>
```

## Spacing Constants

### Responsive Gaps
- **Mobile (default)**: `w-3` (12px)
- **Small screens**: `w-4` (16px) 
- **Medium screens**: `w-6` (24px)
- **Large screens**: `w-[30px]` (30px)

### Container Pattern
```tsx
<div className="flex-1 pl-0 pr-4 md:pr-8 pt-8 pb-8 overflow-auto">
  <div className="max-w-7xl mx-auto px-4 md:px-0">
    // Content
  </div>
</div>
```

## Glassmorphic UI Constants

### Primary Cards
- **Background**: `bg-white/10 backdrop-blur-md`
- **Border**: `border border-white/20`
- **Border Radius**: `rounded-2xl`
- **Shadow**: `shadow-xl`

### Secondary Cards  
- **Background**: `bg-white/5 backdrop-blur-sm`
- **Border**: `border border-white/10`
- **Border Radius**: `rounded-xl`
- **Shadow**: `shadow-lg`

### Sidebar Glassmorphic
- **Background**: `bg-white/5 backdrop-blur-md`
- **Border**: `border-r border-white/20`