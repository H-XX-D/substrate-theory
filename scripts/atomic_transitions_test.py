"""Hydrogen atomic transitions — substrate predictions vs. data (§18.75).

Runs the predictions in :mod:`stiff_medium.atomic_transitions` for the
hydrogen Rydberg, Lyman-α, Balmer-α, 21-cm hyperfine line, fine structure,
and Lamb shift; compares each to the empirical value.

Usage:
    python scripts/atomic_transitions_test.py

Memory: trivial.  Time: < 1 s.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from stiff_medium.atomic_transitions import (
    ALPHA_SUBSTRATE,
    M_E_MEV,
    M_P_MEV,
    MU_P_SUBSTRATE_MUN,
    G_P_SUBSTRATE,
    rydberg_prediction,
    lyman_alpha_prediction,
    balmer_alpha_prediction,
    hyperfine_21cm_prediction,
    fine_structure_prediction,
    lamb_shift_prediction,
    predict_all_hydrogen_transitions,
    HZ_PER_EV,
)


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def print_header() -> None:
    print("=" * 78)
    print("Hydrogen atomic transitions from substrate primitives  (§18.75)")
    print("=" * 78)
    print()
    print(f"  α  (substrate)                = {ALPHA_SUBSTRATE:.10e} = 1/{1.0/ALPHA_SUBSTRATE:.6f}")
    print(f"  m_e (substrate input, §18.21) = {M_E_MEV:.7f} MeV/c²")
    print(f"  m_p (substrate, §18.62.1)     = {M_P_MEV:.5f} MeV/c²")
    print(f"  μ_p (substrate, §18.63.1)     = {MU_P_SUBSTRATE_MUN:+.4f} μ_N")
    print(f"  g_p (substrate, 2 μ_p / μ_N)  = {G_P_SUBSTRATE:.4f}")
    print()


def print_transition(r) -> None:
    """Pretty-print a TransitionResult."""
    sign = "+" if r.relative_error >= 0 else "-"
    pct = abs(r.relative_error) * 100.0
    nu_pred_hz = r.e_predicted_eV * HZ_PER_EV
    nu_obs_hz = r.e_observed_eV * HZ_PER_EV

    print(f"  {r.label}")
    print(f"     formula : {r.formula}")
    if abs(r.e_predicted_eV) >= 1e-3:
        print(f"     predicted = {r.e_predicted_eV:.6e} eV")
        print(f"     observed  = {r.e_observed_eV:.6e} eV")
    else:
        # Sub-meV → also report in MHz / GHz / cm⁻¹
        cm_inv_pred = nu_pred_hz / 2.99792458e10
        cm_inv_obs = nu_obs_hz / 2.99792458e10
        print(f"     predicted = {r.e_predicted_eV:.6e} eV "
              f"= {nu_pred_hz/1e6:.4f} MHz "
              f"= {cm_inv_pred:.6f} cm⁻¹")
        print(f"     observed  = {r.e_observed_eV:.6e} eV "
              f"= {nu_obs_hz/1e6:.4f} MHz "
              f"= {cm_inv_obs:.6f} cm⁻¹")
    print(f"     deviation = {sign}{pct:.4f}%")
    print()


def section(title: str) -> None:
    print()
    print("-" * 78)
    print(f"  {title}")
    print("-" * 78)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print_header()

    # ---- 1. Rydberg ----
    section("(1) Rydberg energy R_y = ½ m_e c² α²")
    r_y = rydberg_prediction()
    print_transition(r_y)

    # ---- 2. Lyman / Balmer ----
    section("(2) Bohr series — Lyman-α and Balmer-α")
    print_transition(lyman_alpha_prediction())
    print_transition(balmer_alpha_prediction())

    # ---- 3. 21-cm hyperfine ----
    section("(3) Hyperfine 21-cm line — most stringent test (α⁴ × m_e/m_p × g_p)")
    print_transition(hyperfine_21cm_prediction())

    # ---- 4. Fine structure ----
    section("(4) Fine structure 2P_3/2 − 2P_1/2 (∝ α⁴)")
    print_transition(fine_structure_prediction())

    # ---- 5. Lamb shift ----
    section("(5) Lamb shift 2S_1/2 − 2P_1/2 (∝ α⁵)")
    print_transition(lamb_shift_prediction())

    # ---- summary ----
    section("Summary table")
    rows = predict_all_hydrogen_transitions()
    fmt = "  {:<46s} {:>14s}  {:>14s}  {:>10s}"
    print(fmt.format("transition", "predicted (eV)", "observed (eV)", "Δ (%)"))
    print("  " + "-" * 76)
    for r in rows:
        # Truncate label for the table
        lbl = r.label.split("(")[0].strip() if "(" in r.label else r.label
        print(
            fmt.format(
                lbl[:46],
                f"{r.e_predicted_eV:.5e}",
                f"{r.e_observed_eV:.5e}",
                f"{r.relative_error*100:+.3f}",
            )
        )

    print()
    print("=" * 78)
    print("Notes:")
    print("  - α is the substrate-derived value (target of photon")
    print("    renormalization on the Möbius bundle, §18.61.5).")
    print("  - g_p = 5.676 from substrate μ_p = +2.838 μ_N (§18.63.1) vs. ")
    print("    measured 5.586. The 21-cm prediction therefore inherits the ")
    print("    ~1.6% error in the substrate proton magnetic moment.")
    print("  - Lamb shift uses Bethe-log K₀/R_y = 7.687 (Bethe 1947); higher-")
    print("    order QED corrections add ~3% — not included here.")
    print("=" * 78)


if __name__ == "__main__":
    main()
