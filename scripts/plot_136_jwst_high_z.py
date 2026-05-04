"""Generate visuals/136_jwst_high_z.png.

Four-panel figure documenting the JWST z>10 galaxy comparison:

  (top-left)  Per-source ratio: substrate vs LCDM phi at fixed M_halo,
              for each curated z>10 source. Shows the "cosmology only"
              part of the boost.
  (top-right) Eps_star contribution + total: substrate's higher stellar
              baryon fraction (0.20 vs LCDM 0.06) gives the dominant boost
              at fixed M_*.
  (bot-left)  UV LF at z=10,12,14 — substrate vs LCDM curves vs binned
              JWST data points (Harikane+2023, Donnan+2023).
  (bot-right) Stellar mass density at z = 7-11 (Labbé 2023 vs substrate vs
              LCDM): the headline JWST tension and substrate's verdict.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.stiff_medium.jwst_high_z_test import (
    JWST_OBSERVED_OVERABUNDANCE_DEX,
    M_UV_to_log_M_star,
    compare_per_source,
    harikane_donnan_z10_LF,
    integrated_stellar_density,
    labbe_2023_density_points,
    make_lcdm_track,
    make_substrate_track,
    run_jwst_high_z_test,
)


OUT_PATH = Path(__file__).resolve().parents[1] / "visuals" / "136_jwst_high_z.png"

CLR_SUB = "#d62728"     # substrate – red
CLR_LCDM = "#1f77b4"    # LCDM – blue
CLR_OBS = "#2ca02c"     # observation – green
CLR_BAND = "#ffd966"    # JWST overabundance band – yellow


def _panel_per_source(ax, result):
    """Top-left: per-source phi excess (substrate vs LCDM at fixed M_halo)."""
    rows = result.sources
    names = [r.name for r in rows]
    excess_dex = [r.log_excess_substrate for r in rows]
    z_vals = [r.z for r in rows]

    # Color by redshift
    colors = plt.cm.plasma(np.linspace(0.15, 0.85, len(rows)))

    bars = ax.barh(np.arange(len(rows)), excess_dex,
                   color=colors, edgecolor="black", linewidth=0.6)
    for i, (b, z) in enumerate(zip(bars, z_vals)):
        ax.text(b.get_width() + (0.02 if b.get_width() >= 0 else -0.02),
                i, f"  z={z:.2f}", va="center",
                ha="left" if b.get_width() >= 0 else "right",
                fontsize=8, color="black")

    ax.axvline(0.0, color="black", linewidth=0.7)
    lo, hi = JWST_OBSERVED_OVERABUNDANCE_DEX
    ax.axvspan(lo, hi, color=CLR_BAND, alpha=0.35,
               label=f"JWST/LCDM observed: {lo:.1f}-{hi:.1f} dex")
    ax.set_yticks(np.arange(len(rows)))
    ax.set_yticklabels(names, fontsize=8)
    ax.set_xlabel(r"$\log_{10}[\, \phi_{\rm sub}(M_h) / \phi_{\rm LCDM}(M_h) \,]$",
                  fontsize=10)
    ax.set_title("Per-source HMF ratio at fixed halo mass\n(cosmology + cube-DM only)",
                 fontsize=10)
    ax.set_xlim(-0.4, max(0.6, max(excess_dex) + 0.2))
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(True, axis="x", alpha=0.3)


def _panel_boost_decomposition(ax, result):
    """Top-right: cosmology vs eps_star vs total boost — stacked bars."""
    cosmo = result.mean_log_excess
    eps = result.eps_star_log_boost_dex
    total = result.total_log_boost_dex

    bars = ax.bar(
        ["Cosmology +\ncube-DM HMF",
         r"$\epsilon_*$"
         f"  ({result.eps_star_substrate:.2f}/"
         f"{result.eps_star_lcdm:.2f})",
         "TOTAL\n(at fixed M*)"],
        [cosmo, eps, total],
        color=[CLR_SUB, "#9467bd", "#000000"],
        edgecolor="black", linewidth=0.7,
    )
    for b, v in zip(bars, [cosmo, eps, total]):
        ax.text(b.get_x() + b.get_width() / 2,
                v + 0.02 if v >= 0 else v - 0.04,
                f"{v:+.2f} dex\n(×{10**v:.2f})",
                ha="center", fontsize=9, fontweight="bold")

    lo, hi = JWST_OBSERVED_OVERABUNDANCE_DEX
    ax.axhspan(lo, hi, color=CLR_BAND, alpha=0.35,
               label=f"JWST/LCDM: {lo:.1f}-{hi:.1f} dex")
    ax.axhline(0.0, color="black", linewidth=0.7)
    ax.set_ylabel(r"$\log_{10}\,[\,\phi_{\rm sub}/\phi_{\rm LCDM}\,]$ (dex)",
                  fontsize=10)
    ax.set_ylim(min(-0.1, cosmo - 0.1), max(total, hi) + 0.3)
    ax.set_title("Boost decomposition at fixed M_*", fontsize=10)
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(True, axis="y", alpha=0.3)


def _panel_uv_lf(ax, substrate, lcdm):
    """Bot-left: UV LF curves at z=10, z=12 with binned obs overlaid."""
    z_panels = [10.0, 12.0, 14.0]
    z_colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    M_UV_grid = np.linspace(-22.5, -19.0, 40)

    for z, c in zip(z_panels, z_colors):
        log_M_star_grid = [M_UV_to_log_M_star(M) for M in M_UV_grid]
        phi_sub = [substrate.stellar_mass_function(z, 10 ** lg)
                   for lg in log_M_star_grid]
        phi_lcdm = [lcdm.stellar_mass_function(z, 10 ** lg)
                    for lg in log_M_star_grid]
        # Renormalize to match obs at the brightest LF bin (illustrative only)
        # so the panel shows the SHAPE of the substrate/LCDM curves vs data
        ax.plot(M_UV_grid, np.log10(np.maximum(phi_sub, 1e-30)),
                color=c, linestyle="-", linewidth=1.4,
                label=f"substrate  z={z:.0f}")
        ax.plot(M_UV_grid, np.log10(np.maximum(phi_lcdm, 1e-30)),
                color=c, linestyle="--", linewidth=1.0,
                label=f"LCDM         z={z:.0f}")

    obs_pts = harikane_donnan_z10_LF()
    for pt in obs_pts:
        # Color by redshift
        c = z_colors[0] if pt.z <= 10.5 else (
            z_colors[1] if pt.z <= 12.5 else z_colors[2]
        )
        ax.errorbar(
            pt.M_UV, pt.log_phi, yerr=pt.log_phi_err,
            fmt="o", color=c, markersize=7, capsize=3,
            markeredgecolor="black", markeredgewidth=0.8, elinewidth=0.8,
        )

    ax.set_xlabel(r"$M_{\rm UV}$ (mag)", fontsize=10)
    ax.set_ylabel(r"$\log_{10}\,\phi$  [Mpc$^{-3}$ dex$^{-1}$]", fontsize=10)
    ax.set_title("UV luminosity function vs JWST data\n(Harikane+2023, Donnan+2023)",
                 fontsize=10)
    ax.invert_xaxis()
    ax.set_ylim(-13, -3)
    ax.legend(fontsize=7, ncol=2, loc="lower left")
    ax.grid(True, alpha=0.3)


def _panel_density(ax, substrate, lcdm):
    """Bot-right: integrated stellar mass density above M_min vs z."""
    pts = labbe_2023_density_points()
    z_vals = [pt.z for pt in pts]
    rho_obs = [pt.log_rho_star for pt in pts]
    rho_err = [pt.log_rho_star_err for pt in pts]
    rho_sub = [np.log10(max(integrated_stellar_density(
        substrate, pt.z, pt.log_M_star_min), 1e-30)) for pt in pts]
    rho_lcdm = [np.log10(max(integrated_stellar_density(
        lcdm, pt.z, pt.log_M_star_min), 1e-30)) for pt in pts]
    labels = [f"z={pt.z:.1f}\n>10$^{{{pt.log_M_star_min:.1f}}}$" for pt in pts]

    x = np.arange(len(pts))
    width = 0.25

    ax.bar(x - width, rho_sub, width, color=CLR_SUB,
           edgecolor="black", linewidth=0.6, label="substrate")
    ax.bar(x, rho_lcdm, width, color=CLR_LCDM,
           edgecolor="black", linewidth=0.6, label="LCDM")
    ax.bar(x + width, rho_obs, width, color=CLR_OBS,
           edgecolor="black", linewidth=0.6, label="JWST obs")

    # Error bars on observed
    ax.errorbar(x + width, rho_obs, yerr=rho_err, fmt="none",
                color="black", capsize=3, linewidth=0.8)

    # Annotate the JWST/LCDM gap on each bin
    for i, (o, l) in enumerate(zip(rho_obs, rho_lcdm)):
        ax.annotate(
            f"obs - LCDM\n= {o-l:+.1f} dex",
            xy=(i + width, o), xytext=(i + 0.05, o + 1.5),
            fontsize=7, ha="left",
            arrowprops=dict(arrowstyle="->", color="gray", lw=0.5),
        )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel(r"$\log_{10}\,\rho_*$  [$M_\odot$ Mpc$^{-3}$]", fontsize=10)
    ax.set_title("Cumulative stellar mass density (Labbé+2023)", fontsize=10)
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(True, axis="y", alpha=0.3)


def main() -> None:
    result = run_jwst_high_z_test()
    substrate = make_substrate_track()
    lcdm = make_lcdm_track()

    fig = plt.figure(figsize=(14.0, 10.0))
    gs = fig.add_gridspec(2, 2, hspace=0.40, wspace=0.30)

    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    _panel_per_source(ax_a, result)
    _panel_boost_decomposition(ax_b, result)
    _panel_uv_lf(ax_c, substrate, lcdm)
    _panel_density(ax_d, substrate, lcdm)

    fig.suptitle(
        "JWST z > 10 galaxies vs substrate (cube-DM + de-saturation) vs ΛCDM\n"
        f"Verdict: {result.verdict}",
        fontsize=12, fontweight="bold", y=0.995,
    )
    fig.text(
        0.5, 0.01,
        f"Total substrate boost at fixed M_* = {result.total_log_boost_dex:+.2f} dex "
        f"(×{10**result.total_log_boost_dex:.2f})    "
        f"= {result.mean_log_excess:+.2f} (cosmology) + "
        f"{result.eps_star_log_boost_dex:+.2f} (eps_*) dex.    "
        f"JWST/LCDM observed gap: 0.5-1.0 dex.",
        ha="center", fontsize=9, style="italic",
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PATH, dpi=150, bbox_inches="tight")
    print(f"Saved {OUT_PATH}")


if __name__ == "__main__":
    main()
