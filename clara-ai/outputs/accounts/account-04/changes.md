# Changelog – account-04
_Generated: 2026-03-05T03:46:26.908144_

**Total changes:** 4

---

## 1. `business_hours`
- **Before (v1):** `{'days': 'Monday to Friday', 'start': '8am', 'end': '5pm', 'timezone': 'America/New_York'}`
- **After  (v2):** `{'days': 'Monday to Friday', 'start': '7am', 'end': '6pm', 'timezone': 'America/New_York'}`

## 2. `emergency_definition`
- **Before (v1):** `['emergency', 'leak', 'failure', 'do you get?']`
- **After  (v2):** `['emergency', 'leak', 'failure', 'do you get?', 'flood']`

## 3. `non_emergency_routing_rules`
- **Before (v1):** `{'main_phone': '305-555-0120', 'destinations': ['Main office line'], 'voicemail': 'after-hours voicemail'}`
- **After  (v2):** `{'main_phone': '305-555-0190', 'destinations': ['Main office line', 'Route those to 305-555-0130 and maria@pureairhvac'], 'voicemail': 'after-hours voicemail'}`

## 4. `additional_contacts`
- **Before (v1):** `[]`
- **After  (v2):** `[{'name': 'Maria Gonzalez', 'email': 'maria@pureairhvac.com'}]`

---

## Summary
- Account : account-04
- Business: PureAir HVAC & Refrigeration out of Miami
- Hours v1: 8am–5pm (Monday to Friday)
- Hours v2: 7am–6pm (Monday to Friday)