"""
extract_memo.py – Rule-based extraction of fully structured account memos
from demo/onboarding transcripts.  Schema matches assignment spec exactly.
No LLM / API keys required.
"""

import re
import json
from config import EMERGENCY_KEYWORDS


def _normalise(text):
    return text.lower().strip()

def _client_lines(text):
    """Extract lines NOT spoken by Clara/interviewer."""
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r"^(Clara|Interviewer|Agent|Rep|Operator|Sales)\s*:", stripped, re.IGNORECASE):
            continue
        if re.match(r"^(Date|Participants|END OF|---)", stripped, re.IGNORECASE):
            continue
        if re.match(r"^[A-Za-z ]+\s*:", stripped):
            content = re.sub(r"^[A-Za-z ]+\s*:\s*", "", stripped)
            lines.append(content.strip())
    return lines

def _find_business_name(text):
    patterns = [
        r"(?:this is|we are|we're|i'm from|i am from|calling from|company is|name is)\s+([A-Z][A-Za-z0-9 &',.\-]+?)(?:\.|,|\n| and | we |$)",
        r"(?:welcome to|thanks for calling|thank you for calling)\s+([A-Z][A-Za-z0-9 &',.\-]+?)(?:\.|,|\n|$)",
        r"(?:–|-)\s+([A-Z][A-Za-z0-9 &',.\-]+?),",
        r"we(?:'re| are)\s+([A-Z][A-Za-z0-9 &',.\-]+?)(?:,|\.|!)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            c = m.group(1).strip().rstrip(".,;!")
            if len(c) > 3:
                return c
    return "Unknown Business"

def _find_hours(text):
    lower = _normalise(text)
    # Timezone
    tz = "local time"
    for pat, zone in [
        (r'\b(eastern|est|edt)\b', "America/New_York"),
        (r'\b(central|cst|cdt)\b', "America/Chicago"),
        (r'\b(mountain|mst|mdt)\b', "America/Denver"),
        (r'\b(pacific|pst|pdt)\b', "America/Los_Angeles"),
    ]:
        if re.search(pat, lower):
            tz = zone
            break

    hours_m = re.search(
        r'(\d{1,2}(?::\d{2})?\s*(?:am|pm))\s*(?:to|through|until|-)\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm))',
        lower
    )
    start = hours_m.group(1).strip() if hours_m else "unknown"
    end   = hours_m.group(2).strip() if hours_m else "unknown"

    days = "Monday to Friday"
    day_range = re.search(
        r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+(?:to|through|-)\s+'
        r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', lower
    )
    if day_range:
        days = f"{day_range.group(1).capitalize()} to {day_range.group(2).capitalize()}"
    elif "monday through saturday" in lower or "monday to saturday" in lower:
        days = "Monday to Saturday"
    elif "monday through friday" in lower or "monday to friday" in lower:
        days = "Monday to Friday"
    elif "seven days" in lower or "7 days" in lower:
        days = "Monday to Sunday"

    return {"days": days, "start": start, "end": end, "timezone": tz}

def _find_address(text):
    m = re.search(
        r'\d+\s+[A-Z][a-zA-Z0-9 .,]+(?:Street|St|Avenue|Ave|Road|Rd|Blvd|Boulevard|Drive|Dr|Lane|Ln|Way|Court|Ct)[^,\n]*',
        text
    )
    return m.group(0).strip() if m else ""

def _find_services(text):
    services = []
    for pat in [
        r"(?:we (?:do|handle|provide|offer|specialize in)|our services include)\s+([^.!\n]+)",
        r"(?:services?)\s+(?:include|like|such as|are)\s+([^.!\n]+)",
    ]:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            parts = re.split(r',\s*|\s+and\s+', m.group(1))
            for p in parts:
                p = p.strip().rstrip(".,;")
                if 3 < len(p) < 60:
                    services.append(p)
    return services or ["General services"]

def _find_emergency_definition(text):
    lower = _normalise(text)
    found = []
    for kw in EMERGENCY_KEYWORDS:
        if kw in lower and kw not in found:
            found.append(kw)
    m = re.search(
        r'(?:emergency|emergencies|urgent)\s+(?:calls?|situations?|types?)[:\s\u2013-]+([^.\n]+)',
        lower
    )
    if m:
        for p in re.split(r',\s*|\s+and\s+', m.group(1)):
            p = p.strip().rstrip(".,;")
            if 2 < len(p) < 50 and p not in found:
                found.append(p)
    return found or ["critical system failure"]

def _find_emergency_routing(text):
    phones = re.findall(r'\b(\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4})\b', text)
    primary_phone = ""
    primary_contact = ""
    em_m = re.search(
        r'(?:emergency|urgent|on-call|dispatch).*?(\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4})',
        text, re.IGNORECASE | re.DOTALL
    )
    if em_m:
        primary_phone = em_m.group(1)
    tech_m = re.search(
        r'(?:on-call|emergency|dispatch)\s+(?:technician|tech|line|contact|number)\s+(?:is\s+)?([A-Z][a-z]+(?: [A-Z][a-z]+)?)',
        text, re.IGNORECASE
    )
    if tech_m:
        primary_contact = tech_m.group(1)
    lower = _normalise(text)
    fallback = "Advise caller to call 911 if life or property is at immediate risk"
    fb_m = re.search(r'(?:fallback|if (?:no one|unavailable|not available))[:\s]+([^.\n]+)', lower)
    if fb_m:
        fallback = fb_m.group(1).strip()
    return {
        "primary_contact": primary_contact or "On-call technician",
        "primary_phone"  : primary_phone or (phones[0] if phones else ""),
        "order"          : ["primary_contact", "fallback"],
        "fallback"       : fallback,
        "transfer_timeout_sec": 30,
    }

def _find_non_emergency_routing(text):
    phones = re.findall(r'\b(\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4})\b', text)
    phone = ""
    main_m = re.search(
        r'(?:main line|front desk|office|general|scheduling|reception)[^.]*?(\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4})',
        text, re.IGNORECASE
    )
    if main_m:
        phone = main_m.group(1)
    destinations = []
    for pat in [
        r'(?:route|transfer|send|forward|direct)\s+(?:[a-z ]+calls?\s+)?(?:to|for)\s+([^,.!\n]+)',
    ]:
        for m in re.finditer(pat, text, re.IGNORECASE):
            dest = m.group(0).strip()
            if len(dest) < 80:
                destinations.append(dest)
    return {
        "main_phone"  : phone or (phones[-1] if len(phones) > 1 else (phones[0] if phones else "")),
        "destinations": destinations or ["Main office line"],
        "voicemail"   : "after-hours voicemail",
    }

def _find_call_transfer_rules(text):
    lower = _normalise(text)
    timeout = 30
    t_m = re.search(r'(\d+)\s*(?:seconds?|sec)', lower)
    if t_m:
        timeout = int(t_m.group(1))
    return {
        "timeout_sec"            : timeout,
        "retries"                : 1,
        "on_fail_message"        : "I'm sorry, I was unable to connect you. I'll make sure someone calls you back shortly.",
        "collect_before_transfer": ["caller_name", "callback_number"],
    }

def _find_integration_constraints(text):
    constraints = []
    for pat in [
        r"(?:never|do not|don't|avoid)\s+(?:create|add|enter|use)\s+([^.!\n]+)",
        r"(?:not allowed|prohibited)\s+(?:to\s+)?([^.!\n]+)",
    ]:
        for m in re.finditer(pat, text, re.IGNORECASE):
            c = m.group(0).strip().rstrip(".,;")
            if len(c) < 120:
                constraints.append(c)
    return constraints

def _find_contact(text):
    contact = {}
    phone_m = re.search(r'\b(\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4})\b', text)
    if phone_m:
        contact["phone"] = phone_m.group(1)
    email_m = re.search(r'[\w.\-]+@[\w.\-]+\.[a-zA-Z]{2,}', text)
    if email_m:
        contact["email"] = email_m.group(0)
    name_m = re.search(
        r"(?:my name is|i am|i'm|this is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        text, re.IGNORECASE
    )
    if name_m:
        contact["name"] = name_m.group(1)
    return contact

def _find_questions(text, memo):
    gaps = []
    hours = memo.get("business_hours", {})
    if hours.get("start") == "unknown":
        gaps.append("Business hours start time not clearly stated")
    if hours.get("end") == "unknown":
        gaps.append("Business hours end time not clearly stated")
    if not memo.get("emergency_routing_rules", {}).get("primary_phone"):
        gaps.append("No emergency callback phone number detected")
    if not memo.get("office_address"):
        gaps.append("Office address not provided")
    for line in _client_lines(text):
        if "?" in line and len(line) > 15:
            gaps.append(f"Client raised: {line.strip()[:100]}")
    return gaps


def extract_memo(transcript, account_id, stage="demo"):
    hours_info = _find_hours(transcript)
    memo = {
        "account_id"                 : account_id,
        "stage"                      : stage,
        "company_name"               : _find_business_name(transcript),
        "contact"                    : _find_contact(transcript),
        "office_address"             : _find_address(transcript),
        "business_hours"             : hours_info,
        "services_supported"         : _find_services(transcript),
        "emergency_definition"       : _find_emergency_definition(transcript),
        "emergency_routing_rules"    : _find_emergency_routing(transcript),
        "non_emergency_routing_rules": _find_non_emergency_routing(transcript),
        "call_transfer_rules"        : _find_call_transfer_rules(transcript),
        "integration_constraints"    : _find_integration_constraints(transcript),
        "after_hours_flow_summary"   : (
            f"Greet caller, confirm office is closed, ask if emergency. "
            f"Emergency: collect name/number/address immediately, attempt transfer, fallback if fails. "
            f"Non-emergency: take message, advise next available time "
            f"({hours_info['days']}, {hours_info['start']}–{hours_info['end']})."
        ),
        "office_hours_flow_summary"  : (
            f"Greet caller warmly, identify purpose, collect name and callback number, "
            f"route/transfer per routing rules, confirm next steps, ask if anything else, close."
        ),
        "notes": "",
    }
    memo["questions_or_unknowns"] = _find_questions(transcript, memo)
    return memo


def load_transcript(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def save_memo(memo, path):
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(memo, f, indent=2)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python extract_memo.py <transcript.txt> <account_id>")
        sys.exit(1)
    t = load_transcript(sys.argv[1])
    m = extract_memo(t, sys.argv[2])
    print(json.dumps(m, indent=2))
