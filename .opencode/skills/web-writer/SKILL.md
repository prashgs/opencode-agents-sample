---
name: web-writer
description: Write a concise README.md for a completed web application at an absolute path
license: MIT
compatibility: opencode
---

# Web Writer Skill

Write a README.md for a generated web application.

## CRITICAL: Use the Absolute Path

The prompt tells you the exact absolute path for the README. Write to it using the `write` tool:
- ✅ CORRECT: `/home/user/webgen-agent/output/todo-app/README.md`
- ❌ WRONG: `README.md`

## README Structure

```markdown
# App Name

One sentence description.

## Features
- Feature 1
- Feature 2

## How to Run

### Frontend Only
Open `index.html` in your browser — no server needed.

### With Backend (only if has_backend is true)
1. `pip install -r requirements.txt`
2. `bash run.sh`
3. Open `index.html` in your browser

## Files
| File | Purpose |
|------|---------|
| index.html | Main page |
| style.css | Styles |
| app.js | Application logic |
```

## Rules
- Be concise — no marketing fluff
- Use real commands and real file names
- Omit backend section if has_backend is false
- Write directly to disk at the absolute path given
