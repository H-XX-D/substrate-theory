"""Atomic emission/absorption spectroscopy in our model (§18.24).

Demonstrates the §18.24 wave-particle picture concretely:

Setup:
- Atom A: excited electron in n=2 Bohr orbit, radiating energy as it
  decays to n=1 (per §18.19 EM radiation reaction).
- Wave field: tracks the EM field oscillation propagating from A.
- Atom B: distant, with electron in n=1 ground state. Can absorb wave
  energy if frequency matches its n=1→n=2 transition.

Predicts:
1. Emission frequency ω = (E_2 − E_1)/ℏ (Bohr correspondence).
2. Wave propagates at c through medium.
3. Atom B absorbs at the matching frequency, exciting electron
   from n=1 to n=2.
4. Energy is conserved: A loses ΔE, field carries ΔE, B gains ΔE.
"""

import numpy as np

from stiff_medium.em_field import EMField1D


# Atomic units: a₀ = 1, m_e = 1, ℏ = 1, e = 1, c = 1/α ≈ 137 (in atomic units)
# For simplicity, we'll use a normalized c=1 (so all lengths are c×time)

# Bohr energy levels for hydrogen (negative bound state energies)
def bohr_energy(n: int, Z: int = 1) -> float:
    """E_n = -Z²/(2 n²) hartree."""
    return -Z**2 / (2 * n**2)


# Bohr orbit radius
def bohr_radius(n: int, Z: int = 1) -> float:
    return n**2 / Z


def main():
    print("Atomic emission/absorption spectroscopy (spec §18.24)\n")

    # Hydrogen 2 → 1 transition (Lyman alpha)
    Z = 1
    n_initial = 2
    n_final = 1

    E_init = bohr_energy(n_initial, Z)  # -0.125 hartree
    E_final = bohr_energy(n_final, Z)   # -0.5 hartree
    deltaE = E_init - E_final           # 0.375 hartree

    # Frequency of emitted wave: ω = ΔE/ℏ. In atomic units (ℏ=1): ω = ΔE
    omega_emission = deltaE  # 0.375 in atomic units
    print(f"Bohr 2 → 1 transition (Lyman α):")
    print(f"  E_initial = {E_init:.4f} hartree")
    print(f"  E_final   = {E_final:.4f} hartree")
    print(f"  ΔE        = {deltaE:.4f} hartree")
    print(f"  Emission frequency ω = {omega_emission:.4f} (atomic units)")
    print(f"  In real units: 2.47 × 10¹⁵ Hz (UV)")
    print(f"  Wavelength: λ = 2π c/ω ≈ {2 * np.pi / omega_emission:.2f} a₀")
    print()

    # Set up wave-field simulation
    # Atom A at x = 0 (emitter), atom B at x = 50 (absorber)
    field = EMField1D(x_min=-10.0, x_max=70.0, n_points=801, c=1.0)

    DT = 0.05  # CFL: c·dt/dx = 1 × 0.05/0.1 = 0.5 ✓
    N_STEPS = 1500

    # Atom A oscillates at omega_emission (modeling decaying excited state)
    # Energy of emission: ΔE. Source amplitude proportional to acceleration.
    # For an oscillator at frequency ω with amplitude A_osc, source ~ ω² A_osc
    A_osc = 1.0
    source_amp = A_osc * omega_emission ** 2

    # Atom B at x = 50, oscillator with natural frequency = omega_emission
    # (resonant) or different (non-resonant)
    absorber_x = 50.0
    omega_absorber = omega_emission  # set to resonant
    abs_pos, abs_vel, abs_max = 0.0, 0.0, 0.0

    # Track field evolution
    for k in range(N_STEPS):
        t = k * DT
        # Atom A emits — model as decaying oscillation at omega_emission
        # Damp the source slowly to simulate finite excited-state lifetime
        decay = np.exp(-t / 200.0)
        src = source_amp * decay * np.sin(omega_emission * t)
        field.step(DT, {0.0: src})

        # Atom B response: oscillator driven by field gradient
        force_on_b = field.gradient_at(absorber_x) - omega_absorber**2 * abs_pos - 0.005 * abs_vel
        abs_vel += force_on_b * DT
        abs_pos += abs_vel * DT
        abs_max = max(abs_max, abs(abs_pos))

        if k in (0, 100, 500, 1000, 1499):
            print(f"  step {k:>4} (t={t:>6.1f}): "
                  f"field@A={field.value_at(0.0):>+8.4f}  "
                  f"field@B={field.value_at(50.0):>+8.4f}  "
                  f"abs_B_pos={abs_pos:>+8.4f}")

    print(f"\nResonant absorber max displacement: {abs_max:.4f}")

    # Now run with NON-resonant absorber
    print("\nNow with NON-RESONANT absorber (ω = 2 × emission)\n")
    field2 = EMField1D(x_min=-10.0, x_max=70.0, n_points=801, c=1.0)
    omega_off = 2 * omega_emission
    abs_pos2, abs_vel2, abs_max2 = 0.0, 0.0, 0.0
    for k in range(N_STEPS):
        t = k * DT
        decay = np.exp(-t / 200.0)
        src = source_amp * decay * np.sin(omega_emission * t)
        field2.step(DT, {0.0: src})
        force_on_b = field2.gradient_at(absorber_x) - omega_off**2 * abs_pos2 - 0.005 * abs_vel2
        abs_vel2 += force_on_b * DT
        abs_pos2 += abs_vel2 * DT
        abs_max2 = max(abs_max2, abs(abs_pos2))

    print(f"Non-resonant absorber max displacement: {abs_max2:.4f}")
    print(f"\nResonant/non-resonant ratio: {abs_max / max(abs_max2, 1e-9):.2f}×")

    if abs_max > 5 * abs_max2:
        print("\n→ Atomic absorption is SELECTIVE: only at the matching transition frequency.")
        print("  This is the spec §18.24 picture: the wave is extended; absorption events")
        print("  occur only when ω matches the absorber's quantized transition energy.")
        print("  E = ℏω comes from the ABSORBER's structure, not the wave's.")


if __name__ == "__main__":
    main()
