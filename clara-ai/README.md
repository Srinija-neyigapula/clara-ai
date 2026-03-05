# Clara AI – Zero-Cost Automation Pipeline

> **Demo call → Retell Agent v1 → Onboarding → Agent v2**  
> 5 demo + 5 onboarding calls. No API keys. No paid services. Pure Python 3.10+.

---

## Architecture & Data Flow

```
inputs/demo/<id>.txt
       │
       ▼
  [extract_memo.py]           ← rule-based regex extractor (zero LLM cost)
       │
       ▼
  account_memo.json (v1)      ← structured JSON: hours, routing, emergencies...
       │
       ▼
  [agent_spec_generator.py]   ← prompt template builder
       │
       ▼
  retell_agent_spec.json (v1) → paste into Retell Dashboard
       │
       └── [task_tracker.py]  → tasks.sqlite  (SQLite task log)

inputs/onboarding/<id>.txt
       │
       ▼
  [merge_memo.py]             ← detects field-level changes vs v1
       │
       ├── account_memo.json (v2)
       ├── retell_agent_spec.json (v2)
       ├── changes.json              ← machine-readable diff
       └── changes.md                ← human-readable changelog
```

### Module Map

| File | Purpose |
|---|---|
| `scripts/config.py` | Central constants, paths, keyword lists |
| `scripts/extract_memo.py` | Regex/rule-based transcript → structured memo |
| `scripts/agent_spec_generator.py` | Memo → Retell system prompt + spec |
| `scripts/merge_memo.py` | v1 memo + onboarding transcript → v2 memo + changes |
| `scripts/changelog.py` | changes list → `changes.json` + `changes.md` |
| `scripts/task_tracker.py` | SQLite task logger (zero-cost Asana mock) |
| `scripts/pipeline_a.py` | Pipeline A orchestrator: Demo → v1 |
| `scripts/pipeline_b.py` | Pipeline B orchestrator: Onboarding → v2 |
| `scripts/run_batch.py` | Batch runner: all 5+5 files |
| `scripts/diff_viewer.py` | CLI diff viewer: v1 vs v2 |
| `dashboard.html` | Web dashboard (open in browser, no server needed) |

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/your-username/clara-ai.git
cd clara-ai

# 2. Run the full pipeline (no install required)
python run.py

# 3. View outputs
ls outputs/accounts/

# 4. Open dashboard (optional)
open dashboard.html   # macOS
# or just double-click dashboard.html in your file explorer
```

**Requirements:** Python 3.10+ · No `pip install` needed · No API keys.

---

## Running the Pipeline

### Full batch (all 5 demo + 5 onboarding)
```bash
python run.py
```

### Single account – Pipeline A (demo → v1)
```bash
python scripts/pipeline_a.py inputs/demo/demo_01.txt
python scripts/pipeline_a.py inputs/demo/demo_01.txt --account-id my-account
```

### Single account – Pipeline B (onboarding → v2)
```bash
# Requires Pipeline A to have run first for this account
python scripts/pipeline_b.py account-01 inputs/onboarding/onboarding_01.txt
```

### View v1 vs v2 diff
```bash
python scripts/diff_viewer.py account-01
```

### View task log
```bash
python scripts/task_tracker.py
```

---

## Adding Your Dataset

**File naming convention:**

| File | Account ID derived |
|---|---|
| `inputs/demo/demo_01.txt` | `account-01` |
| `inputs/onboarding/onboarding_01.txt` | `account-01` |
| `inputs/demo/demo_acme.txt` | `account-acme` |
| `inputs/onboarding/onboarding_acme.txt` | `account-acme` |

Same `<id>` suffix links demo and onboarding to one account. Drop your `.txt` files and run `python run.py`.

---

## Output Structure

```
outputs/
├── accounts/
│   └── <account_id>/
│       ├── v1/
│       │   ├── account_memo.json        ← structured memo (all required fields)
│       │   └── retell_agent_spec.json   ← system prompt + Retell config
│       ├── v2/
│       │   ├── account_memo.json        ← updated memo
│       │   └── retell_agent_spec.json   ← updated spec
│       ├── changes.json                 ← field-level diff (machine-readable)
│       └── changes.md                   ← human-readable changelog
├── batch_summary.json                   ← run metrics, per-account stats
├── task_tracker.json                    ← exported task log
└── tasks.sqlite                         ← SQLite task DB
```

---

## Account Memo JSON – Field Reference

Every account memo includes:

| Field | Description |
|---|---|
| `account_id` | Unique identifier (e.g. `account-01`) |
| `company_name` | Business name extracted from transcript |
| `business_hours` | `{days, start, end, timezone}` |
| `office_address` | Physical address if mentioned |
| `services_supported` | List of services mentioned |
| `emergency_definition` | List of emergency trigger keywords |
| `emergency_routing_rules` | Primary contact, phone, fallback, timeout |
| `non_emergency_routing_rules` | Main phone, destinations, voicemail |
| `call_transfer_rules` | Timeout, retries, collect-before-transfer, fail message |
| `integration_constraints` | E.g. "never create sprinkler jobs in ServiceTrade" |
| `after_hours_flow_summary` | Text description of after-hours handling |
| `office_hours_flow_summary` | Text description of business-hours handling |
| `questions_or_unknowns` | Gaps flagged for human review |
| `notes` | Short freeform notes |

---

## Retell Agent Spec – Field Reference

| Field | Description |
|---|---|
| `version` | `v1` or `v2` |
| `agent_name` | Display name in Retell |
| `voice_style` | Voice ID (e.g. `11labs-Rachel`) |
| `system_prompt` | Full generated prompt |
| `begin_message` | Opening greeting |
| `key_variables` | Extracted: timezone, hours, address, phones |
| `tool_invocation_placeholders` | Internal markers (never shown to caller) |
| `call_transfer_protocol` | Collect info, announce, timeout, retries |
| `fallback_protocol` | What to say/do if transfer fails |

### System Prompt Hygiene
Every generated prompt includes:
- Business hours flow: greeting → identify purpose → collect name/number → route → transfer → fallback → confirm → close
- After-hours flow: greet → inform hours → confirm emergency → collect name/number/address → transfer → fallback → assure callback
- No mention of "function calls" or internal tools to caller
- Clear transfer-fail fallback on every path
- "Anything else?" close on every call
- AI identity not revealed unless sincerely asked

---

## n8n Setup (Optional Orchestrator)

### Docker (recommended)
```bash
docker compose up -d
# Open http://localhost:5678
# Import: workflows/n8n_mock_workflow.json
```

### Direct install
```bash
npx n8n
```

### Environment Variables
```
N8N_BASIC_AUTH_ACTIVE=false
GENERIC_TIMEZONE=America/Chicago
```

See `docker-compose.yml` for full config.

---

## Dashboard

Open `dashboard.html` directly in any browser — no server or install needed.

Features:
- Stats bar: accounts processed, Pipeline A/B success counts, total v1→v2 changes
- Account cards with hours comparison and change count
- Interactive per-account detail: v1→v2 diff, memo JSON viewer, system prompt viewer, changelog

---

## Retell Manual Import

See [RETELL_SETUP.md](RETELL_SETUP.md) for step-by-step instructions to paste the generated spec into the Retell Dashboard (free tier compatible).

---

## Known Limitations

| Area | Current Limitation |
|---|---|
| **Extraction** | Rule-based regex; may miss unusual phrasings |
| **Business name** | Relies on common sentence patterns |
| **Retell** | Manual import only (free tier has no API agent creation) |
| **Task tracker** | SQLite only; no Asana/Jira integration |
| **Transcription** | Accepts `.txt` only; audio needs external tool (e.g. Whisper) |
| **Timezone** | Defaults to "local time" if not stated |

---

## What I Would Improve with Production Access

1. **LLM extraction** — Replace regex with `gpt-4o-mini` structured JSON output (~$0.001/transcript)
2. **Retell API** — Auto-deploy specs via `POST /create-agent` with a paid Retell plan
3. **Real-time transcription** — Pipe audio to Gladia/Deepgram for automatic `.txt` generation
4. **Cloud DB** — Swap SQLite for Supabase free tier (remote, queryable, multi-user)
5. **Asana integration** — Replace SQLite mock with real Asana task API
6. **Webhook triggers** — n8n on AWS EC2 free tier with webhooks from Retell/Gladia
7. **Change alerts** — Email/Slack when v2 modifies critical emergency routing fields

---

## Data & Privacy

- Do not commit real customer PII or raw recordings.
- `.gitignore` excludes `account_memo.json` outputs and `tasks.sqlite` by default.
- Treat all transcripts as confidential.

---

## License

MIT
