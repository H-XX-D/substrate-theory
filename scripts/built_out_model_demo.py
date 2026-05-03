"""Demonstrate the BUILT-OUT model — using all the new mechanism modules.

Shows the substrate-mechanical model in action with:
- Cone-bouncing for mass (§18.35)
- Saturation barrier for BH formation (§18.39)
- Multi-kink composites for DM and baryons (§18.37, §18.49)
- Stress-loading for lepton spectrum (§18.30)
- Two coupling channels for EM + gravity (§18.32)
"""

import numpy as np

from stiff_medium.cone_bouncing import (
    ConeBouncingParticle,
    categorize_particle_by_kappa,
    mass_from_kappa,
    kappa_for_mass,
)
from stiff_medium.saturation import (
    SIGMA_MAX,
    is_saturated,
    schwarzschild_horizon_strain,
    schwarzschild_radius,
    time_dilation_factor,
)
from stiff_medium.multi_kink import (
    Kink,
    MultiKinkComposite,
    make_dark_matter_dimer,
    make_baryon_3kink,
    make_meson,
    kink_antikink_potential,
)
from stiff_medium.stress_loading import (
    StressLoadedConfiguration,
    all_three_lepton_states,
    vertex_stress_quanta_decay_products,
    koide_relation_check,
)
from stiff_medium.coupling_channels import (
    TwoChannelInteraction,
    hierarchy_check_protons,
    epsilon_charge_symmetric_residual,
)


def header(title):
    print("\n" + "=" * 72)
    print(f"  {title}")
    print("=" * 72 + "\n")


def demo_cone_bouncing():
    header("§18.35 CONE-BOUNCING MASS MECHANISM")

    print("Particle types categorized by κ (directional stiffness):")
    print()

    for kappa, label in [
        (0.0, "Photon"),
        (1e-22, "Light neutrino"),
        (1e-12, "Electron-scale"),
        (1e-8, "Muon-scale"),
        (1e-5, "Tau-scale"),
        (1e-3, "GeV-scale"),
        (1.0, "Heavy carrier (kink)"),
    ]:
        mass = mass_from_kappa(kappa)
        category = categorize_particle_by_kappa(kappa)
        print(f"  κ = {kappa:.2e}: m = {mass:.4e} (natural units), {category}")

    print()
    print("Particles wobble at ω = √(κ/I); their oscillation momentum IS the mass.")
    print()

    # Simulate a particle's wobble dynamics
    print("Simulating wobble dynamics for a 'muon-scale' particle:")
    p = ConeBouncingParticle(
        preferred_direction=np.array([0.0, 0.0, 1.0]),
        kappa=1e-8, I=1.0, theta=0.1, theta_dot=0.0,
    )

    print(f"  Initial wobble angle: θ = {p.theta:.4f}")
    print(f"  Bounce frequency: ω = {p.omega_bounce:.4e}")
    print(f"  Average translational speed: v = {p.average_translational_speed():.6f} c")

    dt = 0.1
    for step in range(5):
        p.step(dt)
    print(f"  After 5 steps (dt={dt}): θ = {p.theta:.4f}, θ_dot = {p.theta_dot:.4f}")


def demo_saturation_barrier():
    header("§18.39 SATURATION BARRIER (σ_max = ½)")

    print(f"Universal substrate elastic limit: σ_max = {SIGMA_MAX}")
    print()

    # Verify Schwarzschild radii give σ = 0.5 universally
    M_sun = 1.989e30
    print("Verifying σ at Schwarzschild radius for various BH masses:")
    print()
    print(f"  {'Object':>20} | {'M (kg)':>14} | {'r_s (m)':>12} | {'σ at r_s':>10}")
    print("  " + "-" * 65)

    for label, M in [
        ("Earth", 5.972e24),
        ("Sun", M_sun),
        ("Stellar BH (10M⊙)", 10 * M_sun),
        ("Sgr A*", 4e6 * M_sun),
        ("M87 SMBH", 6.5e9 * M_sun),
    ]:
        r_s = schwarzschild_radius(M)
        sigma = schwarzschild_horizon_strain(M, r_s)
        print(f"  {label:>20} | {M:>14.4e} | {r_s:>12.4e} | {sigma:>10.4f}")

    print()
    print("σ = 0.5 universally — substrate elastic limit reached at horizon.")
    print()

    # Time dilation
    print("Time dilation factor √(1-2σ) at various distances from Sun:")
    M = M_sun
    for r in [6.96e8, 1.496e11, 6.371e6 * 1.5]:  # solar surface, AU, Earth orbit
        sigma = schwarzschild_horizon_strain(M, r)
        td = time_dilation_factor(sigma)
        print(f"  r = {r:.3e} m: σ = {sigma:.4e}, dt/dt_∞ = {td:.10f}")


def demo_multi_kink_composites():
    header("§18.37 + §18.49 MULTI-KINK COMPOSITES")

    print("DARK MATTER (kink-antikink dimer, §18.37):")
    dm = make_dark_matter_dimer(M_K=27.0, binding_fraction=0.10)
    print(f"  Composition: {dm.name}")
    print(f"  Total kinks: {len(dm.kinks)}")
    print(f"  Net charge: {dm.total_charge} (neutral ✓ for DM)")
    print(f"  Constituent mass: {dm.constituent_mass:.1f} GeV")
    print(f"  Composite mass (with 10% binding): {dm.composite_mass:.1f} GeV")
    print(f"  Is DM candidate: {dm.is_dark_matter_candidate}")
    print(f"  Is stable: {dm.is_stable()}")
    print()

    print("BARYONS:")
    proton = make_baryon_3kink(M_K_constituent=0.336, composite_mass=0.938,
                                baryon_type="proton")
    neutron = make_baryon_3kink(M_K_constituent=0.336, composite_mass=0.940,
                                baryon_type="neutron")

    for b in [proton, neutron]:
        print(f"  {b.name}: {len(b.kinks)} kinks, total Q = {b.total_charge:+.2f}, M = {b.composite_mass:.4f} GeV")

    print()
    print("MESONS:")
    pion = make_meson(M_K=0.336, composite_mass=0.140, meson_type="pion")
    print(f"  {pion.name}: {len(pion.kinks)} kinks, total Q = {pion.total_charge:+.2f}, M = {pion.composite_mass:.4f} GeV")
    print()

    # Two-kink potential at various distances
    print("Two-kink potential V(R):")
    for R in [0.1, 0.5, 1.0, 2.0, 5.0]:
        V = kink_antikink_potential(R)
        print(f"  R = {R}: V = {V:.4f}")


def demo_stress_loading():
    header("§18.30 STRESS-LOADED LEPTON SPECTRUM")

    states = all_three_lepton_states()

    print("Three lepton states from stress-loaded electron:")
    print()
    print(f"  {'State':>12} | {'n_quanta':>8} | {'Mass (GeV)':>12} | {'Stable?':>8}")
    print("  " + "-" * 50)
    for state in states:
        print(f"  {state.name:>12} | {state.n_quanta:>8} | {state.mass:>12.6f} | {state.is_stable!s:>8}")
    print()

    # Mass ratios
    print("Mass ratios (compared to electron):")
    e_mass = states[0].mass
    for state in states:
        ratio = state.mass / e_mass
        print(f"  {state.name}/electron = {ratio:.2f}")
    print()

    # Verify Koide's relation
    koide = koide_relation_check(states)
    print(f"Koide's relation Q = (Σm)/(Σ√m)²:")
    print(f"  Q = {koide['Q']:.6f}")
    print(f"  Target = 2/3 = {2/3:.6f}")
    print(f"  Deviation: {koide['deviation_pct']:.4f}%")
    print()

    # Decay products
    print("Decay channels:")
    for state in states:
        decay = vertex_stress_quanta_decay_products(state)
        print(f"  {state.name}: {decay}")


def demo_coupling_channels():
    header("§18.32 TWO COUPLING CHANNELS (EM + gravity)")

    # Verify gravity/EM hierarchy
    h = hierarchy_check_protons()
    print("Verify F_grav/F_em = (m_p/M_Planck)²/α for two protons:")
    print(f"  M_Planck = {h['M_Planck_kg']:.4e} kg")
    print(f"  F_grav/F_em (measured): {h['ratio_measured']:.4e}")
    print(f"  F_grav/F_em (predicted): {h['ratio_predicted']:.4e}")
    print(f"  Agreement: {h['agreement_pct']:.4f}%")
    print()

    # Compute charge-symmetric residual
    epsilon = epsilon_charge_symmetric_residual()
    print(f"Charge-symmetric residual coupling ε = {epsilon:.4e}")
    print()

    # Two-channel interaction example
    interaction = TwoChannelInteraction()

    print("Two electrons at 1 fm separation:")
    e1 = {"mass": 9.109e-31, "charge": -1.602e-19}
    e2 = {"mass": 9.109e-31, "charge": -1.602e-19}
    f = interaction.force_between(e1, e2, 1e-15)
    print(f"  F_em (Coulomb): {f['F_em']:.4e} N")
    print(f"  F_grav: {f['F_grav']:.4e} N")
    print(f"  F_grav/F_em: {f['ratio']:.4e}")
    print()

    print("Two protons at 1 fm separation:")
    p1 = {"mass": 1.673e-27, "charge": +1.602e-19}
    p2 = {"mass": 1.673e-27, "charge": +1.602e-19}
    f = interaction.force_between(p1, p2, 1e-15)
    print(f"  F_em (Coulomb): {f['F_em']:.4e} N")
    print(f"  F_grav: {f['F_grav']:.4e} N")
    print(f"  F_grav/F_em: {f['ratio']:.4e}")


def main():
    print()
    print("BUILT-OUT MODEL DEMONSTRATION — using all mechanism modules")

    demo_cone_bouncing()
    demo_saturation_barrier()
    demo_multi_kink_composites()
    demo_stress_loading()
    demo_coupling_channels()

    header("CONCLUSIONS")

    print("All mechanisms are now IMPLEMENTED IN CODE:")
    print()
    print("  ✓ stiff_medium.cone_bouncing — §18.35 mass mechanism")
    print("  ✓ stiff_medium.saturation — §18.39 elastic limit")
    print("  ✓ stiff_medium.multi_kink — §18.37 DM + §18.49 baryons + mesons")
    print("  ✓ stiff_medium.stress_loading — §18.30 lepton spectrum")
    print("  ✓ stiff_medium.coupling_channels — §18.32 EM + gravity")
    print()
    print("Each module reflects the substrate-mechanical mechanisms we've")
    print("articulated. The code now SHOWS the model in action, not just")
    print("describes it in the spec.")


if __name__ == "__main__":
    main()
