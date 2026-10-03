# PrintEasy

> **MVP in progress.** Upload a PDF from your phone, choose print settings, and a shop-side Windows agent prints it. Built to beat campus print shop queues.

PrintEasy started as a design thinking project: during a 10-minute break, students waste time queueing at the print shop, explaining settings, and fumbling with USB drives. PrintEasy lets them set everything up on their phone beforehand, so printing at the shop takes seconds instead of minutes.

## Status

This is an early MVP that proves the core pipeline only. Some things below are planned and not built yet.

| Feature | Status |
|---|---|
| PDF upload from phone browser | Planned (MVP) |
| Page selection | Planned (MVP) |
| Colour / black and white | Planned (MVP) |
| Single / double sided, flip on long or short edge | Planned (MVP) |
| Copies | Planned (MVP) |
| In-browser preview | Planned (MVP) |
| Shop-side Windows print agent | Planned (MVP) |
| Live job status | Planned (MVP) |
| UPI payments | Not started |
| Multiple shops / shop discovery | Not started |
| Pickup QR / OTP verification | Not started |
| DOC and image uploads | Not started |
| Live queue visibility | Not started |

## How it works

```
[Phone browser] --upload + settings--> [FastAPI backend + SQLite] <--polls every 2s-- [Agent on shop's Windows PC] --> SumatraPDF --> Printer
```

1. The student opens the web page on their phone and picks a PDF.
2. They choose pages, colour, sides (and flip edge), and copies, and see a preview.
3. The backend validates the PDF, cuts it down to the selected pages, and queues the job.
4. The agent on the shop PC picks up the job, downloads the print-ready PDF, and prints it with SumatraPDF.
5. The student sees the status change from queued to printing to printed.

Design choices worth knowing:
- **Page selection is done on the server**, so what you preview is exactly what is printed.
- **The agent only makes outbound requests**, so a shop needs no router setup or port forwarding.
- **Jobs follow a strict state machine** (`queued → claimed → printing → printed / failed`), and claiming a job is atomic so it can never print twice.

## Tech stack

- **Backend:** Python 3.11+, FastAPI, SQLite, pypdf
- **Front end:** single-page HTML/CSS/JavaScript, PDF.js for preview
- **Shop agent:** Python, SumatraPDF (command-line printing on Windows)
- **Tests:** pytest

## Project structure

```
backend/     FastAPI app, database, PDF utilities, static front end
agent/       Windows print agent and SumatraPDF command builder
SPEC.md      Full technical specification
AGENTS.md    Rules for AI coding agents working in this repo
```

## Quick start

> The exact commands may change as the MVP is built. Check each folder for the latest notes.

**Backend**
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
cp .env.example .env             # then set AGENT_KEY to a long random value
```
Run it with Uvicorn as described in the backend notes, binding to `0.0.0.0` if you want to open it from a phone on the same Wi-Fi.

**Shop agent (Windows)**

1. Install Python 3.11+ and [SumatraPDF](https://www.sumatrapdfreader.org/).
2. `pip install -r agent/requirements.txt`
3. Set the environment variables: `SERVER_URL`, `AGENT_KEY`, `PRINTER_NAME`, `SUMATRA_PATH`.
4. Test without printing: `python agent/agent.py --dry-run`
5. Run for real: `python agent/agent.py`

**Tests**
```bash
pytest
```

## Testing on real hardware

The automated tests run without a printer. Some things can only be checked by hand:
- Print to "Microsoft Print to PDF" to confirm the pipeline works.
- On a real duplex printer, print a 4-page PDF with each page labelled, and check long-edge vs short-edge flipping.
- Open the page on a real phone browser on the same Wi-Fi.

Printer drivers do not always honour colour and duplex requests, so always test on the actual printer a shop uses.

## Roadmap

1. Finish the MVP (upload, settings, preview, agent, status)
2. Release-on-arrival printing (print only when the student reaches the shop)
3. Pickup QR / OTP
4. UPI payments and automatic refunds
5. Multiple shops, with only online shops listed
6. Live queue visibility ("2 orders ahead of you")
7. DOC and image support

## Team

Design thinking project by Sanjay Santu, Sebin Lalu, Tejassh Tharayil, and Nikhil Stalin.

## Aligned with the UN SDGs

- **SDG 9:** Industry, Innovation and Infrastructure
- **SDG 12:** Responsible Consumption and Production (preview cuts misprints and wasted paper)
- **SDG 4:** Quality Education (less break time lost to queueing)

## License

Not yet chosen. Add a `LICENSE` file before sharing the code publicly.
