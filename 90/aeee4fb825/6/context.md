# Session Context

## User Prompts

### Prompt 1

Unknown skill: claude-dashboard:setup

### Prompt 2

이 컴에 설치된 claude가 오류가 생긴것 같은데 점검 바람

### Prompt 3

# Claude Dashboard Setup

Configure the claude-dashboard status line plugin with widget system support.

## Arguments

- **No arguments**: Interactive mode (asks questions)
- **With arguments**: Direct configuration mode

### Direct Mode Arguments

- `ko`: Display mode
  - `compact` (default): 1 line (model, context, cost, rateLimit5h, rateLimit7d, rateLimit7dSonnet, zaiUsage)
  - `normal`: 2 lines (+ projectInfo, sessionId, sessionDuration, burnRate, todoProgress)
  - `detailed`: 4 lines (+ dep...

### Prompt 4

Base directory for this skill: /home/nuri/.claude/plugins/cache/bkit-marketplace/bkit/1.5.5/skills/pdca

# PDCA Skill

> Unified Skill for managing PDCA cycle. Supports the entire Plan → Design → Do → Check → Act flow.

## Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `plan [feature]` | Create Plan document | `/pdca plan user-auth` |
| `design [feature]` | Create Design document | `/pdca design user-auth` |
| `do [feature]` | Do phase guide (start...

### Prompt 5

# Check CLI Usage

Display usage limits for all AI CLIs (Claude, Codex, Gemini, z.ai) and recommend the one with the most available capacity.

## Usage

```bash
# Interactive output with colors
/claude-dashboard:check-usage

# JSON output for scripting
/claude-dashboard:check-usage --json

# Specify language (en or ko)
/claude-dashboard:check-usage --lang ko
/claude-dashboard:check-usage --lang en
```

## Output

Shows usage for each installed CLI:
- **Claude**: 5h and 7d rate limits with reset ...

