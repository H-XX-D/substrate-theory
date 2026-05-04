"""Tests for the PDG 2024 substrate hadron-mass test harness."""

from __future__ import annotations

import math

import pytest

from src.stiff_medium.hadron_mass_test import (
    PDG_2024,
    FAMILY_OCTET,
    FAMILY_DECUPLET,
    FAMILY_LIGHT_PS,
    FAMILY_LIGHT_V,
    FAMILY_HEAVY,
    HadronReport,
    HadronResidual,
    predict_substrate,
    run_hadron_mass_test,
)
from src.stiff_medium.hadron_spectrum import HadronSpectrum


# ---------------------------------------------------------------------------
# PDG reference table coverage
# ---------------------------------------------------------------------------


def test_pdg_2024_covers_required_targets() -> None:
    """All 22 user-supplied targets are present in the reference dict."""
    required = (
        # 12 baryons (8 octet + 4 decuplet representatives)
        "p", "n", "Lambda",
        "Sigma+", "Sigma0", "Sigma-",
        "Xi0", "Xi-",
        "Delta", "Sigma*0", "Xi*0", "Omega-",
        # 10 mesons (5 light PS + 3 light V + 2 heavy)
        "pi0", "pi", "K0", "K", "eta",
        "rho", "omega", "phi",
        "J/psi", "Upsilon",
    )
    for name in required:
        assert name in PDG_2024, name
        assert PDG_2024[name] > 0.0


def test_pdg_2024_proton_is_canonical() -> None:
    assert PDG_2024["p"] == pytest.approx(938.272, abs=1e-3)
    assert PDG_2024["n"] == pytest.approx(939.565, abs=1e-3)


def test_pdg_2024_omega_is_canonical() -> None:
    assert PDG_2024["Omega-"] == pytest.approx(1672.45, abs=1e-2)


def test_pdg_2024_jpsi_upsilon() -> None:
    assert PDG_2024["J/psi"] == pytest.approx(3096.900, abs=1e-3)
    assert PDG_2024["Upsilon"] == pytest.approx(9460.30, abs=1e-2)


# ---------------------------------------------------------------------------
# Family classification
# ---------------------------------------------------------------------------


def test_families_partition_pdg_table() -> None:
    """Every PDG_2024 entry belongs to exactly one family."""
    families = (
        FAMILY_OCTET, FAMILY_DECUPLET,
        FAMILY_LIGHT_PS, FAMILY_LIGHT_V, FAMILY_HEAVY,
    )
    union = set()
    for fam in families:
        union |= set(fam)
    assert union == set(PDG_2024.keys())
    # No double-counting:
    flat = []
    for fam in families:
        flat.extend(fam)
    assert len(flat) == len(set(flat))


# ---------------------------------------------------------------------------
# Predictor for each PDG entry
# ---------------------------------------------------------------------------


def test_predict_substrate_returns_finite_for_all() -> None:
    hs = HadronSpectrum()
    for name in PDG_2024:
        pred = predict_substrate(name, hs)
        assert math.isfinite(pred)
        assert pred > 0.0


def test_predict_substrate_unknown_raises() -> None:
    with pytest.raises(KeyError):
        predict_substrate("not_a_hadron")


def test_predict_delta_average_matches_quartet_mean() -> None:
    """Δ in this module is the isospin-averaged value over the quartet."""
    hs = HadronSpectrum()
    quartet = [hs.baryon_mass(n) for n in ("Delta++", "Delta+", "Delta0", "Delta-")]
    assert predict_substrate("Delta", hs) == pytest.approx(
        sum(quartet) / 4.0, rel=1e-12
    )


def test_predict_jpsi_uses_cc_vector_formula() -> None:
    """J/ψ should be the cc̄ vector-channel cell-pair mass."""
    from src.stiff_medium.b3_constants import LAMBDA_QCD_MEV
    from src.stiff_medium.hadron_spectrum import QUARK_TORQUE, B_MESON, G_V
    expected = LAMBDA_QCD_MEV * (2.0 * QUARK_TORQUE["c"] + G_V * B_MESON)
    assert predict_substrate("J/psi") == pytest.approx(expected, rel=1e-12)


# ---------------------------------------------------------------------------
# Residual + report structure
# ---------------------------------------------------------------------------


def test_run_returns_full_report() -> None:
    rpt = run_hadron_mass_test()
    assert isinstance(rpt, HadronReport)
    assert rpt.n_total == len(PDG_2024)
    assert rpt.n_total >= 22
    for r in rpt.residuals:
        assert isinstance(r, HadronResidual)
        assert math.isfinite(r.rel_err)


def test_report_text_contains_key_lines() -> None:
    text = run_hadron_mass_test().to_text()
    assert "PDG 2024" in text
    assert "OVERALL" in text
    assert "Per-family statistics" in text
    # Key family lines:
    for fam in ("octet", "decuplet", "light_ps", "light_v", "heavy"):
        assert fam in text


def test_overall_mean_is_finite() -> None:
    rpt = run_hadron_mass_test()
    assert math.isfinite(rpt.mean_abs_rel)
    assert rpt.mean_abs_rel >= 0.0


def test_family_stats_cover_all_families() -> None:
    fs = run_hadron_mass_test().family_stats()
    fams = {f.family for f in fs}
    assert fams == {"octet", "decuplet", "light_ps", "light_v", "heavy"}
    for f in fs:
        assert f.n >= 1
        assert math.isfinite(f.mean_abs_rel)
        assert math.isfinite(f.max_abs_rel)
        assert f.max_abs_rel >= f.mean_abs_rel - 1e-12


# ---------------------------------------------------------------------------
# Honest verdict: regression-ratchet thresholds
# ---------------------------------------------------------------------------


def test_proton_at_sub_1_percent() -> None:
    rpt = run_hadron_mass_test()
    p = next(r for r in rpt.residuals if r.name == "p")
    assert abs(p.rel_err) < 0.01, p


def test_delta_at_sub_1_percent() -> None:
    rpt = run_hadron_mass_test()
    d = next(r for r in rpt.residuals if r.name == "Delta")
    assert abs(d.rel_err) < 0.01, d


def test_decuplet_family_mean_under_10_percent() -> None:
    fs = next(f for f in run_hadron_mass_test().family_stats() if f.family == "decuplet")
    assert fs.mean_abs_rel < 0.10


def test_octet_family_mean_under_10_percent() -> None:
    fs = next(f for f in run_hadron_mass_test().family_stats() if f.family == "octet")
    assert fs.mean_abs_rel < 0.10


def test_light_ps_family_breaks_at_eta() -> None:
    """η is the worst light-PS residual (mixing not modeled)."""
    fs = next(f for f in run_hadron_mass_test().family_stats() if f.family == "light_ps")
    # mean is large because η + K span the SU(3) singlet-octet split
    assert fs.worst == "eta"
    assert fs.max_abs_rel > 0.20  # η residual is 30%+ low


def test_heavy_quarkonia_break_as_expected() -> None:
    """Heavy quarkonia underpredict (no Coulomb correction in leading model)."""
    rpt = run_hadron_mass_test()
    jpsi = next(r for r in rpt.residuals if r.name == "J/psi")
    upsilon = next(r for r in rpt.residuals if r.name == "Upsilon")
    # Both should be NEGATIVE (underprediction) and large.
    assert jpsi.rel_err < -0.20
    assert upsilon.rel_err < -0.50
