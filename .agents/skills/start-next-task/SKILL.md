---
name: start-next-task
description: Start or resume planning in this repository by reading TASKS.md, finding the next pending task, checking AGENTS.md plus relevant docs/code, then analyzing and explaining the task in Plan mode without implementing it. Use when the user asks for next steps, next task, task prioritization, starting a new thread from TASKS.md, planning the next repo task, or understanding the next item in local task tracking.
---

# Start Next Task

## Default Mode

Use this skill as a planning and explanation workflow. Do not start implementing
the selected task during the same turn unless the user explicitly asks to execute
after the plan has been presented.

If Codex Plan mode is available or active, stay in Plan mode. If Plan mode is not
available as a tool/surface, behave as planning-only: analyze, explain, list
decisions, and stop before edits or AWS mutations.

## Workflow

1. Establish the repo context.
   - Use the current working directory as the repo unless the user names another path.
   - Read `AGENTS.md` first.
   - Read `TASKS.md`, `README.md`, and only the docs/code relevant to the next pending task.
   - Check `git status --short` before making changes.

2. Identify the task.
   - Treat `TASKS.md` as the source of truth.
   - Pick the first unchecked task in the earliest active phase unless the user names a specific task.
   - If the next task depends on an earlier incomplete task, say so and work on the blocker first.
   - If the user asks only for "siguientes pasos" or prioritization, answer from `TASKS.md` without editing files.
   - If a Codex thread-title tool is available, rename the current thread after identifying the task. Use a short title like `Fase 2 - Crear budget AWS` or `Fase 4 - Conectar chat`.

3. Plan the work.
   - State the selected task and why it is next.
   - Explain what the task means in practical terms.
   - Summarize the smallest useful implementation/validation plan.
   - Identify decisions, assumptions, risks, and expected outputs.
   - Mention required tools, such as tests, linters, browser, GitHub, AWS MCP, or other MCP servers.
   - For AWS work, use AWS MCP when available and do not send prompts, answers, documents, extracted text, secrets, or private user data to AWS MCP.

4. Stop before execution.
   - Do not edit files, create AWS resources, run mutating commands, or mark tasks complete during the planning turn.
   - Ask at most one concise question only if a decision is required before implementation.
   - If the task is ready to execute, end with the concrete next action the user can request, such as "puedo ponerme a ello".

5. Prepare validation, but do not run it unless read-only validation is useful.
   - Name the tests, linters, browser checks, or MCP validations that should be run during implementation.
   - For AWS tasks, distinguish documentation/availability checks from account mutations.
   - Do not update `TASKS.md` until implementation actually completes.

## Response Shape

For this skill, keep the answer short:

- Next task
- Thread title updated, if available
- Relevant context checked
- Explanation of the task
- Proposed implementation plan
- Validation to run
- Open decision or blocker, only if real
