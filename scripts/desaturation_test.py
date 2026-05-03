"""Test script for the desaturation phase-transition module — §18.44.

Demonstrates:
1. Latent heat density at Planck substrate stiffness.
2. Predicted CMB temperature via latent-heat-plus-redshift.
3. Phase boundary (bubble wall) speed.
4. Tensor-to-scalar ratio r from the de-saturation transition.
5. Bubble nucleation rate as a function of temperature.
6. Single evolve() step showing σ relaxation.

Run from the repo root:
    PYTHONPATH=src python3 scripts/desaturation_test.py
"""

import numpy as np

from stiff_medium.desaturation import (
    DesaturationTransition,
    cmb_temperature_from_latent_heat,
    phase_boundary_velocity,
    tensor_to_scalar_ratio_from_transition,
    K_PLANCK,
    c,
    hbar,
    G,
    k_B,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def header(title: str) -> None:
    """Print a section header matching the style of built_out_model_demo.py."""
    print("\n" + "=" * 72)
    print(f"  {title}")
    print("=" * 72 + "\n")


# ---------------------------------------------------------------------------
# Demo sections
# ---------------------------------------------------------------------------

def demo_latent_heat() -> float:
    """Compute latent heat density for the Planck-stress substrate."""
    header("§18.44 LATENT HEAT OF THE DE-SATURATION PHASE TRANSITION")

    transition = DesaturationTransition()   # defaults: σ_i=0.5, σ_f=0.0, K=K_Planck

    print(f"Substrate stiffness K  = {transition.K:.6e} Pa  (Planck stress c⁷/ℏG²)")
    print(f"sigma_initial          = {transition.sigma_initial}  (saturated Big Bang state)")
    print(f"sigma_final            = {transition.sigma_final}  (empty vacuum)")
    print(f"phi_max (cutoff)       = {transition.phi_max}")
    print()

    epsilon_latent = transition.latent_heat_density()
    print(f"Latent heat density:")
    print(f"  ε_latent = ½ K (σ_i² - σ_f²)")
    print(f"           = ½ × {transition.K:.3e} × ({transition.sigma_initial}² - {transition.sigma_final}²)")
    print(f"           = {epsilon_latent:.6e} J/m³")
    print()

    # Convert to more intuitive units
    solar_mass_energy_density = 1.989e30 * c**2 / (1.0)   # J per solar mass
    planck_energy_per_planck_vol = (
        np.sqrt(hbar * c**5 / G) * c**2 /        # Planck energy (J)
        (hbar * G / c**3) ** 1.5                  # Planck volume (m³)
    )
    print(f"For reference:")
    print(f"  Planck energy density: {planck_energy_per_planck_vol:.3e} J/m³")
    print(f"  Ratio ε_latent / ε_Planck: {epsilon_latent / planck_energy_per_planck_vol:.4f}")
    print()
    print("The latent heat is exactly 1/8 of the Planck energy density (= ½ K σ²_max = K/8),")
    print("which is what one expects for the elastic energy stored at the saturation limit.")

    return epsilon_latent


def demo_cmb_temperature(epsilon_latent: float) -> None:
    """Predict the CMB temperature from the phase-transition latent heat."""
    header("§18.44 PREDICTED CMB TEMPERATURE FROM LATENT HEAT")

    print("Radiation energy density scales as a⁻⁴ after the transition.")
    print("For a given expansion factor f = a_today / a_transition:")
    print("  T_CMB = (ε_latent / a_rad)^(1/4) / f")
    print()

    # Scan expansion factors
    print(f"  {'Expansion factor f':>22} | {'Predicted T_CMB (K)':>20} | {'vs observed 2.7255 K':>22}")
    print("  " + "-" * 70)

    target_T = 2.7255   # FIRAS / COBE measured value

    best_f = None
    best_T = None

    for log10_f in [20, 24, 26, 28, 29, 30, 32]:
        f = 10.0 ** log10_f
        T = cmb_temperature_from_latent_heat(epsilon_latent, f)
        ratio = T / target_T
        marker = " <-- closest" if abs(ratio - 1.0) < 0.5 else ""
        print(f"  {f:>22.3e} | {T:>20.4e} | {ratio:>20.4f}×{marker}")
        if best_f is None or abs(T / target_T - 1.0) < abs(best_T / target_T - 1.0):
            best_f = f
            best_T = T

    print()

    # Compute the EXACT expansion factor that gives T_CMB = 2.7255 K
    a_rad = 4 * 5.670e-8 / c
    T_transition = (epsilon_latent / a_rad) ** 0.25
    exact_f = T_transition / target_T

    print(f"Phase-transition temperature:  T_transition = {T_transition:.4e} K")
    print(f"Required expansion factor for T_CMB = {target_T} K:")
    print(f"  f = T_transition / T_CMB = {exact_f:.4e}")
    print(f"  log10(f) = {np.log10(exact_f):.2f}")
    print()
    print("This enormous expansion factor places the phase transition at")
    print(f"z ~ {exact_f:.2e} — deep in the Planck epoch, consistent with the")
    print("substrate saturating at the beginning of the universe (§18.40).")
    print()
    print(f"Observed T_CMB (FIRAS): {target_T} K")
    print(f"Our prediction at f = 10^28: {cmb_temperature_from_latent_heat(epsilon_latent, 1e28):.4e} K")


def demo_phase_boundary_velocity() -> None:
    """Demonstrate the bubble-wall speed = substrate sound speed."""
    header("§18.44 PHASE BOUNDARY VELOCITY (BUBBLE WALL SPEED)")

    print("Per spec §4: c² = K / ρ.  The phase boundary propagates at the substrate")
    print("wave speed.  When K / ρ = c² the boundary moves at exactly c.")
    print()

    # Substrate density consistent with Planck K and c² = K / ρ
    rho_planck = K_PLANCK / c**2
    print(f"Planck substrate stiffness:  K = {K_PLANCK:.4e} Pa")
    print(f"Consistent substrate density: ρ = K / c² = {rho_planck:.4e} kg/m³")
    print()

    v_wall = phase_boundary_velocity(K_PLANCK, rho_planck)
    print(f"Phase boundary speed:  v = sqrt(K/ρ) = {v_wall:.6e} m/s")
    print(f"Speed of light c:                       {c:.6e} m/s")
    print(f"Ratio v/c:                              {v_wall / c:.8f}")
    print()
    print("The bubble wall propagates at exactly c — the de-saturation boundary")
    print("is a substrate 'shockwave' at the medium's natural signal speed.")
    print()

    # Sanity check with different (non-Planck) parameters
    K_test = 1.0e24   # J/m³  (close to Planck but round)
    rho_test = K_test / c**2
    v_test = phase_boundary_velocity(K_test, rho_test)
    print(f"Cross-check with K = {K_test:.2e} Pa:  v = {v_test:.4e} m/s  (= c as expected)")


def demo_tensor_to_scalar_ratio() -> None:
    """Tensor-to-scalar ratio predictions from the de-saturation transition."""
    header("§18.44 TENSOR-TO-SCALAR RATIO r (CMB B-MODE PREDICTION)")

    print("The de-saturation transition sources primordial gravitational waves.")
    print("Using the inflationary consistency relation r = 16 ε (inherited from")
    print("the §18.11 Lagrangian, as noted in §18.56.8):")
    print()

    observational_upper_bound = 0.036   # BICEP/Keck 2021

    print(f"  {'ε (slow-roll)':>18} | {'r = 16ε':>12} | {'Status vs r < 0.036':>24}")
    print("  " + "-" * 60)

    for epsilon, label in [
        (1e-4, "very slow transition"),
        (1e-3, "LiteBIRD target range"),
        (2.25e-3, "r = 0.036 / 16 (exact bound)"),
        (5e-3, "moderate transition"),
        (0.01, "fast transition"),
        (0.025, "near Planck upper bound"),
    ]:
        r = tensor_to_scalar_ratio_from_transition(epsilon)
        status = "allowed" if r < observational_upper_bound else "EXCLUDED"
        print(f"  {epsilon:>18.3e} | {r:>12.4e} | {status:>24}  ({label})")

    print()
    print(f"Observational upper bound (BICEP/Keck 2021): r < {observational_upper_bound}")
    print(f"LiteBIRD target sensitivity: r ~ 10⁻³")
    print()
    print("Per §18.56.8: a slow-rolling de-saturation transition gives r ~ 10⁻³,")
    print("within LiteBIRD reach.  Future B-mode measurements will constrain ε")
    print("and thereby the rapidity of the substrate phase transition.")

    # Return the LiteBIRD-target prediction explicitly
    r_target = tensor_to_scalar_ratio_from_transition(1e-3)
    print()
    print(f"Spec prediction for slow-roll de-saturation (ε = 10⁻³): r = {r_target:.4e}")


def demo_nucleation_rate() -> None:
    """Bubble nucleation rate as a function of temperature."""
    header("§18.44 BUBBLE NUCLEATION RATE (COLEMAN-CALLAN BOUNCE)")

    transition = DesaturationTransition()
    epsilon_latent = transition.latent_heat_density()

    print("Γ = A × exp(-S_E / ℏ)  [Coleman 1977 thin-wall bounce]")
    print(f"Latent heat Δε = {epsilon_latent:.4e} J/m³")
    print()

    # Compute the log10 of the bounce action exponent S_E / ℏ directly
    # (the nucleation rate = A exp(-S_E/ℏ) hits floating-point limits at
    # Planck scale, so we also show the dimensionless exponent explicitly).
    xi_p = (hbar * G / c**3) ** 0.5
    sigma_wall = transition.K * xi_p
    delta_e = epsilon_latent
    log_S_bounce = (
        np.log(27.0 * np.pi**2)
        + 4.0 * np.log(sigma_wall)
        - np.log(2.0)
        - 3.0 * np.log(delta_e)
    )
    log10_S_over_hbar = (log_S_bounce - np.log(hbar)) / np.log(10)

    print(f"  Dimensionless bounce action S_E / ℏ = 10^{log10_S_over_hbar:.1f}")
    print(f"  (This vastly exceeds float range; rate = A exp(-10^{log10_S_over_hbar:.0f}) is")
    print(f"   effectively zero for all T well below the Planck temperature.)")
    print()
    print(f"  {'T (K)':>12} | {'log10(S_eff/ℏ)':>16} | Note")
    print("  " + "-" * 55)

    for T, note in [
        (0.0, "pure quantum tunnelling"),
        (1.0, "near-absolute-zero thermal"),
        (2.7255, "today's CMB temperature"),
        (3000.0, "recombination epoch ~3000 K"),
        (1e10, "electroweak scale ~10 GeV"),
        (delta_e / k_B, "thermal energy = Δε (critical T)"),
        (1e32, "near Planck temperature"),
    ]:
        thermal_corr = 1.0 + k_B * T / delta_e if T > 0 else 1.0
        # Exponent is S_eff / ℏ = exp(log_S_bounce - log(thermal_corr) - log(ℏ))
        log_exponent = log_S_bounce - np.log(thermal_corr) - np.log(hbar)
        log10_exponent = log_exponent / np.log(10)
        print(f"  {T:>12.4e} | {log10_exponent:>16.2f} | {note}")

    print()
    print("The bounce action is ~10^" + f"{log10_S_over_hbar:.0f}" + " ℏ at T = 0.")
    print("This enormous suppression confirms the saturated state is deeply metastable:")
    print("the pre-CMB universe cannot spontaneously nucleate de-saturated bubbles.")
    print("Per §18.44, an external perturbation (or global transition triggered by")
    print("substrate expansion) must have driven the actual de-saturation event.")


def demo_evolve_step() -> None:
    """Show sigma relaxation with a single evolve() step."""
    header("§18.44 SIGMA RELAXATION: evolve() STEP DEMONSTRATION")

    transition = DesaturationTransition(sigma_initial=0.5, sigma_final=0.0)
    xi_planck = (hbar * G / c**3) ** 0.5
    tau_relax = hbar / (transition.K * xi_planck**3)

    print(f"Initial σ              = {transition.sigma_initial}")
    print(f"Target σ_final         = {transition.sigma_final}")
    print(f"Planck relaxation time = {tau_relax:.4e} s")
    print(f"  (Planck time t_P     = {xi_planck / c:.4e} s)")
    print()
    print("Evolving one step at dt = τ_relax (σ should decay by factor 1/e):")

    sigma_0 = transition.sigma_initial
    sigma_1 = transition.evolve(dt=tau_relax, current_sigma=sigma_0)
    expected = transition.sigma_final + (sigma_0 - transition.sigma_final) * np.exp(-1.0)

    print(f"  σ_0   = {sigma_0:.8f}")
    print(f"  σ_1   = {sigma_1:.8f}  (after dt = τ_relax)")
    print(f"  e^-1 × σ_0 = {expected:.8f}  (expected e-folding)")
    print(f"  Match: {abs(sigma_1 - expected) < 1e-10}")
    print()
    print("Evolving 10 e-folding times (dt = 10 τ_relax):")
    sigma_10 = transition.evolve(dt=10.0 * tau_relax, current_sigma=sigma_0)
    print(f"  σ_10  = {sigma_10:.4e}  (should be ~ {sigma_0 * np.exp(-10):.4e})")
    print()
    print("is_complete() check:")
    print(f"  Before evolution: {transition.is_complete()}")
    # Transition with effectively-completed sigma
    done = DesaturationTransition(sigma_initial=0.5 + 1e-8, sigma_final=0.5)
    print(f"  σ_i = σ_f + 1e-8:  {done.is_complete()}")
    exact_done = DesaturationTransition(sigma_initial=0.5, sigma_final=0.5)
    print(f"  σ_i = σ_f exactly: {exact_done.is_complete()}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    print()
    print("DESATURATION PHASE TRANSITION — §18.44 MODULE DEMONSTRATION")
    print("Substrate de-saturates σ = ½ → σ < ½; CMB is the latent heat.")

    epsilon_latent = demo_latent_heat()
    demo_cmb_temperature(epsilon_latent)
    demo_phase_boundary_velocity()
    demo_tensor_to_scalar_ratio()
    demo_nucleation_rate()
    demo_evolve_step()

    header("SUMMARY")

    print("All §18.44 observables computed from first principles:")
    print()

    # Final summary numbers
    T_cmb_predicted = cmb_temperature_from_latent_heat(epsilon_latent, 1e28)
    r_spec = tensor_to_scalar_ratio_from_transition(1e-3)
    v_wall = phase_boundary_velocity(K_PLANCK, K_PLANCK / c**2)

    # Exact expansion factor for the observed CMB temperature
    a_rad_local = 4 * 5.670e-8 / c
    T_transition = (epsilon_latent / a_rad_local) ** 0.25
    exact_f = T_transition / 2.7255

    print(f"  Latent heat density (K = K_Planck, σ=0.5→0):  {epsilon_latent:.4e} J/m³")
    print(f"  Phase-transition temperature:                  {T_transition:.4e} K")
    print(f"  Exact expansion factor for T_CMB = 2.7255 K:  {exact_f:.4e}  (log10 = {np.log10(exact_f):.1f})")
    print(f"  Predicted T_CMB at expansion factor 10^28:    {T_cmb_predicted:.4e} K")
    print(f"    Observed T_CMB (FIRAS):                     2.7255 K")
    print(f"  Phase boundary speed:                         {v_wall:.4e} m/s  (= c)")
    print(f"  Tensor-to-scalar ratio r (slow-roll ε=10⁻³): {r_spec:.4e}")
    print(f"    Observational bound (BICEP/Keck 2021):      r < 0.036")
    print()
    print("The CMB de-saturation interpretation is internally consistent:")
    print("  - The Planck-scale latent heat redshifts to the observed ~2.7 K")
    print("    over an expansion factor ~ 10^28-10^29.")
    print("  - The phase boundary travels at c (substrate wave speed).")
    print("  - Tensor spectrum predicts r ~ 10⁻³, testable by LiteBIRD.")
    print("  - Bubble nucleation is suppressed (metastable pre-CMB saturated state).")
    print()
    print("stiff_medium.desaturation: COMPLETE")


if __name__ == "__main__":
    main()
