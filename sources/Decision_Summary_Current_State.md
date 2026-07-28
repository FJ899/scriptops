# Current Decision Summary

## Decision 1 — Product identity

ScriptOps should not be positioned primarily as:
- screenplay analyzer,
- AI writer,
- prompt manager,
- or generic idea analyzer.

It should be positioned as:

> Local truth control for AI-assisted narrative and idea-heavy projects.

## Decision 2 — RC1 boundary

RC1 builds the smallest stable local workflow.

RC1 includes:
- local project structure,
- tasks,
- context bundle,
- manual WebAI candidate import,
- structural validation,
- simple impact report,
- approve / reject / revision decision,
- decision log with why,
- Git commit,
- dirty-state detection,
- smoke test.

RC1 excludes:
- browser helper,
- API integrations,
- autonomous Agent,
- AI Guard,
- semantic graph automation,
- full IdeaOps,
- dashboard,
- export pipeline,
- multi-user.

## Decision 3 — Collaboration style

The human is the concept owner, not the implementation operator.

Chat responses should explain:
- direction,
- reason,
- risk,
- recommendation.

Technical instructions belong in Markdown artifacts.

## Decision 4 — Idea capture

Future valuable ideas should become Markdown records, not chat fragments.

Minimum folders:
```text
ideas/
  inbox/
  triaged/
  parked/
  rejected/
  promoted/

decisions/
```

This can be added as RC1-light without implementing full IdeaOps.

## Decision 5 — Codex workflow

Codex should not receive one giant prompt.

Codex should work in stages:
1. understand and plan,
2. scaffold,
3. implement core project init/status,
4. implement task/context/run,
5. implement import/validate/impact,
6. implement decision/commit,
7. add tests/smoke-test,
8. harden.

## Decision 6 — Agent workflow

ChatGPT Agent may operate WebAI or browser workflows, but only as an operator.

Agent may create candidates.
Agent may not approve, commit, edit canon, or change rules without human approval.
