# AGENTS.md: rules for any AI coding agent working in this repo

Read `SPEC.md` first. It is the source of truth for scope, API, and behaviour.

## Scope
- Build only what SPEC.md section 2 lists. Section 3 is explicitly out of scope: do not add it, even as a "nice to have".
- If the spec is ambiguous, pick the simplest reasonable option, write the assumption in the commit message and in your summary, and continue. Only stop to ask if you are truly blocked.
- If you think the spec is wrong, say so in your summary instead of silently deviating.

## Environment
- You are running on Linux with no printer and no SumatraPDF. Never try to install or run them.
- The agent's SumatraPDF call must be testable with the subprocess call mocked, and the `--dry-run` flag must work.
- Windows and real-printer testing is done by a human later. List anything that needs it in your summary.

## Code standards
- Python 3.11+, type hints, short docstrings, small functions.
- No bare `except:`. Handle errors explicitly and return clear messages.
- Never hard-code secrets. Config comes from environment variables. Keep `.env.example` up to date.
- Subprocess calls use an argument list, never `shell=True`.
- Keep dependencies to those listed in SPEC.md section 5. Ask before adding any.
- Do not invent library features or command-line flags. If you are unsure (especially SumatraPDF options or PDF.js setup), say so in the code comment and in your summary.

## Workflow
- Work on a branch named for the milestone (e.g. `m1-backend-foundation`). Never commit to `main` directly.
- Before finishing a milestone: run the full test suite, fix failures, and make sure the code starts without errors.
- Commit in small logical commits with clear messages.
- Do not delete or rewrite tests to make them pass. If a test is wrong, explain why.

## Final summary (end of every milestone)
Report, briefly:
1. What was built (files)
2. Exact command to run the tests and the result
3. Assumptions made and deviations from the spec
4. Anything uncertain or needing human verification
5. Exact commands to run what was built
