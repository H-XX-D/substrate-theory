"""Canonical fine-structure-constant audit.

Run from the repository root:

    PYTHONPATH=src python3 scripts/alpha_audit.py
"""

from __future__ import annotations

import argparse
import math
from collections.abc import Sequence

from stiff_medium.alpha_audit import (
    AlphaAuditSummary,
    build_alpha_audit_summary,
    pct_inv,
    signed_delta_alpha,
    signed_delta_inv,
    validate_target_constants,
)
from stiff_medium.alpha_derivation import (
    AlphaDerivationAudit,
    run_alpha_derivation_audit,
)
from stiff_medium.alpha_two_loop import (
    AlphaTwoLoopAudit,
    TwoLoopResult,
    run_alpha_two_loop_audit,
)


def print_two_loop_result(label: str, result: TwoLoopResult, target_inv: float) -> None:
    print(
        f"  {label:20s} beta^2/pi={result.beta_squared / math.pi:.9f} "
        f"1/alpha={result.inv_alpha_2loop:.9f} "
        f"delta={signed_delta_inv(result, target_inv):+.9f} "
        f"pct={pct_inv(result, target_inv):.9f}%"
    )


def print_derivation_audit(audit: AlphaDerivationAudit) -> None:
    print("FINE-STRUCTURE CONSTANT DERIVATION AUDIT")
    print(f"target inverse alpha: {audit.target_inv_alpha:.9f}")
    print(f"target alpha:         {audit.target_alpha:.15f}")
    print()

    print("RG")
    print(f"  1/alpha(M_Z) computed:  {audit.inv_alpha_mz_computed:.9f}")
    print(f"  1/alpha(M_Z) measured:  {audit.inv_alpha_mz_measured:.9f}")
    print(f"  required 1/alpha_bare at 27 GeV: {audit.inv_alpha_bare_required_27gev:.9f}")
    print(f"  round-trip 1/alpha(m_e):         {audit.rg_roundtrip_inv_alpha_me:.9f}")
    print(f"  round-trip delta alpha:          {audit.rg_roundtrip_delta_alpha:+.3e}")
    print()

    print("Beta constraints")
    print(f"  alpha-bare target beta^2/pi: {audit.beta_alpha_bare_pi:.9f}")
    print(f"  RG-inverted beta^2/pi:       {audit.beta_rg_pi:.9f}")
    print(f"  Higgs/W beta^2/pi:           {audit.beta_higgs_w_pi:.9f}")
    print(f"  beta gap alpha-bare vs H/W:  {audit.beta_gap_pi:.9f}")
    print(f"  Higgs/W m_H/m_W:             {audit.higgs_w_ratio:.9f}")
    print(f"  Higgs/W g_Thirring:          {audit.higgs_w_g_thirring:.9f}")
    print(f"  Higgs/W positive alpha:      {audit.higgs_w_has_positive_alpha}")
    print()

    print("Scan")
    print(f"  fully consistent points: {audit.n_fully_consistent_scan_points}")
    print(f"  best scan 1/alpha(m_e):  {audit.best_scan_inv_alpha:.9f}")
    print()

    print("Conclusion")
    print(f"  {audit.conclusion}")


def print_two_loop_audit(audit: AlphaTwoLoopAudit) -> None:
    print("TWO-LOOP FINE-STRUCTURE CONSTANT AUDIT")
    print(f"target inverse alpha: {audit.target_inv_alpha:.9f}")
    print(f"target alpha:         {audit.target_alpha:.15f}")
    print()

    print("Two-loop candidates")
    print_two_loop_result("1-loop scan beta", audit.baseline, audit.target_inv_alpha)
    print_two_loop_result("fixed beta 3.91pi", audit.fixed_beta, audit.target_inv_alpha)
    if audit.fitted_beta is not None:
        print_two_loop_result("continuous beta fit", audit.fitted_beta, audit.target_inv_alpha)
        print("  continuous beta fit is calibration, not prediction")
    print()

    print("Best non-fitted finite result")
    fixed = audit.fixed_beta
    print(f"  beta^2/pi:        {fixed.beta_squared / math.pi:.9f}")
    print(f"  1/alpha:          {fixed.inv_alpha_2loop:.9f}")
    print(f"  signed delta inv: {signed_delta_inv(fixed, audit.target_inv_alpha):+.9f}")
    print(f"  abs pct inv:      {pct_inv(fixed, audit.target_inv_alpha):.9f}%")
    print(f"  alpha:            {fixed.alpha_2loop:.15f}")
    print(f"  signed delta a:   {signed_delta_alpha(fixed, audit.target_alpha):+.15e}")
    print()

    print("Independent Higgs/W beta")
    print(f"  beta^2/pi:      {audit.higgs_w_beta_pi:.9f}")
    print(f"  m_H/m_W:        {audit.higgs_w_ratio:.9f}")
    print(f"  g_Thirring:     {audit.higgs_w_g_thirring:.9f}")
    print(f"  positive alpha: {audit.higgs_w_has_positive_alpha}")
    print()

    print("Conclusion")
    print(f"  {audit.conclusion}")


def print_honest_conclusion(
    summary: AlphaAuditSummary,
) -> None:
    derivation = summary.derivation
    two_loop = summary.two_loop
    fixed = summary.two_loop.fixed_beta
    print("HONEST REPRODUCIBLE CONCLUSION")
    print(
        "  The branch does not derive alpha from first principles: "
        f"{derivation.n_fully_consistent_scan_points} fully consistent "
        "alpha/Higgs-W scan points were found."
    )
    print(
        "  Best fixed two-loop result: "
        f"1/alpha={fixed.inv_alpha_2loop:.9f}, "
        f"delta={summary.fixed_delta_inv_alpha:+.9f} "
        f"({summary.fixed_abs_pct_inv_alpha:.9f}%)."
    )
    print(
        "  In alpha itself this is "
        f"{fixed.alpha_2loop:.15f}, "
        f"delta={summary.fixed_delta_alpha:+.15e}."
    )
    print(
        "  Exact agreement appears only when beta is fitted to CODATA; "
        "the independent Higgs/W beta is outside the positive-alpha branch "
        "of the current Coleman map."
    )


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "mode",
        nargs="?",
        choices=("all", "derivation", "two-loop"),
        default="all",
        help="audit section to print",
    )
    args = parser.parse_args(argv)

    if args.mode == "derivation":
        derivation = run_alpha_derivation_audit()
        validate_target_constants(derivation)
        print_derivation_audit(derivation)
        return

    if args.mode == "two-loop":
        two_loop = run_alpha_two_loop_audit()
        validate_target_constants(two_loop)
        print_two_loop_audit(two_loop)
        return

    summary = build_alpha_audit_summary()
    print_derivation_audit(summary.derivation)
    print()
    print_two_loop_audit(summary.two_loop)
    print()
    print_honest_conclusion(summary)


if __name__ == "__main__":
    main()
