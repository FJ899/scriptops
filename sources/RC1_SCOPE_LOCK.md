# RC1 Scope Lock

## Build only RC1

The goal is not to build the full ScriptOps vision.

The goal is to prove the local control loop:

```text
project init
→ task
→ context bundle
→ WebAI candidate import
→ validation
→ impact report
→ human decision
→ decision log
→ Git commit
→ smoke test
```

## RC1 includes

- local CLI,
- single-user mode,
- Git-backed project,
- SQLite metadata,
- task creation,
- context bundle,
- HANDSHAKE v2 generation,
- prompt-ready file,
- manual WebAI output import,
- structural validation,
- simple canon-impact report,
- approve / reject / revision request,
- decision log with `why`,
- integrity status check,
- smoke test.

## RC1 may include lightweight IdeaOps foundation

Only if low effort:

```text
ideas/
  inbox/
  triaged/
  parked/
  rejected/
  promoted/

decisions/
```

No AI idea triage in RC1.

## RC1 must not include

- browser helper,
- direct API calls to OpenAI / Claude / Gemini,
- ChatGPT Agent automation,
- autonomous writing,
- automatic approve,
- automatic canon edits from AI output,
- multi-user,
- dashboard,
- GUI/TUI,
- vector database,
- semantic graph automation,
- AI Guard,
- Rule Miner,
- Retcon Engine,
- export pipeline,
- voice interface,
- cloud sync.

## If in doubt

Prefer the narrower RC1 scope.

Report the larger idea as post-MVP, not as implementation.
