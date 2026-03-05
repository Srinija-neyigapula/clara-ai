"""
run.py – Main entry point for the Clara AI pipeline.

Runs the full batch: all demo files through Pipeline A,
then all onboarding files through Pipeline B.

Usage:
    python run.py
"""

import sys
import os

# Add scripts/ to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

from run_batch import run_batch

if __name__ == "__main__":
    print("=" * 60)
    print("  Clara AI Pipeline – Zero-Cost Automation")
    print("=" * 60)
    result = run_batch()
    print("\nPipeline complete.")
    print(f"  Accounts processed : {result.get('total_accounts', 0)}")
    print(f"  Errors             : {result.get('total_errors', 0)}")
    print(f"  Batch summary      : outputs/batch_summary.json")
    print(f"  Task log           : outputs/tasks.sqlite")
    print("=" * 60)
