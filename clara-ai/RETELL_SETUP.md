# Retell Agent Setup Guide

## Free-Tier Constraint

Retell's free tier does **not** support programmatic agent creation via API.  
This pipeline outputs a complete **Retell Agent Spec JSON** that you paste manually into the Retell Dashboard — a 2-minute process per account.

---

## Step-by-Step: Creating an Agent in Retell (Manual Import)

### 1. Sign Up / Log In
Go to [https://www.retellai.com/](https://www.retellai.com/) and create a free account.

### 2. Create a New Agent
- Click **"Create Agent"** in the top-right.
- Select **"Blank Agent"**.

### 3. Set Agent Name
Use the `agent_name` value from your spec file:
```
outputs/accounts/<account_id>/v2/retell_agent_spec.json
```
Example: `"Greenfield HVAC Services – AI Receptionist (v2)"`

### 4. Set Voice
Use the `voice_style` value from the spec (e.g. `"11labs-Rachel"`).  
In Retell: go to **Voice** tab → search for the voice ID.

### 5. Paste System Prompt
- Click **"System Prompt"** tab.
- Copy the entire `system_prompt` string from the spec JSON.
- Paste it into the prompt editor.

### 6. Set Begin Message
Copy `begin_message` from the spec and paste it into the **"Begin Message"** field.

### 7. Configure Transfer Protocol (if supported)
The spec includes:
```json
"call_transfer_protocol": {
  "collect_before_transfer": ["caller_name", "callback_number"],
  "timeout_sec": 30,
  "retries": 1
}
```
Set these values in Retell's **Call Transfer** settings if available on your tier.

### 8. Save and Test
Click **Save**. Use Retell's built-in **test call** feature to verify the agent.

---

## Where Are the Spec Files?

After running `python run.py`:

| Account | v1 Spec | v2 Spec |
|---------|---------|---------|
| account-01 | `outputs/accounts/account-01/v1/retell_agent_spec.json` | `outputs/accounts/account-01/v2/retell_agent_spec.json` |
| account-02 | `outputs/accounts/account-02/v1/retell_agent_spec.json` | `outputs/accounts/account-02/v2/retell_agent_spec.json` |
| account-bens_electric | `outputs/accounts/account-bens_electric/v1/retell_agent_spec.json` | `outputs/accounts/account-bens_electric/v2/retell_agent_spec.json` |

---

## Production Path (If Budget Available)

With a paid Retell plan, replace the manual import with:

```python
import requests

def create_retell_agent(spec: dict, api_key: str) -> dict:
    response = requests.post(
        "https://api.retellai.com/create-agent",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "agent_name": spec["agent_name"],
            "voice_id": spec["voice_style"],
            "response_engine": {
                "type": "retell-llm",
                "llm_id": "<your_llm_id>"
            },
            "begin_message": spec["begin_message"],
        }
    )
    return response.json()
```

Set `RETELL_API_KEY` in your environment and call this after generating each spec.

---

## API Key Location (Retell Dashboard)
Settings → **API Keys** → Copy the key → Set as environment variable:
```bash
export RETELL_API_KEY=your_key_here
```
