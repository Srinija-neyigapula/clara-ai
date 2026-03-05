"""
pipeline_b.py – Pipeline B: Onboarding transcript + v1 memo → v2 memo, spec & changelog.

Usage:
    python scripts/pipeline_b.py account-01 inputs/onboarding/onboarding_01.txt
"""

import os
import sys
import argparse
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config       import ACCOUNTS_DIR
from extract_memo import extract_memo, load_transcript, save_memo
from merge_memo   import merge_memo, load_memo
from agent_spec_generator import generate_agent_spec, save_spec
from changelog    import generate_changelog, save_changelog
from task_tracker import log_task


def run_pipeline_b(account_id: str, transcript_path: str) -> dict:
    """
    Run Pipeline B for a single onboarding transcript.

    Returns the generated v2 agent spec dict.
    """
    print(f"[Pipeline B] account={account_id}  transcript={transcript_path}")

    # ── Load v1 memo ──────────────────────────────────────────────────
    v1_memo_path = os.path.join(ACCOUNTS_DIR, account_id, "v1", "account_memo.json")
    if not os.path.exists(v1_memo_path):
        raise FileNotFoundError(
            f"v1 memo not found for account '{account_id}'. "
            f"Run Pipeline A first.\nExpected: {v1_memo_path}"
        )
    v1_memo = load_memo(v1_memo_path)

    # ── Load & extract onboarding transcript ─────────────────────────
    transcript = load_transcript(transcript_path)
    onboarding_memo = extract_memo(transcript, account_id, stage="onboarding")

    # ── Merge v1 + onboarding → v2 ───────────────────────────────────
    v2_memo, changes = merge_memo(v1_memo, onboarding_memo, onboarding_text=transcript)

    # ── Generate v2 agent spec ────────────────────────────────────────
    v2_spec = generate_agent_spec(v2_memo, version="v2")

    # ── Save outputs ──────────────────────────────────────────────────
    v2_dir = os.path.join(ACCOUNTS_DIR, account_id, "v2")
    os.makedirs(v2_dir, exist_ok=True)

    v2_memo_path = os.path.join(v2_dir, "account_memo.json")
    v2_spec_path = os.path.join(v2_dir, "retell_agent_spec.json")
    save_memo(v2_memo, v2_memo_path)
    save_spec(v2_spec, v2_spec_path)

    # ── Generate & save changelog ─────────────────────────────────────
    changelog_json, changelog_md = generate_changelog(changes, account_id, v1_memo, v2_memo)
    account_dir = os.path.join(ACCOUNTS_DIR, account_id)
    save_changelog(changelog_json, changelog_md, account_dir)

    print(f"  ✓ v2 Memo      → {v2_memo_path}")
    print(f"  ✓ v2 Spec      → {v2_spec_path}")
    print(f"  ✓ Changelog    → {account_dir}/changes.json / changes.md")
    print(f"  ✓ Changes found: {len(changes)}")

    # ── Log task ──────────────────────────────────────────────────────
    log_task(account_id, "pipeline_b", version="v2", details={
        "transcript": transcript_path,
        "changes_count": len(changes),
    })

    return v2_spec


# ─────────────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline B – Onboarding → v2 spec")
    parser.add_argument("account_id",  help="Account ID (must have v1 memo)")
    parser.add_argument("transcript",  help="Path to onboarding transcript .txt file")
    args = parser.parse_args()

    run_pipeline_b(args.account_id, args.transcript)
