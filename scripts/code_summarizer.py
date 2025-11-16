# scripts/summarize_changes.py

import subprocess
import sys
from pathlib import Path

from scripts.code_summarizer import summarize_diff


def get_diff() -> str:
    """
    Get diff between current HEAD and main.
    You can adjust this depending on your branch strategy.
    """
    diff = subprocess.check_output(
        ["git", "diff", "origin/main...HEAD"],
        text=True,
        stderr=subprocess.STDOUT,
    )

    # Truncate if huge
    max_chars = 6000
    if len(diff) > max_chars:
        diff = diff[:max_chars] + "\n\n...[diff truncated]"

    return diff


def main():
    diff = get_diff()
    if not diff.strip():
        print("No diff found. Exiting.")
        sys.exit(0)

    summary = summarize_diff(diff)

    # Option 1: print to stdout (shows up in CI logs)
    print("===== AI Code Summary & Review =====")
    print(summary)

    # Option 2: save to file (for artifacts or later steps)
    out_path = Path("ai_code_summary.md")
    out_path.write_text(summary, encoding="utf-8")
    print(f"\nSummary written to {out_path}")


if __name__ == "__main__":
    main()
