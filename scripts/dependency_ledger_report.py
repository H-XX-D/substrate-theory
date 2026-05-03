"""Print the stiff-medium dependency ledger.

Run:
    PYTHONPATH=src python scripts/dependency_ledger_report.py
"""

from __future__ import annotations

from stiff_medium.dependency_ledger import active_work_queue, format_markdown, format_summary


def main() -> None:
    """Print summary, active queue, and Markdown table."""
    print(format_summary())
    print()
    print("Active work queue")
    print("=================")
    for entry in active_work_queue():
        print(
            f"{entry.claim_id}: {entry.claim} "
            f"({entry.sector}, {entry.tag.value}, {entry.risk.value})"
        )
        if entry.next_step:
            print(f"  next: {entry.next_step}")
    print()
    print("Markdown ledger")
    print("===============")
    print(format_markdown())


if __name__ == "__main__":
    main()
