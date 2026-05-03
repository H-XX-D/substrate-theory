#!/usr/bin/env python3
"""Print the missing-piece hypothesis tests."""

from __future__ import annotations

from stiff_medium.missing_piece_hypotheses import run_missing_piece_hypothesis_tests


def banner(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def main() -> None:
    data = run_missing_piece_hypothesis_tests()

    banner("1. UV / PLANCK SUPPRESSION")
    print(f"Required chi_UV = l_P/xi_e = {data['uv_target_ratio']:.6e}")
    print("Top small-form candidates:")
    for cand in data["uv_candidates"][:8]:
        print(
            f"  {cand.formula:<44} value={cand.value:.3e} "
            f"err={cand.relative_error * 100:+7.2f}%  {cand.verdict}"
        )
    print("Verdict: exp(-16*pi) times a saturation prefactor is the right size,")
    print("but this is only useful if the model derives a 16*pi UV action.")

    banner("2. LEPTON FOOT/KOIDE PHASE")
    lep = data["lepton_phase"]
    print(f"Empirical branch delta/pi     = {lep['empirical_delta_pi']:.9f}")
    print(f"Conjugate branch delta/pi     = {lep['conjugate_delta_pi']:.9f}")
    print(
        "Z3 orbit of empirical branch  = "
        + ", ".join(f"{x:.9f}" for x in lep["z3_orbit"])
    )
    for key in ("empirical_point", "conjugate_point", "pi_over_6_point", "seven_pi_over_five_point"):
        p = lep[key]
        print(
            f"  {p.label:<22} delta/pi={p.delta_pi:.9f} "
            f"mu/e={p.ratio_mu_e:9.3f} tau/e={p.ratio_tau_e:10.3f} "
            f"Q+={p.positive_koide_q:.6f} signs={p.root_signs}  {p.verdict}"
        )
    print("Best small rational phases by ratio error:")
    for rat in lep["best_rationals"][:5]:
        print(
            f"  {rat.p:>2}/{rat.q:<2} pi  delta/pi={rat.delta_pi:.9f} "
            f"err_mu={rat.error_mu_pct:+7.2f}% "
            f"err_tau={rat.error_tau_pct:+7.2f}% "
            f"combined={rat.combined_error_pct:7.2f}%"
        )
    print("Verdict: pi/6 is topologically clean but is on the wrong positive-root")
    print("branch.  7pi/5 is close in phase but bad in mass ratios because the")
    print("small electron root makes this sector hypersensitive.")

    banner("3. CKM / CABIBBO SELECTOR")
    ckm = data["ckm_rationals"]
    print(f"Rational angles within 1% using n*pi/d, d<=120: {len(ckm)}")
    for cand in ckm[:8]:
        print(
            f"  {cand.formula:<10} theta={cand.theta_deg:10.6f} deg "
            f"err={cand.error_deg_pct:+7.3f}%"
        )
    print("Examples that make denominator 55 non-unique:")
    for item in data["ckm_55_examples"]:
        print(f"  {item}")
    print("Verdict: 4pi/55 is a nice near-miss, but rational scans are too easy.")
    print("The missing object is still a substrate mixing operator H_mix.")

    banner("4. COSMOLOGY TRANSFER WINDOW")
    windows = data["transfer_windows"]
    req = windows[0].required_f_vis
    print(f"Required f_vis <= {req:.3e} for delta_m=0.0236 and deltaT/T=1e-5")
    print("Toy windows that pass both f_galaxy and acoustic visibility:")
    shown = 0
    for win in windows:
        if win.passes_visibility and win.keeps_acoustic_visible:
            print(
                f"  {win.family:<7} k_cut={win.k_cut_mpc:5.3f} "
                f"n={win.steepness:<2} f_acoustic={win.f_at_acoustic:.3e} "
                f"f_galaxy={win.f_at_galaxy:.3e}"
            )
            shown += 1
            if shown >= 6:
                break
    print("Verdict: a steep opacity window can hide percent-level proto-matter")
    print("from the CMB on paper.  The physics of that opacity is still missing.")

    banner("5. DARK MATTER DIMER CROSS SECTION")
    for row in data["dm_cross_sections"]:
        print(
            f"  R={row.radius_fm:6.1f} fm  sigma={row.sigma_cm2:.3e} cm^2  "
            f"sigma/m={row.sigma_over_m_cm2_per_g:.3e} cm^2/g  {row.verdict}"
        )
    print(
        f"Radius for sigma/m=0.1 cm^2/g: {data['dm_radius_for_0p1']:.2f} fm"
    )
    print(f"Radius for sigma/m=1.0 cm^2/g: {data['dm_radius_for_1']:.2f} fm")
    print("Verdict: a QCD-size 49 GeV dimer is essentially collisionless;")
    print("halo-scale self-interaction needs a much larger composite radius.")

    banner("6. MATTER ORIENTATION WITHOUT ONE-SHOT BARYOGENESIS")
    for row in data["orientation_bias"]:
        print(
            f"  f_anti<{row.target_anti_fraction:.0e}: "
            f"DeltaE/T_eff >= {row.delta_e_over_t_eff:6.2f}, "
            f"tau/epoch <= {row.tau_over_epoch_max:.4f}  {row.verdict}"
        )
    print("Verdict: removing Big-Bang baryogenesis does not remove the need for")
    print("an orientation-selection law at the de-saturation transition.")


if __name__ == "__main__":
    main()
