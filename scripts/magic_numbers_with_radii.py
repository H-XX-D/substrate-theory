"""Shell-filling with proper spatial radii and per-shell weights.

In a 3D harmonic oscillator (or any radial potential):
  - Each shell n has a characteristic radius r_n ~ √(n + 3/2) · ξ_HO
  - Each shell occupies a 3D shell-volume V_n ~ r_n²·dr_n
  - Each nucleon in shell n contributes weight w_n × mass

Weights matter because:
  - Outer-shell nucleons have larger r → smaller Coulomb energy
  - Outer-shell nucleons have smaller density → smaller substrate strain coupling
  - Each shell's binding contribution scales differently

The previous script counted states but ignored r and w. This one fixes that.
"""

from __future__ import annotations
import math


# Harmonic-oscillator shell radial scale: r_n = √(n + 3/2) × ξ_HO
# (in natural units where ξ_HO = 1)

def shell_radius(n: int) -> float:
    """RMS radius of HO shell n in units of ξ_HO."""
    return math.sqrt(n + 1.5)


def shell_volume_density(n: int) -> float:
    """Volume occupied by shell n: V_n ~ 4π r_n² dr_n.

    For HO, dr_n ≈ ξ_HO (shell thickness is constant in HO).
    """
    return 4.0 * math.pi * shell_radius(n)**2


def shell_weight_factor(n: int, n_states: int) -> float:
    """Weight per nucleon in shell n.

    In substrate model: weight ∝ 1/r_n² (closer nucleons couple more strongly
    to substrate strain).
    """
    return 1.0 / shell_radius(n)**2


# Subshell ordering with shell-index n (radial node + l)
# Format: (label, n_radial, l, j, n_states)
SUBSHELLS = [
    ('1s_1/2',  0, 0, 0.5, 2),
    ('1p_3/2',  0, 1, 1.5, 4),
    ('1p_1/2',  0, 1, 0.5, 2),
    ('1d_5/2',  0, 2, 2.5, 6),
    ('2s_1/2',  1, 0, 0.5, 2),
    ('1d_3/2',  0, 2, 1.5, 4),
    ('1f_7/2',  0, 3, 3.5, 8),
    ('2p_3/2',  1, 1, 1.5, 4),
    ('1f_5/2',  0, 3, 2.5, 6),
    ('2p_1/2',  1, 1, 0.5, 2),
    ('1g_9/2',  0, 4, 4.5, 10),
    ('1g_7/2',  0, 4, 3.5, 8),
    ('2d_5/2',  1, 2, 2.5, 6),
    ('2d_3/2',  1, 2, 1.5, 4),
    ('3s_1/2',  2, 0, 0.5, 2),
    ('1h_11/2', 0, 5, 5.5, 12),
    ('1h_9/2',  0, 5, 4.5, 10),
    ('2f_7/2',  1, 3, 3.5, 8),
    ('2f_5/2',  1, 3, 2.5, 6),
    ('3p_3/2',  2, 1, 1.5, 4),
    ('3p_1/2',  2, 1, 0.5, 2),
    ('1i_13/2', 0, 6, 6.5, 14),
]

REAL_MAGIC = {2, 8, 20, 28, 50, 82, 126}


def shell_principal_n(n_radial: int, l: int) -> int:
    """HO principal quantum number n = 2*n_radial + l."""
    return 2 * n_radial + l


def fill_shells_with_weights() -> list:
    """Return cumulative occupation, total radius-weighted mass, and binding."""
    cum = 0
    total_mass = 0.0
    total_strain = 0.0  # radius-weighted strain
    rows = []
    for label, n_rad, l, j, n_states in SUBSHELLS:
        n_principal = shell_principal_n(n_rad, l)
        r = shell_radius(n_principal)
        w = shell_weight_factor(n_principal, n_states)
        # Mass contribution per nucleon (1) × weight per shell
        mass_contrib = n_states * 1.0
        # Substrate strain coupling per nucleon: strain ~ K/r²
        # so strain energy per shell = n_states × strain coupling × cell volume
        strain_contrib = n_states * w
        cum += n_states
        total_mass += mass_contrib
        total_strain += strain_contrib
        is_magic = '★' if cum in REAL_MAGIC else ''
        rows.append({
            'label': label,
            'n_principal': n_principal,
            'l': l,
            'j': j,
            'n_states': n_states,
            'cumulative': cum,
            'r_shell': r,
            'weight': w,
            'mass_per_nucleon_in_shell': 1.0,  # each nucleon = 1 mass unit
            'strain_per_nucleon': w,
            'is_magic': is_magic,
            'cum_mass': total_mass,
            'cum_strain': total_strain,
        })
    return rows


def main() -> None:
    print("Shell filling with proper RADII and WEIGHTS")
    print("=" * 90)
    print()
    print("Each shell n has:")
    print("  - radius r_n = √(n + 3/2) × ξ_HO")
    print("  - weight per nucleon w_n = 1/r_n² (substrate coupling falls off with r²)")
    print()

    print(f"{'subshell':>10s} {'n':>3s} {'l':>3s} {'j':>5s} {'states':>7s} "
          f"{'cum':>5s} {'r/ξ':>8s} {'w':>8s} {'cum_strain':>12s} {'magic':>8s}")
    rows = fill_shells_with_weights()
    for row in rows:
        print(f"  {row['label']:>8s} {row['n_principal']:>2d} {row['l']:>2d} "
              f"{row['j']:>4.1f} {row['n_states']:>5d} {row['cumulative']:>5d} "
              f"{row['r_shell']:>6.3f}  {row['weight']:>6.3f}    "
              f"{row['cum_strain']:>10.3f}    {row['is_magic']:>6s}")

    print()
    print("KEY: weight per shell DECREASES with shell index n")
    print("  inner shell (n=0): w = 1/1.5 = 0.667")
    print("  outer shell (n=6): w = 1/7.5 = 0.133")
    print("  → inner-shell nucleons contribute 5× more substrate strain than outer-shell")

    print()
    print("=" * 90)
    print("Per-shell binding contribution (with weights AND radii respected):")
    print("=" * 90)
    print()
    print(f"{'shell label':>10s} {'A':>4s} {'r':>6s} {'BE_strong (×weight)':>22s} "
          f"{'BE_em (×Z²/r)':>18s}")

    # Compute BE contributions including radial dependence
    K_INTERNAL = 1.0
    K_PAIR = 1.0/125
    K_EM = 7.2973525643e-3

    for row in rows:
        if not row['is_magic']:
            continue
        A_shell = row['cumulative']
        r = row['r_shell']
        # BE_strong: each nucleon contributes K_INTERNAL × w_shell
        # Pair bonds also weighted by 1/r (since shared face area ~ 1/r)
        BE_strong = A_shell * K_INTERNAL * row['weight']
        BE_pair_bond = A_shell * (A_shell - 1) / 2 * K_PAIR / r  # /r for shell distance
        # BE_em: Coulomb scales as Z(Z-1)/r — electron coupling weighted
        Z = A_shell // 2  # rough estimate
        BE_coulomb = -Z * (Z - 1) * K_EM / r if r > 0 else 0
        print(f"  {row['label']:>8s}    {A_shell:>3d}  {r:>5.3f}  "
              f"{BE_strong + BE_pair_bond:>20.3f}    {BE_coulomb:>16.5f}")

    print()
    print("=" * 90)
    print("Comparison: are radii and weights now respected?")
    print("=" * 90)
    print()
    print("ANSWER: Yes — each shell has its own radius r_n and per-nucleon weight w_n.")
    print("  - Weights: inner-shell coupling is 5× stronger than outer-shell.")
    print("  - Radii: pair bonds /r and Coulomb repulsion /r both respect spatial extent.")
    print()
    print("This is now consistent with:")
    print("  - Mass scaling: each nucleon = 1 mass unit (no shell-dependent mass)")
    print("  - Coupling scaling: shell-dependent w via 1/r² substrate response")
    print("  - Coulomb: shell-dependent Z²/r repulsion")
    print()
    print("The remaining question: does the substrate Lagrangian DERIVE w = 1/r²")
    print("from first principles? In the HO this is standard (potential is r²/2),")
    print("but the substrate's L = ½K|∇P|² gives a different scaling. Need to check")
    print("whether the substrate's natural radial profile matches HO.")


if __name__ == "__main__":
    main()
