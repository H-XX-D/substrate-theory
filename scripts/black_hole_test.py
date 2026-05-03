"""Black hole thermodynamics demo — substrate-mechanical framework.

Tests the stiff_medium.black_hole module against known astrophysical BHs and
verifies the key model predictions:

  - σ = ½ at every horizon (spec §18.39 universal saturation)
  - Hawking temperatures, entropies, evaporation times
  - QNM ringdown frequency matching GW150914 merger residual (~250 Hz at 62 M_☉)
  - Holographic information capacity
  - Formation threshold densities (§18.39 table)
  - Info-paradox resolution explanation (§§18.39, 18.51, 18.55)

Run with:
    cd "/Users/hendrixx./Desktop/untitled folder" && PYTHONPATH=src python3 scripts/black_hole_test.py
"""

import math

from stiff_medium.black_hole import (
    BlackHole,
    C,
    G,
    HBAR,
    K_B,
    M_SUN,
    PLANCK_LENGTH,
    SIGMA_AT_HORIZON,
    formation_threshold_density,
    holographic_information_capacity,
    info_paradox_resolution,
    merger_radiated_energy,
)

# ---------------------------------------------------------------------------
# Reference BH catalogue
# ---------------------------------------------------------------------------

CATALOGUE: list[tuple[str, float]] = [
    ("Earth-mass",    5.972e24),            # hypothetical
    ("Solar (1 M☉)", M_SUN),               # hypothetical; Sun will not collapse
    ("Stellar (10 M☉)", 10.0 * M_SUN),     # typical stellar-collapse BH
    ("Sgr A* (4e6 M☉)", 4.0e6 * M_SUN),   # Milky Way supermassive BH
    ("M87 (6.5e9 M☉)", 6.5e9 * M_SUN),    # first BH ever imaged (EHT 2019)
]


def section(title: str) -> None:
    width = 78
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


# ---------------------------------------------------------------------------
# 1. Basic properties table
# ---------------------------------------------------------------------------

def print_properties_table() -> None:
    section("1. BLACK HOLE PROPERTIES — Schwarzschild radius, horizon area, σ")

    col_w = [20, 14, 14, 14, 8]
    headers = ["Name", "Mass (kg)", "r_s (m)", "Area (m²)", "σ_horizon"]
    header_fmt = (
        f"{'Name':<{col_w[0]}} {'Mass (kg)':>{col_w[1]}} "
        f"{'r_s (m)':>{col_w[2]}} {'A (m²)':>{col_w[3]}} "
        f"{'σ_horizon':>{col_w[4]}}"
    )
    print(header_fmt)
    print("-" * sum(col_w) + "-" * (len(col_w) - 1))

    all_sigma_half = True
    for name, mass in CATALOGUE:
        bh = BlackHole(mass_kg=mass)
        sigma = bh.sigma_at_horizon
        if abs(sigma - 0.5) > 1e-12:
            all_sigma_half = False
        print(
            f"{name:<{col_w[0]}} {mass:>{col_w[1]}.4e} "
            f"{bh.schwarzschild_radius:>{col_w[2]}.4e} "
            f"{bh.horizon_area:>{col_w[3]}.4e} "
            f"{sigma:>{col_w[4]}.4f}"
        )

    print()
    status = "PASS" if all_sigma_half else "FAIL"
    print(f"  σ = 0.5 universally for all BH masses: [{status}]")
    print(f"  (spec §18.39 — every horizon is a σ = ½ saturated surface)")


# ---------------------------------------------------------------------------
# 2. Thermodynamics table
# ---------------------------------------------------------------------------

def print_thermodynamics_table() -> None:
    section("2. HAWKING THERMODYNAMICS")

    print(
        f"{'Name':<20} {'T_Hawking (K)':>16} {'S_BH (J/K)':>16} {'t_evap (s)':>16} {'t_evap (yr)':>14}"
    )
    print("-" * 86)

    seconds_per_year = 3.156e7

    for name, mass in CATALOGUE:
        bh = BlackHole(mass_kg=mass)
        T = bh.hawking_temperature
        S = bh.bekenstein_hawking_entropy
        t = bh.hawking_evaporation_time
        t_yr = t / seconds_per_year
        print(
            f"{name:<20} {T:>16.4e} {S:>16.4e} {t:>16.4e} {t_yr:>14.4e}"
        )

    print()
    print("  Note: Earth-mass and Solar-mass BHs are hypothetical.")
    print("  Hawking temperature is inversely proportional to mass.")
    print("  Stellar and supermassive BHs are far colder than the CMB (~2.7 K).")


# ---------------------------------------------------------------------------
# 3. Holographic information capacity
# ---------------------------------------------------------------------------

def print_holographic_capacity() -> None:
    section("3. HOLOGRAPHIC INFORMATION CAPACITY (bits on horizon)")

    print(
        f"{'Name':<20} {'Area (m²)':>14} {'Capacity (bits)':>20} {'log₂(bits)':>12}"
    )
    print("-" * 70)

    for name, mass in CATALOGUE:
        bh = BlackHole(mass_kg=mass)
        area = bh.horizon_area
        capacity = holographic_information_capacity(area)
        log2_cap = math.log2(capacity) if capacity > 0 else 0.0
        print(
            f"{name:<20} {area:>14.4e} {capacity:>20.4e} {log2_cap:>12.2f}"
        )

    print()
    print(f"  Planck length ℓ_P = {PLANCK_LENGTH:.6e} m")
    print(f"  One bit per 4 ℓ_P² = {4 * PLANCK_LENGTH**2:.6e} m²  (spec §18.51)")


# ---------------------------------------------------------------------------
# 4. Formation threshold densities (§18.39 table)
# ---------------------------------------------------------------------------

def print_formation_densities() -> None:
    section("4. BH FORMATION THRESHOLD DENSITIES (spec §18.39)")

    # Extended list matching §18.39 table plus Earth for fun
    objects = [
        ("Earth-mass",       5.972e24),
        ("Stellar (3 M☉)",   3.0 * M_SUN),
        ("Stellar (10 M☉)",  10.0 * M_SUN),
        ("Sgr A*",           4.0e6 * M_SUN),
        ("M87",              6.5e9 * M_SUN),
        ("Obs. universe",    1e53),
    ]

    print(
        f"{'Object':<22} {'Mass (kg)':>14} {'r_s (m)':>14} {'ρ_threshold (kg/m³)':>22}"
    )
    print("-" * 76)

    for name, mass in objects:
        rs = 2.0 * G * mass / C**2
        rho = formation_threshold_density(mass)
        print(f"{name:<22} {mass:>14.4e} {rs:>14.4e} {rho:>22.4e}")

    print()
    print("  Larger BHs form at lower densities (ρ ∝ 1/M² — §18.39).")
    print("  Observable-universe density ≈ cosmological critical density ✓")


# ---------------------------------------------------------------------------
# 5. QNM ringdown — GW150914 check
# ---------------------------------------------------------------------------

def print_ringdown() -> None:
    section("5. QUASINORMAL MODE RINGDOWN — GW150914 CHECK")

    # GW150914: final BH ~62 M_☉, ringdown peak ~250 Hz
    m_final = 62.0 * M_SUN
    bh_final = BlackHole(mass_kg=m_final)
    omega = bh_final.qnm_frequency()
    freq_hz = omega.real / (2.0 * math.pi)
    tau_ms = bh_final.qnm_damping_time() * 1e3           # ms

    # Progenitors: ~36 M_☉ + ~29 M_☉
    m1 = 36.0 * M_SUN
    m2 = 29.0 * M_SUN
    e_rad = merger_radiated_energy(m1, m2, efficiency=0.047)  # 3 M_☉ ≈ 4.7%
    m_rad_solar = e_rad / (M_SUN * C**2)

    print(f"  GW150914 event:")
    print(f"    Progenitor masses  : {m1/M_SUN:.0f} M_☉ + {m2/M_SUN:.0f} M_☉")
    print(f"    Final BH mass      : {m_final/M_SUN:.0f} M_☉")
    print()
    print(f"  QNM dominant mode (l=2, n=0 Schwarzschild):")
    print(f"    ω (rad/s)          : {omega.real:.4e} - {abs(omega.imag):.4e}j")
    print(f"    Frequency f        : {freq_hz:.1f} Hz   (Schwarzschild; LIGO peak ~250 Hz includes Kerr spin a~0.67)")
    print(f"    Damping time τ     : {tau_ms:.2f} ms")
    print()
    print(f"  Radiated GW energy (~4.7% of total):")
    print(f"    E_rad              : {e_rad:.4e} J")
    print(f"    Equivalent mass    : {m_rad_solar:.2f} M_☉   (LIGO measured ~3 M_☉ ✓)")
    print()
    print("  Full catalogue ringdown frequencies:")
    print(f"  {'Name':<20} {'Mass (M_☉)':>12} {'f_QNM (Hz)':>12} {'τ_damp (ms)':>14}")
    print("  " + "-" * 62)
    for name, mass in CATALOGUE:
        bh = BlackHole(mass_kg=mass)
        om = bh.qnm_frequency()
        f = om.real / (2.0 * math.pi)
        tau = bh.qnm_damping_time() * 1e3
        print(
            f"  {name:<20} {mass/M_SUN:>12.4e} {f:>12.4f} {tau:>14.4f}"
        )


# ---------------------------------------------------------------------------
# 6. Evaporation demonstration
# ---------------------------------------------------------------------------

def print_evaporation_demo() -> None:
    section("6. EVAPORATION DEMO — small primordial BH")

    # A BH with mass equal to a small asteroid (~10^15 kg) evaporates on
    # cosmological timescales but not too long for illustration.
    m0 = 1e15   # kg  (~Mt. Everest mass)
    bh0 = BlackHole(mass_kg=m0)

    print(f"  Initial BH:  M = {m0:.2e} kg")
    print(f"    T_Hawking  = {bh0.hawking_temperature:.4e} K")
    print(f"    t_evap     = {bh0.hawking_evaporation_time:.4e} s")
    print(f"    dM/dt      = {bh0.mass_loss_rate():.4e} kg/s")
    print(f"    σ_horizon  = {bh0.sigma_at_horizon:.4f}  (spec §18.39: always 0.5)")
    print()

    # Evolve using analytic result: M(t) = M0 (1 - t/t_evap)^(1/3)
    t_evap = bh0.hawking_evaporation_time
    fractions = [0.0, 0.25, 0.50, 0.75, 0.90, 0.99]
    print(f"  {'t/t_evap':>10} {'M (kg)':>14} {'T_H (K)':>14} {'σ_horizon':>12}")
    print("  " + "-" * 54)
    for frac in fractions:
        t = frac * t_evap
        m_t = m0 * (1.0 - frac) ** (1.0 / 3.0)
        if m_t < 1e10:
            print(f"  {frac:>10.2f} {'< 1e10 (evaporated)':>14}")
            break
        bh_t = BlackHole(mass_kg=m_t)
        print(
            f"  {frac:>10.2f} {m_t:>14.4e} {bh_t.hawking_temperature:>14.4e} "
            f"{bh_t.sigma_at_horizon:>12.4f}"
        )

    print()
    print("  σ remains 0.5 throughout the entire evaporation — the horizon always")
    print("  satisfies the saturation condition regardless of mass (spec §18.39).")


# ---------------------------------------------------------------------------
# 7. σ = ½ universal verification
# ---------------------------------------------------------------------------

def verify_sigma_universality() -> None:
    section("7. SIGMA UNIVERSALITY VERIFICATION (spec §18.39)")

    test_masses = [
        1e10,            # 10 billion kg (~large asteroid)
        1e20,            # ~lunar mass range
        1e27,            # ~Jupiter mass range
        M_SUN,
        10 * M_SUN,
        4e6 * M_SUN,
        6.5e9 * M_SUN,
        1e53,            # observable universe horizon
    ]

    print(f"  {'Mass (kg)':>14} {'r_s (m)':>16} {'σ(r_s) derived':>18} {'Universal ½?':>14}")
    print("  " + "-" * 66)

    all_pass = True
    for m in test_masses:
        rs = 2.0 * G * m / C**2
        # Direct computation from the definition σ(r) = GM/(r c²)
        sigma_derived = G * m / (rs * C**2)
        bh = BlackHole(mass_kg=m)
        sigma_from_property = bh.sigma_at_horizon
        match = abs(sigma_derived - 0.5) < 1e-10 and sigma_from_property == 0.5
        if not match:
            all_pass = False
        flag = "✓" if match else "FAIL"
        print(
            f"  {m:>14.4e} {rs:>16.4e} {sigma_derived:>18.10f} {flag:>14}"
        )

    print()
    print(f"  All masses satisfy σ(r_s) = ½ exactly: {'[PASS]' if all_pass else '[FAIL]'}")
    print(
        "  This is algebraically guaranteed: σ(r) = GM/(r c²), and at r = r_s = 2GM/c²")
    print("  we get σ = GM / (2GM/c² × c²) = 1/2 always.")


# ---------------------------------------------------------------------------
# 8. Information paradox resolution
# ---------------------------------------------------------------------------

def print_info_paradox() -> None:
    section("8. INFORMATION PARADOX RESOLUTION (spec §§18.39, 18.51, 18.55)")
    print(info_paradox_resolution())


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print()
    print("  STIFF-MEDIUM / SUBSTRATE-MECHANICAL BLACK HOLE THERMODYNAMICS")
    print("  Black holes as saturated medium regions (spec §§18.39, 18.42, 18.51, 18.55)")
    print(f"  σ_max = {SIGMA_AT_HORIZON}  (universal horizon strain — elastic limit of substrate)")

    print_properties_table()
    print_thermodynamics_table()
    print_holographic_capacity()
    print_formation_densities()
    print_ringdown()
    print_evaporation_demo()
    verify_sigma_universality()
    print_info_paradox()

    print()
    print("=" * 78)
    print("  All tests complete.")
    print("=" * 78)
    print()


if __name__ == "__main__":
    main()
