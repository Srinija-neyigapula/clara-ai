# Setup Guide

## Prerequisites

- Python 3.10 or higher
- No additional packages required

## Verify Python version

```bash
python --version
# or
python3 --version
```

## Run the pipeline

```bash
python run.py
```

## Adding transcripts

Place demo transcripts in `inputs/demo/` as `demo_<id>.txt`.  
Place onboarding transcripts in `inputs/onboarding/` as `onboarding_<id>.txt`.

Use the same `<id>` for paired demo/onboarding (e.g. `demo_acme.txt` + `onboarding_acme.txt`).

## Viewing outputs

After running, check `outputs/accounts/` for generated memos, specs, and changelogs.

Use the diff viewer:
```bash
python scripts/diff_viewer.py account-01
```

## Task log

```bash
python scripts/task_tracker.py
```
