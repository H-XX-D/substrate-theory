"""Generate visuals/123_bbn_test.png.

Three-panel figure:
  (top)    bar chart of n-σ deviation per primordial-abundance observable
           (Y_p, D/H, ³He/H, ⁷Li/H) with substrate predictions vs PDG/Planck.
  (middle) abundances vs baryon-to-photon ratio η, with Planck-fixed η band
           and observed central values.
  (bottom) Li-7 puzzle resolution: SBBN vs substrate-suppressed prediction
           against the Spite-plateau observation, with substrate suppression
           factor as the only knob.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.stiff_medium.bbn_test import (
    OBS_D_H_X1E5_CENTRAL,
    OBS_D_H_X1E5_SIGMA,
    OBS_HE3_H_X1E5_CENTRAL,
    OBS_HE3_H_X1E5_SIGMA,
    OBS_LI7_H_X1E10_CENTRAL,
    OBS_LI7_H_X1E10_SIGMA,
    OBS_Y_P_CENTRAL,
    OBS_Y_P_SIGMA,
    run_bbn_test,
    scan_eta,
)

OUT_PATH = Path(__file__).resolve().parents[1] / "visuals" / "123_bbn_test.png"

ETA_PLANCK = 6.10e-10


def main() -> None:
    res = run_bbn_test()
    scan = scan_eta(eta_min=2.0e-10, eta_max=1.5e-9, n_pts=80)

    fig = plt.figure(figsize=(13.0, 13.0))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.0, 1.6, 1.0], hspace=0.42)

    # ---------------- Panel A: n-σ bars ---------------- #
    ax_a = fig.add_subplot(gs[0, 0])
    keys = ["Y_p", "D/H", "He-3/H", "Li-7/H"]
    nice = [r"$Y_p$  (⁴He)", r"$D/H$", r"$^3$He$/H$", r"$^7$Li$/H$  (substrate-suppressed)"]
    nsig = [res.rows[k].n_sigma for k in keys]

    # Add an extra bar for SBBN ⁷Li (no suppression)
    nsig_sbbn_li7 = res.li7_sbbn_n_sigma

    x = np.arange(len(keys) + 1)
    bar_labels = nice + [r"$^7$Li$/H$  (SBBN, no substrate)"]
    bar_values = nsig + [nsig_sbbn_li7]

    colors = ["#2ca02c" if v <= 2.0 else "#d62728" for v in bar_values]
    ax_a.bar(x, bar_values, color=colors, edgecolor="black", linewidth=0.6)

    ax_a.axhline(2.0, color="black", linestyle="--", alpha=0.7, label="2σ threshold")
    ax_a.axhline(5.0, color="gray", linestyle=":", alpha=0.6, label="5σ")

    for i, v in enumerate(bar_values):
        ax_a.text(i, v + 0.15, f"{v:.2f}σ", ha="center", fontsize=9, fontweight="bold")

    ax_a.set_xticks(x)
    ax_a.set_xticklabels(bar_labels, rotation=12, ha="right", fontsize=9)
    ax_a.set_ylabel("|prediction − observation| / σ", fontsize=10)
    ax_a.set_ylim(0, max(bar_values) * 1.18 + 0.5)
    ax_a.set_title(
        "Substrate BBN predictions vs PDG 2024 / Planck 2018\n"
        f"Verdict: {res.verdict}",
        fontsize=11,
    )
    ax_a.legend(loc="upper left", fontsize=8)
    ax_a.grid(True, axis="y", alpha=0.3)

    # ---------------- Panel B: abundances vs η ---------------- #
    ax_b = fig.add_subplot(gs[1, 0])

    # Twin axes — Y_p on a separate scale (it's roughly constant ~0.247)
    eta_arr = np.array(scan.eta_grid)

    # Plot D/H, ³He/H, ⁷Li/H_SBBN, ⁷Li/H_substrate on one log axis
    ax_b.loglog(eta_arr, np.array(scan.D_H_x1e5),
                color="#1f77b4", linewidth=2.0, label=r"D/H $\times 10^5$")
    ax_b.loglog(eta_arr, np.array(scan.He3_H_x1e5),
                color="#ff7f0e", linewidth=2.0, label=r"$^3$He/H $\times 10^5$")
    ax_b.loglog(eta_arr, np.array(scan.Li7_H_x1e10_sbbn),
                color="#d62728", linewidth=2.0, linestyle="--",
                label=r"$^7$Li/H $\times 10^{10}$ (SBBN, no substrate)")
    ax_b.loglog(eta_arr, np.array(scan.Li7_H_x1e10_sub),
                color="#2ca02c", linewidth=2.5,
                label=r"$^7$Li/H $\times 10^{10}$ (substrate-suppressed ÷3)")

    # Observed bands at Planck η
    eb_x = ETA_PLANCK
    ax_b.errorbar(eb_x, OBS_D_H_X1E5_CENTRAL, yerr=OBS_D_H_X1E5_SIGMA,
                  color="#1f77b4", marker="s", markersize=8, capsize=4,
                  label=None)
    ax_b.errorbar(eb_x * 0.92, OBS_HE3_H_X1E5_CENTRAL, yerr=OBS_HE3_H_X1E5_SIGMA,
                  color="#ff7f0e", marker="s", markersize=8, capsize=4,
                  label=None)
    ax_b.errorbar(eb_x * 1.08, OBS_LI7_H_X1E10_CENTRAL, yerr=OBS_LI7_H_X1E10_SIGMA,
                  color="#2ca02c", marker="s", markersize=8, capsize=4,
                  label=None)

    # Planck-fixed η vertical band
    ax_b.axvspan(ETA_PLANCK * 0.997, ETA_PLANCK * 1.003,
                 color="gray", alpha=0.25,
                 label=r"$\eta_\mathrm{Planck} = 6.10\times10^{-10}$")
    ax_b.axvline(ETA_PLANCK, color="gray", linestyle=":", alpha=0.7)

    # Annotate squares = observed
    ax_b.plot([], [], "ks", markersize=8, label="observed (1σ bars)")

    ax_b.set_xlabel(r"baryon-to-photon ratio $\eta = n_B/n_\gamma$", fontsize=10)
    ax_b.set_ylabel("primordial abundance (scaled)", fontsize=10)
    ax_b.set_title(
        "Light-element abundances vs $\\eta$  (substrate inherits SBBN η-fits)",
        fontsize=11,
    )
    ax_b.legend(loc="lower left", fontsize=8.5, framealpha=0.92, ncol=1)
    ax_b.grid(True, which="both", alpha=0.3)

    # ---------------- Panel C: Li-7 puzzle ---------------- #
    ax_c = fig.add_subplot(gs[2, 0])

    sbbn_val = res.li7_sbbn_prediction_x1e10
    sub_val = res.li7_substrate_prediction_x1e10
    obs_val = OBS_LI7_H_X1E10_CENTRAL
    obs_sig = OBS_LI7_H_X1E10_SIGMA

    # Sweep substrate suppression factor
    sup_grid = np.linspace(1.0, 6.0, 80)
    li7_sweep = sbbn_val / sup_grid

    ax_c.plot(sup_grid, li7_sweep, color="#1f77b4", linewidth=2.5,
              label="substrate-suppressed ⁷Li/H")
    ax_c.axhline(obs_val, color="#2ca02c", linewidth=2,
                 label=f"observed Spite plateau = {obs_val} × 10⁻¹⁰")
    ax_c.fill_between(sup_grid, obs_val - obs_sig, obs_val + obs_sig,
                      color="#2ca02c", alpha=0.20, label="observed 1σ")
    ax_c.fill_between(sup_grid, obs_val - 2 * obs_sig, obs_val + 2 * obs_sig,
                      color="#2ca02c", alpha=0.10, label="observed 2σ")

    ax_c.axhline(sbbn_val, color="#d62728", linestyle="--",
                 label=f"SBBN (no substrate) = {sbbn_val:.2f} × 10⁻¹⁰")
    ax_c.axvline(3.0, color="black", linestyle=":", alpha=0.7,
                 label="default substrate suppression = 3")
    ax_c.scatter([3.0], [sub_val], s=120, color="black", zorder=10,
                 label=f"substrate ({sub_val:.2f} × 10⁻¹⁰, "
                       f"{res.li7_substrate_n_sigma:.2f}σ)")

    ax_c.set_xlabel("substrate Be-7 destruction factor (§18.66 proto-matter)",
                    fontsize=10)
    ax_c.set_ylabel(r"$^7$Li$/H \times 10^{10}$", fontsize=10)
    ax_c.set_title(
        f"Lithium-7 puzzle: SBBN over-predicts by "
        f"{sbbn_val / obs_val:.1f}× ({res.li7_sbbn_n_sigma:.1f}σ); "
        f"substrate ÷3 brings it to {res.li7_substrate_n_sigma:.2f}σ",
        fontsize=11,
    )
    ax_c.set_ylim(0, sbbn_val * 1.15)
    ax_c.set_xlim(1.0, 6.0)
    ax_c.legend(loc="upper right", fontsize=8.5, framealpha=0.95)
    ax_c.grid(True, alpha=0.3)

    fig.suptitle(
        "BBN test (visuals/123): substrate primordial-abundance predictions",
        fontsize=13, y=0.995,
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PATH, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {OUT_PATH}")


if __name__ == "__main__":
    main()
