🚀 Master Project Initialization Prompt: Onboarding & Context Engineering (for Cam, Arizona, EasyIn APIs, etc.)
0. Quick Setup
Project Name: [e.g., Cam, Arizona, EasyIn APIs, etc.]
GitHub Repository URL: [paste here]
Team/Stakeholders: [optional]

**Insert initial notes, goals, stakeholders as needed]

(AI agent: Create these as top-of-file comments in all markdown files you generate, and prompt the user if any is missing.)

1. General Instructions & Sequence
Repository Context:
Use the MCP server (or file tree if local) to fully ingest and summarize all technical files and context in the specified repository BEFORE generating new or modified content.
Wait for this step to complete before file scaffolding.

Project Scaffold & File Generation:
Strictly use the following structure; do not create non-standard files/folders unless instructed.

text
/project-root
├── PLANNING.md                 # Vision, architecture, and LLM/agent onboarding
├── TASK.md                     # Living, agent- and human-readable task list
├── initial.md                  # Kickoff context, chronology, project constraints
├── claude.md                   # Notes & special prompts for Claude/agents
├── design-rules.md             # (Insert supplied verbatim via user, see below)
├── programming-rules.md        # (See merged rules below—do not duplicate)
├── README.md                   # Setup, usage, quickstart referencing all onboard files
├── .env                        # Only if environment/config actually needed
├── /docs/                      # For further technical references or ingestion
├── /examples/                  # Example code/templates
├── /tests/                     # (Stub only, unless otherwise instructed)
Bootstrapping for Clarity and Reproducibility:

Include a “Purpose” or “How to Use This File” comment block atop each markdown/config file.

Summarize project context, and cross-link related docs at the top of README.md, PLANNING.md, and programming-rules.md.

2. Core Project Files & Content Templates
PLANNING.md
Purpose: Vision, onboarding, and agent context specification.
This document provides architectural overviews, role/agent setup, key technical/contextual facts, and any domain-specific constraints as onboarding material for all agents/developers on this project.

Example Initial Content:

text
# Project Overview: [Project Name]
- Tech stack: [list main stack]
- Key APIs: [e.g., EasyIn APIs: endpoints, protocols, supported auth methods]
- Architectural diagram: [add as code/ASCII, or link to /docs/ if available]
- Constraints: [e.g., privacy, deployment, hosting]
- Stakeholders: [list]
- Agent onboarding requirements: [minimum context or tool permissions needed]
TASK.md
Purpose: Living prioritized task list for all contributors (agents & humans).
Update entries continuously; use checkboxes for completion.
Example structure:

text
# Task List
- [ ] [Short summary: e.g., Implement EasyIn API OAuth connector]
- [x] [Completed task]
initial.md
Purpose: Session zero/kickoff facts, initial context, and any project “rules of the road”—track the founding assumptions and project constraints at the very start.

“First-message” summary (how/why this repo was started)

Major constraints, e.g., must integrate with Cam systems, no new libraries without approval, etc.

Any reset/roll-back instructions or known showstoppers

claude.md
Purpose: Agent-specific usage notes for Claude (or other agents):

Any “system prompt” guidance or command-mode usage (“You are an agent…”)

File naming, committing, and branch management instructions specific to agent workflows

Prompts for test, review, or deployment triggers
(Insert additional onboarding notes here as project evolves.)

design-rules.md
Purpose: UI, styleguide, and UX rule integration.

Insert your own supplied design rules block VERBATIM here.

At the top, link to any SF Symbols icon/table snippets or icon guidance needed for this project.

(See guidance for SF Symbols snippet below for react-native/Icon usage if relevant.)

programming-rules.md
Purpose: Centralize all actionable programming, style, and API rules for code generation, review, and maintenance.

Merged Programming & Coding Rules (Start of File; update as needed):
text
# General Programming Guidelines for AI Assistance

These rules guide AI code generation and modification to promote code quality, consistency, and maintainability across all projects.

## 1. Core Principles

- **Clarity and Simplicity:**  
  Favor solutions that are idiomatic, readable, and well-aligned with the project’s established tech stack.  
  Use explicit file, function, and variable names.  
  Comment only for complex or non-obvious code and all // TODO markers.

- **Iterative Change:**  
  When possible, extend/refine existing patterns before introducing new paradigms or refactoring.  
  Remove all obsolete code/implementations if major changes are required and document rationales.

- **Focus and Precision:**  
  Address only the scope of the requested task; avoid drive-by code changes or non-requested refactoring.  
  Specify precise file paths, names, and affected modules in all PRs and code reviews.

- **Componentization & Modularity (UI Projects):**  
  - Break features into small, reusable, well-defined components/functions.
  - Keep files focused & ideally under ~300 lines—split as appropriate.
  - Define clear TypeScript interfaces/types for all API, component, and hook inputs/outputs.

- **DRY (Don’t Repeat Yourself):**  
  Proactively check for existing functionality before writing new code; centralize reusable logic in shared libs/utilities/directories.

- **Error Handling:**  
  - Wrap async or risky sections in `try/catch`.  
  - Always check response/returned data before use (avoid null/undefined bugs).
  - Show user-friendly error messages in UI/stateful flows and handle all error/loading states for API calls.

- **API Usage:**  
  - Use typed/fetch client or canonical hooks for all endpoint calls.
  - Never hardcode secrets/configs—use `.env` or similar.

- **Testing:**  
  - When requested, generate appropriate test file stubs using mainstream frameworks (Jest, Vitest, Cypress, React Testing Library, etc).
  - Limit complex mocking and exhaustive test cases unless specifically instructed; focus on coverage of main functions/components/routes.

## 2. Environment Configuration

- Never hardcode sensitive keys or environment-specific configuration.
- Use environment variables and `.env` files (but never modify .env in code unless instructed).
- Only change project configs (next.config.js, tailwind.config.js, package.json, etc.) if specifically requested.

## 3. Data Handling and State

- Only use real data, props, or API in development/production code (mock data for Storybook/tests only).
- Always null/undefined-check all fetched/external data before using.
- Prefer standard mechanisms for state (e.g., React useState) and, for shared/global state, maintain existing state management libraries if present (Redux, Zustand, Pinia, etc.).

## 4. App Workflow: Single Instance Protection

- Application/server must enforce a startup check for multiple instances (e.g., by listening on a reserved port). If the port is taken, log a human-friendly message and exit.  
  Apply this in all initialization scripts.

## 5. Miscellaneous

- All content containers (especially text areas) should have a max width of 60% (left-aligned) for optimal readability (never full width).
- Do not alter core project structure or import new libraries without confirmation from the team/lead.
- IMPORTANT FOR IDE or Claude Code: Never start actually coding anything until the user says the magic password, which is : "Action". If you don't see this word in the instructions, that means you need to provide a response as a CTO explaining what you plan to do and that you understand the instructions. And then you request the magic password to get started actually coding. Also, every output must start with a heading that says what the change is, since I'm using multiple terminals.
- # assume repo is ~/proj
cd ~/proj
git worktree add ../proj-api-refactor main
git worktree add ../proj-bug-142 main

Scoped Task Directory Rule (Multi-Agent/Terminal Safety)

For all development or automation tasks, operate only within the explicitly assigned working directory (the dedicated work-tree) for your task—usually named according to the task, branch, or ticket (e.g., ../[CURRENT-TASK]).

Never create, modify, or delete files or code outside this working directory, unless your instructions explicitly permit it.

If your solution requires access to shared libraries or modules, always import them; do not copy or edit shared files inside your scoped work-tree.

All code changes, commits, and file saves must be made exclusively on a branch named for your current task (e.g., CURRENT-TASK or as assigned).

This rule applies at all times, whether working solo, with multiple agents, or across several terminal sessions. It prevents accidental cross-pollination, merge conflicts, and unintended side effects between parallel work streams.

In summary:
Always scope your edits, new files, and commits to the task's dedicated directory and branch only. Never operate outside your assigned space unless specifically clarified.

# open two VS Code windows:
code ../proj-api-refactor   # with Claude extension
code ../proj-bug-142

# editing is now fully sandboxed; commits stay on separate branches

AI Development Time & Complexity Estimation Guidelines
When providing implementation estimates
   as Claude Code, use the following
  realistic AI-assisted development
  timelines:

  Time Scale (1-5 Rating System)

  - 1/5: 5-10 minutes (simple UI changes,
   basic functions)
  - 2/5: 15-20 minutes (component
  refactors, API integrations)
  - 3/5: 30-45 minutes (complex features,
   multiple file changes)
  - 4/5: 1-2 hours (architectural
  changes, extensive testing)
  - 5/5: 2-4 hours (major refactors, new
  systems)

  Estimation Format

  When asked for implementation
  estimates, always provide:
  1. Task Description (brief, specific)
  2. Complexity (1-5): Technical
  difficulty
  3. Time Required (1-5): Based on AI
  timelines above
  4. Confidence (1-5): Likelihood of
  smooth implementation

  Key Principles

  - AI can generate/modify code 10-20x
  faster than human developers
  - Complex logic takes longer than
  repetitive changes
  - Testing and edge cases add time, not
  initial implementation
  - Multiple file coordination increases
  time more than single file complexity

  Example

  "Add floating map controls" -
  Complexity: 2/5, Time: 1/5 (10 min),
  Confidence: 5/5

  Remember: These are AI-assisted
  timelines, not human developer
  estimates. Always clarify this
  distinction when providing estimates.

## 6. Documentation and References

- Cross-reference additional rules or onboarding detail in PLANNING.md as “see [PLANNING.md](./PLANNING.md)” or “see [initial.md](./initial.md)” instead of duplicating the same text.

(Agents and human contributors: Always refer to this file and linked onboarding docs during project work. Update as rules evolve, and link new files here as they are formalized.)

README.md
Purpose: Quickstart, overview, and doc navigation index.
At the top, clearly reference all key onboarding files (PLANNING.md, TASK.md, claude.md, design-rules.md, programming-rules.md) and how/when to consult each.
Public entrypoint for all contributors.

/docs/, /examples/, /tests/
Stub empty unless further technical references, code examples, or test instructions are supplied.

3. Design Rules File (design-rules.md)
(Insert your supplied design rules only—do NOT generate/expand here. Just a placeholder with a comment for agent to “Paste up-to-date design rules below”.)

4. SF Symbols UI Guidance (For React Native/iOS Projects)
Paste the following snippet into design-rules.md whenever SF Symbols are used:

text
### SF Symbols Usage

* **SF Symbols app:** Always verify symbol names using the official app/documentation.
* **Preferred Library:** [Insert here, e.g. react-native-sfsymbols]
* **Table Example:**
| UI Element        | SF Symbol Name         | State/Variant | Weight | Scale | Notes                  |
|-------------------|-----------------------|---------------|--------|-------|------------------------|
| Settings (tab)    | gearshape             | .fill         | medium | large | Accent color on active |
| Share Action      | square.and.arrow.up   | .fill         | regular| medium| Toolbar/default style  |

*Always consult latest Apple and component library docs for symbol compatibility and updates.*
5. Usage and Handoff
Run this prompt in any new repo or at the start of a greenfield project.

After agent or CLAUDE has read the current repo (always supply the correct repository path!), regenerate each file according to the latest rules and user-supplied guidance.

Be proactive about flagging duplicate rules, legacy onboarding, or ambiguous doc structure.

Here is the link to my GitHug repo with the template and framework you should use for setting up our new project: https://github.com/growthpigs/context-engineering-intro