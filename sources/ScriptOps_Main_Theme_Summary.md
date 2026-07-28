# ScriptOps — Main Theme Summary

## One-line definition

ScriptOps is a local truth-control system for AI-assisted narrative and idea-heavy projects.

## Better than "screenplay analyzer"

The old framing:

> a tool for analyzing a screenplay

is too small.

The better framing:

> a local system that preserves canon, decisions, ideas, rejected reasoning and change impact while using WebAI as a candidate generator.

## Core product law

AI output is never truth.

A WebAI answer, ChatGPT Agent output or Codex suggestion is only a candidate.

A candidate becomes project truth only after:
1. it is validated,
2. its impact is understood,
3. the human approves it,
4. the decision is logged,
5. and the change is committed.

## Why this matters

AI chats generate valuable material, but they also create chaos:
- good ideas disappear,
- attractive bad ideas enter the project,
- repeated mistakes are forgotten,
- decisions lose their reasons,
- WebAI becomes fake memory,
- and late-stage changes break hidden dependencies.

ScriptOps exists to prevent this.

## What ScriptOps should protect

ScriptOps should be a tool that:

- does not allow good ideas to disappear,
- does not allow bad ideas to enter canon only because they sound good,
- remembers why something was rejected,
- detects repeated failure patterns,
- turns idea chaos into decisions,
- and prevents Agent/WebAI from becoming the source of truth.

## The product engine

ScriptOps turns this:

```text
idea / AI output / change request
```

into this:

```text
candidate
→ context
→ validation
→ impact report
→ human decision
→ log
→ commit or rejection
```

## The strongest long-term capability

The most important future capability is not "AI writes better scenes".

The strongest capability is:

> If this detail changes, what breaks?

Examples:
- the hero's blue eyes must become green,
- a product has no license and must be removed,
- a location must be renamed,
- a secret is revealed too early,
- a character cannot know a fact before scene 23.

ScriptOps should find:
- occurrences,
- dependencies,
- affected scenes,
- affected decisions,
- stale outputs,
- and required reviews.

This is the Narrative Change Impact Engine.

## RC1 focus

RC1 should not try to implement the entire vision.

RC1 should prove the core loop:

```text
local project
→ task
→ context bundle
→ WebAI candidate
→ validation
→ impact report
→ human decision
→ log
→ commit
```

## Post-MVP focus

After RC1 proves value:
- better impact analysis,
- IdeaOps,
- rule mining,
- retcon engine,
- browser helper,
- Agent-assisted operations,
- dashboard,
- semantic graph,
- export pipeline.

## Main anti-scope rule

A valuable idea may be preserved without being implemented now.

This is the difference between:
- protecting vision,
- and destroying focus.
