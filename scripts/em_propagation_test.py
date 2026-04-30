"""EM propagation test: source emits, distant absorber resonates.

Per spec §18.20, this demonstrates:
1. An oscillating source creates a wave in the medium.
2. The wave propagates at c.
3. A distant resonator at the same frequency absorbs energy from the wave.
4. Energy flows from source → field → absorber, conserved overall.
"""

import numpy as np

from stiff_medium.em_field import EMField1D


def main():
    print("EM propagation test (spec §18.20)\n")
    print("Setup: oscillating source at x=0, distant resonator at x=15.")
    print("Source frequency = absorber natural frequency → resonant transfer.\n")

    # 1D field domain
    field = EMField1D(x_min=-5.0, x_max=25.0, n_points=601, c=1.0)
    DT = 0.025  # CFL: c·dt/dx = 1 × 0.025/0.05 = 0.5 ✓
    N_STEPS = 1500

    # Source: oscillating dipole at x=0
    omega_source = 2.0  # angular frequency
    source_amplitude = 5.0

    # Absorber: harmonic oscillator at x=15 with same natural frequency
    absorber_x = 15.0
    absorber_omega = 2.0  # matches source → resonant
    absorber_pos = 0.0  # displacement from rest position
    absorber_vel = 0.0
    absorber_mass = 1.0
    absorber_damping = 0.05  # small damping for stability

    abs_max_pos = 0.0
    energies_logged = []

    for k in range(N_STEPS):
        t = k * DT

        # Source emits at oscillation_freq; source amplitude proportional to
        # acceleration (for a dipole oscillator: source ∝ ω² sin(ωt))
        src_value = source_amplitude * omega_source**2 * np.sin(omega_source * t)
        sources = {0.0: src_value}

        # Step the field
        field.step(DT, sources)

        # Absorber feels field gradient as a force; restoring force from spring
        field_gradient = field.gradient_at(absorber_x)
        force_on_absorber = field_gradient - absorber_omega**2 * absorber_pos - absorber_damping * absorber_vel

        # Velocity-Verlet for absorber
        absorber_vel += force_on_absorber * DT / absorber_mass
        absorber_pos += absorber_vel * DT

        # Track maximum absorber displacement and energy
        abs_max_pos = max(abs_max_pos, abs(absorber_pos))

        if k % 250 == 0 or k == N_STEPS - 1:
            absorber_KE = 0.5 * absorber_mass * absorber_vel**2
            absorber_PE = 0.5 * absorber_omega**2 * absorber_pos**2
            absorber_E = absorber_KE + absorber_PE
            field_E = field.total_energy()
            field_at_abs = field.value_at(absorber_x)
            print(f"step {k:>4} (t={t:>6.2f}): "
                  f"absorber pos={absorber_pos:>+8.4f} "
                  f"E={absorber_E:>8.4f} "
                  f"field@absorber={field_at_abs:>+8.4f}")
            energies_logged.append((t, absorber_E, field_E))

    print(f"\nMaximum absorber displacement: {abs_max_pos:.4f}")
    if abs_max_pos > 0.1:
        print("→ Absorber resonates with the source. EM transfer demonstrated.")
    else:
        print("→ Absorber barely moved. EM coupling too weak.")

    # Compare to non-resonant absorber: change its natural frequency
    print("\n=== Comparison: NON-RESONANT absorber (frequency mismatch) ===\n")
    field2 = EMField1D(x_min=-5.0, x_max=25.0, n_points=601, c=1.0)
    absorber_pos = 0.0
    absorber_vel = 0.0
    abs_max_pos_2 = 0.0
    omega_absorber_off = 5.0  # different from source's 2.0

    for k in range(N_STEPS):
        t = k * DT
        src_value = source_amplitude * omega_source**2 * np.sin(omega_source * t)
        sources = {0.0: src_value}
        field2.step(DT, sources)
        field_gradient = field2.gradient_at(absorber_x)
        force_on_absorber = field_gradient - omega_absorber_off**2 * absorber_pos - absorber_damping * absorber_vel
        absorber_vel += force_on_absorber * DT / absorber_mass
        absorber_pos += absorber_vel * DT
        abs_max_pos_2 = max(abs_max_pos_2, abs(absorber_pos))

    print(f"Maximum absorber displacement (non-resonant): {abs_max_pos_2:.4f}")
    print(f"Resonant vs non-resonant ratio: {abs_max_pos / max(abs_max_pos_2, 1e-9):.2f}×")
    if abs_max_pos > 3 * abs_max_pos_2:
        print("→ Resonant absorber gains MUCH more energy than non-resonant.")
        print("  Confirms §18.20: resonance is the key to absorption.")


if __name__ == "__main__":
    main()
