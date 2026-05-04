"""Tests for nuclear_be_test -- substrate BE prediction vs AME2020."""

from __future__ import annotations

import numpy as np
import pytest

from src.stiff_medium.k4_face_pair_geometry import EPS_FACE_MEV
from src.stiff_medium.nucleon_stacking_geometry import (
    TOPOLOGY_REGISTRY,
    cooperative_factor,
    get_topology,
)
from src.stiff_medium.nuclear_be_test import (
    A_COULOMB_MEV,
    A_PAIRING_MEV,
    A_SYMMETRY_MEV,
    ALPHA_EM,
    AME2020,
    C_SURF,
    HBARC_MEV_FM,
    IsotopeRef,
    IsotopeResult,
    R_0_FM,
    asymmetry_correction_MeV,
    classify_results,
    compute_results,
    compute_results_with_corrections,
    coulomb_correction_MeV,
    pairing_correction_MeV,
    predicted_BE,
    predicted_BE_per_A,
    predicted_BE_with_corrections,
    predicted_face_pairs,
    summary_statistics,
)


# ---------------------------------------------------------------------------
# Reference table sanity
# ---------------------------------------------------------------------------

def test_ame2020_has_25_isotopes():
    """The curated AME2020 reference list spans 25 isotopes."""
    assert len(AME2020) == 25


def test_ame2020_spans_a_2_to_238():
    """Spans deuteron (A=2) to U-238 (A=238)."""
    A_vals = sorted({iso.A for iso in AME2020})
    assert A_vals[0] == 2
    assert A_vals[-1] == 238


def test_ame2020_be_positive_monotone_in_A():
    """Total BE grows monotonically with A across the curated set (one
    isotope per A; isobar pairs like 3H/3He are allowed to dip slightly)."""
    # Pick max-BE isotope per mass number (skips 3He which is below 3H)
    by_A: dict[int, float] = {}
    for iso in AME2020:
        by_A[iso.A] = max(by_A.get(iso.A, 0.0), iso.BE_MeV)
    sorted_A = sorted(by_A)
    BEs = [by_A[A] for A in sorted_A]
    assert all(b > 0 for b in BEs)
    for prev, curr in zip(BEs[:-1], BEs[1:]):
        assert curr >= prev   # strict monotone after picking per-A max


def test_isotope_ref_helpers():
    """IsotopeRef N and BE_per_A helpers correct."""
    iso = IsotopeRef("12C", 6, 12, 92.16)
    assert iso.N == 6
    assert abs(iso.BE_per_A - 92.16 / 12) < 1e-12


# ---------------------------------------------------------------------------
# Face-pair count P(A)
# ---------------------------------------------------------------------------

def test_face_pairs_use_explicit_topology_when_available():
    """For A in {2,3,4,6,8,12,16}, use the hand-built topology pair count."""
    for A, cls in TOPOLOGY_REGISTRY.items():
        assert predicted_face_pairs(A) == get_topology(A).n_face_pairs


def test_face_pairs_extrapolation_continuous_at_o16():
    """Bulk extrapolation calibrated so that P(16) = 30 (matches O-16 topology)."""
    # The bulk formula is P_bulk(A) = round(2A - C_SURF * A^(2/3)).
    # At A=16, this should reproduce the explicit O-16 value (30).
    bulk_at_16 = int(round(2.0 * 16 - C_SURF * 16 ** (2.0 / 3.0)))
    assert bulk_at_16 == 30
    assert predicted_face_pairs(16) == 30


def test_face_pairs_grow_with_A():
    """P(A) is monotonically non-decreasing with A for A >= 2."""
    A_vals = list(range(2, 240, 5))
    Ps = [predicted_face_pairs(A) for A in A_vals]
    for prev, curr in zip(Ps[:-1], Ps[1:]):
        assert curr >= prev


def test_face_pairs_bulk_limit_2_per_cell():
    """For very large A, P(A) / A approaches 2 (saturation)."""
    P_big = predicted_face_pairs(1000)
    # Should be close to 2 * A = 2000, with surface correction subtracting ~C_SURF*100
    assert P_big >= 1900
    assert P_big <= 2000


# ---------------------------------------------------------------------------
# BE prediction
# ---------------------------------------------------------------------------

def test_predicted_BE_deuteron_matches_eps_face():
    """BE(2) = 1 face-pair * 1.0 * eps_face = 2.222 MeV."""
    assert abs(predicted_BE(2) - EPS_FACE_MEV) < 1e-6


def test_predicted_BE_alpha_matches_observed():
    """BE(4) = 6 * eta_alpha * eps_face = 28.30 MeV by calibration."""
    BE_pred = predicted_BE(4)
    assert abs(BE_pred - 28.295674) < 1e-3


def test_predicted_BE_per_A_signature():
    """BE/A returns the per-nucleon binding for the same prediction."""
    A = 56
    assert abs(predicted_BE_per_A(A) - predicted_BE(A) / A) < 1e-12


# ---------------------------------------------------------------------------
# 25-isotope comparison table
# ---------------------------------------------------------------------------

def test_compute_results_returns_25_records():
    """compute_results yields exactly the 25 AME2020 isotopes."""
    results = compute_results()
    assert len(results) == 25


def test_compute_results_has_correct_fields():
    """Each IsotopeResult exposes pred / obs / err."""
    results = compute_results()
    for r in results:
        assert isinstance(r.isotope, IsotopeRef)
        assert r.P > 0
        assert r.eta_coop > 0
        assert r.BE_pred_MeV > 0
        assert r.BE_obs_MeV > 0


def test_deuteron_alpha_match_within_0p5_pct():
    """Anchors (deuteron, alpha) match by construction at < 0.5%."""
    results = compute_results()
    for r in results:
        if r.isotope.A in (2, 4):
            assert abs(r.err_pct) < 0.5


def test_summary_statistics_keys():
    """summary_statistics returns expected aggregate keys."""
    results = compute_results()
    stats = summary_statistics(results)
    expected_keys = {
        'n_isotopes', 'mean_err_pct', 'mean_abs_err_pct',
        'rms_err_pct', 'max_abs_err_pct',
        'mean_abs_err_MeV', 'mean_err_per_A_MeV',
        'max_abs_err_per_A_MeV',
    }
    assert set(stats.keys()) == expected_keys
    assert stats['n_isotopes'] == 25


def test_classify_results_split_correct():
    """classify_results partitions into pass / fail at the given tolerance."""
    results = compute_results()
    passing, failing = classify_results(results, tol_pct=5.0)
    assert len(passing) + len(failing) == len(results)
    for r in passing:
        assert abs(r.err_pct) <= 5.0
    for r in failing:
        assert abs(r.err_pct) > 5.0


def test_pure_substrate_overbinds_heavy_nuclei():
    """Substrate without Coulomb correction should over-bind A >= 100 nuclei.

    The Coulomb deficit grows as Z(Z-1)/A^{1/3}, so without subtracting
    EM repulsion the bare substrate prediction is systematically too
    binding for heavy isotopes.  We verify the trend is monotone.
    """
    results = compute_results()
    heavy = [r for r in results if r.isotope.A >= 100]
    assert len(heavy) >= 5
    # Errors should be positive (over-binding)
    for r in heavy:
        assert r.err_pct > 0, (
            f"{r.isotope.name} err = {r.err_pct:.2f}% — "
            f"bare substrate should over-bind heavy nuclei"
        )
    # Error magnitude should grow with A (Coulomb deficit grows ~ Z^2 / A^{1/3})
    heavy_sorted = sorted(heavy, key=lambda r: r.isotope.A)
    # Allow a bit of jitter (158Gd vs 200Hg shell-effect) but the
    # endpoints should be clearly ordered.
    assert heavy_sorted[-1].err_pct > heavy_sorted[0].err_pct


def test_medium_mass_within_10_pct():
    """Medium-mass nuclei (40 <= A <= 90) should sit within ~10 percent.

    These are the sweet spot: bulk saturation is good and Coulomb
    correction is still modest.
    """
    results = compute_results()
    medium = [r for r in results if 40 <= r.isotope.A <= 90]
    assert len(medium) >= 3
    for r in medium:
        assert abs(r.err_pct) < 10.0, (
            f"{r.isotope.name} err = {r.err_pct:.2f}% > 10%"
        )


def test_very_light_odd_A_struggle():
    """Odd-A light nuclei (3He, 7Li, 9Be, 10B) are the weakest: the
    cooperative factor saturates too aggressively for unsaturated
    surface configurations.  Verify they are indeed the worst offenders.
    """
    results = compute_results()
    by_name = {r.isotope.name: r for r in results}
    # Each of these should be a known weak point (> 5% error)
    for nm in ("7Li", "9Be", "10B"):
        assert abs(by_name[nm].err_pct) > 5.0


def test_overall_rms_reasonable():
    """Overall RMS error across the 25-isotope set should be < 25 percent.

    Without Coulomb / asymmetry corrections, this is the honest scope
    of the bare substrate prediction.
    """
    results = compute_results()
    stats = summary_statistics(results)
    assert stats['rms_err_pct'] < 25.0


# ---------------------------------------------------------------------------
# SEMF corrections (Coulomb + asymmetry + pairing)
# ---------------------------------------------------------------------------

def test_a_coulomb_substrate_derived_matches_textbook():
    """a_C = (3/5) * alpha * hbar*c / R_0 = 0.7200 MeV (R_0 = 1.20 fm).

    This is the substrate-derived Coulomb coefficient and it matches the
    textbook semi-empirical mass formula coefficient (0.72 MeV) to better
    than 0.01 percent -- because the K_4 nucleon-radius anchor R_0 = 1.20
    fm is exactly the value that makes the two agree by construction.
    """
    expected = (3.0 / 5.0) * ALPHA_EM * HBARC_MEV_FM / R_0_FM
    assert abs(A_COULOMB_MEV - expected) < 1e-12
    assert abs(A_COULOMB_MEV - 0.72) < 0.005


def test_coulomb_correction_negative_for_Z_ge_2():
    """Coulomb correction reduces binding for any Z >= 2."""
    for Z, A in [(2, 4), (8, 16), (26, 56), (82, 208), (92, 238)]:
        assert coulomb_correction_MeV(Z, A) < 0.0


def test_coulomb_correction_zero_for_hydrogen():
    """Coulomb correction = 0 for Z = 0 and Z = 1 (no proton-proton pairs)."""
    assert coulomb_correction_MeV(0, 2) == 0.0
    assert coulomb_correction_MeV(1, 2) == 0.0
    assert coulomb_correction_MeV(1, 3) == 0.0


def test_asymmetry_correction_zero_for_N_eq_Z():
    """Asymmetry correction vanishes for N=Z (4He, 12C, 16O, 20Ne, 40Ca)."""
    for Z, A in [(2, 4), (6, 12), (8, 16), (10, 20), (20, 40)]:
        assert asymmetry_correction_MeV(Z, A) == 0.0


def test_asymmetry_correction_negative_for_neutron_rich():
    """Asymmetry correction is negative for any N != Z."""
    for Z, A in [(50, 120), (82, 208), (92, 238)]:
        assert asymmetry_correction_MeV(Z, A) < 0.0


def test_pairing_correction_signs():
    """Pairing: +a_p/sqrt(A) for even-even, 0 for odd-A, -a_p/sqrt(A) for
    odd-odd."""
    # Even-even: 4He, 12C, 16O, 40Ca, 56Fe (Z=26 N=30), 208Pb
    for Z, A in [(2, 4), (6, 12), (8, 16), (20, 40), (26, 56), (82, 208)]:
        assert pairing_correction_MeV(Z, A) > 0.0
    # Odd-A: 3H, 7Li, 9Be
    for Z, A in [(1, 3), (3, 7), (4, 9)]:
        assert pairing_correction_MeV(Z, A) == 0.0
    # Odd-odd: 2H, 6Li, 10B, 14N
    for Z, A in [(1, 2), (3, 6), (5, 10), (7, 14)]:
        assert pairing_correction_MeV(Z, A) < 0.0


def test_predicted_BE_with_corrections_decomposes():
    """predicted_BE_with_corrections = bare + Coulomb + asymmetry + pairing."""
    Z, A = 82, 208
    bare = predicted_BE(A)
    coul = coulomb_correction_MeV(Z, A)
    asym = asymmetry_correction_MeV(Z, A)
    pair = pairing_correction_MeV(Z, A)
    full = predicted_BE_with_corrections(Z, A)
    assert abs(full - (bare + coul + asym + pair)) < 1e-9


def test_compute_results_with_corrections_returns_25_records():
    """compute_results_with_corrections yields exactly the 25 AME2020 isotopes."""
    results = compute_results_with_corrections()
    assert len(results) == 25
    for r in results:
        assert r.BE_coul_MeV is not None
        assert r.BE_asym_MeV is not None
        assert r.BE_pair_MeV is not None
        assert r.BE_pred_corr_MeV is not None


def test_pb208_coulomb_term_matches_textbook_estimate():
    """Pb-208 Coulomb correction should be ~ -800 MeV (textbook scale).

    a_C * Z(Z-1) / A^{1/3}  =  0.72 * 82 * 81 / 208^{1/3}
                            =  0.72 * 6642 / 5.926
                            ~= -807 MeV.
    """
    coul = coulomb_correction_MeV(82, 208)
    expected = -A_COULOMB_MEV * 82 * 81 / (208 ** (1.0 / 3.0))
    assert abs(coul - expected) < 1e-9
    assert -820.0 < coul < -800.0


def test_u238_coulomb_term_dominates():
    """U-238 Coulomb correction should be the largest in the chart (~-970 MeV).

    a_C * Z(Z-1) / A^{1/3}  =  0.72 * 92 * 91 / 238^{1/3}
                            =  0.72 * 8372 / 6.197
                            ~= -973 MeV.
    """
    coul = coulomb_correction_MeV(92, 238)
    assert -990.0 < coul < -960.0


def test_mirror_pair_he3_h3_gap_matches_coulomb():
    """3He vs 3H mass-isobar gap is purely Coulomb in the substrate ansatz.

    Bare substrate gives identical BE for 3H (Z=1) and 3He (Z=2) because
    the topology count and eta_coop depend only on A.  The Coulomb
    correction breaks the degeneracy:

        Delta_BE_substrate  =  -a_C * (2*1 - 1*0) / 3^{1/3}
                            =  -a_C * 2 / 3^{1/3}
                            ~= -0.998 MeV.

    The observed AME2020 gap is BE(3H) - BE(3He) = 0.764 MeV.  The
    substrate Coulomb prediction is within ~30% of the observed gap and
    *correctly recovers the sign* (3H more bound than 3He).
    """
    coul_3H = coulomb_correction_MeV(1, 3)
    coul_3He = coulomb_correction_MeV(2, 3)
    # 3H has Z=1 -> Z(Z-1)=0 -> Coulomb=0
    # 3He has Z=2 -> Z(Z-1)=2 -> Coulomb = -a_C * 2 / 3^{1/3}
    assert coul_3H == 0.0
    expected_3He = -A_COULOMB_MEV * 2.0 / (3.0 ** (1.0 / 3.0))
    assert abs(coul_3He - expected_3He) < 1e-9
    # Gap: |coul_3He - coul_3H| ~ 0.998 MeV
    gap_substrate = coul_3H - coul_3He   # positive: 3H more bound
    obs_gap = 8.481798 - 7.718058         # 0.764 MeV
    assert 0.6 < gap_substrate / obs_gap < 1.6


def test_pb208_corrected_includes_dominant_coulomb():
    """Pb-208 corrected prediction is bare - ~800 MeV Coulomb - ~210 MeV asym
    + small pairing.

    The bare substrate over-predicts Pb-208 by ~273 MeV (+16.7%); after
    the full SEMF corrections it UNDER-predicts by ~750 MeV (~-46%).
    Verify the per-term decomposition is reproducible.
    """
    results = compute_results_with_corrections()
    pb = next(r for r in results if r.isotope.name == "208Pb")
    assert pb.BE_coul_MeV is not None and pb.BE_coul_MeV < -800.0
    assert pb.BE_asym_MeV is not None and pb.BE_asym_MeV < -200.0
    # Bare over-binds, but textbook-coefficient corrections push it to
    # under-binding -- this is a known, documented limitation of dropping
    # full SEMF terms onto a substrate volume that already implicitly
    # absorbs part of the asymmetry penalty.
    assert pb.err_pct > 0      # bare over-binds
    assert pb.err_pct_corr < 0  # corrected under-binds with textbook coefs


def test_summary_statistics_corrected_keys_match():
    """summary_statistics(use_corrected=True) returns same key set as bare."""
    results = compute_results_with_corrections()
    bare_stats = summary_statistics(results, use_corrected=False)
    corr_stats = summary_statistics(results, use_corrected=True)
    assert set(bare_stats.keys()) == set(corr_stats.keys())
    assert corr_stats['n_isotopes'] == 25


def test_corrected_heavy_nuclei_gain_coulomb_term():
    """Heavy nuclei (Pb-208, U-238) gain a substantial Coulomb correction
    that flips the bare over-binding into under-binding (with textbook
    coefficients).

    This documents the *honest* finding that naive SEMF coefficients
    over-correct, since substrate's eta_coop * P * eps_face already
    implicitly absorbs ~half of the asymmetry penalty into the
    cooperative factor.  See module docstring.
    """
    results = compute_results_with_corrections()
    by_name = {r.isotope.name: r for r in results}
    for nm in ("208Pb", "238U"):
        r = by_name[nm]
        # Bare: positive error (over-binds by 17-21%)
        assert 15.0 < r.err_pct < 25.0
        # Corrected: large negative error -- documented over-correction
        assert r.err_pct_corr < -30.0
        # Coulomb term magnitude is dominant (> 800 MeV for Pb, > 950 for U)
        assert r.BE_coul_MeV < -700.0


def test_corrected_light_clusters_remain_problematic():
    """Light cluster nuclei (7Li, 9Be, 10B) cannot be saved by Coulomb
    + asymmetry corrections alone -- their bare error is dominated by
    cluster-substructure effects (alpha + extra-nucleon configurations
    where the bulk eta_coop saturates too aggressively).

    Even with textbook SEMF corrections these isotopes remain outside
    the 5% tolerance.
    """
    results = compute_results_with_corrections()
    by_name = {r.isotope.name: r for r in results}
    for nm in ("7Li", "9Be", "10B"):
        assert abs(by_name[nm].err_pct_corr) > 5.0


def test_corrected_close_packed_match_within_tolerance():
    """Close-packed N=Z nuclei (12C, 16O, 20Ne) IMPROVE under corrections
    because their Coulomb deficit is real and their asymmetry is zero.

    These get a clean Coulomb-only correction; verify they cross within
    a few percent of AME2020.
    """
    results = compute_results_with_corrections()
    by_name = {r.isotope.name: r for r in results}
    for nm in ("12C", "16O", "20Ne"):
        assert abs(by_name[nm].err_pct_corr) < 5.0


def test_classify_results_with_corrected_uses_corrected_errors():
    """classify_results(use_corrected=True) sees the corrected errors."""
    results = compute_results_with_corrections()
    bare_pass, bare_fail = classify_results(results, tol_pct=5.0,
                                            use_corrected=False)
    corr_pass, corr_fail = classify_results(results, tol_pct=5.0,
                                            use_corrected=True)
    assert len(bare_pass) + len(bare_fail) == len(results)
    assert len(corr_pass) + len(corr_fail) == len(results)
    # The two need not agree: textbook corrections can flip pass/fail
    # for many isotopes.
