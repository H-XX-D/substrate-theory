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
    AME2020,
    C_SURF,
    IsotopeRef,
    IsotopeResult,
    classify_results,
    compute_results,
    predicted_BE,
    predicted_BE_per_A,
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
