# Closed-Room B2B Negotiation Hub v2 (AI Hackathon 2.0 – Use Case 1)

Buyer agent + 2–3 supplier agents negotiate in **isolated rooms** through a deterministic counter-offer
loop. The best deal wins and a **Purchase Order PDF** is generated.

## Run locally in VS Code
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows   (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py             # opens http://localhost:8501
python test_core.py              # optional self-test
```
No API key needed (rule-based agents). For LLM agents: copy `.env.example` -> `.env`, add a key, and turn on
**Use LLM agents** in the sidebar. Press **F5** in VS Code to run/debug (`.vscode/launch.json`).

## New in v2
| Feature | Where | Demo tip |
|---|---|---|
| 🔴 **Live replay** | sidebar toggle + speed | Each offer streams into the chat with a typing indicator while the price chart updates |
| 🛡️ **Red-team lab** | "Red-team lab" tab | Pick a preset attack, then switch the two defence layers off to see the leak; use **attack matrix** to compare all 4 settings |
| 📊 **Savings dashboard** | Outcome → "Savings dashboard" | Saved vs budget and vs average first ask, cycle time, effort avoided, annual projection (assumptions editable) |
| 🔊 **Audio** | "Transcripts & audio" | Play full negotiation, one supplier, or the deal summary. Separate buyer/supplier voices, speed, click a line to jump. Also downloads a .txt transcript |

Audio uses the browser's built-in speech engine (Chrome / Edge / Safari), so it needs no extra packages or keys.
Pick different voices in the two dropdowns if only one sounds available.

## Architecture
| File | Role |
|---|---|
| `models.py` | Pydantic schemas + supplier cost model |
| `agents.py` | Buyer / Supplier agents (private state, LiteLLM + guardrails + rule fallback, `probe()` for red-team) |
| `orchestrator.py` | Round loop, anonymised market pressure, weighted scoring, leak audit |
| `security.py` | Input filter (prompt-injection patterns) + output redactor (masks private numbers) |
| `analytics.py` | Savings and time metrics |
| `audio.py` | Transcript builder and browser text-to-speech player |
| `po_generator.py` | ReportLab PO PDF |
| `app.py` | Streamlit UI |
| `test_core.py` | Self-test of engine, guardrails, security, PO |

## Notes
- Red-team lab without an API key uses a *simulated unguarded model* that spills secrets when asked, so the
  defence layers have something to stop. With an LLM enabled, the real model replies and the same layers apply.
- Scoring: 60% price, 25% delivery, 15% payment terms.
- Savings "manual baseline" figures are assumptions you can edit, not measured data.
