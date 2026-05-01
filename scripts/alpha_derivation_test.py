"""Compatibility wrapper for the fine-structure-constant derivation audit.

Run from the repository root:

    PYTHONPATH=src python3 scripts/alpha_derivation_test.py
"""

from __future__ import annotations

from alpha_audit import main


if __name__ == "__main__":
    main(["derivation"])
