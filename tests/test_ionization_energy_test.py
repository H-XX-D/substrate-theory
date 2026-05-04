"""Tests for ionization_energy_test -- substrate Schroedinger first IE H..Ar."""

from __future__ import annotations

import pytest

from src.stiff_medium.atom_substrate import RYDBERG_EV
from src.stiff_medium.b3_constants import K_rank
from src.stiff_medium.ionization_energy_test import (
    ELEMENT_SYMBOLS,
    GROUP_LABEL,
    HF_ORBITAL_HARTREE,
    MEASURED_IE_EV,
    SIGMA_PP,
    SIGMA_SP,
    Z_EFF_CALIBRATED_EXTENDED,
    build_rows,
    group_breakdown,
    k_rank_zeff_for_least_bound,
    predict_ionization_energy,
    predict_substrate_HF,
    run_test,
    slater_zeff_for_least_bound,
)


# --------------------------------------------------------------------------- #
# Coverage / data integrity                                                   #
# --------------------------------------------------------------------------- #

def test_measured_table_covers_h_through_ar():
    for Z in range(1, 19):
        assert Z in MEASURED_IE_EV
        assert MEASURED_IE_EV[Z] > 0.0
        assert Z in ELEMENT_SYMBOLS
        assert Z in GROUP_LABEL


def test_calibrated_table_extends_to_18():
    for Z in range(1, 19):
        assert Z in Z_EFF_CALIBRATED_EXTENDED
        assert Z_EFF_CALIBRATED_EXTENDED[Z] > 0.0


# --------------------------------------------------------------------------- #
# Slater zero-knob: hard checks on the ones it gets RIGHT and WRONG           #
# --------------------------------------------------------------------------- #

def test_slater_hydrogen_exact():
    """H has no other electrons -> Slater Z_eff = 1, IE = Rydberg exactly."""
    z, ie = predict_ionization_energy(1, "slater")
    assert z == pytest.approx(1.0)
    assert ie == pytest.approx(RYDBERG_EV, rel=1e-12)


def test_slater_helium_overshoots():
    """He: Slater Z_eff = 1.70 -> IE = 39.3 eV, +60% over measured 24.6 eV.

    This is a known limitation of Slater's rules and of the substrate-
    Schroedinger formula as a zero-knob predictor; record it as such.
    """
    z, ie = predict_ionization_energy(2, "slater")
    assert z == pytest.approx(1.70, abs=1e-3)
    assert ie > 35.0
    assert ie < 45.0


def test_slater_lithium_within_10pct():
    """Li 2s electron: Slater (s = 1.7) gives Z_eff = 1.3 -> IE = 5.75 eV (+7%)."""
    _, ie = predict_ionization_energy(3, "slater")
    err = 100.0 * abs(ie - MEASURED_IE_EV[3]) / MEASURED_IE_EV[3]
    assert err < 10.0


def test_slater_p_shell_blowup():
    """Slater grossly OVER-predicts for B..Ne and Al..Ar (p-shell electrons).

    Sentinel test: error >= 50% for every p-shell row-2/row-3 element.
    """
    p_shell = [5, 6, 7, 8, 9, 10, 13, 14, 15, 16, 17, 18]
    for Z in p_shell:
        _, ie = predict_ionization_energy(Z, "slater")
        meas = MEASURED_IE_EV[Z]
        err = 100.0 * abs(ie - meas) / meas
        assert err > 50.0, f"Z={Z}: Slater error {err:.1f}% (expected >50%)"


def test_slater_zeff_monotone_within_period():
    """Within a period, Slater Z_eff INCREASES monotonically with Z."""
    # Period 2: Li (Z=3) .. Ne (Z=10)
    period2 = [slater_zeff_for_least_bound(Z) for Z in range(3, 11)]
    for a, b in zip(period2, period2[1:]):
        assert b > a
    # Period 3: Na (Z=11) .. Ar (Z=18)
    period3 = [slater_zeff_for_least_bound(Z) for Z in range(11, 19)]
    for a, b in zip(period3, period3[1:]):
        assert b > a


# --------------------------------------------------------------------------- #
# Calibrated mode: substrate-Schroedinger n^{-2} structural form is exact     #
# --------------------------------------------------------------------------- #

def test_calibrated_recovers_measured_for_all_18():
    """One Z_eff per element makes the substrate-Schroedinger eigenvalue match
    every measured IE within 0.1% (machine precision of the calibration).

    This shows the structural form  IE = Ry * Z_eff^2 / n^2  is correct;
    the only thing 'fitted' is one effective charge per atom.
    """
    rows = build_rows(18)
    for r in rows:
        assert r.err_calibrated_pct < 0.1, (
            f"{r.symbol}: pred {r.pred_calibrated_eV:.4f} vs "
            f"measured {r.measured_eV:.4f}, err {r.err_calibrated_pct:.4f}%"
        )


def test_calibrated_h_and_ne_match_atom_substrate_table():
    """Calibrated Z_eff for Z=1..10 must equal the values in atom_substrate."""
    from src.stiff_medium.atom_substrate import Z_EFF_LEAST_BOUND
    for Z in range(1, 11):
        assert Z_EFF_CALIBRATED_EXTENDED[Z] == pytest.approx(
            Z_EFF_LEAST_BOUND[Z], rel=1e-12
        )


# --------------------------------------------------------------------------- #
# build_rows / run_test                                                        #
# --------------------------------------------------------------------------- #

def test_build_rows_returns_18_entries():
    rows = build_rows(18)
    assert len(rows) == 18
    assert rows[0].symbol == "H"
    assert rows[-1].symbol == "Ar"


def test_run_test_summary_keys():
    res = run_test()
    assert set(res["summary"].keys()) == {     # type: ignore[union-attr]
        "n_elements",
        "slater_mean_pct",
        "slater_max_pct",
        "krank_mean_pct",
        "krank_max_pct",
        "substrate_HF_mean_pct",
        "substrate_HF_max_pct",
        "calibrated_mean_pct",
        "calibrated_max_pct",
    }
    assert int(res["summary"]["n_elements"]) == 18    # type: ignore[index]
    # Calibrated mean error must be < 0.01% (it's machine-precision)
    assert res["summary"]["calibrated_mean_pct"] < 0.01   # type: ignore[index,operator]
    # Slater mean error is large (sentinel: > 100%)
    assert res["summary"]["slater_mean_pct"] > 100.0      # type: ignore[index,operator]
    # K_rank substrate refinement -- order-of-magnitude better than Slater,
    # well below 30%, but not below 5% (no per-element knobs)
    assert res["summary"]["krank_mean_pct"] < 30.0        # type: ignore[index,operator]
    assert res["summary"]["krank_mean_pct"] < res["summary"]["slater_mean_pct"] / 10.0   # type: ignore[index]
    # Substrate-HF Koopmans -- mean below 10% (zero-element-knob HF)
    assert res["summary"]["substrate_HF_mean_pct"] < 10.0       # type: ignore[index,operator]
    # Substrate-HF beats K_rank substantially
    assert (
        res["summary"]["substrate_HF_mean_pct"]                                # type: ignore[index]
        < res["summary"]["krank_mean_pct"] / 2.0                               # type: ignore[index]
    )


def test_group_breakdown_categories():
    rows = build_rows(18)
    bd = group_breakdown(rows, "err_slater_pct")
    expected = {"row1_s", "row2_s", "row2_p", "row3_s", "row3_p"}
    assert set(bd.keys()) == expected
    # row2_s (Li, Be) is the best Slater group; row2_p the worst.
    s_means = {g: bd[g]["mean_pct"] for g in bd}
    assert s_means["row2_s"] < s_means["row2_p"]
    assert s_means["row2_s"] < s_means["row3_p"]


def test_best_group_slater_is_row2_s():
    """Slater zero-knob fits the s-shell of period 2 (Li, Be) best of all 5
    groups (mean error ~ 23% there; >300% for p-groups)."""
    res = run_test()
    assert res["best_group_slater"] == "row2_s"


# --------------------------------------------------------------------------- #
# Sanity: predicted IE always positive, n_least matches Aufbau                #
# --------------------------------------------------------------------------- #

def test_predicted_ies_positive_in_all_modes():
    for Z in range(1, 19):
        for mode in ("slater", "krank", "substrate_HF", "calibrated"):
            _, ie = predict_ionization_energy(Z, mode)
            assert ie > 0.0, f"Z={Z}, mode={mode}: IE = {ie}"


def test_predict_unknown_mode_raises():
    with pytest.raises(ValueError):
        predict_ionization_energy(1, mode="bogus")


# --------------------------------------------------------------------------- #
# K_rank substrate refinement: substrate-derived intra-shell screening        #
# --------------------------------------------------------------------------- #

def test_sigma_constants_derived_from_K_rank():
    """sigma_pp and sigma_sp are forced by canonical K_rank=5 4-simplex."""
    assert SIGMA_PP == pytest.approx(1.0 - 1.0 / K_rank)
    assert SIGMA_PP == pytest.approx(4.0 / 5.0)
    assert SIGMA_SP == pytest.approx(1.0 - 1.0 / (K_rank * K_rank))
    assert SIGMA_SP == pytest.approx(24.0 / 25.0)
    # K_rank=5 confirmed by canonical b3_constants
    assert K_rank == 5


def test_krank_hydrogen_exact():
    """H still has Z_eff = 1, so K_rank refinement is trivially exact."""
    z, ie = predict_ionization_energy(1, "krank")
    assert z == pytest.approx(1.0)
    assert ie == pytest.approx(RYDBERG_EV, rel=1e-12)


def test_krank_p_shell_outperforms_slater():
    """For every 2p / 3p element, K_rank screening beats Slater by >5x."""
    p_shell = [5, 6, 7, 8, 9, 10, 13, 14, 15, 16, 17, 18]
    for Z in p_shell:
        _, ie_sl = predict_ionization_energy(Z, "slater")
        _, ie_kr = predict_ionization_energy(Z, "krank")
        meas = MEASURED_IE_EV[Z]
        err_sl = 100.0 * abs(ie_sl - meas) / meas
        err_kr = 100.0 * abs(ie_kr - meas) / meas
        assert err_kr * 5.0 < err_sl, (
            f"Z={Z}: Slater {err_sl:.1f}%, K_rank {err_kr:.1f}% -- K_rank "
            f"should beat Slater by 5x"
        )


def test_krank_s_shell_unchanged():
    """For s-targets, K_rank substitution does not change s-on-s screening,
    so the prediction equals Slater's."""
    s_targets = [1, 2, 3, 4, 11, 12]
    for Z in s_targets:
        _, ie_sl = predict_ionization_energy(Z, "slater")
        _, ie_kr = predict_ionization_energy(Z, "krank")
        assert ie_sl == pytest.approx(ie_kr, rel=1e-9), (
            f"Z={Z}: K_rank rule must equal Slater for s-targets"
        )


def test_krank_mean_error_below_25_pct():
    """K_rank substrate model: mean abs error < 25% across H..Ar."""
    rows = build_rows(18)
    errs = [r.err_krank_pct for r in rows]
    mean_err = sum(errs) / len(errs)
    assert mean_err < 25.0, f"K_rank mean = {mean_err:.2f}%"


# --------------------------------------------------------------------------- #
# Substrate-HF (Roothaan-HF orbitals + Koopmans)                              #
# --------------------------------------------------------------------------- #

def test_HF_orbital_table_covers_h_through_ar():
    for Z in range(1, 19):
        assert Z in HF_ORBITAL_HARTREE
        assert HF_ORBITAL_HARTREE[Z] < 0.0   # bound-state orbital


def test_HF_hydrogen_exact():
    """H 1s HF eigenvalue is exactly -0.5 Hartree -> 13.6057 eV."""
    z_eq, ie = predict_substrate_HF(1)
    assert ie == pytest.approx(13.6057, abs=1e-3)
    # Diagnostic Z_eff_eq for H must be 1
    assert z_eq == pytest.approx(1.0, abs=1e-3)


def test_HF_mean_error_below_10_pct():
    """Substrate-HF (Roothaan-HF + Koopmans): mean abs err < 10% across H..Ar."""
    rows = build_rows(18)
    errs = [r.err_HF_pct for r in rows]
    mean_err = sum(errs) / len(errs)
    assert mean_err < 10.0, f"Substrate-HF mean = {mean_err:.2f}%"


def test_HF_outperforms_K_rank_on_average():
    """HF Koopmans should beat the K_rank substrate refinement on average,
    because HF carries proper exchange treatment from a self-consistent solve."""
    rows = build_rows(18)
    err_kr = sum(r.err_krank_pct for r in rows) / len(rows)
    err_hf = sum(r.err_HF_pct for r in rows) / len(rows)
    assert err_hf < err_kr, (
        f"K_rank mean {err_kr:.2f}%, HF mean {err_hf:.2f}% -- HF should win"
    )


def test_HF_oxygen_is_largest_anomaly():
    """Half-filled p-shell (O, Z=8) is the worst Koopmans anomaly because
    Koopmans misses the spin-coupling exchange-stabilisation effect."""
    rows = build_rows(18)
    o_row = next(r for r in rows if r.Z == 8)
    other_p = [r for r in rows if r.ell_least == 1 and r.Z != 8]
    assert o_row.err_HF_pct > max(r.err_HF_pct for r in other_p), (
        "O (half-filled 2p^4) should have the largest HF Koopmans error "
        "among all p-shell elements"
    )


def test_predict_substrate_HF_unknown_Z_raises():
    with pytest.raises(ValueError):
        predict_substrate_HF(19)


# --------------------------------------------------------------------------- #
# Cross-mode: ranking of methods on mean error                                #
# --------------------------------------------------------------------------- #

def test_method_ranking_on_mean_error():
    """Calibrated < Substrate-HF < K_rank < Slater (mean abs error)."""
    res = run_test()
    s = res["summary"]
    assert s["calibrated_mean_pct"]   < s["substrate_HF_mean_pct"]   # type: ignore[index]
    assert s["substrate_HF_mean_pct"] < s["krank_mean_pct"]          # type: ignore[index]
    assert s["krank_mean_pct"]        < s["slater_mean_pct"]         # type: ignore[index]
