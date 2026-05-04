"""Generate visuals/133_pantheon_test.png.

Three-panel figure for the Pantheon+ supernova H_0 test:

  (top)    Hubble diagram: distance modulus mu(z) overlay of substrate
           (H_0 = 71.92), SH0ES + Pantheon+ best fit (H_0 = 73.04), and
           Planck (H_0 = 67.40), with the binned Pantheon+ central values
           plotted as data points with 1-sigma error bars.

  (middle) Residual plot: mu_obs - mu_model per bin, for substrate, SH0ES,
           and Planck, with the 1-sigma scatter band overlaid.  Visualises
           which model best fits the binned Pantheon+ Hubble diagram.

  (bottom) H_0 sigma-distance bar chart: substrate prediction overlaid on
           SH0ES, Pantheon+ alone, Planck, with 1-sigma bars and the
           Hubble tension band shaded.  Annotates n-sigma to each anchor.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.stiff_medium.pantheon_test import (
    OMEGA_M_PANTHEON,
    OMEGA_M_PLANCK,
    OMEGA_M_SHOES,
    PANTHEON_ALONE_H0,
    PANTHEON_ALONE_SIGMA,
    PANTHEON_BINNED,
    PLANCK_H0,
    PLANCK_SIGMA,
    SHOES_PANTHEON_H0,
    SHOES_PANTHEON_SIGMA,
    SUBSTRATE_H0,
    SUBSTRATE_H0_SIGMA,
    distance_modulus,
    run_pantheon_test,
)

OUT_PATH = Path(__file__).resolve().parents[1] / "visuals" / "133_pantheon_test.png"


def main() -> None:
    res = run_pantheon_test()

    fig = plt.figure(figsize=(12.5, 14.0))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.4, 1.0, 1.0], hspace=0.40)

    # ---------------- Panel A: Hubble diagram ---------------- #
    ax_a = fig.add_subplot(gs[0, 0])

    z_grid = np.logspace(np.log10(0.01), np.log10(1.6), 200)
    mu_sub = np.array([distance_modulus(z, SUBSTRATE_H0, OMEGA_M_PANTHEON) for z in z_grid])
    mu_shoes = np.array([distance_modulus(z, SHOES_PANTHEON_H0, OMEGA_M_SHOES) for z in z_grid])
    mu_planck = np.array([distance_modulus(z, PLANCK_H0, OMEGA_M_PLANCK) for z in z_grid])

    ax_a.plot(z_grid, mu_sub, color="#1f77b4", linewidth=2.5,
              label=f"substrate  H$_0$ = {SUBSTRATE_H0} km/s/Mpc")
    ax_a.plot(z_grid, mu_shoes, color="#d62728", linewidth=2.0, linestyle="--",
              label=f"SH0ES + Pantheon+  H$_0$ = {SHOES_PANTHEON_H0}")
    ax_a.plot(z_grid, mu_planck, color="#2ca02c", linewidth=2.0, linestyle=":",
              label=f"Planck  H$_0$ = {PLANCK_H0}")

    z_pts = np.array([b[0] for b in PANTHEON_BINNED])
    mu_pts = np.array([b[1] for b in PANTHEON_BINNED])
    sig_pts = np.array([b[2] for b in PANTHEON_BINNED])
    ax_a.errorbar(z_pts, mu_pts, yerr=sig_pts, fmt="ko", markersize=6,
                  capsize=4, linewidth=1.0, elinewidth=1.2,
                  label="Pantheon+ binned mu (Brout+2022)", zorder=10)

    ax_a.set_xscale("log")
    ax_a.set_xlabel(r"redshift $z$", fontsize=11)
    ax_a.set_ylabel(r"distance modulus $\mu = m - M$  [mag]", fontsize=11)
    ax_a.set_title(
        "Pantheon+ Hubble diagram: substrate H$_0$ = 71.92 km/s/Mpc vs SH0ES, Planck",
        fontsize=12,
    )
    ax_a.legend(loc="lower right", fontsize=9.5, framealpha=0.95)
    ax_a.grid(True, which="both", alpha=0.3)
    ax_a.set_xlim(0.012, 1.7)

    # ---------------- Panel B: Residuals vs z ---------------- #
    ax_b = fig.add_subplot(gs[1, 0])

    res_sub = np.array([r.residual_substrate for r in res.residuals])
    res_shoes = np.array([r.residual_shoes for r in res.residuals])
    res_planck = np.array([r.residual_planck for r in res.residuals])
    sigma_arr = np.array([r.sigma_mu for r in res.residuals])

    ax_b.errorbar(z_pts, res_sub, yerr=sigma_arr, fmt="o", color="#1f77b4",
                  markersize=7, capsize=3, linewidth=1.5,
                  label=f"substrate  $\\chi^2/N$ = {res.chi2_substrate / res.n_bins:.3f}")
    ax_b.plot(z_pts, res_shoes, "s--", color="#d62728", markersize=6,
              linewidth=1.5, alpha=0.85,
              label=f"SH0ES  $\\chi^2/N$ = {res.chi2_shoes / res.n_bins:.3f}")
    ax_b.plot(z_pts, res_planck, "^:", color="#2ca02c", markersize=6,
              linewidth=1.5, alpha=0.85,
              label=f"Planck  $\\chi^2/N$ = {res.chi2_planck / res.n_bins:.3f}")

    ax_b.axhline(0.0, color="black", linewidth=0.7, alpha=0.6)
    ax_b.fill_between(z_pts, -sigma_arr, sigma_arr, color="gray", alpha=0.15,
                      label=r"$\pm 1\sigma$ SN scatter band")

    ax_b.set_xscale("log")
    ax_b.set_xlabel(r"redshift $z$", fontsize=11)
    ax_b.set_ylabel(r"$\mu_\mathrm{obs} - \mu_\mathrm{model}$  [mag]", fontsize=11)
    ax_b.set_title(
        "Distance-modulus residuals vs Pantheon+ binned mu (best-fit central)",
        fontsize=12,
    )
    ax_b.legend(loc="upper right", fontsize=9.5, framealpha=0.95)
    ax_b.grid(True, which="both", alpha=0.3)
    ax_b.set_xlim(0.012, 1.7)
    y_max = max(0.30, max(np.max(np.abs(res_planck)), np.max(np.abs(res_sub) + sigma_arr)) * 1.1)
    ax_b.set_ylim(-y_max, y_max)

    # ---------------- Panel C: H_0 anchor comparison ---------------- #
    ax_c = fig.add_subplot(gs[2, 0])

    anchors = [
        ("SH0ES + Pantheon+\n(Riess+2022)", SHOES_PANTHEON_H0, SHOES_PANTHEON_SIGMA, "#d62728", "late"),
        ("Pantheon+ alone\n(Brout+2022)", PANTHEON_ALONE_H0, PANTHEON_ALONE_SIGMA, "#ff7f0e", "late"),
        ("substrate\n(B3 prediction)", SUBSTRATE_H0, SUBSTRATE_H0_SIGMA, "#1f77b4", "B3"),
        ("Planck 2018\n(LambdaCDM)", PLANCK_H0, PLANCK_SIGMA, "#2ca02c", "early"),
    ]

    y_pos = np.arange(len(anchors))[::-1]  # top-down listing
    h0s = [a[1] for a in anchors]
    sigs = [a[2] for a in anchors]
    colors = [a[3] for a in anchors]
    labels = [a[0] for a in anchors]

    # Tension band (Planck to SH0ES)
    ax_c.axvspan(PLANCK_H0, SHOES_PANTHEON_H0, color="gold", alpha=0.18,
                 label="Hubble tension band")

    ax_c.errorbar(h0s, y_pos, xerr=sigs, fmt="o", capsize=6,
                  markersize=12, linewidth=2.5, ecolor="black",
                  markerfacecolor="white", markeredgecolor="black", zorder=5)

    for i, (h0, sig, col) in enumerate(zip(h0s, sigs, colors)):
        ax_c.scatter([h0], [y_pos[i]], s=220, color=col, zorder=10,
                     edgecolor="black", linewidth=1.0)

    # Substrate annotation arrows
    nsig_shoes = res.n_sigma_vs_shoes
    nsig_pa = res.n_sigma_vs_pantheon_alone
    nsig_planck = res.n_sigma_vs_planck

    sub_y = y_pos[2]
    ax_c.annotate(f"{nsig_shoes:.1f}σ", xy=((SHOES_PANTHEON_H0 + SUBSTRATE_H0) / 2, sub_y - 0.30),
                  ha="center", fontsize=10, fontweight="bold", color="#d62728")
    ax_c.annotate(f"{nsig_pa:.1f}σ", xy=((PANTHEON_ALONE_H0 + SUBSTRATE_H0) / 2, sub_y - 0.55),
                  ha="center", fontsize=10, fontweight="bold", color="#ff7f0e")
    ax_c.annotate(f"{nsig_planck:.1f}σ", xy=((PLANCK_H0 + SUBSTRATE_H0) / 2, sub_y + 0.30),
                  ha="center", fontsize=10, fontweight="bold", color="#2ca02c")

    ax_c.set_yticks(y_pos)
    ax_c.set_yticklabels(labels, fontsize=10)
    ax_c.set_xlabel(r"$H_0$  [km/s/Mpc]", fontsize=11)
    ax_c.set_xlim(65.0, 76.5)
    ax_c.set_title(
        f"Substrate H$_0$ inside tension band; "
        f"{nsig_shoes:.1f}σ from SH0ES, {nsig_planck:.1f}σ from Planck",
        fontsize=12,
    )
    ax_c.grid(True, axis="x", alpha=0.3)
    ax_c.legend(loc="lower right", fontsize=9.5, framealpha=0.95)

    fig.suptitle(
        "Pantheon+ test (visuals/133): substrate H$_0$ = 71.92 km/s/Mpc vs SN Ia + CMB anchors",
        fontsize=13, y=0.995,
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PATH, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {OUT_PATH}")


if __name__ == "__main__":
    main()
