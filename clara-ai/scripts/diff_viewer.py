"""
diff_viewer.py – Pretty-print v1 vs v2 diff for an account.

Usage:
    python scripts/diff_viewer.py account-01
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ACCOUNTS_DIR


def view_diff(account_id: str) -> None:
    account_dir = os.path.join(ACCOUNTS_DIR, account_id)
    v1_path  = os.path.join(account_dir, "v1", "account_memo.json")
    v2_path  = os.path.join(account_dir, "v2", "account_memo.json")
    chg_path = os.path.join(account_dir, "changes.json")

    if not os.path.exists(v1_path):
        print(f"[ERROR] v1 memo not found: {v1_path}")
        return
    if not os.path.exists(v2_path):
        print(f"[ERROR] v2 memo not found: {v2_path}")
        return

    with open(v1_path)  as f: v1 = json.load(f)
    with open(v2_path)  as f: v2 = json.load(f)

    print(f"\n{'='*60}")
    print(f"  Account: {account_id}  |  Business: {v2.get('business_name')}")
    print(f"{'='*60}")

    fields = ["business_hours", "operating_days", "emergencies", "routing", "contact"]
    for field in fields:
        old_val = v1.get(field)
        new_val = v2.get(field)
        changed = old_val != new_val
        marker = "CHANGED" if changed else "same"
        print(f"\n  [{marker}] {field}")
        if changed:
            print(f"    v1: {old_val}")
            print(f"    v2: {new_val}")
        else:
            print(f"    {old_val}")

    if os.path.exists(chg_path):
        with open(chg_path) as f:
            chg = json.load(f)
        print(f"\n  Total recorded changes: {chg.get('total_changes', '?')}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python diff_viewer.py <account_id>")
        sys.exit(1)
    view_diff(sys.argv[1])
