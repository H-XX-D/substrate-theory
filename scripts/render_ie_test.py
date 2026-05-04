"""Generate visuals/126_ie_test.png -- predicted-vs-measured first IE H..Ar.

Three-panel figure:
  (left)   Bar chart: measured vs Slater (zero-knob) vs Calibrated (one-knob)
           IE for all 18 elements H..Ar.
  (centre) % residual per element under both modes (log-scale).
  (right)  Group breakdown: mean residual per row/subshell group (Slater).

The figure makes the verdict visually obvious:
  - calibrated bars match measured to machine precision (n^{-2} form is right)
  - Slater bars track measured for s-shell (H..Be, Na..Mg) but blow up by
    3-5x for p-shell electrons (B..Ne, Al..Ar)
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.stiff_medium.ionization_energy_test import build_rows, group_breakdown


OUT_PATH = (
    Path(__file__).resolve().parents[1] / "visuals" / "126_ie_test.png"
)


def main() -> None:
    rows = build_rows(18)
    n = len(rows)
    syms = [r.symbol for r in rows]
    Z = [r.Z for r in rows]
    meas = np.array([r.measured_eV for r in rows])
    pred_sl = np.array([r.pred_slater_eV for r in rows])
    pred_ca = np.array([r.pred_calibrated_eV for r in rows])
    err_sl = np.array([r.err_slater_pct for r in rows])
    err_ca = np.array([max(r.err_calibrated_pct, 1e-4) for r in rows])

    fig = plt.figure(figsize=(18.0, 7.0))
    gs = fig.add_gridspec(1, 3, width_ratios=[2.5, 2.0, 1.4])
    ax_bar = fig.add_subplot(gs[0, 0])
    ax_err = fig.add_subplot(gs[0, 1])
    ax_grp = fig.add_subplot(gs[0, 2])

    # ------------------- left: predicted vs measured -------------------- #
    x = np.arange(n)
    w = 0.27
    ax_bar.bar(x - w, meas,    w, label="Measured (NIST)",
               color="#222222")
    ax_bar.bar(x,     pred_ca, w, label="Substrate Schroedinger\n(calibrated Z_eff, 1 knob/element)",
               color="#1f77b4")
    ax_bar.bar(x + w, pred_sl, w, label="Substrate Schroedinger\n(Slater rules, 0 knobs)",
               color="#d62728", alpha=0.8)
    ax_bar.set_yscale("log")
    ax_bar.set_ylabel(r"first ionization energy [eV] (log)")
    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(syms, fontsize=10)
    ax_bar.set_title(
        "Substrate Schroedinger first ionization energy: H .. Ar\n"
        "calibrated form matches NIST exactly; zero-knob Slater overshoots p-shell"
    )
    ax_bar.legend(loc="upper left", fontsize=8.5)
    ax_bar.grid(True, axis="y", which="both", alpha=0.3)

    # mark the s/p subshell boundary
    for boundary in (4.5, 12.5):    # between Be/B and Mg/Al (0-indexed)
        ax_bar.axvline(boundary, color="grey", linestyle=":", alpha=0.5)

    # ------------------- centre: % residual ----------------------------- #
    ax_err.semilogy(
        x, err_sl, "o-", color="#d62728",
        label="Slater (0-knob): mean = "
              f"{np.mean(err_sl):.0f}%, max = {np.max(err_sl):.0f}%",
        markersize=8,
    )
    ax_err.semilogy(
        x, err_ca, "s-", color="#1f77b4",
        label=f"Calibrated (1-knob): mean = {np.mean(err_ca):.4f}%",
        markersize=6,
    )
    ax_err.axhline(5.0,   color="green",  linestyle="--", alpha=0.6,
                   label="5% (publishable agreement threshold)")
    ax_err.axhline(100.0, color="orange", linestyle="--", alpha=0.6,
                   label="100% (factor-of-2 wrong)")
    ax_err.set_ylabel(r"|predicted - measured| / measured  [%]  (log)")
    ax_err.set_xticks(x)
    ax_err.set_xticklabels(syms, fontsize=10)
    ax_err.set_ylim(1e-4, 1e3)
    ax_err.set_title(
        "Per-element % residual\n"
        "(zero-knob substrate Schroedinger fails for p-shell electrons)"
    )
    ax_err.legend(loc="upper left", fontsize=8.5)
    ax_err.grid(True, axis="y", which="both", alpha=0.3)
    for boundary in (4.5, 12.5):
        ax_err.axvline(boundary, color="grey", linestyle=":", alpha=0.5)

    # ------------------- right: group breakdown ------------------------- #
    bd_sl = group_breakdown(rows, "err_slater_pct")
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
    means_ca = [bd_ca[g]["mean_pct"] for g in group_order]
    xg = np.arange(len(group_order))
    wg = 0.4
    ax_grp.bar(xg - wg / 2.0, means_sl, wg, color="#d62728",
               alpha=0.85, label="Slater (0-knob)")
    ax_grp.bar(xg + wg / 2.0, np.maximum(means_ca, 1e-4), wg,
               color="#1f77b4", label="Calibrated (1-knob)")
    ax_grp.set_yscale("log")
    ax_grp.set_xticks(xg)
    ax_grp.set_xticklabels([pretty[g] for g in group_order], fontsize=9)
    ax_grp.set_ylabel("mean abs % error (log)")
    ax_grp.set_title("Group breakdown\n(s-shells fit; p-shells fail in 0-knob)")
    ax_grp.legend(loc="upper left", fontsize=8)
    ax_grp.grid(True, axis="y", which="both", alpha=0.3)

    fig.tight_layout()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PATH, dpi=150)
    print(f"saved {OUT_PATH}")


if __name__ == "__main__":
    main()
