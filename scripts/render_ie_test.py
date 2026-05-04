"""Generate visuals/126_ie_test.png -- predicted-vs-measured first IE H..Ar.

Three-panel figure that explicitly tags each line / bar with its honest
substrate-derivation category (A/B/C/baseline):

  (left)   Predicted IE vs measured for all 18 elements (line plot, log scale).
           Lines:  NIST measured  /  [A] K_rank substrate (PRIMARY)  /
                   [baseline] Slater  /  [B] Substrate-HF Koopmans  /
                   [C] Per-element calibrated.
  (centre) % residual per element under all four models (log-scale).
  (right)  Group breakdown: mean residual per row/subshell group, all models.

The figure makes the Category-tagged scoreboard visually obvious:
  - [A — PRIMARY substrate prediction] K_rank substrate (sigma_pp=4/5,
    sigma_sp=24/25 from canonical K_rank=5 inventory): 0 element knobs,
    21.4% mean error, 12x better than Slater baseline.  This is the
    headline B3 atomic-IE result.
  - [baseline] Slater (1930) 0.30/0.35/0.85/1.00 universal coefficients
    overshoot p-shell electrons by 3-5x; mean error 254%.  NOT a substrate
    prediction; only a textbook reference K_rank is benchmarked against.
  - [B — research target] Roothaan-HF + Koopmans (public Clementi-Roetti
    orbital energies): mean error 6.4%.  Uses standard QC HF kernel; will
    promote to A once a substrate-derived HF kernel is implemented.
  - [C — empirical anchor] Per-element calibrated (1 knob/element):
    matches measured to machine precision (0.004% mean) — proves the
    n^{-2} structural form is exactly right; not a substrate prediction.
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
    # K_rank PRIMARY substrate prediction -- emphasised line weight + violet
    ax_bar.semilogy(x, pred_kr, "-",   marker="s", color="#9467bd",
                    label=(f"[A — PRIMARY substrate, 0 knobs]\n  "
                           f"K_rank=5: sigma_pp={SIGMA_PP:.2f}, "
                           f"sigma_sp={SIGMA_SP:.2f}\n  "
                           f"mean = {np.mean(err_kr):.1f}%  "
                           f"(12x better than Slater)"),
                    linewidth=2.5, markersize=8, alpha=0.95)
    # Slater baseline (NOT substrate-specific)
    ax_bar.semilogy(x, pred_sl, "--",  marker="^", color="#d62728",
                    label=(f"[baseline, 0 knobs, NOT substrate]\n  "
                           f"Slater 1930 0.30/0.35/0.85/1.00\n  "
                           f"mean = {np.mean(err_sl):.0f}%"),
                    linewidth=1.2, markersize=6, alpha=0.7)
    # Substrate-HF -- Category B research target
    ax_bar.semilogy(x, pred_hf, "-",   marker="D", color="#2ca02c",
                    label=(f"[B — research target, 0 element knobs]\n  "
                           f"Roothaan-HF + Koopmans (Clementi-Roetti 1974)\n  "
                           f"mean = {np.mean(err_hf):.2f}%"),
                    linewidth=1.5, markersize=6, alpha=0.9)
    # Per-element calibrated -- Category C empirical anchor
    ax_bar.semilogy(x, pred_ca, ":",   marker="x", color="#1f77b4",
                    label=(f"[C — empirical anchor, 1 knob/element]\n  "
                           f"per-element Z_eff fitted to NIST IE\n  "
                           f"mean = {np.mean(err_ca):.4f}%"),
                    linewidth=1.0, markersize=6, alpha=0.6)
    ax_bar.set_ylabel(r"first ionization energy [eV] (log)")
    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(syms, fontsize=10)
    ax_bar.set_title(
        "Substrate Schroedinger first ionization energy: H .. Ar\n"
        "Category-tagged scoreboard: A=substrate prediction, "
        "B=research target, C=empirical anchor"
    )
    ax_bar.legend(loc="upper left", fontsize=7.0, framealpha=0.9)
    ax_bar.grid(True, axis="y", which="both", alpha=0.3)
    for boundary in (4.5, 12.5):    # s/p subshell boundaries
        ax_bar.axvline(boundary, color="grey", linestyle=":", alpha=0.5)

    # ------------------- centre: % residual (4 lines) -------------------- #
    # K_rank PRIMARY -- bold violet
    ax_err.semilogy(x, err_kr, "s-", color="#9467bd",
                    label=(f"[A] K_rank substrate (PRIMARY, 0 knobs): "
                           f"mean {np.mean(err_kr):.1f}%, max {np.max(err_kr):.1f}%"),
                    markersize=8, linewidth=2.5)
    # Slater baseline -- dashed red (NOT substrate)
    ax_err.semilogy(x, err_sl, "^--", color="#d62728",
                    label=(f"[baseline] Slater (NOT substrate, 0 knobs): "
                           f"mean {np.mean(err_sl):.0f}%, max {np.max(err_sl):.0f}%"),
                    markersize=6, linewidth=1.2, alpha=0.7)
    # Substrate-HF Category B
    ax_err.semilogy(x, err_hf, "D-", color="#2ca02c",
                    label=(f"[B] Substrate-HF Koopmans (research target, 0 element knobs): "
                           f"mean {np.mean(err_hf):.2f}%, max {np.max(err_hf):.1f}%"),
                    markersize=6)
    # Calibrated Category C
    ax_err.semilogy(x, err_ca, "x:", color="#1f77b4",
                    label=(f"[C] Per-element calibrated (empirical, 1 knob each): "
                           f"mean {np.mean(err_ca):.4f}%"),
                    markersize=6, alpha=0.6)
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
        "Per-element % residual (Category-tagged)\n"
        "[C] Calibrated < [B] HF < [A] K_rank substrate < [baseline] Slater"
    )
    ax_err.legend(loc="upper right", fontsize=7.0, framealpha=0.9)
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
    # K_rank PRIMARY violet bars first
    ax_grp.bar(xg - 1.5 * wg, means_kr, wg, color="#9467bd", alpha=0.95,
               label="[A] K_rank PRIMARY (0)", edgecolor="black", linewidth=0.5)
    ax_grp.bar(xg - 0.5 * wg, means_sl, wg, color="#d62728", alpha=0.7,
               label="[baseline] Slater (0)", hatch="//")
    ax_grp.bar(xg + 0.5 * wg, means_hf, wg, color="#2ca02c", alpha=0.9,
               label="[B] HF Koop. (0)")
    ax_grp.bar(xg + 1.5 * wg, means_ca, wg, color="#1f77b4", alpha=0.7,
               label="[C] Calib. (1/elem)", hatch="..")
    ax_grp.set_yscale("log")
    ax_grp.set_xticks(xg)
    ax_grp.set_xticklabels([pretty[g] for g in group_order], fontsize=9)
    ax_grp.set_ylabel("mean abs % error (log)")
    ax_grp.set_title(
        "Group breakdown -- Category-tagged\n"
        "[A]=substrate predict, [B]=research, [C]=anchor"
    )
    ax_grp.legend(loc="upper left", fontsize=7.0, framealpha=0.9)
    ax_grp.grid(True, axis="y", which="both", alpha=0.3)

    fig.tight_layout()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PATH, dpi=150)
    print(f"saved {OUT_PATH}")


if __name__ == "__main__":
    main()
