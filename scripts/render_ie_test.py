"""Generate visuals/126_ie_test.png -- predicted-vs-measured first IE H..Ar.

Three-panel figure with FOUR lines per panel:
  (left)   Predicted IE vs measured for all 18 elements (line plot, log scale)
           Lines: NIST / Slater bare (0-knob) / Substrate-HF (Roothaan-HF +
           Koopmans, 0 knob) / Per-element calibrated (1 knob/element).
  (centre) % residual per element under all four models (log-scale).
  (right)  Group breakdown: mean residual per row/subshell group, all models.

The figure makes the verdict visually obvious:
  - Calibrated lines match measured to machine precision (n^{-2} form is right)
  - Slater bars overshoot p-shell electrons by 3-5x
  - K_rank substrate refinement (0-knob, sigma_pp=4/5, sigma_sp=24/25) cuts
    the mean p-shell error by ~12x relative to Slater
  - Roothaan-HF + Koopmans (0-knob, public Clementi-Roetti orbital energies)
    pulls mean error to ~6%, with O/S the worst (half-filled p-shell anomaly)
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.stiff_medium.ionization_energy_test import (
    SIGMA_PP,
    SIGMA_SP,
    build_rows,
    group_breakdown,
)


OUT_PATH = (
    Path(__file__).resolve().parents[1] / "visuals" / "126_ie_test.png"
)


def main() -> None:
    rows = build_rows(18)
    n = len(rows)
    syms = [r.symbol for r in rows]
    meas    = np.array([r.measured_eV         for r in rows])
    pred_sl = np.array([r.pred_slater_eV      for r in rows])
    pred_kr = np.array([r.pred_krank_eV       for r in rows])
    pred_hf = np.array([r.pred_HF_eV          for r in rows])
    pred_ca = np.array([r.pred_calibrated_eV  for r in rows])
    err_sl  = np.array([r.err_slater_pct      for r in rows])
    err_kr  = np.array([r.err_krank_pct       for r in rows])
    err_hf  = np.array([r.err_HF_pct          for r in rows])
    err_ca  = np.array([max(r.err_calibrated_pct, 1e-4) for r in rows])

    fig = plt.figure(figsize=(20.0, 7.5))
    gs = fig.add_gridspec(1, 3, width_ratios=[2.5, 2.5, 1.6])
    ax_bar = fig.add_subplot(gs[0, 0])
    ax_err = fig.add_subplot(gs[0, 1])
    ax_grp = fig.add_subplot(gs[0, 2])

    x = np.arange(n)

    # ------------------- left: predicted vs measured (4 lines) ----------- #
    ax_bar.semilogy(x, meas,    "k-",  marker="o", label="NIST measured",
                    linewidth=2.5, markersize=8)
    ax_bar.semilogy(x, pred_sl, "-",   marker="^", color="#d62728",
                    label=f"Slater bare (0 knobs)\n  mean = {np.mean(err_sl):.0f}%",
                    linewidth=1.5, markersize=7, alpha=0.85)
    ax_bar.semilogy(x, pred_kr, "-",   marker="s", color="#9467bd",
                    label=(f"K_rank substrate (0 knobs)\n  "
                           f"sigma_pp={SIGMA_PP:.2f}, sigma_sp={SIGMA_SP:.2f}\n  "
                           f"mean = {np.mean(err_kr):.1f}%"),
                    linewidth=1.5, markersize=6, alpha=0.85)
    ax_bar.semilogy(x, pred_hf, "-",   marker="D", color="#2ca02c",
                    label=(f"Substrate-HF (Roothaan-HF + Koopmans, 0 knobs)\n  "
                           f"Clementi-Roetti 1974 orbitals\n  "
                           f"mean = {np.mean(err_hf):.2f}%"),
                    linewidth=1.5, markersize=6, alpha=0.9)
    ax_bar.semilogy(x, pred_ca, "-",   marker="x", color="#1f77b4",
                    label=(f"Per-element calibrated (1 knob/element)\n  "
                           f"mean = {np.mean(err_ca):.4f}%"),
                    linewidth=1.0, markersize=6)
    ax_bar.set_ylabel(r"first ionization energy [eV] (log)")
    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(syms, fontsize=10)
    ax_bar.set_title(
        "Substrate Schroedinger first ionization energy: H .. Ar\n"
        "Four screening models -- four data lines + NIST measured"
    )
    ax_bar.legend(loc="upper left", fontsize=7.5, framealpha=0.9)
    ax_bar.grid(True, axis="y", which="both", alpha=0.3)
    for boundary in (4.5, 12.5):    # s/p subshell boundaries
        ax_bar.axvline(boundary, color="grey", linestyle=":", alpha=0.5)

    # ------------------- centre: % residual (4 lines) -------------------- #
    ax_err.semilogy(x, err_sl, "^-", color="#d62728",
                    label=f"Slater (0-knob): mean {np.mean(err_sl):.0f}%, max {np.max(err_sl):.0f}%",
                    markersize=7)
    ax_err.semilogy(x, err_kr, "s-", color="#9467bd",
                    label=f"K_rank substrate (0-knob): mean {np.mean(err_kr):.1f}%, max {np.max(err_kr):.1f}%",
                    markersize=6)
    ax_err.semilogy(x, err_hf, "D-", color="#2ca02c",
                    label=f"Substrate-HF Koopmans (0-knob): mean {np.mean(err_hf):.2f}%, max {np.max(err_hf):.1f}%",
                    markersize=6)
    ax_err.semilogy(x, err_ca, "x-", color="#1f77b4",
                    label=f"Calibrated (1-knob): mean {np.mean(err_ca):.4f}%",
                    markersize=6)
    ax_err.axhline(2.0,   color="darkblue",  linestyle="--", alpha=0.6,
                   label="2% (target)")
    ax_err.axhline(5.0,   color="green",  linestyle="--", alpha=0.5,
                   label="5% (publishable)")
    ax_err.axhline(100.0, color="orange", linestyle="--", alpha=0.5,
                   label="100% (factor-of-2)")
    ax_err.set_ylabel(r"|predicted - measured| / measured  [%]  (log)")
    ax_err.set_xticks(x)
    ax_err.set_xticklabels(syms, fontsize=10)
    ax_err.set_ylim(1e-4, 1e3)
    ax_err.set_title(
        "Per-element % residual (4 models)\n"
        "Calibrated < Substrate-HF < K_rank < Slater  (clear method ranking)"
    )
    ax_err.legend(loc="upper right", fontsize=7.5, framealpha=0.9)
    ax_err.grid(True, axis="y", which="both", alpha=0.3)
    for boundary in (4.5, 12.5):
        ax_err.axvline(boundary, color="grey", linestyle=":", alpha=0.5)

    # ------------------- right: group breakdown (4-bar) ------------------ #
    bd_sl = group_breakdown(rows, "err_slater_pct")
    bd_kr = group_breakdown(rows, "err_krank_pct")
    bd_hf = group_breakdown(rows, "err_HF_pct")
    bd_ca = group_breakdown(rows, "err_calibrated_pct")
    group_order = ["row1_s", "row2_s", "row2_p", "row3_s", "row3_p"]
    pretty = {
        "row1_s": "row1\n(s)",
        "row2_s": "row2\n(s)",
        "row2_p": "row2\n(p)",
        "row3_s": "row3\n(s)",
        "row3_p": "row3\n(p)",
    }
    means_sl = [bd_sl[g]["mean_pct"] for g in group_order]
    means_kr = [bd_kr[g]["mean_pct"] for g in group_order]
    means_hf = [bd_hf[g]["mean_pct"] for g in group_order]
    means_ca = [max(bd_ca[g]["mean_pct"], 1e-4) for g in group_order]
    xg = np.arange(len(group_order))
    wg = 0.20
    ax_grp.bar(xg - 1.5 * wg, means_sl, wg, color="#d62728", alpha=0.9,
               label="Slater (0)")
    ax_grp.bar(xg - 0.5 * wg, means_kr, wg, color="#9467bd", alpha=0.9,
               label="K_rank (0)")
    ax_grp.bar(xg + 0.5 * wg, means_hf, wg, color="#2ca02c", alpha=0.9,
               label="HF Koop. (0)")
    ax_grp.bar(xg + 1.5 * wg, means_ca, wg, color="#1f77b4", alpha=0.9,
               label="Calib. (1)")
    ax_grp.set_yscale("log")
    ax_grp.set_xticks(xg)
    ax_grp.set_xticklabels([pretty[g] for g in group_order], fontsize=9)
    ax_grp.set_ylabel("mean abs % error (log)")
    ax_grp.set_title(
        "Group breakdown\n"
        "K_rank knocks down p-shell error;\nHF further reduces it"
    )
    ax_grp.legend(loc="upper left", fontsize=7.5, framealpha=0.9)
    ax_grp.grid(True, axis="y", which="both", alpha=0.3)

    fig.tight_layout()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PATH, dpi=150)
    print(f"saved {OUT_PATH}")


if __name__ == "__main__":
    main()
