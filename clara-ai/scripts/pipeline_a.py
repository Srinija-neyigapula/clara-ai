"""
pipeline_a.py – Pipeline A: Demo transcript → v1 account memo + Retell agent spec.

Usage:
    python scripts/pipeline_a.py inputs/demo/demo_01.txt
    python scripts/pipeline_a.py inputs/demo/demo_01.txt --account-id my-account
"""

import os
import sys
import argparse

# Allow running from project root or scripts/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config       import ACCOUNTS_DIR
from extract_memo import extract_memo, load_transcript, save_memo
from agent_spec_generator import generate_agent_spec, save_spec
from task_tracker import log_task


def run_pipeline_a(transcript_path: str, account_id: str = None) -> dict:
    """
    Run Pipeline A for a single demo transcript.

    Returns the generated v1 agent spec dict.
    """
    # ── Derive account_id from filename if not given ──────────────────
    if not account_id:
        base = os.path.splitext(os.path.basename(transcript_path))[0]  # e.g. demo_01
        suffix = base.replace("demo_", "").replace("demo-", "")
        account_id = f"account-{suffix}"

    print(f"[Pipeline A] account={account_id}  transcript={transcript_path}")

    # ── Load transcript ───────────────────────────────────────────────
    transcript = load_transcript(transcript_path)

    # ── Extract memo ──────────────────────────────────────────────────
    memo = extract_memo(transcript, account_id, stage="demo")

    # ── Generate agent spec ───────────────────────────────────────────
    spec = generate_agent_spec(memo, version="v1")

    # ── Save outputs ──────────────────────────────────────────────────
    out_dir = os.path.join(ACCOUNTS_DIR, account_id, "v1")
    os.makedirs(out_dir, exist_ok=True)

    memo_path = os.path.join(out_dir, "account_memo.json")
    spec_path = os.path.join(out_dir, "retell_agent_spec.json")
    save_memo(memo, memo_path)
    save_spec(spec, spec_path)

    print(f"  ✓ Memo  → {memo_path}")
    print(f"  ✓ Spec  → {spec_path}")

    # ── Log task ──────────────────────────────────────────────────────
    log_task(account_id, "pipeline_a", version="v1", details={
        "transcript": transcript_path,
        "business_name": memo.get("business_name"),
    })

    return spec


# ─────────────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline A – Demo → v1 spec")
    parser.add_argument("transcript", help="Path to demo transcript .txt file")
    parser.add_argument("--account-id", default=None, help="Override account ID")
    args = parser.parse_args()

    run_pipeline_a(args.transcript, args.account_id)
