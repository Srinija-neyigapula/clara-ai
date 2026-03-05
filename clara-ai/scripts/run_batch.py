"""
run_batch.py – Processes all demo/onboarding pairs in inputs/ directory.
Outputs a batch_summary.json at the end.
"""

import os
import sys
import json
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config      import DEMO_DIR, ONBOARDING_DIR, ACCOUNTS_DIR, BATCH_SUMMARY
from pipeline_a  import run_pipeline_a
from pipeline_b  import run_pipeline_b
from task_tracker import export_tasks_json
from config      import OUTPUTS_DIR


def _id_from_filename(fname: str, prefix: str) -> str:
    """e.g. 'demo_01.txt' → '01', 'onboarding_bens_electric.txt' → 'bens_electric'"""
    base = os.path.splitext(fname)[0]
    return base.replace(prefix + "_", "").replace(prefix + "-", "")


def run_batch() -> dict:
    os.makedirs(DEMO_DIR,       exist_ok=True)
    os.makedirs(ONBOARDING_DIR, exist_ok=True)
    os.makedirs(OUTPUTS_DIR,    exist_ok=True)

    summary = {
        "run_at"    : datetime.datetime.utcnow().isoformat(),
        "pipeline_a": [],
        "pipeline_b": [],
        "errors"    : [],
    }

    # ── Collect demo files ────────────────────────────────────────────
    demo_files = sorted(
        f for f in os.listdir(DEMO_DIR) if f.endswith(".txt")
    )

    # ── Pipeline A ────────────────────────────────────────────────────
    for fname in demo_files:
        suffix = _id_from_filename(fname, "demo")
        account_id = f"account-{suffix}"
        path = os.path.join(DEMO_DIR, fname)
        try:
            run_pipeline_a(path, account_id)
            summary["pipeline_a"].append({"account_id": account_id, "status": "ok"})
        except Exception as e:
            msg = f"Pipeline A failed for {account_id}: {e}"
            print(f"[ERROR] {msg}")
            summary["errors"].append(msg)
            summary["pipeline_a"].append({"account_id": account_id, "status": "error", "error": str(e)})

    # ── Pipeline B ────────────────────────────────────────────────────
    onboarding_files = sorted(
        f for f in os.listdir(ONBOARDING_DIR) if f.endswith(".txt")
    )
    for fname in onboarding_files:
        suffix = _id_from_filename(fname, "onboarding")
        account_id = f"account-{suffix}"
        path = os.path.join(ONBOARDING_DIR, fname)
        try:
            run_pipeline_b(account_id, path)
            summary["pipeline_b"].append({"account_id": account_id, "status": "ok"})
        except FileNotFoundError as e:
            msg = f"Pipeline B skipped {account_id} (no v1 memo): {e}"
            print(f"[WARN]  {msg}")
            summary["errors"].append(msg)
            summary["pipeline_b"].append({"account_id": account_id, "status": "skipped", "error": str(e)})
        except Exception as e:
            msg = f"Pipeline B failed for {account_id}: {e}"
            print(f"[ERROR] {msg}")
            summary["errors"].append(msg)
            summary["pipeline_b"].append({"account_id": account_id, "status": "error", "error": str(e)})

    # ── Save outputs ──────────────────────────────────────────────────
    summary["total_accounts"] = len(set(
        [r["account_id"] for r in summary["pipeline_a"]] +
        [r["account_id"] for r in summary["pipeline_b"]]
    ))
    summary["total_errors"] = len(summary["errors"])
    summary["pipeline_a_success"] = sum(1 for r in summary["pipeline_a"] if r["status"] == "ok")
    summary["pipeline_b_success"] = sum(1 for r in summary["pipeline_b"] if r["status"] == "ok")
    summary["pipeline_a_failed"]  = sum(1 for r in summary["pipeline_a"] if r["status"] != "ok")
    summary["pipeline_b_failed"]  = sum(1 for r in summary["pipeline_b"] if r["status"] != "ok")
    # Per-account change counts
    account_stats = []
    for r in summary["pipeline_b"]:
        aid = r["account_id"]
        chg_path = os.path.join(ACCOUNTS_DIR, aid, "changes.json")
        changes_count = 0
        if os.path.exists(chg_path):
            import json as _json
            with open(chg_path) as f:
                chg = _json.load(f)
            changes_count = chg.get("total_changes", 0)
        account_stats.append({"account_id": aid, "v1_to_v2_changes": changes_count, "status": r["status"]})
    summary["account_stats"] = account_stats

    with open(BATCH_SUMMARY, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n[Batch] Summary → {BATCH_SUMMARY}")

    # Export task tracker to JSON as well
    task_json_path = os.path.join(OUTPUTS_DIR, "task_tracker.json")
    export_tasks_json(task_json_path)
    print(f"[Batch] Tasks   → {task_json_path}")

    return summary


if __name__ == "__main__":
    result = run_batch()
    print(f"\nDone. Accounts: {result['total_accounts']}, Errors: {result['total_errors']}")
