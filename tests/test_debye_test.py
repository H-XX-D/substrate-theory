"""Tests for src/stiff_medium/debye_test.py.

Required claims:
    (a) Schema integrity:    every row in run_test() carries the expected
        keys with positive numeric values.
    (b) Sound-speed identities: Debye-averaged c_s satisfies the textbook
        identity 3/c_D³ = 1/c_L³ + 2/c_T³ to machine precision.
    (c) Atomic density formula: n_atoms = N_A · ρ / M to 1e-12 relative.
    (d) Anchor matches: diamond, copper, aluminum predictions reproduce the
        baseline values quoted in user_context (2228, 343, ~430 K) at the
        few-percent level.
    (e) Scaling: predicted Θ_D scales as expected with c_s and n.
    (f) Aggregate fit quality: at least 10/14 materials within 10%, and
        log-log Pearson r > 0.99 over the full set.
    (g) render_debye_test produces a non-empty PNG at the canonical path.
"""

from __future__ import annotations

import math
import os
from pathlib import Path

import numpy as np
import pytest

from src.stiff_medium.debye_test import (
    HBAR,
    KB,
    MATERIALS,
    Material,
    N_A,
    debye_average_speed,
    debye_temperature,
    longitudinal_speed,
    material_sound_speeds,
    predict_theta_D,
    render_debye_test,
    run_test,
    transverse_speed,
)


# --------------------------------------------------------------------------- #
# Claim (a): schema integrity                                                  #
# --------------------------------------------------------------------------- #


def test_run_test_schema():
    res = run_test()
    assert "rows" in res and "summary" in res
    rows = res["rows"]
    assert set(rows.keys()) == set(MATERIALS.keys())
    expected_keys = {
        "name", "lattice", "rho_mass", "B_GPa", "G_GPa", "n_atoms",
        "c_L", "c_T", "c_Debye",
        "theta_pred", "theta_meas", "rel_err",
    }
    for name, row in rows.items():
        assert set(row.keys()) == expected_keys, f"{name}: schema mismatch"
        # All numeric scalars (except 'name' and 'lattice') must be positive
        for k, v in row.items():
            if k in ("name", "lattice"):
                continue
            if k == "rel_err":
                continue   # may be slightly negative
            assert v > 0.0, f"{name}: {k} not positive ({v})"


def test_summary_contains_expected_keys():
    res = run_test()
    s = res["summary"]
    expected = {
        "n_materials", "mean_rel_err", "mean_abs_rel_err",
        "median_abs_rel_err", "max_abs_rel_err",
        "max_rel_err_material", "rms_rel_err",
        "pearson_r", "pearson_log_r",
        "loglog_slope", "loglog_intercept",
        "within_5pct", "within_10pct", "within_20pct",
    }
    assert expected.issubset(set(s.keys()))


# --------------------------------------------------------------------------- #
# Claim (b): Debye-averaging identity                                          #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("name", list(MATERIALS.keys()))
def test_debye_average_identity(name):
    """3/c_D³ must equal 1/c_L³ + 2/c_T³ to machine precision."""
    mat = MATERIALS[name]
    c_L, c_T, c_D = material_sound_speeds(mat)
    lhs = 3.0 / c_D ** 3
    rhs = 1.0 / c_L ** 3 + 2.0 / c_T ** 3
    assert math.isclose(lhs, rhs, rel_tol=1.0e-12), (
        f"{name}: Debye averaging broken (lhs={lhs}, rhs={rhs})"
    )


def test_longitudinal_faster_than_transverse():
    """Physically, c_L > c_T always (since 4G/3 > 0)."""
    for name, mat in MATERIALS.items():
        c_L, c_T, _ = material_sound_speeds(mat)
        assert c_L > c_T, f"{name}: c_L ({c_L}) <= c_T ({c_T})"


def test_debye_average_between_T_and_L():
    """c_T < c_D < c_L for every material."""
    for name, mat in MATERIALS.items():
        c_L, c_T, c_D = material_sound_speeds(mat)
        assert c_T < c_D < c_L, (
            f"{name}: c_D not between c_T and c_L "
            f"(c_T={c_T}, c_D={c_D}, c_L={c_L})"
        )


# --------------------------------------------------------------------------- #
# Claim (c): atomic-density identity                                           #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("name", list(MATERIALS.keys()))
def test_atomic_density_formula(name):
    mat = MATERIALS[name]
    expected = N_A * mat.rho_mass / mat.M_molar
    assert math.isclose(mat.n_atoms_per_m3, expected, rel_tol=1.0e-12), (
        f"{name}: n = N_A·ρ/M broken"
    )


# --------------------------------------------------------------------------- #
# Claim (d): canonical anchor materials match user_context targets             #
# --------------------------------------------------------------------------- #


def test_diamond_within_5pct():
    """Diamond Θ_D should match measured 2230 K within 5%."""
    row = predict_theta_D(MATERIALS["Diamond"])
    assert abs(row["rel_err"]) < 0.05, (
        f"Diamond Θ_D = {row['theta_pred']:.1f} K, measured 2230, "
        f"rel err {row['rel_err']:+.2%}"
    )


def test_copper_within_2pct():
    """Copper Θ_D should match measured 343 K within 2% (anchor calibration)."""
    row = predict_theta_D(MATERIALS["Copper"])
    assert abs(row["rel_err"]) < 0.02, (
        f"Copper Θ_D = {row['theta_pred']:.1f} K, measured 343, "
        f"rel err {row['rel_err']:+.2%}"
    )


def test_aluminum_within_5pct():
    """Aluminum Θ_D should match measured 428 K within 5%."""
    row = predict_theta_D(MATERIALS["Aluminum"])
    assert abs(row["rel_err"]) < 0.05, (
        f"Aluminum Θ_D = {row['theta_pred']:.1f} K, measured 428, "
        f"rel err {row['rel_err']:+.2%}"
    )


def test_silicon_within_2pct():
    """Silicon Θ_D should match measured 645 K within 2%."""
    row = predict_theta_D(MATERIALS["Silicon"])
    assert abs(row["rel_err"]) < 0.02, (
        f"Silicon Θ_D = {row['theta_pred']:.1f} K, measured 645, "
        f"rel err {row['rel_err']:+.2%}"
    )


# --------------------------------------------------------------------------- #
# Claim (e): scaling behaviour                                                 #
# --------------------------------------------------------------------------- #


def test_theta_D_proportional_to_c_s():
    """Doubling c_s must double Θ_D (with n fixed)."""
    n = 8.49e28        # Cu number density
    base = debye_temperature(2620.0, n)
    doubled = debye_temperature(5240.0, n)
    assert math.isclose(doubled / base, 2.0, rel_tol=1.0e-12)


def test_theta_D_scales_with_n_cube_root():
    """Θ_D ∝ n^{1/3}: 8x density => 2x Θ_D."""
    cs = 3000.0
    base = debye_temperature(cs, 1.0e28)
    octupled = debye_temperature(cs, 8.0e28)
    assert math.isclose(octupled / base, 2.0, rel_tol=1.0e-12)


# --------------------------------------------------------------------------- #
# Claim (f): aggregate fit quality                                             #
# --------------------------------------------------------------------------- #


def test_at_least_10_materials_within_10pct():
    """Substrate prediction must hit ≥10/14 materials within 10%."""
    s = run_test()["summary"]
    assert s["within_10pct"] >= 10, (
        f"Only {s['within_10pct']}/14 within 10%"
    )


def test_at_least_12_materials_within_20pct():
    s = run_test()["summary"]
    assert s["within_20pct"] >= 12


def test_log_log_pearson_above_0p99():
    """Geometric correlation must be ≥0.99 across 14× Θ_D dynamic range."""
    s = run_test()["summary"]
    assert s["pearson_log_r"] > 0.99, (
        f"log-log pearson r = {s['pearson_log_r']:.4f}"
    )


def test_loglog_slope_near_unity():
    """log(pred) = m·log(meas) + b: slope m must be within 0.10 of 1.0."""
    s = run_test()["summary"]
    assert abs(s["loglog_slope"] - 1.0) < 0.10, (
        f"log-log slope = {s['loglog_slope']:.3f}"
    )


def test_mean_abs_residual_under_10pct():
    s = run_test()["summary"]
    assert s["mean_abs_rel_err"] < 0.10, (
        f"mean |rel err| = {s['mean_abs_rel_err']:.2%}"
    )


def test_mean_rel_err_unbiased_within_8pct():
    """Mean (signed) residual reflects systematic bias; should be small."""
    s = run_test()["summary"]
    assert abs(s["mean_rel_err"]) < 0.08, (
        f"mean signed err = {s['mean_rel_err']:+.2%}"
    )


# --------------------------------------------------------------------------- #
# Claim (g): visual renders                                                    #
# --------------------------------------------------------------------------- #


def test_render_debye_test_writes_png(tmp_path):
    out = tmp_path / "124_debye_test.png"
    path = render_debye_test(out_path=str(out))
    assert os.path.exists(path)
    assert os.path.getsize(path) > 5_000, "PNG suspiciously small"


# --------------------------------------------------------------------------- #
# Sanity: physical constants                                                   #
# --------------------------------------------------------------------------- #


def test_physical_constants_correct():
    """Spot-check: HBAR, KB, N_A are CODATA 2019 SI values."""
    assert math.isclose(HBAR, 1.054571817e-34, rel_tol=1.0e-12)
    assert math.isclose(KB,   1.380649e-23,    rel_tol=1.0e-12)
    assert math.isclose(N_A,  6.02214076e23,   rel_tol=1.0e-12)
