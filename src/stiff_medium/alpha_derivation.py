"""Audit the current attempt to derive alpha from the substrate model.

This module keeps the reproducible diagnostics motivated by spec §§18.9,
18.34, 18.45, 18.46, 18.48. None of these is a complete derivation; the spec
is explicit that a rigorous result requires multi-loop bundle field theory
(§18.48.7 item 1). What we do here is:

  1. Compute everything the one-loop Coleman-bosonization route gives us.
  2. Invert the RG equations to ask "which bare coupling flows to α(0) = 1/137?"
  3. Use the breather/W-mass ratio m_H/m_W = 2 sin(β²/16) to constrain β².
  4. Combine the constraints and look for a self-consistent β².

The module is deliberately honest about what is and is not derived:

  - α(0) = 1/137.035999177 is a target number we want to predict.
  - Coleman bosonization relates β² ↔ g_Thirring ↔ α_bare, but gives α_bare ≈ 0
    near the free-fermion point — far from 1/137.
  - RG running can tell us what α_bare must be at the substrate scale, but that
    is a CONSTRAINT on β², not a derivation of it.
  - The Möbius bundle fixes the TOPOLOGY (charge quantisation, spin-½) but does
    NOT fix the MAGNITUDE of α without additional Lagrangian dynamics.
  - The breather formula pins β² ≈ 4.54 π from the observed m_H/m_W = 1.558, but
    that β² gives α_bare far from 1/137 via naive bosonization.

CONCLUSION (as of this computation): no single naive β² satisfies both
  α(0) = 1/137 AND m_H/m_W = 1.558 simultaneously from the leading-order
  bosonization relation.  The gap between the two constraints is large — not a
  small numerical accident.  What is needed to close it is stated explicitly at
  the end of the module (multi-loop renormalisation on the Möbius bundle, not
  perturbative patches).

References
----------
    spec §18.9   : α = e²/(Kξ⁴) dimensional route
    spec §18.34  : structural correspondence to QED → RG running inherited
    spec §18.45  : encompassing Lagrangian
    spec §18.46  : derived constants from substrate primitives
    spec §18.48  : breather masses M_n = 2 M_K sin(nβ²/16)
    Coleman 1975 : sine-Gordon / Thirring duality, Phys. Rev. D 11, 2088
    Dashen-Hasslacher-Neveu 1975: breather spectrum

Modules used
------------
    stiff_medium.mobius_bundle : coleman_bosonization_g
    stiff_medium.rg_running    : RGRunning, M_E_GEV, M_Z_GEV, run_alpha_to_M_Z
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

from stiff_medium.mobius_bundle import coleman_bosonization_g
from stiff_medium.physical_constants import (
    ALPHA_THOMSON_CODATA_2022,
    INV_ALPHA_THOMSON_CODATA_2022,
)
from stiff_medium.rg_running import (
    RGRunning,
    M_E_GEV,
    M_Z_GEV,
    run_alpha_to_M_Z,
)

# ---------------------------------------------------------------------------
# Physical and model constants
# ---------------------------------------------------------------------------

PI: Final[float] = math.pi

# Target values we are trying to derive
ALPHA_TARGET: Final[float] = ALPHA_THOMSON_CODATA_2022
INV_ALPHA_TARGET: Final[float] = INV_ALPHA_THOMSON_CODATA_2022

# W-boson mass [GeV]
M_W_GEV: Final[float] = 80.379
# Higgs-boson mass [GeV] — ATLAS 2025 most-precise measurement (spec §18.52.4)
M_H_GEV: Final[float] = 125.22
# Observed Higgs-to-W mass ratio
M_H_OVER_M_W_MEASURED: Final[float] = M_H_GEV / M_W_GEV  # ≈ 1.558

# Kink mass estimate (per spec §18.22, numerical analysis consistent with observed α and m_e)
M_KINK_GEV: Final[float] = 27.0

# Substrate scale — conjectured scale at which the kink crystallises.
# Identifying with the kink mass: Q_substrate ~ M_kink (a natural UV cutoff for the
# effective theory before the kink forms).
Q_SUBSTRATE_GEV: Final[float] = M_KINK_GEV

# Free-fermion point in the Coleman duality
BETA_SQ_FREE_FERMION: Final[float] = 4.0 * PI  # β² = 4π ≈ 12.566

# Kosterlitz-Thouless / soliton condensation transition
BETA_SQ_KT: Final[float] = 8.0 * PI  # β² = 8π ≈ 25.133


# ---------------------------------------------------------------------------
# Route 1 — Coleman bosonization: β² → g_Thirring → α_bare
# ---------------------------------------------------------------------------


@dataclass
class BosonizationResult:
    """Result of the Coleman-bosonization derivation for a given β².

    Attributes:
        beta_squared: Sine-Gordon coupling β² used.
        g_thirring: Thirring fermion coupling g = π(4π/β² − 1).
        alpha_bare: Bare fine-structure constant from g_bare²/(4π).
            Defined as |g|/(π²) following the convention in rg_running.py
            (α_bare = g/π²).  Zero if g ≤ 0 (free/attractive regime).
        alpha_bare_alt: Alternative normalisation: g²/(4π × π²).
            This corresponds to treating g as the electromagnetic coupling
            amplitude (g_em² = g, α = g_em²/(4π)).
        comment: Human-readable interpretation.
    """

    beta_squared: float
    g_thirring: float
    alpha_bare: float
    alpha_bare_alt: float
    comment: str


def bosonization_alpha(beta_squared: float) -> BosonizationResult:
    """Compute α_bare from Coleman bosonization at the given β².

    Derivation chain (spec §18.9, Coleman 1975):

        g_Thirring = π(4π/β² − 1)          [Coleman duality]
        α_bare     = g / π²                  [coupling extraction, convention 1]
        α_bare_alt = g² / (4π³)             [convention 2: g plays role of e²/(ℏc)]

    Convention 1 treats g directly as the dimensionless EM coupling squared
    (the Thirring model coupling IS the charge coupling).  Convention 2 treats
    sqrt(g) as the charge amplitude and computes α = e²/(4π) with e² = g.

    At β² = 4π (free fermion): g = 0, both α_bare vanish — no interaction.
    At β² < 4π: g > 0, repulsive Thirring regime; α_bare > 0.
    At β² > 4π: g < 0, attractive; unphysical for α (clamped to 0).

    Args:
        beta_squared: Sine-Gordon coupling constant β².  Must be positive.

    Returns:
        BosonizationResult dataclass with all derived quantities.

    Raises:
        ValueError: If beta_squared is not positive.
    """
    if beta_squared <= 0.0:
        raise ValueError(f"beta_squared must be positive; got {beta_squared!r}")

    g = coleman_bosonization_g(beta_squared)

    if g <= 0.0:
        alpha_bare = 0.0
        alpha_bare_alt = 0.0
        comment = (
            f"β²={beta_squared:.4f}: g={g:.6f} ≤ 0 (free or attractive Thirring regime). "
            "No positive α_bare from bosonization at this β². "
            "Physical regime requires β² < 4π."
        )
    else:
        alpha_bare = g / (PI**2)
        alpha_bare_alt = g**2 / (4.0 * PI**3)
        comment = (
            f"β²={beta_squared:.4f}: g={g:.6f}, "
            f"α_bare(conv1)={alpha_bare:.6f} [1/{1/alpha_bare:.1f}], "
            f"α_bare(conv2)={alpha_bare_alt:.6f} [1/{1/alpha_bare_alt:.1f}]"
        )

    return BosonizationResult(
        beta_squared=beta_squared,
        g_thirring=g,
        alpha_bare=alpha_bare,
        alpha_bare_alt=alpha_bare_alt,
        comment=comment,
    )


def beta_sq_for_alpha_target_bosonization(
    alpha_target: float = ALPHA_TARGET,
    convention: int = 1,
) -> float:
    """Invert the bosonization relation to find β² that gives α_target.

    Solves α_target = g/π² (conv1) or α_target = g²/(4π³) (conv2)
    for g, then inverts g = π(4π/β² − 1) to find β².

    This gives the β² that would be NEEDED if naive one-loop bosonization
    were the complete story.  The spec is clear it is not — but computing
    this value makes the gap explicit.

    Args:
        alpha_target: Target α value.  Default: CODATA 2022 alpha(0).
        convention: 1 → α = g/π²; 2 → α = g²/(4π³).

    Returns:
        β² that solves the equation.

    Raises:
        ValueError: If convention is not 1 or 2.
    """
    if convention == 1:
        g_needed = alpha_target * PI**2
    elif convention == 2:
        g_needed = math.sqrt(alpha_target * 4.0 * PI**3)
    else:
        raise ValueError(f"convention must be 1 or 2; got {convention!r}")

    # g = π(4π/β² − 1) → 4π/β² = g/π + 1 → β² = 4π / (g/π + 1)
    beta_sq = 4.0 * PI / (g_needed / PI + 1.0)
    return beta_sq


# ---------------------------------------------------------------------------
# Route 2 — RG running: find α_bare at substrate scale that flows to α(0)
# ---------------------------------------------------------------------------


@dataclass
class RGRouteResult:
    """Result of the RG-running route to α.

    Attributes:
        alpha_bare_at_substrate: α_bare that, when run DOWN from Q_substrate
            to m_e, gives α(0) ≈ 1/137.
        inv_alpha_bare: 1/α_bare.
        alpha_at_me: α after running from Q_substrate down to m_e.
        alpha_at_mz: α at M_Z scale from the same running.
        residual_at_target: |α(0) − α_target|.
        consistent: True when residual < 1e-5 (0.0007% of α).
    """

    alpha_bare_at_substrate: float
    inv_alpha_bare: float
    alpha_at_me: float
    alpha_at_mz: float
    residual_at_target: float
    consistent: bool


def rg_route(
    q_substrate_gev: float = Q_SUBSTRATE_GEV,
    alpha_target: float = ALPHA_TARGET,
) -> RGRouteResult:
    """Find the α_bare value at the substrate scale that flows to α(0)=1/137.

    Strategy: the RGRunning object runs α from any reference (Q_ref, α_ref)
    to any target Q.  We want to run DOWNWARD: from Q_substrate to m_e.

    Key insight: since the one-loop QED beta function is known analytically,
    we can simply set the REFERENCE to m_e (where α = 1/137) and ask for
    α at Q_substrate by running UPWARD.  That α(Q_substrate) is exactly the
    α_bare that the substrate must supply.

    This is NOT a derivation of 1/137 — it's a CONSTRAINT on what α_bare
    must be.  We then convert that α_bare to a β² via the bosonization
    relation and ask whether that β² makes sense.

    Note on the round-trip residual: this should be numerically zero apart
    from floating-point roundoff.  The RG step is implemented symmetrically
    across fermion thresholds and across the hadronic VP step.

    Args:
        q_substrate_gev: Substrate energy scale [GeV].  Default: M_kink ≈ 27 GeV.
        alpha_target: Low-energy α to match.  Default: CODATA 2022 alpha(0).

    Returns:
        RGRouteResult with the full diagnostics.
    """
    rg = RGRunning(q_ref_gev=M_E_GEV, alpha_ref=alpha_target)

    # Run FROM m_e upward to Q_substrate → this gives α(Q_substrate)
    alpha_subst = rg.alpha_at_scale(q_substrate_gev)
    inv_alpha_subst = 1.0 / alpha_subst

    # Also compute the round-trip: run down from Q_substrate to m_e
    rg_down = RGRunning(q_ref_gev=q_substrate_gev, alpha_ref=alpha_subst)
    alpha_at_me_roundtrip = rg_down.alpha_at_scale(M_E_GEV)
    alpha_at_mz_roundtrip = rg_down.alpha_at_scale(M_Z_GEV)

    residual = abs(alpha_at_me_roundtrip - alpha_target)

    return RGRouteResult(
        alpha_bare_at_substrate=alpha_subst,
        inv_alpha_bare=inv_alpha_subst,
        alpha_at_me=alpha_at_me_roundtrip,
        alpha_at_mz=alpha_at_mz_roundtrip,
        residual_at_target=residual,
        consistent=residual < 1e-5,
    )


def beta_sq_from_rg_constraint(
    q_substrate_gev: float = Q_SUBSTRATE_GEV,
    convention: int = 1,
) -> dict[str, float]:
    """Compute β² implied by the RG constraint α_bare → α(0) = 1/137.

    Chains Routes 1 and 2: first find what α_bare must be at the substrate
    scale (Route 2), then invert the bosonization relation to find the β²
    that would produce that α_bare (Route 1 inverted).

    Args:
        q_substrate_gev: Substrate energy scale [GeV].
        convention: Bosonization convention (1 or 2).

    Returns:
        Dictionary with alpha_bare, beta_sq, g_thirring, and commentary.
    """
    rg_result = rg_route(q_substrate_gev=q_substrate_gev)
    alpha_bare = rg_result.alpha_bare_at_substrate

    beta_sq = beta_sq_for_alpha_target_bosonization(alpha_bare, convention=convention)

    g_check = coleman_bosonization_g(beta_sq)
    if convention == 1:
        alpha_check = g_check / PI**2
    else:
        alpha_check = g_check**2 / (4.0 * PI**3)

    return {
        "q_substrate_gev": q_substrate_gev,
        "alpha_bare_needed": alpha_bare,
        "inv_alpha_bare_needed": 1.0 / alpha_bare,
        "beta_sq_implied": beta_sq,
        "beta_sq_in_units_of_pi": beta_sq / PI,
        "g_thirring_at_implied_beta_sq": g_check,
        "alpha_check": alpha_check,
        "roundtrip_error": abs(alpha_check - alpha_bare),
        "convention": convention,
    }


# ---------------------------------------------------------------------------
# Route 3 — Higgs/W mass ratio: m_H/m_W = 2 sin(β²/16) → β² → α
# ---------------------------------------------------------------------------


@dataclass
class HiggsWConstraintResult:
    """Result of constraining β² from the Higgs/W mass ratio.

    The sine-Gordon breather formula (Dashen-Hasslacher-Neveu 1975, spec §18.48):

        M_n / M_K = 2 sin(n β²/16)

    for breather mode n = 1 gives the first bound state mass M_1.
    Identifying M_1 with the Higgs mass m_H and M_K with the W-boson mass m_W
    (both are the fundamental scales of electroweak symmetry breaking in the model):

        m_H / m_W = 2 sin(β²/16)    →    β² = 16 arcsin(m_H/(2 m_W))

    This is SUGGESTIVE but NOT derived (spec §18.52.4 explicitly says so).

    Attributes:
        m_h_over_m_w_measured: Measured Higgs/W mass ratio ≈ 1.558.
        m_h_over_m_w_at_beta_sq: Predicted ratio from β².
        beta_sq_implied: β² solving the constraint equation.
        beta_sq_in_pi: β² / π (dimensionless).
        alpha_bare_boson_conv1: α_bare at this β² via bosonization conv 1.
        alpha_bare_boson_conv2: α_bare at this β² via bosonization conv 2.
        alpha_at_me_if_bare_conv1: α(m_e) if the bare coupling at Q_substrate
            equals α_bare_boson_conv1 (running downward).
        consistency_gap_inv_alpha: |1/α_predicted − 1/α_target|.
    """

    m_h_over_m_w_measured: float
    m_h_over_m_w_at_beta_sq: float
    beta_sq_implied: float
    beta_sq_in_pi: float
    alpha_bare_boson_conv1: float
    alpha_bare_boson_conv2: float
    alpha_at_me_if_bare_conv1: float
    consistency_gap_inv_alpha: float


def higgs_w_constraint(
    n_breather: int = 1,
    m_h_gev: float = M_H_GEV,
    m_w_gev: float = M_W_GEV,
    q_substrate_gev: float = Q_SUBSTRATE_GEV,
) -> HiggsWConstraintResult:
    """Constrain β² from the observed m_H/m_W ratio via the breather formula.

    Uses DHN breather formula M_n = 2 M_K sin(n β²/16) with:
      - Breather mode n (default 1 for fundamental Higgs-like state)
      - M_1 identified with Higgs mass m_H
      - M_K identified with W-boson mass m_W (the electroweak scale kink)

    The resulting β² is then fed through bosonization to get α_bare,
    which is run down to m_e to check against 1/137.

    Args:
        n_breather: Breather mode number (1 = first/lightest state).
        m_h_gev: Higgs-boson mass [GeV].  Default: 125.22 (ATLAS 2025).
        m_w_gev: W-boson mass [GeV].  Default: 80.379.
        q_substrate_gev: Substrate scale for RG running [GeV].

    Returns:
        HiggsWConstraintResult with all diagnostics.

    Raises:
        ValueError: If m_h_gev > 2 * n_breather * m_w_gev (arcsin argument > 1).
    """
    ratio = m_h_gev / m_w_gev
    arcsin_arg = ratio / 2.0

    if arcsin_arg > 1.0:
        raise ValueError(
            f"m_H / (2 m_W) = {arcsin_arg:.4f} > 1: no real β² satisfies "
            f"the breather formula for n={n_breather}."
        )

    beta_sq = 16.0 * math.asin(arcsin_arg / n_breather)

    # Verify round-trip
    ratio_predicted = 2.0 * n_breather * math.sin(beta_sq / 16.0)

    # Get α_bare from bosonization at this β²
    bos_result = bosonization_alpha(beta_sq)
    alpha_bare_c1 = bos_result.alpha_bare
    alpha_bare_c2 = bos_result.alpha_bare_alt

    # Run α_bare (conv 1) down from Q_substrate to m_e
    if alpha_bare_c1 > 0.0:
        rg = RGRunning(q_ref_gev=q_substrate_gev, alpha_ref=alpha_bare_c1)
        alpha_at_me = rg.alpha_at_scale(M_E_GEV)
    else:
        alpha_at_me = 0.0

    gap = abs(1.0 / alpha_at_me - INV_ALPHA_TARGET) if alpha_at_me > 0.0 else float("inf")

    return HiggsWConstraintResult(
        m_h_over_m_w_measured=ratio,
        m_h_over_m_w_at_beta_sq=ratio_predicted,
        beta_sq_implied=beta_sq,
        beta_sq_in_pi=beta_sq / PI,
        alpha_bare_boson_conv1=alpha_bare_c1,
        alpha_bare_boson_conv2=alpha_bare_c2,
        alpha_at_me_if_bare_conv1=alpha_at_me,
        consistency_gap_inv_alpha=gap,
    )


# ---------------------------------------------------------------------------
# Route 4 — Self-consistency scan: find β² satisfying all constraints
# ---------------------------------------------------------------------------


@dataclass
class ConsistencyRow:
    """One row in the self-consistency table.

    A β² value is judged against three simultaneous constraints:

    1. Bosonization (conv 1) gives α_bare that, when run to m_e, lands at 1/137.
    2. Breather formula gives m_H/m_W = 1.558.
    3. β² is in the physical range (0, 8π) for a non-trivial soliton theory.

    Attributes:
        beta_sq: The trial β² value.
        g_thirring: Coleman coupling at this β².
        alpha_bare_c1: α_bare from convention 1.
        alpha_bare_c2: α_bare from convention 2.
        alpha_at_me_c1: α(m_e) after running from Q_substrate with α_bare_c1.
        inv_alpha_at_me_c1: 1/α(m_e) from conv 1.
        breather_ratio: 2 sin(β²/16) — the predicted m_H/m_W.
        delta_inv_alpha: |1/α(m_e) − 137.036| from conv 1.
        delta_ratio: |breather_ratio − 1.558|.
        satisfies_alpha: True if delta_inv_alpha < 5 (within ~4% of target).
        satisfies_ratio: True if delta_ratio < 0.05 (within ~3% of measured).
        fully_consistent: True only when BOTH constraints are simultaneously met.
    """

    beta_sq: float
    g_thirring: float
    alpha_bare_c1: float
    alpha_bare_c2: float
    alpha_at_me_c1: float
    inv_alpha_at_me_c1: float
    breather_ratio: float
    delta_inv_alpha: float
    delta_ratio: float
    satisfies_alpha: bool
    satisfies_ratio: bool
    fully_consistent: bool


@dataclass(frozen=True)
class AlphaDerivationAudit:
    """Compact conclusion for the current alpha-derivation attempt."""

    target_inv_alpha: float
    target_alpha: float
    inv_alpha_mz_computed: float
    inv_alpha_mz_measured: float
    rg_roundtrip_inv_alpha_me: float
    rg_roundtrip_delta_alpha: float
    inv_alpha_bare_required_27gev: float
    beta_alpha_bare_pi: float
    beta_rg_pi: float
    beta_higgs_w_pi: float
    beta_gap_pi: float
    higgs_w_ratio: float
    higgs_w_g_thirring: float
    higgs_w_has_positive_alpha: bool
    n_fully_consistent_scan_points: int
    best_scan_inv_alpha: float
    conclusion: str


def self_consistency_scan(
    beta_sq_min: float = 0.5 * PI,
    beta_sq_max: float = 8.0 * PI,
    n_steps: int = 2000,
    q_substrate_gev: float = Q_SUBSTRATE_GEV,
    alpha_tol_inv_alpha: float = 5.0,
    ratio_tol: float = 0.05,
) -> list[ConsistencyRow]:
    """Scan β² values and check all four constraints simultaneously.

    For each β² in [beta_sq_min, beta_sq_max]:
      - Compute g_Thirring and α_bare via Coleman bosonization.
      - Run α_bare from Q_substrate down to m_e.
      - Compute the DHN breather ratio 2 sin(β²/16).
      - Assess whether the result is consistent with α(0)=1/137 AND
        m_H/m_W = 1.558.

    This produces the complete "candidate table" described in the task brief.

    Args:
        beta_sq_min: Lower bound of β² scan.  Default: π/2.
        beta_sq_max: Upper bound.  Default: 8π (KT transition).
        n_steps: Number of scan points.
        q_substrate_gev: Substrate scale for RG running.
        alpha_tol_inv_alpha: Tolerance on |1/α(m_e) − 137.036|.
            Default 5.0 means within ±4% of the target inverse alpha.
        ratio_tol: Tolerance on |m_H/m_W_predicted − 1.558|.

    Returns:
        List of ConsistencyRow for ALL scan points (so the caller can
        analyse and display results however they choose).
    """
    rows: list[ConsistencyRow] = []
    beta_sq_values = [
        beta_sq_min + i * (beta_sq_max - beta_sq_min) / (n_steps - 1)
        for i in range(n_steps)
    ]

    for beta_sq in beta_sq_values:
        bos = bosonization_alpha(beta_sq)
        g = bos.g_thirring
        a_bare_c1 = bos.alpha_bare
        a_bare_c2 = bos.alpha_bare_alt

        # Run α_bare down to m_e (only meaningful if α_bare > 0)
        if a_bare_c1 > 1e-10:
            rg = RGRunning(q_ref_gev=q_substrate_gev, alpha_ref=a_bare_c1)
            a_me = rg.alpha_at_scale(M_E_GEV)
        else:
            a_me = 0.0

        inv_a_me = 1.0 / a_me if a_me > 1e-20 else float("inf")

        # Breather formula: 2 sin(β²/16).
        # Note: β²/16 > π/2 for β² > 8π — would give sin > 1 which is unphysical.
        # We only scan up to 8π so this is safe.
        breather_arg = beta_sq / 16.0
        breather_ratio = 2.0 * math.sin(breather_arg) if breather_arg <= PI / 2.0 else float("nan")

        delta_inv = abs(inv_a_me - INV_ALPHA_TARGET) if math.isfinite(inv_a_me) else float("inf")
        delta_rat = abs(breather_ratio - M_H_OVER_M_W_MEASURED) if math.isfinite(breather_ratio) else float("inf")

        sat_alpha = delta_inv < alpha_tol_inv_alpha
        sat_ratio = delta_rat < ratio_tol

        rows.append(
            ConsistencyRow(
                beta_sq=beta_sq,
                g_thirring=g,
                alpha_bare_c1=a_bare_c1,
                alpha_bare_c2=a_bare_c2,
                alpha_at_me_c1=a_me,
                inv_alpha_at_me_c1=inv_a_me,
                breather_ratio=breather_ratio if math.isfinite(breather_ratio) else 0.0,
                delta_inv_alpha=delta_inv,
                delta_ratio=delta_rat,
                satisfies_alpha=sat_alpha,
                satisfies_ratio=sat_ratio,
                fully_consistent=sat_alpha and sat_ratio,
            )
        )

    return rows


def run_alpha_derivation_audit(n_steps: int = 2000) -> AlphaDerivationAudit:
    """Return the compact, reproducible alpha-derivation audit."""
    rg_check = run_alpha_to_M_Z()
    rg27 = rg_route(Q_SUBSTRATE_GEV)

    beta_alpha_bare = beta_sq_for_alpha_target_bosonization(ALPHA_TARGET, convention=1)
    beta_rg = beta_sq_from_rg_constraint(Q_SUBSTRATE_GEV, convention=1)["beta_sq_implied"]

    hw = higgs_w_constraint()
    hw_bos = bosonization_alpha(hw.beta_sq_implied)

    rows = self_consistency_scan(n_steps=n_steps)
    physical_rows = [r for r in rows if math.isfinite(r.inv_alpha_at_me_c1) and r.alpha_at_me_c1 > 0]
    best_alpha = min(physical_rows, key=lambda r: r.delta_inv_alpha, default=None)
    best_inv_alpha = best_alpha.inv_alpha_at_me_c1 if best_alpha is not None else float("inf")
    n_fully_consistent = sum(1 for r in rows if r.fully_consistent)

    return AlphaDerivationAudit(
        target_inv_alpha=INV_ALPHA_TARGET,
        target_alpha=ALPHA_TARGET,
        inv_alpha_mz_computed=float(rg_check["inv_alpha_MZ_predicted"]),
        inv_alpha_mz_measured=float(rg_check["inv_alpha_MZ_measured"]),
        rg_roundtrip_inv_alpha_me=1.0 / rg27.alpha_at_me,
        rg_roundtrip_delta_alpha=rg27.alpha_at_me - ALPHA_TARGET,
        inv_alpha_bare_required_27gev=rg27.inv_alpha_bare,
        beta_alpha_bare_pi=beta_alpha_bare / PI,
        beta_rg_pi=float(beta_rg) / PI,
        beta_higgs_w_pi=hw.beta_sq_in_pi,
        beta_gap_pi=abs(beta_alpha_bare / PI - hw.beta_sq_in_pi),
        higgs_w_ratio=hw.m_h_over_m_w_at_beta_sq,
        higgs_w_g_thirring=hw_bos.g_thirring,
        higgs_w_has_positive_alpha=hw_bos.g_thirring > 0.0 and hw_bos.alpha_bare > 0.0,
        n_fully_consistent_scan_points=n_fully_consistent,
        best_scan_inv_alpha=best_inv_alpha,
        conclusion=(
            "No first-principles alpha derivation: the alpha-matching beta values "
            "are constraints/calibrations, and the independent Higgs/W beta is "
            "outside the positive-alpha branch of the current Coleman map."
        ),
    )
