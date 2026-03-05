"""
config.py – Central configuration for the Clara AI pipeline.
"""

import os

# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUTS_DIR  = os.path.join(BASE_DIR, "inputs")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
SCHEMAS_DIR = os.path.join(BASE_DIR, "schemas")

DEMO_DIR        = os.path.join(INPUTS_DIR, "demo")
ONBOARDING_DIR  = os.path.join(INPUTS_DIR, "onboarding")
ACCOUNTS_DIR    = os.path.join(OUTPUTS_DIR, "accounts")
TASK_TRACKER_DB = os.path.join(OUTPUTS_DIR, "tasks.sqlite")
BATCH_SUMMARY   = os.path.join(OUTPUTS_DIR, "batch_summary.json")

# ─────────────────────────────────────────────
# Voice / agent defaults
# ─────────────────────────────────────────────
DEFAULT_VOICE = "11labs-Rachel"
DEFAULT_LANGUAGE = "en-US"
FALLBACK_PHONE = "the main office line"

# ─────────────────────────────────────────────
# Keyword sets used by the extractor
# ─────────────────────────────────────────────
EMERGENCY_KEYWORDS = [
    "emergency", "urgent", "fire", "flood", "leak", "outage",
    "critical", "breakdown", "failure", "hazard", "gas leak",
    "power out", "no heat", "no power", "burst pipe",
]

HOURS_PATTERNS = [
    r"(\d{1,2}(?::\d{2})?\s*(?:am|pm))\s*(?:to|through|until|-)\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm))",
    r"(\d{1,2}(?::\d{2})?)\s*(?:to|-)\s*(\d{1,2}(?::\d{2})?)\s*(am|pm)?",
]

DAYS_PATTERNS = [
    r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
    r"(mon|tue|wed|thu|fri|sat|sun)",
    r"(weekday|weekend|week\s*day|week\s*end)s?",
    r"(monday\s*(?:through|to|-)\s*friday)",
    r"(monday\s*(?:through|to|-)\s*saturday)",
]
