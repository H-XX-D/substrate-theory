"""Tests for src.stiff_medium.generation_map."""

from __future__ import annotations

import math
import os
import sys

import numpy as np
import pytest

# Ensure src/ is on path
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

from stiff_medium.generation_map import (  # noqa: E402
    GenerationMap,
    LEPTON_MASSES_MEV,
)


@pytest.fixture
def gmap() -> GenerationMap:
    return GenerationMap()


def test_constants(gmap: GenerationMap) -> None:
    assert gmap.n_M == 268
    assert gmap.K_pair == 2
    assert gmap.K_rank == 5


def test_mu_over_e_high_precision(gmap: GenerationMap) -> None:
    pred = gmap.lepton_ratio(2, 1)
    obs = LEPTON_MASSES_MEV["mu"] / LEPTON_MASSES_MEV["e"]
    err_pct = 100.0 * abs(pred - obs) / obs
    assert err_pct < 0.01, f"mu/e error {err_pct:.4f}% exceeded 0.01%"


def test_tau_over_e_within_2_5_percent(gmap: GenerationMap) -> None:
    pred = gmap.lepton_ratio(3, 1)
    obs = LEPTON_MASSES_MEV["tau"] / LEPTON_MASSES_MEV["e"]
    err_pct = 100.0 * abs(pred - obs) / obs
    assert err_pct < 2.5, f"tau/e error {err_pct:.3f}% exceeded 2.5%"


def test_tau_over_mu_reasonable(gmap: GenerationMap) -> None:
    pred = gmap.lepton_ratio(3, 2)
    obs = LEPTON_MASSES_MEV["tau"] / LEPTON_MASSES_MEV["mu"]
    err_pct = 100.0 * abs(pred - obs) / obs
    # ~2.14% expected
    assert err_pct < 3.0


def test_inverse_ratios(gmap: GenerationMap) -> None:
    assert math.isclose(
        gmap.lepton_ratio(1, 2) * gmap.lepton_ratio(2, 1), 1.0, rel_tol=1e-12
    )
    assert math.isclose(gmap.lepton_ratio(2, 2), 1.0)


def test_chain_consistency(gmap: GenerationMap) -> None:
    direct = gmap.lepton_ratio(3, 1)
    chained = gmap.lepton_ratio(2, 1) * gmap.lepton_ratio(3, 2)
    assert math.isclose(direct, chained, rel_tol=1e-12)


def test_invalid_pair_raises(gmap: GenerationMap) -> None:
    with pytest.raises(ValueError):
        gmap.lepton_ratio(4, 1)


def test_verify_lepton_masses_structure(gmap: GenerationMap) -> None:
    out = gmap.verify_lepton_masses()
    for key in ("mu/e", "tau/mu", "tau/e"):
        assert key in out
        assert set(out[key]) == {"predicted", "observed", "error_pct"}


def test_neutrino_predictions_both_hierarchies(gmap: GenerationMap) -> None:
    nh = gmap.predict_neutrino_ratios("NH")
    ih = gmap.predict_neutrino_ratios("IH")
    assert any("nu2/nu1" in k for k in nh)
    assert any("nu3/nu1" in k for k in ih)


def test_quark_predictions_present(gmap: GenerationMap) -> None:
    out = gmap.predict_quark_ratios()
    for k in ("c/u", "t/c", "t/u", "s/d", "b/s", "b/d"):
        assert k in out


def test_determinism(gmap: GenerationMap) -> None:
    a = gmap.verify_lepton_masses()
    b = gmap.verify_lepton_masses()
    assert a == b
    assert gmap.lepton_ratio(3, 1) == gmap.lepton_ratio(3, 1)
    assert gmap.predict_quark_ratios() == gmap.predict_quark_ratios()


def test_report_runs(gmap: GenerationMap, capsys: pytest.CaptureFixture) -> None:
    txt = gmap.report()
    assert "Substrate Generation Map" in txt
    captured = capsys.readouterr()
    assert "Substrate Generation Map" in captured.out
