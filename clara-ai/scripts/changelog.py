"""
changelog.py – Generates a Markdown and JSON changelog from a list of
field-level changes produced by merge_memo.
"""

import json
import datetime
import os


def generate_changelog(changes: list, account_id: str, v1_memo: dict, v2_memo: dict) -> tuple[dict, str]:
    """
    Produce changelog JSON and Markdown string.

    Returns
    -------
    (changelog_dict, markdown_string)
    """
    now = datetime.datetime.utcnow().isoformat()
    changelog = {
        "account_id"  : account_id,
        "generated_at": now,
        "total_changes": len(changes),
        "changes"     : changes,
    }

    lines = [
        f"# Changelog – {account_id}",
        f"_Generated: {now}_",
        "",
        f"**Total changes:** {len(changes)}",
        "",
        "---",
        "",
    ]

    if not changes:
        lines.append("No changes detected between v1 and v2.")
    else:
        for i, ch in enumerate(changes, 1):
            field = ch.get("field", "unknown")
            old   = ch.get("old")
            new   = ch.get("new")
            lines.append(f"## {i}. `{field}`")
            lines.append(f"- **Before (v1):** `{old}`")
            lines.append(f"- **After  (v2):** `{new}`")
            lines.append("")

    lines += [
        "---",
        "",
        "## Summary",
        f"- Account : {account_id}",
        f"- Business: {v2_memo.get('company_name', v2_memo.get('business_name', 'N/A'))}",
        f"- Hours v1: {v1_memo.get('business_hours', {}).get('start','?')}–{v1_memo.get('business_hours', {}).get('end','?')} ({v1_memo.get('business_hours', {}).get('days','?')})",
        f"- Hours v2: {v2_memo.get('business_hours', {}).get('start','?')}–{v2_memo.get('business_hours', {}).get('end','?')} ({v2_memo.get('business_hours', {}).get('days','?')})",
    ]

    return changelog, "\n".join(lines)


def save_changelog(changelog: dict, md: str, base_dir: str) -> None:
    os.makedirs(base_dir, exist_ok=True)
    with open(os.path.join(base_dir, "changes.json"), "w") as f:
        json.dump(changelog, f, indent=2)
    with open(os.path.join(base_dir, "changes.md"), "w") as f:
        f.write(md)
