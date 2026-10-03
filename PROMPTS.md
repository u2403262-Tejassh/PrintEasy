# Using these with the code-execution session (GitHub-connected)

## One-time setup (you do this, before starting any session)
1. Create a NEW private GitHub repo (e.g. `easyprint`). Connect only this repo to the site if it lets you choose.
2. Add `SPEC.md` and `AGENTS.md` to the repo root on `main` and commit them.
3. Each milestone below = one session. Paste the prompt, let it work, then review the branch/diff before merging into `main`.

## Between milestones
- Read the diff. Pay particular attention to: upload handling, the agent key, and the subprocess call.
- Run the tests yourself locally if you can (`pip install -r backend/requirements.txt && pytest`).
- Merge to `main` only when tests pass and you're happy. The next session starts from `main`.
- The model is chosen randomly per session, so SPEC.md and AGENTS.md are what keep the style and decisions consistent. If a session drifts out of scope, reply: "Out of scope per SPEC.md section 3. Remove it."

---

## M1: Backend foundation

```
Read SPEC.md and AGENTS.md in this repo and follow them exactly.

Milestone M1, branch name: m1-backend-foundation

Build only:
- backend/config.py, backend/models.py, backend/pdf_utils.py, backend/db.py
- backend/requirements.txt
- backend/tests/test_pdf_utils.py and backend/tests/test_db.py
- .gitignore (Python, venv, data/, .env, agent.log) and .env.example

pdf_utils.py must contain: parse_pages(spec, total), validate_pdf, make_print_pdf(src, dst, spec) that returns the page count, and a helper that computes sheets (SPEC section 8).
db.py must contain: schema creation, create_job, get_job, an ATOMIC claim_next_job, update_status with state-machine validation (raise a clear exception on invalid transitions), and requeue_stale_claims.

Write thorough pytest tests as listed in SPEC section 16 for these modules, including a threaded concurrency test for the atomic claim. Generate test PDFs in code with pypdf, no fixture files.
Do not build the API routes yet.

Create a virtualenv, install the requirements, run the tests until they pass, commit, and push the branch. End with the final summary described in AGENTS.md.
```

---

## M2: API routes

```
Read SPEC.md and AGENTS.md in this repo and follow them exactly. M1 is merged into main.

Milestone M2, branch name: m2-api

Build only:
- backend/main.py with all routes from SPEC section 12 (public and agent)
- backend/tests/test_api.py using FastAPI's TestClient
- update requirements.txt and .env.example if needed
- a placeholder backend/static/index.html (just a heading; the real one comes in M4)

Include: upload validation (SPEC section 9, enforcing the size limit while reading), the X-Agent-Key check with hmac.compare_digest, 409 on invalid transitions, deletion of the uploaded original after trimming, a cleanup task for old print-ready files, stale-claim recovery, and refusing to start if AGENT_KEY is unset.
Include a full-flow test: upload -> agent claims -> downloads file -> printing -> printed -> public status shows printed.

Run all tests until they pass, commit, push the branch, and end with the final summary from AGENTS.md. Also start the server once in the background and call it with curl to confirm it really runs, then stop it.
```

---

## M3: Shop agent

```
Read SPEC.md and AGENTS.md in this repo and follow them exactly. M1 and M2 are merged into main.

Milestone M3, branch name: m3-agent

Build only:
- agent/config.py, agent/sumatra.py, agent/agent.py, agent/requirements.txt
- agent/tests/test_sumatra.py and agent/tests/test_agent.py
- an "Agent setup (Windows)" section appended to README.md (create README.md if missing)

Follow SPEC section 14 exactly, including: sumatra.py as a pure function that returns an argument list, --dry-run mode, retry with backoff on network errors, 120s timeout, temp-file cleanup, the local file of handled job IDs for idempotency, and logging to console and agent.log.
Tests must mock the subprocess call (you are on Linux, SumatraPDF is not available) and cover every combination of colour, duplex, and copies, success, non-zero exit, timeout, cleanup, and duplicate-job protection.
Also run the real backend locally, create a job through the API, and run the agent with --dry-run against it to prove the whole loop works end to end. Show the log output.

The README section must explain: installing Python and SumatraPDF on Windows, finding the exact printer name, setting the environment variables, running the agent, and a manual test plan using "Microsoft Print to PDF".
In your summary, clearly list the SumatraPDF command-line options I must verify in its official docs.

Run all tests until they pass, commit, push the branch, and end with the final summary from AGENTS.md.
```

---

## M4: Front end

```
Read SPEC.md and AGENTS.md in this repo and follow them exactly. M1 to M3 are merged into main.

Milestone M4, branch name: m4-frontend

Build only backend/static/index.html (single file, vanilla JS and CSS, no build step) following SPEC section 13.

Use PDF.js 3.11.174 from cdnjs with the worker configured correctly (GlobalWorkerOptions.workerSrc). Mobile-first layout, large touch targets. Include: file picker, thumbnails with selected/unselected styling, live page-range validation against the page count (the same rules as SPEC section 8, with friendly messages), colour toggle, single/double sided with the long/short edge option explained in plain language, copies, submit, and status polling every 2 seconds with friendly messages. Show server errors clearly.

You cannot test this on a real phone. Do what you can: start the backend and confirm the page is served and that the JS has no syntax errors (for example by running it through a headless browser if one is available, or by at least linting it). Tell me clearly what you could and could not verify, and give me a short manual checklist to test on my phone.

Commit, push the branch, and end with the final summary from AGENTS.md.
```

---

## M5: Review and hardening

```
Read SPEC.md and AGENTS.md in this repo. M1 to M4 are merged into main.

Milestone M5, branch name: m5-review

1. Review the entire repo against SPEC.md. List every deviation and every bug you can find, with file and line, before changing anything.
2. Review security: file upload handling, path traversal, the agent key, command injection in the agent's subprocess call (printer name, file path, settings), cleanup of temp and uploaded files, and error messages leaking internals. List each issue with severity.
3. Fix the issues, adding tests for each fix.
4. Complete the README.md: install, configure, run the backend, run the agent, test from a phone on the same Wi-Fi (including how to bind the server so other devices can reach it and how to find the PC's local IP), and troubleshooting.
5. Add a manual test checklist for a real duplex printer: a 4-page PDF with pages labelled PAGE 1 to PAGE 4, testing long edge and short edge, colour vs black and white, copies, and page selection. Say what correct output looks like for each case.

Run all tests until they pass, commit, push the branch, and end with the final summary from AGENTS.md.
```

---

## Bug template (use in a new session whenever something breaks on your machine)

```
Read SPEC.md and AGENTS.md in this repo and follow them.

Something is broken. Branch: main (or say which).

What I did: <exact steps>
What I expected: <...>
What happened: <...>

Full error / traceback / log output:
<paste everything, do not trim>

Find the root cause and explain it in 2 to 3 sentences. Write a failing test that reproduces it if possible, then fix it with the smallest change, make sure all tests pass, commit on a branch named fix-<short-name>, and push. Do not change anything unrelated.
```

---

## After M5, on your own machine (the agent can't do these)
1. Verify the SumatraPDF flags against its official docs.
2. Run the agent on the Windows PC with Microsoft Print to PDF.
3. Test on a real duplex printer with the labelled 4-page PDF.
4. Test the front end on a real phone.
5. If something fails, use the bug template with the exact error output.
