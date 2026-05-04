"""BCS universal gap ratio: substrate prediction vs measured superconductors.

The substrate-paired Cooper-bridge ground state predicts a UNIVERSAL,
parameter-free weak-coupling ratio between the zero-temperature gap and
the critical temperature:

       2 Δ(0) / (k_B T_c)  =  2 π / e^γ   ≃   3.527754

where γ = 0.5772156649... is the Euler-Mascheroni constant.  The same
result is the BCS-1957 universal ratio, derived in the substrate
ontology from the paired-strain bridge unbinding condition (see
``superconductivity_substrate.SuperconductivitySimulator.bcs_ratio``).

This module compares that prediction against tabulated literature
values of (T_c, 2Δ(0)) for ten elemental and one multiband
superconductor.

Materials
---------
The reference table here is independently sourced (Tinkham, Carbotte,
NIST, PDG element-card values) and intentionally distinct from the
back-solved Hg/HBCCO calibration table in
``superconductivity_substrate.REFERENCE_SUPERCONDUCTORS`` --- this is a
*test*, not a refit:

    name     T_c (K)     2Δ(0) (meV)     class
    -------  ----------  --------------  -----------------------------
    Hg        4.15        1.41            elemental, weak-coupling BCS
    Pb        7.20        2.74            elemental, strong-coupling BCS
    Sn        3.72        1.15            elemental, weak-coupling BCS
    Al        1.20        0.34            elemental, weak-coupling BCS
    Nb        9.25        3.05            elemental, weak/strong-borderline BCS
    V         5.40        1.55            elemental, weak-coupling BCS
    Ta        4.48        1.40            elemental, weak-coupling BCS
    In        3.40        1.05            elemental, weak-coupling BCS
    Tl        2.39        0.74            elemental, weak-coupling BCS
    MgB_2    39.0        14.0             multiband (σ + π), expected to deviate

The measured ratio R_meas = 2Δ(0) / (k_B T_c) is compared to the
substrate prediction R_pred = 2π / e^γ ≃ 3.528.  Per-material percent
deviation is reported.

API
---
``MATERIALS``                  : tuple of ``MaterialDatum`` (immutable).
``BCS_RATIO_PRED``             : float, 2π/e^γ.
``measured_ratio(T_c, gap)``   : compute R_meas from K and meV.
``deviation_percent(R)``       : (R - R_pred) / R_pred * 100.
``run_test()``                 : returns a list of ``ResultRow`` with
                                 (name, T_c, gap_meV, R_meas, dev_pct,
                                 within_5pct).
``summary_stats(rows)``        : mean / max / min |dev|, n_within_5pct.
``render_bcs_gap_ratio_test()``: matplotlib bar-chart figure for the
                                 visuals/120 PNG.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

import math

import numpy as np


# ---------------------------------------------------------------------------
# Physical constants (SI)
# ---------------------------------------------------------------------------

K_B:        float = 1.380649e-23           # J/K   Boltzmann
EV_PER_J:   float = 1.0 / 1.602176634e-19  # eV / J
K_B_MEV_K:  float = (K_B * EV_PER_J) * 1e3 # 1 K -> meV  (= 0.0861733...)


# ---------------------------------------------------------------------------
# Substrate / BCS prediction
# ---------------------------------------------------------------------------

EULER_GAMMA:    float = 0.5772156649015329
BCS_RATIO_PRED: float = 2.0 * math.pi / math.exp(EULER_GAMMA)
# = 3.527753977724091


# ---------------------------------------------------------------------------
# Reference data (literature)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MaterialDatum:
    """One measured superconductor entry.

    Attributes
    ----------
    name      : symbol / label.
    T_c_K     : critical temperature (K), measured at zero applied field
                and ambient pressure.
    gap_meV   : full gap 2 Δ(0) in milli-electronvolts at T -> 0.
    klass     : qualitative class -- ``"elemental"``, ``"multiband"``.
    note      : short physics note (coupling regime / known anomalies).
    """
    name:    str
    T_c_K:   float
    gap_meV: float
    klass:   str
    note:    str


MATERIALS: Tuple[MaterialDatum, ...] = (
    MaterialDatum("Hg",   4.15,  1.41, "elemental",
                  "Onnes 1911; mildly strong-coupling"),
    MaterialDatum("Pb",   7.20,  2.74, "elemental",
                  "Strong-coupling Eliashberg, ratio ~4.4 known"),
    MaterialDatum("Sn",   3.72,  1.15, "elemental",
                  "Weak-coupling, near-textbook BCS"),
    MaterialDatum("Al",   1.20,  0.34, "elemental",
                  "Weak-coupling reference, ratio ~3.3-3.5"),
    MaterialDatum("Nb",   9.25,  3.05, "elemental",
                  "Weak-/strong-coupling borderline; 2-band hints"),
    MaterialDatum("V",    5.40,  1.55, "elemental",
                  "Weak-coupling, near textbook"),
    MaterialDatum("Ta",   4.48,  1.40, "elemental",
                  "Weak-coupling, near textbook"),
    MaterialDatum("In",   3.40,  1.05, "elemental",
                  "Weak-coupling, near textbook"),
    MaterialDatum("Tl",   2.39,  0.74, "elemental",
                  "Weak-coupling, near textbook"),
    MaterialDatum("MgB2", 39.0, 14.00, "multiband",
                  "Two-band sigma+pi: dominant sigma gap, deviation expected"),
)


# ---------------------------------------------------------------------------
# Core arithmetic
# ---------------------------------------------------------------------------

def measured_ratio(T_c_K: float, gap_meV: float) -> float:
    """Return R_meas = 2Δ(0) / (k_B T_c), DIMENSIONLESS.

    ``gap_meV`` is the full gap 2Δ(0) in meV (the literature convention
    used throughout this module's table).  ``T_c_K`` is in Kelvin.

    R_meas = (gap_meV * 1e-3 / EV_PER_J) / (K_B * T_c_K)
           = gap_meV / (K_B_MEV_K * T_c_K).
    """
    if T_c_K <= 0.0:
        raise ValueError(f"T_c must be > 0, got {T_c_K!r}")
    if gap_meV <= 0.0:
        raise ValueError(f"gap must be > 0, got {gap_meV!r}")
    return float(gap_meV / (K_B_MEV_K * T_c_K))


def deviation_percent(R_meas: float, R_pred: float = BCS_RATIO_PRED) -> float:
    """Return (R_meas - R_pred) / R_pred * 100."""
    return float((R_meas - R_pred) / R_pred * 100.0)


# ---------------------------------------------------------------------------
# Test driver
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ResultRow:
    """Per-material BCS gap ratio test result."""
    name:           str
    T_c_K:          float
    gap_meV:        float
    klass:          str
    R_meas:         float
    R_pred:         float
    dev_pct:        float
    within_5pct:    bool
    note:           str


def run_test(
    materials: Iterable[MaterialDatum] = MATERIALS,
    R_pred:    float = BCS_RATIO_PRED,
    threshold_pct: float = 5.0,
) -> List[ResultRow]:
    """Compute R_meas, deviation, and pass/fail at ``threshold_pct``.

    Returns one ``ResultRow`` per input material.  Order is preserved.
    """
    rows: List[ResultRow] = []
    for m in materials:
        R = measured_ratio(m.T_c_K, m.gap_meV)
        d = deviation_percent(R, R_pred)
        rows.append(ResultRow(
            name=m.name,
            T_c_K=m.T_c_K,
            gap_meV=m.gap_meV,
            klass=m.klass,
            R_meas=R,
            R_pred=R_pred,
            dev_pct=d,
            within_5pct=abs(d) <= threshold_pct,
            note=m.note,
        ))
    return rows


def summary_stats(rows: List[ResultRow]) -> dict:
    """Aggregate statistics across a result set.

    Returns a dict with:
        n             : number of materials
        n_within_5pct : count of |deviation| <= 5 %
        mean_abs_dev  : mean |deviation| in percent
        max_abs_dev   : max  |deviation| in percent
        min_abs_dev   : min  |deviation| in percent
        elemental_only: same five fields but restricted to klass=="elemental"
    """
    if not rows:
        raise ValueError("empty rows")
    abs_devs = np.array([abs(r.dev_pct) for r in rows], dtype=float)
    n_pass   = int(sum(1 for r in rows if r.within_5pct))
    elem     = [r for r in rows if r.klass == "elemental"]
    elem_abs = np.array([abs(r.dev_pct) for r in elem], dtype=float)
    elem_pass = int(sum(1 for r in elem if r.within_5pct))
    return {
        "n":             len(rows),
        "n_within_5pct": n_pass,
        "mean_abs_dev":  float(abs_devs.mean()),
        "max_abs_dev":   float(abs_devs.max()),
        "min_abs_dev":   float(abs_devs.min()),
        "elemental_only": {
            "n":             len(elem),
            "n_within_5pct": elem_pass,
            "mean_abs_dev":  float(elem_abs.mean()) if len(elem) else 0.0,
            "max_abs_dev":   float(elem_abs.max())  if len(elem) else 0.0,
            "min_abs_dev":   float(elem_abs.min())  if len(elem) else 0.0,
        },
    }


# ---------------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------------

def render_bcs_gap_ratio_test(out_path: str) -> str:
    """Render a bar chart of measured 2Δ/(k_B T_c) per material vs the
    substrate prediction 2π/e^γ ≃ 3.528.  Saves PNG to ``out_path`` and
    returns the path.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = run_test()
    names    = [r.name        for r in rows]
    R_vals   = [r.R_meas      for r in rows]
    devs     = [r.dev_pct     for r in rows]
    klasses  = [r.klass       for r in rows]

    color_for = {
        "elemental":  "#1f77b4",  # tab:blue
        "multiband":  "#9467bd",  # tab:purple
    }
    bar_colors = [color_for.get(k, "gray") for k in klasses]

    fig, (ax1, ax2) = plt.subplots(
        nrows=2, ncols=1, figsize=(11.0, 8.5),
        gridspec_kw=dict(height_ratios=[3, 2], hspace=0.35),
    )

    # ---- top: measured ratio per material vs prediction line --------
    bars = ax1.bar(names, R_vals, color=bar_colors, edgecolor="black",
                   linewidth=0.8)
    ax1.axhline(BCS_RATIO_PRED, color="crimson", linestyle="--",
                linewidth=1.8,
                label=f"Substrate / BCS prediction $2\\pi/e^\\gamma$ "
                      f"= {BCS_RATIO_PRED:.3f}")
    # +-5% guide bands
    ax1.axhspan(BCS_RATIO_PRED * 0.95, BCS_RATIO_PRED * 1.05,
                color="crimson", alpha=0.10, label="+/- 5 % band")
    ax1.set_ylabel(r"$2\Delta(0) / (k_B T_c)$  (dimensionless)",
                   fontsize=11)
    ax1.set_title("BCS universal gap ratio: substrate prediction vs "
                  "measured superconductors",
                  fontsize=12)
    # Tighten the y-axis around the data band so deviations are visible
    # but leave headroom so bar labels and legend don't collide.
    ax1.set_ylim(0.0, 6.2)
    ax1.grid(axis="y", alpha=0.3)
    # numeric labels on bars (placed above the bar top)
    for bar, r in zip(bars, rows):
        ax1.text(bar.get_x() + bar.get_width() / 2.0,
                 bar.get_height() + 0.05,
                 f"{r.R_meas:.2f}",
                 ha="center", va="bottom", fontsize=8)

    # legend swatches for class -- placed at upper left, above the
    # 6.2 axis ceiling and above all bar heights.
    from matplotlib.patches import Patch
    handles, _ = ax1.get_legend_handles_labels()
    handles.extend([
        Patch(color=color_for["elemental"], label="elemental"),
        Patch(color=color_for["multiband"], label="multiband"),
    ])
    ax1.legend(handles=handles, loc="upper left", fontsize=9,
               framealpha=0.95, ncol=2)

    # ---- bottom: percent deviation ---------------------------------
    bars2 = ax2.bar(names, devs, color=bar_colors, edgecolor="black",
                    linewidth=0.8)
    ax2.axhline(0.0, color="black", linewidth=0.8)
    ax2.axhspan(-5.0, 5.0, color="crimson", alpha=0.10,
                label="+/- 5 % match band")
    ax2.set_ylabel("deviation from\nprediction (%)", fontsize=11)
    ax2.grid(axis="y", alpha=0.3)
    ax2.legend(loc="lower left", fontsize=9)
    for bar, r in zip(bars2, rows):
        y = bar.get_height()
        offset = 0.6 if y >= 0 else -1.4
        ax2.text(bar.get_x() + bar.get_width() / 2.0,
                 y + offset,
                 f"{r.dev_pct:+.1f}%",
                 ha="center", va="bottom" if y >= 0 else "top",
                 fontsize=8)

    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return out_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_table(rows: List[ResultRow]) -> None:
    print(f"\nBCS gap ratio test: substrate prediction = {BCS_RATIO_PRED:.6f}")
    print(f"({'name':<6}  {'T_c[K]':>7}  {'2D[meV]':>8}  "
          f"{'R_meas':>7}  {'dev[%]':>8}  {'<=5%':>6}  class")
    for r in rows:
        flag = "Y" if r.within_5pct else " "
        print(f" {r.name:<6}  {r.T_c_K:>7.2f}  {r.gap_meV:>8.3f}  "
              f"{r.R_meas:>7.3f}  {r.dev_pct:>+8.2f}  {flag:>6}  "
              f"{r.klass}")


def main() -> None:
    rows = run_test()
    _print_table(rows)
    stats = summary_stats(rows)
    print("\nAggregate (all materials):")
    print(f"  n={stats['n']}, n_within_5pct={stats['n_within_5pct']}, "
          f"mean|dev|={stats['mean_abs_dev']:.2f}%, "
          f"max|dev|={stats['max_abs_dev']:.2f}%")
    elem = stats["elemental_only"]
    print("Aggregate (elemental only):")
    print(f"  n={elem['n']}, n_within_5pct={elem['n_within_5pct']}, "
          f"mean|dev|={elem['mean_abs_dev']:.2f}%, "
          f"max|dev|={elem['max_abs_dev']:.2f}%")


__all__ = [
    "BCS_RATIO_PRED",
    "EULER_GAMMA",
    "K_B_MEV_K",
    "MATERIALS",
    "MaterialDatum",
    "ResultRow",
    "deviation_percent",
    "main",
    "measured_ratio",
    "render_bcs_gap_ratio_test",
    "run_test",
    "summary_stats",
]


if __name__ == "__main__":  # pragma: no cover
    main()
