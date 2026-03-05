"""
merge_memo.py – Merges onboarding transcript data into v1 memo to produce v2.
Tracks all field-level changes.
"""

import copy
import re
import json
from config import EMERGENCY_KEYWORDS


def _detect_hour_update(text, v1_memo):
    patterns = [
        r"change(?:d)?\s+(?:our\s+)?hours?\s+to\s+([^.]+)",
        r"update(?:d)?\s+(?:our\s+)?hours?\s+to\s+([^.]+)",
        r"new\s+hours?\s+(?:are|will be)\s+([^.]+)",
        r"now\s+open\s+([^.!\n]+)",
        r"hours?\s+(?:are now|changed to|updated to)\s+([^.]+)",
    ]
    lower = text.lower()
    for pat in patterns:
        m = re.search(pat, lower)
        if m:
            new_val = m.group(1).strip().rstrip(".,;")
            return new_val
    return None

def _detect_day_update(text):
    lower = text.lower()
    day_range = re.search(
        r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+(?:to|through|-)\s+'
        r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', lower
    )
    if day_range:
        return f"{day_range.group(1).capitalize()} to {day_range.group(2).capitalize()}"
    return None

def _detect_new_hours_time(text):
    lower = text.lower()
    m = re.search(
        r'(\d{1,2}(?::\d{2})?\s*(?:am|pm))\s*(?:to|through|-)\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm))',
        lower
    )
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return None, None

def _detect_emergency_additions(text, existing):
    lower = text.lower()
    added = []
    # Explicit "add X to emergency" patterns
    for pat in [
        r'add\s+"?([a-z ]+?)"?\s+(?:to\s+(?:the\s+)?emergency|as (?:an?\s+)?emergency)',
        r'include\s+"?([a-z ]+?)"?\s+as\s+(?:an?\s+)?emergency',
    ]:
        for m in re.finditer(pat, lower):
            kw = m.group(1).strip().rstrip(".,")
            if kw not in existing and len(kw) > 2:
                added.append(kw)
    # Also catch new emergency keywords not yet in existing list
    for kw in EMERGENCY_KEYWORDS:
        if kw in lower and kw not in existing and kw not in added:
            added.append(kw)
    return added

def _detect_new_contacts(text):
    """Find new staff/contact lines in the onboarding transcript."""
    contacts = []
    patterns = [
        r'(?:hired|new|added)\s+(?:a\s+)?(?:new\s+)?([a-z ]+?),?\s+([A-Z][a-z]+ [A-Z][a-z]+)',
        r'(?:her|his)\s+(?:direct\s+)?line\s+is\s+(\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4})',
    ]
    name_m = re.search(r'(?:hired|new|added)[^,\n]+,?\s+([A-Z][a-z]+ [A-Z][a-z]+)', text)
    phone_m = re.search(r'(?:her|his|their)\s+(?:direct\s+)?line\s+is\s+(\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4})', text, re.IGNORECASE)
    email_m = re.search(r'([\w.\-]+@[\w.\-]+\.[a-zA-Z]{2,})', text)
    if name_m or phone_m:
        c = {}
        if name_m:
            c["name"] = name_m.group(1)
        if phone_m:
            c["phone"] = phone_m.group(1)
        if email_m:
            c["email"] = email_m.group(0)
        contacts.append(c)
    return contacts

def _detect_new_routing(text, existing_routing):
    """Pick up new routing rules from onboarding."""
    new_routes = []
    for pat in [
        r'route\s+([^.!\n]+?)\s+(?:to|for)\s+([^.!\n]+)',
        r'(?:forward|send|direct)\s+([^.!\n]+?)\s+to\s+([^.!\n]+)',
    ]:
        for m in re.finditer(pat, text, re.IGNORECASE):
            r = m.group(0).strip().rstrip(".,;")
            if len(r) < 100 and r not in existing_routing:
                new_routes.append(r)
    return new_routes

def _detect_new_constraints(text, existing):
    new_c = []
    for pat in [
        r'(?:also\s+)?(?:add|update)[:\s]+(?:never|do not|don\'t)\s+([^.!\n]+)',
        r'(?:never|do not|don\'t)\s+([^.!\n]+)',
    ]:
        for m in re.finditer(pat, text, re.IGNORECASE):
            c = m.group(0).strip().rstrip(".,;")
            if len(c) < 120 and c not in existing:
                new_c.append(c)
    return new_c


def merge_memo(v1_memo, onboarding_memo, onboarding_text=""):
    v2 = copy.deepcopy(v1_memo)
    v2["stage"] = "onboarding"
    changes = []

    # ── Business hours ─────────────────────────────────────────────────
    if onboarding_text:
        new_days = _detect_day_update(onboarding_text)
        new_start, new_end = _detect_new_hours_time(onboarding_text)
        old_h = v1_memo.get("business_hours", {})
        new_h = dict(old_h)
        h_changed = False
        if new_days and new_days != old_h.get("days"):
            new_h["days"] = new_days
            h_changed = True
        if new_start and new_start != old_h.get("start"):
            new_h["start"] = new_start
            h_changed = True
        if new_end and new_end != old_h.get("end"):
            new_h["end"] = new_end
            h_changed = True
        if h_changed:
            changes.append({"field": "business_hours", "old": old_h, "new": new_h})
            v2["business_hours"] = new_h

    # ── Emergency definition ───────────────────────────────────────────
    if onboarding_text:
        existing_em = list(v1_memo.get("emergency_definition", []))
        added_em = _detect_emergency_additions(onboarding_text, existing_em)
        if added_em:
            new_em = existing_em + added_em
            changes.append({"field": "emergency_definition", "old": existing_em, "new": new_em})
            v2["emergency_definition"] = new_em

    # ── Non-emergency routing ──────────────────────────────────────────
    if onboarding_text:
        existing_routing = v1_memo.get("non_emergency_routing_rules", {}).get("destinations", [])
        new_routes = _detect_new_routing(onboarding_text, existing_routing)
        if new_routes:
            merged = list(dict.fromkeys(existing_routing + new_routes))
            old_ner = v1_memo.get("non_emergency_routing_rules", {})
            new_ner = dict(old_ner)
            new_ner["destinations"] = merged
            # Check for new main phone
            phones = re.findall(r'\b(\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4})\b', onboarding_text)
            if phones:
                new_ner["main_phone"] = phones[0]
            changes.append({"field": "non_emergency_routing_rules", "old": old_ner, "new": new_ner})
            v2["non_emergency_routing_rules"] = new_ner

    # ── Integration constraints ────────────────────────────────────────
    if onboarding_text:
        existing_c = list(v1_memo.get("integration_constraints", []))
        new_c = _detect_new_constraints(onboarding_text, existing_c)
        if new_c:
            merged_c = list(dict.fromkeys(existing_c + new_c))
            changes.append({"field": "integration_constraints", "old": existing_c, "new": merged_c})
            v2["integration_constraints"] = merged_c

    # ── Contact updates from onboarding ──────────────────────────────
    if onboarding_text:
        new_contacts = _detect_new_contacts(onboarding_text)
        if new_contacts:
            # Store as additional_contacts list
            existing_ac = v1_memo.get("additional_contacts", [])
            merged_ac = existing_ac + [c for c in new_contacts if c not in existing_ac]
            changes.append({"field": "additional_contacts", "old": existing_ac, "new": merged_ac})
            v2["additional_contacts"] = merged_ac

    # ── Merge open questions ──────────────────────────────────────────
    v2["questions_or_unknowns"] = list(dict.fromkeys(
        v1_memo.get("questions_or_unknowns", []) +
        onboarding_memo.get("questions_or_unknowns", [])
    ))

    return v2, changes


def load_memo(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_memo(memo, path):
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(memo, f, indent=2)
