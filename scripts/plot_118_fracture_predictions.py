"""Generate visuals/118_fracture_predictions.png.

Two-panel figure:
  (left)  bar chart of r_p across all 12 materials for the four formulas;
  (right) scatter plot substrate vs Irwin plane-stress with annotated ratios
          to plane-strain and Dugdale.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.stiff_medium.fracture_substrate_test import MATERIALS, run_test


OUT_PATH = Path(__file__).resolve().parents[1] / "visuals" / "118_fracture_predictions.png"


def main() -> None:
    res = run_test()
    rows = res["rows"]
    names = list(rows.keys())
    sub = np.array([rows[n]["substrate_m"] for n in names]) * 1.0e6  # to um
    ips = np.array([rows[n]["irwin_ps_m"] for n in names]) * 1.0e6
    ipe = np.array([rows[n]["irwin_pe_m"] for n in names]) * 1.0e6
    dug = np.array([rows[n]["dugdale_m"] for n in names]) * 1.0e6

    fig, (ax_bar, ax_sc) = plt.subplots(
        1, 2, figsize=(16.0, 7.0), gridspec_kw={"width_ratios": [2.0, 1.0]}
    )

    # ---------- left: bar chart ---------- #
    x = np.arange(len(names))
    w = 0.20
    ax_bar.bar(x - 1.5 * w, sub, w, label="Substrate", color="#1f77b4")
    ax_bar.bar(x - 0.5 * w, ips, w, label="Irwin plane stress",
               color="#ff7f0e", alpha=0.65, edgecolor="black", linewidth=0.4)
    ax_bar.bar(x + 0.5 * w, ipe, w, label="Irwin plane strain",
               color="#2ca02c")
    ax_bar.bar(x + 1.5 * w, dug, w, label="Dugdale", color="#d62728")
    ax_bar.set_yscale("log")
    ax_bar.set_ylabel(r"plastic-zone radius $r_p$ [$\mu$m]  (log)")
    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(names, rotation=40, ha="right", fontsize=9)
    ax_bar.set_title(
        "Predicted crack-tip plastic-zone radius across 12 materials\n"
        "Substrate prediction overlaps Irwin plane-stress to machine "
        "precision"
    )
    ax_bar.legend(loc="upper left", fontsize=9)
    ax_bar.grid(True, axis="y", alpha=0.3, which="both")

    # ---------- right: scatter ---------- #
    ax_sc.loglog(ips, sub, "o", color="#1f77b4", markersize=8,
                 label="substrate vs Irwin PS  (slope 1)")
    lim = [min(min(sub), min(ips)) * 0.5, max(max(sub), max(ips)) * 2.0]
    ax_sc.plot(lim, lim, "k--", alpha=0.6, label="y = x")
    ax_sc.plot(lim, [v / 3.0 for v in lim], "g:", alpha=0.6,
               label="Irwin plane strain (sub/3)")
    ax_sc.plot(lim, [v * (np.pi ** 2) / 4.0 for v in lim], "r:", alpha=0.6,
               label=r"Dugdale ($\pi^2/4 \times$ sub)")
    ax_sc.set_xlim(lim)
    ax_sc.set_ylim(lim)
    ax_sc.set_xlabel(r"Irwin plane-stress $r_p$  [$\mu$m]")
    ax_sc.set_ylabel(r"Substrate $r_p$  [$\mu$m]")
    ax_sc.set_aspect("equal", "box")
    ax_sc.set_title(
        "Substrate vs standard formulas\n"
        f"ratio sub/IrwinPS = {res['ratios']['substrate_over_irwin_ps']:.3f}, "
        f"sub/IrwinPE = {res['ratios']['substrate_over_irwin_pe']:.3f}, "
        f"sub/Dugdale = {res['ratios']['substrate_over_dugdale']:.3f}"
    )
    ax_sc.legend(loc="lower right", fontsize=8)
    ax_sc.grid(True, which="both", alpha=0.3)

    fig.tight_layout()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PATH, dpi=150)
    print(f"saved {OUT_PATH}")


if __name__ == "__main__":
    main()
