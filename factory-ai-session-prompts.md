# Factory.ai Session Prompt Templates
_A cheat-sheet for keeping each chat lean, productive, and continuous._

## How to Use This Guide
Copy-paste the relevant prompt at the **start**, **mid-point**, or **end** of every session.  
These templates:

* Inject just enough context to stay within the token window.  
* Nudge Factory’s memory system to retain key facts.  
* Remind you to commit code / docs regularly.

You can tweak wording, but try to keep them short.

---

## Quick Reference

| Phase | Copy-This Prompt | Purpose |
|-------|-----------------|---------|
| Start | `🟢 SESSION START: …` | Load goals + critical context |
| Mid   | `🟡 CHECKPOINT: …` | Progress check & lightweight save |
| End   | `🔴 SESSION END: …` | Summarise, commit, store memory |

Detailed versions below.

---

## 1. Start-of-Session Prompts

### Prompt A – Fresh Start
```
🟢 SESSION START:
Project = “Waterfall”.
Branch = `waterfall-implementation`.
Goal for this session: <write your single sentence goal>.
Key facts you should remember: MongoDB runs locally via Homebrew, backend port 5001, React client port 3000.
Please load any relevant memory and tell me the **one best next step**.
```
**Why it works**

* Provides **minimal but critical** project context (project name, branch, env ports).  
* States a single clear goal to focus the assistant.  
* Triggers memory recall by explicitly referencing facts.

### Prompt B – Returning Mid-Project
```
🟢 SESSION START (RETURN):
Same Waterfall project & branch.
Reminder: last commit hash <paste if known>.
Today’s focus: <one task>.
Load memory + suggest quickest path.
```
* Even shorter; good when you just need momentum.  

---

## 2. Mid-Session (Checkpoint) Prompts

### Prompt C – Progress & Mini Save
```
🟡 CHECKPOINT:
What we’ve done so far (1-2 bullets):
1. …
2. …
Are there any quick commits, file saves, or tests we should run now?
Keep answer concise (≤ 6 lines).
```
* Keeps the context small by summarising yourself.  
* Encourages incremental commits.

### Prompt D – Clarify Blocking Issue
```
🟡 PAUSE:
I’m stuck at <describe issue in one sentence>.
Please propose the smallest diagnostic command or code change to unblock me.
```
* Direct, focuses on smallest next action, avoids verbose exchanges.

---

## 3. End-of-Session Prompts

### Prompt E – Wrap-Up & Commit
```
🔴 SESSION END:
List clearly in ≤5 bullets:
• Work completed.
• Files changed (paths only).
• Commands you recommend I run before next session (tests, commit, push).
Then store any new constants in memory (ports, credentials placeholders, etc.).
Respond ONLY with the bullet list + “Memory updated”.
```
* Ensures you leave with an actionable todo.  
* Keeps output tight by instructing the assistant on format.  
* Explicit memory save request.

### Prompt F – Handoff to Next Session / Teammate
```
🔴 HANDOFF:
Brief for next collaborator:
<one-paragraph summary>.
Key open tasks: <list>.
Please commit & push changes if not yet done, then conclude.
```
* Ideal when multiple users share the project.

---

## Tips for Lean Sessions

1. **One Goal Rule** – tell the assistant just one primary objective each session.  
2. **Self-Summarise** – before asking, give 1-2 sentence context; saves tokens.  
3. **Auto-Triggers** – enable low-risk auto-accept for `ls`, `git status`, etc.  
4. **Frequent Commits** – treat every Mid-Session checkpoint as a potential `git commit ‑m "feat: …"` moment.  
5. **Store Constants Early** – ask the assistant to “remember” env variables once, then reference them by name.

---

Happy building!
