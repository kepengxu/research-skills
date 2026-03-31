---
name: roadmap-md
description: Keep project roadmaps written down in a local ROADMAP.md file and update them throughout multi-step work. Use when starting a feature, bugfix, refactor, research task, or any task that benefits from a persistent execution plan, progress tracking, next steps, and decision logging. Also use when the user asks for a roadmap, plan file, milestone tracking, or wants Claude to keep ROADMAP.md current during implementation.
---

# Roadmap Md

Persist the working roadmap to disk instead of keeping it only in conversation state.

Prefer `ROADMAP.md` in the current workspace. If the repository already contains `ROADMP.md`, treat that as the project’s existing convention and update that file instead of creating a second roadmap file.

## Workflow

Follow this workflow whenever the skill is active.

1. Detect the roadmap file path.
2. Create the roadmap file if it does not exist.
3. Write an initial roadmap before substantial implementation.
4. Update the roadmap after meaningful progress, scope changes, blockers, or decisions.
5. Check the roadmap again before finishing your response on longer tasks.

## File selection rule

Choose the roadmap file in this order:

1. `./ROADMAP.md`
2. `./ROADMP.md`
3. If neither exists, create `./ROADMAP.md`

Do not maintain both files at once unless the user explicitly asks for that.

## When to update the roadmap

Update the roadmap whenever one of these happens:

- a non-trivial task starts
- a plan becomes clearer after code reading or investigation
- a task is completed
- a new subtask appears
- a blocker or risk is found
- the implementation approach changes
- tests fail or reveal follow-up work
- the user changes priorities or scope

For very small one-shot edits, a roadmap update is optional.

## What to write

Keep the file short, current, and practical.

Use this default structure:

```markdown
# Roadmap

## Goal
- One short statement of the user’s actual objective.

## Current status
- What is done
- What is in progress
- What is blocked

## Plan
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

## Decisions
- Decision: <chosen approach>
- Why: <brief reason>

## Open questions
- Question or uncertainty

## Next update trigger
- What event should cause the next roadmap refresh
```

Adapt the sections if the task is simpler, but keep the file readable.

## Update rules

When updating the roadmap:

- preserve useful existing content
- mark completed items clearly
- add newly discovered work immediately
- remove stale steps that no longer apply
- keep future steps concrete and actionable
- keep wording aligned with the current repo state
- prefer replacing vague status with specific status

Do not let the roadmap drift away from the actual work.

## Behavior rules

- Write the roadmap early on long tasks, not at the very end.
- Treat the roadmap as a living execution log, not a one-time plan.
- If you already use an in-session todo/task system, keep the file aligned with it.
- If the user already has a preferred roadmap format, follow it.
- If another project document already acts as the execution plan, update that only if the user clearly wants it; otherwise use the roadmap file.

## Minimal examples

### Example: start of task

```markdown
# Roadmap

## Goal
- Add export support for experiment summaries.

## Current status
- Investigating existing export path.

## Plan
- [ ] Inspect current report generation flow
- [ ] Add export format support
- [ ] Verify output with a sample run

## Decisions
- Decision: extend existing exporter instead of adding a parallel code path
- Why: keep output logic in one place

## Open questions
- Whether CSV and JSON should ship together

## Next update trigger
- After identifying the exporter entry point
```

### Example: after progress

```markdown
## Current status
- Existing exporter located and understood
- CSV export implemented
- JSON export still pending

## Plan
- [x] Inspect current report generation flow
- [x] Add CSV export format support
- [ ] Add JSON export format support
- [ ] Verify output with a sample run

## Decisions
- Decision: share one normalization step across CSV and JSON
- Why: avoid divergent field handling

## Next update trigger
- After JSON export is wired and tested
```

## Output expectation

When working on a task, keep the roadmap file updated silently as part of normal execution. Mention roadmap updates to the user only when it is materially useful, such as:

- introducing the plan
- calling out scope changes
- reporting blockers
- pointing the user to the file path for review
