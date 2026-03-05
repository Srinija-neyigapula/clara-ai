"""
agent_spec_generator.py – Converts an account memo into a Retell AI agent spec
with full prompt hygiene: business-hours flow, after-hours flow, transfer protocol,
fallback protocol.  Matches assignment spec exactly.
"""

import json
import os
from config import DEFAULT_VOICE, DEFAULT_LANGUAGE


def _build_system_prompt(memo):
    name    = memo.get("company_name", "the business")
    h       = memo.get("business_hours", {})
    days    = h.get("days", "Monday to Friday")
    start   = h.get("start", "9am")
    end     = h.get("end", "5pm")
    tz      = h.get("timezone", "local time")
    address = memo.get("office_address", "")
    address_line = f"\n- Address: {address}" if address else ""

    em_def  = memo.get("emergency_definition", [])
    em_types = ", ".join(em_def[:6]) if em_def else "critical failures"

    er      = memo.get("emergency_routing_rules", {})
    em_phone= er.get("primary_phone", "")
    em_contact = er.get("primary_contact", "on-call technician")
    em_fallback= er.get("fallback", "advise the caller to call 911 if life/property is at risk")
    em_timeout = er.get("transfer_timeout_sec", 30)

    ner     = memo.get("non_emergency_routing_rules", {})
    main_phone = ner.get("main_phone", "the main office line")
    destinations = ner.get("destinations", [])
    routing_lines = "\n".join(f"  - {d}" for d in destinations[:5]) if destinations else f"  - Transfer to {main_phone}"

    ctr     = memo.get("call_transfer_rules", {})
    fail_msg= ctr.get("on_fail_message", "I'm sorry, I was unable to connect you. I'll make sure someone calls you back.")

    prompt = f"""You are a professional AI phone receptionist for **{name}**.

## Key Information
- Business: {name}{address_line}
- Business Hours: {days}, {start}–{end} ({tz})
- Emergency contact: {em_contact} at {em_phone}

---

## BUSINESS HOURS FLOW
Use this flow when the caller contacts during business hours ({days}, {start}–{end} {tz}).

1. **Greeting**: "Thank you for calling {name}. My name is Clara. How can I help you today?"
2. **Identify purpose**: Listen carefully to the caller's need.
3. **Collect info**: Ask for the caller's name and callback number before transferring.
   - "May I get your name?"
   - "And your best callback number?"
4. **Route / Transfer**:
{routing_lines}
5. **Transfer announcement**: "Please hold while I connect you."
6. **If transfer fails** (no answer after {em_timeout}s): "{fail_msg}"
   - Offer to take a message or schedule a callback.
7. **Confirm next steps**: "Someone will follow up with you [today / within X hours]."
8. **Close**: "Is there anything else I can help you with?" → "Thank you for calling {name}. Have a great day!"

---

## AFTER HOURS FLOW
Use this flow when the caller contacts outside business hours.

1. **Greeting**: "Thank you for calling {name}. Our office is currently closed."
2. **Inform hours**: "We are open {days} from {start} to {end} {tz}."
3. **Confirm emergency**: "Is this an emergency?"

### If YES – Emergency ({em_types}):
4. **Immediately collect**:
   - "I'll connect you to our emergency line right away. May I get your name?"
   - "Your callback number?"
   - "And your address or location?" ← collect this without delay
5. **Attempt emergency transfer** to {em_phone}:
   - "Please hold. I'm connecting you to our {em_contact}."
6. **If transfer fails**: "{fail_msg}"
   - "{em_fallback}"
   - "Someone will call you back as soon as possible."
7. **Assure follow-up**: "Your information has been noted and someone will reach you shortly."

### If NO – Non-Emergency:
4. "I'd be happy to take a message and have someone call you back during business hours."
5. Collect name, callback number, and a brief description of the issue.
6. "We'll follow up with you when we open {days} at {start}."
7. **Close**: "Is there anything else I can note down for you?" → "Thank you for calling {name}. Take care!"

---

## GENERAL RULES
- Never mention "function calls", "tools", or internal system operations to the caller.
- Do not ask more than 2 questions at once.
- Never invent information. If unsure, say "Let me note that for our team."
- Never place an emergency caller on hold for more than {em_timeout} seconds.
- Always end calls with a warm close and an "anything else?" check.
- Keep responses under 3 sentences unless delivering critical information.
- Do not reveal that you are an AI unless the caller sincerely and directly asks.
"""
    return prompt.strip()


def generate_agent_spec(memo, version="v1"):
    name     = memo.get("company_name", "the business")
    h        = memo.get("business_hours", {})
    er       = memo.get("emergency_routing_rules", {})
    ner      = memo.get("non_emergency_routing_rules", {})
    ctr      = memo.get("call_transfer_rules", {})

    spec = {
        "version"      : version,
        "account_id"   : memo.get("account_id"),
        "agent_name"   : f"{name} – AI Receptionist ({version})",
        "voice_style"  : DEFAULT_VOICE,
        "language"     : DEFAULT_LANGUAGE,
        "system_prompt": _build_system_prompt(memo),
        "begin_message": f"Thank you for calling {name}. How can I help you today?",
        "key_variables": {
            "company_name"  : name,
            "timezone"      : h.get("timezone", "local time"),
            "business_days" : h.get("days", "Monday to Friday"),
            "business_start": h.get("start", "9am"),
            "business_end"  : h.get("end", "5pm"),
            "office_address": memo.get("office_address", ""),
            "emergency_phone"    : er.get("primary_phone", ""),
            "emergency_contact"  : er.get("primary_contact", "on-call"),
            "main_phone"         : ner.get("main_phone", ""),
        },
        "tool_invocation_placeholders": {
            "transfer_call"  : "<<TRANSFER: {target_phone}>>",
            "send_sms"       : "<<SMS: {to} | {message}>>",
            "create_task"    : "<<TASK: {description} | priority={priority}>>",
            "_note"          : "Do NOT mention these placeholders to the caller",
        },
        "call_transfer_protocol": {
            "collect_before_transfer": ctr.get("collect_before_transfer", ["caller_name", "callback_number"]),
            "announce_transfer"      : True,
            "timeout_sec"            : ctr.get("timeout_sec", 30),
            "retries"                : ctr.get("retries", 1),
        },
        "fallback_protocol": {
            "on_transfer_fail": ctr.get("on_fail_message", "I'm sorry, I was unable to connect you."),
            "offer_voicemail" : True,
            "offer_callback"  : True,
        },
        "interruption_threshold": 100,
        "responsiveness"        : 1.0,
        "enable_backchannel"    : True,
    }
    return spec


def save_spec(spec, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python agent_spec_generator.py <memo.json>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        memo = json.load(f)
    spec = generate_agent_spec(memo)
    print(json.dumps(spec, indent=2))
