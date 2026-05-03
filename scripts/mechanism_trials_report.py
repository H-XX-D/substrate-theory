#!/usr/bin/env python3
"""Print concrete mechanism trials for the weak sectors."""

from __future__ import annotations

from stiff_medium.mechanism_trials import run_mechanism_trials


def banner(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def main() -> None:
    data = run_mechanism_trials()

    banner("1. UV PHASE-SLIP ACTION")
    for row in data["uv"]:
        print(
            f"  {row.name:<48} S={row.action:9.5f} "
            f"S_err={row.action_error_pct:+7.3f}% "
            f"chi_err={row.chi_error_pct:+8.2f}%  {row.verdict}"
        )

    banner("2. LEPTON POSITIVE-ROOT VERTEX PHASE")
    for row in data["leptons"]:
        print(
            f"  {row.name:<48} delta/pi={row.delta_pi:.9f} "
            f"phase_err={row.phase_error_pct:+7.3f}% "
            f"mu_err={row.mu_error_pct:+8.3f}% "
            f"tau_err={row.tau_error_pct:+8.3f}%  {row.verdict}"
        )

    banner("3. CKM OVERLAP")
    for row in data["ckm"]:
        print(
            f"  {row.name:<48} sin={row.sin_theta:.9f} "
            f"theta={row.theta_deg:.6f} deg "
            f"sin_err={row.sin_error_pct:+7.3f}%  {row.verdict}"
        )

    banner("4. COSMOLOGY OPACITY")
    cosmo = data["cosmology"]
    print(
        f"  {cosmo.name}: k_cut={cosmo.k_cut_mpc:.3f} Mpc^-1, "
        f"n={cosmo.steepness}, f_acoustic={cosmo.f_acoustic:.3e}, "
        f"f_galaxy={cosmo.f_galaxy:.3e}, required<={cosmo.required_f_vis:.3e}"
    )
    print(f"  {cosmo.verdict}")

    banner("5. DARK MATTER POLARIZATION HALO")
    dm = data["dark_matter"]
    print(
        f"  {dm.name}: R={dm.radius_fm:.3f} fm, "
        f"sigma/m={dm.sigma_over_m:.3e} cm^2/g"
    )
    print(f"  {dm.verdict}")

    banner("6. MATTER ORIENTATION BIAS")
    for row in data["orientation"]:
        print(
            f"  {row.name:<48} S={row.action:8.4f} "
            f"f_anti={row.anti_fraction:.3e}  {row.verdict}"
        )

    banner("MECHANISM QUEUE")
    print("  Most promising trial: lepton boundary + loop correction.")
    print("  Best cross-sector pattern: loop/zero-mode determinants keep recurring.")
    print("  Main risk: several trials still need the actual substrate operator/saddle.")


if __name__ == "__main__":
    main()
