"""Tests for ``src.stiff_medium.bcs_gap_ratio_test``.

Covers:
    * the substrate / BCS prediction constant 2π/e^γ
    * the dimensional ``measured_ratio`` arithmetic
    * deviation_percent sign and magnitude
    * the literature data table is well-formed and immutable
    * cross-check with the existing ``superconductivity_substrate``
      module so the two stay in sync (same constant)
    * ``run_test`` returns one row per material and respects the
      threshold flag
    * ``summary_stats`` aggregates correctly, including the elemental-
      only restriction
    * known per-material outcomes:
        - Sn / Ta / In / Tl elemental weak-coupling materials match
          within 5%
        - Pb (strong-coupling Eliashberg) deviates above 20%
        - MgB_2 (multiband sigma+pi) deviates above 15%
    * the renderer writes a non-empty PNG to disk
"""

from __future__ import annotations

import math
import os
import tempfile

import pytest

from src.stiff_medium.bcs_gap_ratio_test import (
    BCS_RATIO_PRED,
    EULER_GAMMA,
    K_B_MEV_K,
    MATERIALS,
    MaterialDatum,
    ResultRow,
    deviation_percent,
    measured_ratio,
    render_bcs_gap_ratio_test,
    run_test,
    summary_stats,
)


# ---------------------------------------------------------------------------
# Constant: substrate / BCS prediction
# ---------------------------------------------------------------------------

def test_prediction_constant_value():
    """2 π / e^γ to 12 digits."""
    assert math.isclose(BCS_RATIO_PRED, 3.527753977724091, rel_tol=1e-12)


def test_prediction_definition_matches_2pi_over_eEgamma():
    """The constant equals 2π / exp(γ) by construction."""
    assert math.isclose(
        BCS_RATIO_PRED, 2.0 * math.pi / math.exp(EULER_GAMMA), rel_tol=1e-15
    )


def test_euler_gamma_value():
    """Euler-Mascheroni γ to 16 digits."""
    assert math.isclose(EULER_GAMMA, 0.5772156649015329, rel_tol=1e-15)


def test_kB_meV_per_K_value():
    """k_B in meV/K = 0.0861733... (textbook)."""
    assert math.isclose(K_B_MEV_K, 0.08617333262145178, rel_tol=1e-9)


def test_prediction_matches_superconductivity_substrate_module():
    """Cross-check: ``superconductivity_substrate`` exposes the same
    universal ratio.  Drift between the two would be a code-quality bug.
    """
    from src.stiff_medium.superconductivity_substrate import (
        BCS_UNIVERSAL_GAP_RATIO,
    )
    assert math.isclose(BCS_RATIO_PRED, BCS_UNIVERSAL_GAP_RATIO,
                        rel_tol=1e-15)


# ---------------------------------------------------------------------------
# Arithmetic: measured_ratio + deviation_percent
# ---------------------------------------------------------------------------

def test_measured_ratio_pb_value():
    """Pb: 2Δ=2.74 meV, T_c=7.20 K -> R = 2.74 / (k_B*7.20) ~ 4.416."""
    R = measured_ratio(7.20, 2.74)
    expected = 2.74 / (K_B_MEV_K * 7.20)
    assert math.isclose(R, expected, rel_tol=1e-12)
    assert math.isclose(R, 4.4156, rel_tol=1e-3)


def test_measured_ratio_dimensional_consistency():
    """If we double the gap, the ratio doubles; if we double T_c,
    the ratio halves.
    """
    R0 = measured_ratio(5.0, 1.0)
    assert math.isclose(measured_ratio(5.0, 2.0), 2.0 * R0, rel_tol=1e-12)
    assert math.isclose(measured_ratio(10.0, 1.0), 0.5 * R0, rel_tol=1e-12)


@pytest.mark.parametrize("Tc, gap", [
    (0.0, 1.0), (-1.0, 1.0), (1.0, 0.0), (1.0, -1.0),
])
def test_measured_ratio_rejects_nonpositive(Tc, gap):
    with pytest.raises(ValueError):
        measured_ratio(Tc, gap)


def test_deviation_percent_zero_when_match():
    assert deviation_percent(BCS_RATIO_PRED) == 0.0


def test_deviation_percent_sign():
    """R > pred -> positive deviation; R < pred -> negative."""
    assert deviation_percent(BCS_RATIO_PRED * 1.10) > 0
    assert deviation_percent(BCS_RATIO_PRED * 0.90) < 0


def test_deviation_percent_magnitude():
    """Exact 10% deviation reported as +10.0."""
    assert math.isclose(
        deviation_percent(BCS_RATIO_PRED * 1.10), 10.0, rel_tol=1e-12
    )


# ---------------------------------------------------------------------------
# MATERIALS table
# ---------------------------------------------------------------------------

def test_materials_table_has_ten_entries():
    assert len(MATERIALS) == 10


def test_materials_includes_expected_names():
    expected = {"Hg", "Pb", "Sn", "Al", "Nb", "V", "Ta", "In", "Tl", "MgB2"}
    actual = {m.name for m in MATERIALS}
    assert actual == expected


def test_materials_are_immutable():
    """MaterialDatum is a frozen dataclass."""
    m = MATERIALS[0]
    with pytest.raises((AttributeError, Exception)):  # FrozenInstanceError
        m.T_c_K = 999.9  # type: ignore[misc]


def test_materials_have_positive_values():
    for m in MATERIALS:
        assert m.T_c_K > 0.0
        assert m.gap_meV > 0.0
        assert m.klass in {"elemental", "multiband"}


# ---------------------------------------------------------------------------
# run_test
# ---------------------------------------------------------------------------

def test_run_test_returns_one_row_per_material():
    rows = run_test()
    assert len(rows) == len(MATERIALS)
    assert [r.name for r in rows] == [m.name for m in MATERIALS]


def test_run_test_within_5pct_flag_consistent():
    rows = run_test(threshold_pct=5.0)
    for r in rows:
        assert r.within_5pct == (abs(r.dev_pct) <= 5.0)


def test_run_test_threshold_strict_vs_loose():
    """Tightening threshold to 1% strictly reduces (or holds) the number
    of materials that pass; loosening to 30% accepts everyone here.
    """
    n_strict = sum(r.within_5pct for r in run_test(threshold_pct=1.0))
    n_default = sum(r.within_5pct for r in run_test(threshold_pct=5.0))
    n_loose = sum(r.within_5pct for r in run_test(threshold_pct=30.0))
    assert n_strict <= n_default <= n_loose
    assert n_loose == len(MATERIALS)


def test_run_test_R_pred_carries_through():
    """The R_pred field on each row equals the prediction passed in."""
    rows = run_test(R_pred=4.0)
    for r in rows:
        assert r.R_pred == 4.0


# ---------------------------------------------------------------------------
# Per-material expected verdicts
# ---------------------------------------------------------------------------

def _row(name: str) -> ResultRow:
    rows = run_test()
    for r in rows:
        if r.name == name:
            return r
    raise KeyError(name)


@pytest.mark.parametrize("name", ["Sn", "Ta", "In", "Tl"])
def test_weak_coupling_elementals_match_within_5pct(name):
    """Sn, Ta, In, Tl are textbook weak-coupling and should hit 3.528
    within 5%.
    """
    r = _row(name)
    assert r.within_5pct, (
        f"{name}: |dev|={abs(r.dev_pct):.2f}% > 5% threshold"
    )


def test_pb_strong_coupling_deviates_above_20pct():
    """Pb is the canonical strong-coupling material (Carbotte review,
    ratio ~4.4); should deviate by > 20%.
    """
    r = _row("Pb")
    assert r.dev_pct > 20.0, (
        f"Pb deviation {r.dev_pct:+.2f}% expected > +20% (strong coupling)"
    )


def test_mgb2_multiband_deviates_above_15pct():
    """MgB_2 is two-band sigma+pi; using the dominant sigma gap
    (~14 meV) gives > 15% above the single-band BCS line.
    """
    r = _row("MgB2")
    assert r.dev_pct > 15.0, (
        f"MgB2 deviation {r.dev_pct:+.2f}% expected > +15% (multiband)"
    )


def test_hg_mildly_strong_coupling():
    """Hg deviates above 5% but well below Pb (mildly strong-coupling)."""
    r = _row("Hg")
    assert r.dev_pct > 5.0
    assert r.dev_pct < _row("Pb").dev_pct


# ---------------------------------------------------------------------------
# summary_stats
# ---------------------------------------------------------------------------

def test_summary_stats_keys():
    stats = summary_stats(run_test())
    for key in ("n", "n_within_5pct", "mean_abs_dev",
                "max_abs_dev", "min_abs_dev", "elemental_only"):
        assert key in stats
    for key in ("n", "n_within_5pct", "mean_abs_dev",
                "max_abs_dev", "min_abs_dev"):
        assert key in stats["elemental_only"]


def test_summary_stats_consistency():
    rows = run_test()
    stats = summary_stats(rows)
    assert stats["n"] == len(rows)
    assert stats["n_within_5pct"] == sum(r.within_5pct for r in rows)
    assert stats["min_abs_dev"] <= stats["mean_abs_dev"] <= stats["max_abs_dev"]


def test_summary_stats_elemental_subset():
    rows = run_test()
    stats = summary_stats(rows)
    elem_count = sum(1 for r in rows if r.klass == "elemental")
    assert stats["elemental_only"]["n"] == elem_count
    assert stats["elemental_only"]["n"] == 9
    assert stats["n"] - stats["elemental_only"]["n"] == 1  # MgB2


def test_summary_stats_empty_raises():
    with pytest.raises(ValueError):
        summary_stats([])


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------

def test_render_bcs_gap_ratio_test_writes_png():
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "120_bcs_ratio_test.png")
        path = render_bcs_gap_ratio_test(out)
        assert path == out
        assert os.path.isfile(path)
        assert os.path.getsize(path) > 5_000  # non-trivial PNG
        # PNG signature: 0x89 'P' 'N' 'G'
        with open(path, "rb") as fh:
            head = fh.read(8)
        assert head[:4] == b"\x89PNG"
