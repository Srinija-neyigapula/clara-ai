# Changelog – account-02
_Generated: 2026-03-05T03:46:26.883342_

**Total changes:** 5

---

## 1. `business_hours`
- **Before (v1):** `{'days': 'Monday to Saturday', 'start': '7am', 'end': '5pm', 'timezone': 'America/Denver'}`
- **After  (v2):** `{'days': 'Monday to Saturday', 'start': '7am', 'end': '6pm', 'timezone': 'America/Denver'}`

## 2. `emergency_definition`
- **Before (v1):** `['emergency', 'flood', 'leak', 'gas leak', 'burst pipe', 'be handled?']`
- **After  (v2):** `['emergency', 'flood', 'leak', 'gas leak', 'burst pipe', 'be handled?', 'failure']`

## 3. `non_emergency_routing_rules`
- **Before (v1):** `{'main_phone': '602-555-0140', 'destinations': ['route to our main office at 602-555-0140'], 'voicemail': 'after-hours voicemail'}`
- **After  (v2):** `{'main_phone': '602-555-0155', 'destinations': ['route to our main office at 602-555-0140', 'Route all new customer calls to Angela at 602-555-0155 instead of the main line'], 'voicemail': 'after-hours voicemail'}`

## 4. `integration_constraints`
- **Before (v1):** `["never create sprinkler jobs in ServiceTrade – we don't handle sprinkler systems"]`
- **After  (v2):** `["never create sprinkler jobs in ServiceTrade – we don't handle sprinkler systems", 'also add: never book a job that requires commercial permits without confirming with management first', 'never book a job that requires commercial permits without confirming with management first']`

## 5. `additional_contacts`
- **Before (v1):** `[]`
- **After  (v2):** `[{'name': 'Angela Torres', 'phone': '602-555-0155', 'email': 'angela@sunriseplumbing.com'}]`

---

## Summary
- Account : account-02
- Business: Sunrise Plumbing Co
- Hours v1: 7am–5pm (Monday to Saturday)
- Hours v2: 7am–6pm (Monday to Saturday)