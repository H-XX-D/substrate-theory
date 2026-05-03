"""Kink-antikink scattering dynamics test — §§18.37, 18.48-49, 18.30.

Tests:
1. Pair production threshold for M_K = 27 GeV  (expected E_min = 54 GeV)
2. Bhabha scattering cross-section at √s = 100 GeV
3. Klein-Nishina (Compton) cross-section at 1 MeV photon energy
4. Kink-antikink annihilation kinematics
5. Elastic kink-kink scattering
6. Collider event simulation (kink_antikink and electron_positron beams)
7. Cross-section energy dependence scan
8. Conservation law verification for all processes

Run with:
    cd "/Users/hendrixx./Desktop/untitled folder" && PYTHONPATH=src python3 scripts/scattering_test.py
"""

import math

import numpy as np

from stiff_medium.multi_kink import Kink
from stiff_medium.scattering import (
    GEV_INV2_TO_M2,
    M_ELECTRON_GEV,
    M_K_CANONICAL,
    ALPHA,
    KinkScattering,
    ScatteringEvent,
    annihilation_cross_section,
    bhabha_scattering_cross_section,
    compton_cross_section,
    elastic_cross_section,
    pair_production_threshold,
    simulate_collider_event,
)


# ---------------------------------------------------------------------------
# Output helpers — same style as multi_kink_binding_test.py
# ---------------------------------------------------------------------------


def header(title: str) -> None:
    """Print a section header in the style used across substrate scripts."""
    print("\n" + "=" * 72)
    print(f"  {title}")
    print("=" * 72 + "\n")


def _pass_fail(condition: bool) -> str:
    return "PASS" if condition else "FAIL"


# ---------------------------------------------------------------------------
# Test 1 — Pair production threshold
# ---------------------------------------------------------------------------


def test_pair_production_threshold() -> None:
    header("1. PAIR PRODUCTION THRESHOLD  (§18.49, §18.53.2)")

    M_K = M_K_CANONICAL  # 27.0 GeV (§18.22)
    E_min = pair_production_threshold(M_K)

    print(f"Kink rest mass   M_K         = {M_K:.4f} GeV  (§18.22 canonical)")
    print(f"Threshold energy E_min       = {E_min:.4f} GeV")
    print(f"Expected         2 × M_K     = {2 * M_K:.4f} GeV")
    print()

    expected = 2.0 * M_K
    ok_value = abs(E_min - expected) < 1e-9
    print(f"  E_min == 2 M_K             : {_pass_fail(ok_value)}  "
          f"(got {E_min:.6f}, expected {expected:.6f})")

    # Kinematic check: photon at threshold has zero kink c.m. momentum
    p_cm_at_threshold = math.sqrt(
        max((E_min / 2.0) ** 2 - M_K**2, 0.0)
    )
    ok_pcm = p_cm_at_threshold < 1e-6
    print(f"  p_cm at threshold ~ 0      : {_pass_fail(ok_pcm)}  "
          f"(p_cm = {p_cm_at_threshold:.2e} GeV)")

    # Just above threshold: kinks should be nearly at rest
    E_above = E_min * 1.01
    p_cm_above = math.sqrt(max((E_above / 2.0) ** 2 - M_K**2, 0.0))
    ok_above_thresh = p_cm_above > 0.0
    print(f"  E = 1.01 × E_min: p_cm > 0 : {_pass_fail(ok_above_thresh)}  "
          f"(p_cm = {p_cm_above:.4f} GeV)")

    # Below threshold: pair production forbidden
    E_below = E_min * 0.99
    try:
        scatterer = KinkScattering(M_K=M_K, rng_seed=42)
        scatterer.pair_production(photon_energy=E_below, target=None)
        ok_raises = False
    except ValueError:
        ok_raises = True
    print(f"  E < threshold raises ValueError: {_pass_fail(ok_raises)}")

    print()
    print("Summary: pair production threshold is exactly 2 M_K = 54 GeV.")


# ---------------------------------------------------------------------------
# Test 2 — Bhabha cross-section at sqrt(s) = 100 GeV
# ---------------------------------------------------------------------------


def test_bhabha_cross_section() -> None:
    header("2. BHABHA SCATTERING  e+e- -> e+e-  (§18.49.8, QED inheritance)")

    sqrt_s = 100.0  # GeV  (LEP2 energy)
    sigma_gev2 = bhabha_scattering_cross_section(sqrt_s)
    sigma_m2 = sigma_gev2 * GEV_INV2_TO_M2
    sigma_pb = sigma_m2 / 1e-40  # convert m² → picobarn (1 pb = 10⁻⁴⁰ m²)

    print(f"Center-of-mass energy  √s          = {sqrt_s:.1f} GeV")
    print(f"Fine-structure constant α           = {ALPHA:.8f}")
    print()
    print(f"σ_Bhabha   [GeV⁻²]                = {sigma_gev2:.6e}")
    print(f"σ_Bhabha   [m²]                   = {sigma_m2:.6e}")
    print(f"σ_Bhabha   [pb]                   = {sigma_pb:.4f}")
    print()

    # Point cross-section at 100 GeV: σ_point = 4π α² / (3 s) ≈ 1.7 nb ≈ 1700 pb
    # Bhabha is dominated by t-channel exchange, so σ_Bhabha > σ_point
    sigma_point_pb = (4.0 * math.pi * ALPHA**2 / (3.0 * sqrt_s**2)) * GEV_INV2_TO_M2 / 1e-40
    print(f"σ_point (4πα²/3s)   [pb]          = {sigma_point_pb:.4f}")
    print(f"σ_Bhabha / σ_point               = {sigma_pb / sigma_point_pb:.4f}")
    print()

    # Sanity checks: σ should be positive, fall as 1/s, and be near σ_point
    ok_positive = sigma_gev2 > 0.0
    ok_order = 0.1 < sigma_pb / sigma_point_pb < 100.0  # within 2 orders of magnitude
    ok_scale = 1.0 < sigma_pb < 1e5  # expect ~1–10^4 pb range for LEP energies
    print(f"  σ > 0                          : {_pass_fail(ok_positive)}")
    print(f"  σ within 2 orders of σ_point   : {_pass_fail(ok_order)}")
    print(f"  σ in range [1, 1e5] pb         : {_pass_fail(ok_scale)}")

    # Energy dependence: σ(200 GeV) < σ(100 GeV)  (falls as 1/s)
    sigma_200 = bhabha_scattering_cross_section(200.0)
    ok_falls = sigma_200 < sigma_gev2
    print(f"  σ(200 GeV) < σ(100 GeV) [1/s] : {_pass_fail(ok_falls)}")

    # Ratio should be ~4 (σ ∝ 1/s → 4x drop from 100 to 200 GeV)
    ratio = sigma_gev2 / sigma_200
    ok_ratio = 3.0 < ratio < 8.0
    print(f"  σ(100)/σ(200) ≈ 4 (got {ratio:.2f}) : {_pass_fail(ok_ratio)}")


# ---------------------------------------------------------------------------
# Test 3 — Compton / Klein-Nishina cross-section at 1 MeV
# ---------------------------------------------------------------------------


def test_compton_cross_section() -> None:
    header("3. COMPTON SCATTERING  gamma+e -> gamma+e  Klein-Nishina  (§18.49.8)")

    E_gamma_MeV = 1.0   # MeV
    E_gamma_GeV = E_gamma_MeV * 1e-3

    sigma_kn_gev2 = compton_cross_section(E_gamma_GeV)
    sigma_kn_m2   = sigma_kn_gev2 * GEV_INV2_TO_M2
    # Thomson cross-section σ_T = 6.6524 × 10⁻²⁹ m² (CODATA)
    sigma_T_m2 = 6.6524587e-29  # m²

    print(f"Photon energy   E_γ                = {E_gamma_MeV:.1f} MeV  = {E_gamma_GeV:.4f} GeV")
    print(f"Electron mass   m_e                = {M_ELECTRON_GEV * 1e3:.6f} MeV")
    x = E_gamma_GeV / M_ELECTRON_GEV
    print(f"Dimensionless   x = E_γ/m_e        = {x:.6f}")
    print()
    print(f"σ_KN   [GeV⁻²]                    = {sigma_kn_gev2:.6e}")
    print(f"σ_KN   [m²]                       = {sigma_kn_m2:.6e}")
    print(f"σ_T    [m²] (Thomson reference)   = {sigma_T_m2:.6e}")
    print(f"σ_KN / σ_T                        = {sigma_kn_m2 / sigma_T_m2:.6f}")
    print()

    # At 1 MeV (x ≈ 1.96) the KN cross-section should be below Thomson
    ok_positive = sigma_kn_gev2 > 0.0
    # At x~2 we expect σ_KN/σ_T ≈ 0.68 (from known tables)
    ratio_kn_t = sigma_kn_m2 / sigma_T_m2
    ok_below_thomson = ratio_kn_t < 1.0
    # At 1 MeV, x = E_γ/m_e ≈ 1.96; the Klein-Nishina formula gives σ_KN/σ_T ≈ 0.32
    # (verified against NIST/PDG tables: σ_KN ≈ 2.1×10⁻²⁹ m², σ_T = 6.65×10⁻²⁹ m²).
    ok_range = 0.20 < ratio_kn_t < 1.0  # correct range for x ~ 2 (Klein-Nishina suppression)
    print(f"  σ_KN > 0                        : {_pass_fail(ok_positive)}")
    print(f"  σ_KN < σ_T (below Thomson)      : {_pass_fail(ok_below_thomson)}")
    print(f"  0.20 < σ_KN/σ_T < 1.0 (x~2)   : {_pass_fail(ok_range)}")

    # Low-energy limit: x → 0  →  σ_KN → σ_T
    sigma_kn_low = compton_cross_section(1e-6)  # 1 keV
    sigma_kn_low_m2 = sigma_kn_low * GEV_INV2_TO_M2
    ratio_low = sigma_kn_low_m2 / sigma_T_m2
    ok_thomson_limit = abs(ratio_low - 1.0) < 0.01  # should be within 1% of σ_T
    print(f"  x→0 limit: σ_KN/σ_T = {ratio_low:.5f} (expect ~1.0): {_pass_fail(ok_thomson_limit)}")

    # High-energy limit: σ ∝ ln(2x)/x (decreasing)
    sigma_high_1 = compton_cross_section(100.0)   # 100 GeV
    sigma_high_2 = compton_cross_section(1000.0)  # 1 TeV
    ok_high_decreasing = sigma_high_2 < sigma_high_1
    print(f"  High-E: σ(1 TeV) < σ(100 GeV)  : {_pass_fail(ok_high_decreasing)}")


# ---------------------------------------------------------------------------
# Test 4 — Kink-antikink annihilation kinematics
# ---------------------------------------------------------------------------


def test_pair_annihilation() -> None:
    header("4. KINK-ANTIKINK ANNIHILATION  kink+antikink -> 2 photons  (§18.37, §18.53.2)")

    M_K = M_K_CANONICAL  # 27 GeV
    scatterer = KinkScattering(M_K=M_K, rng_seed=42)

    # Head-on collision: kink moves in +x, antikink in -x
    # Each with small kinetic energy (non-relativistic ~ 1 GeV lab kinetic)
    KE = 5.0  # GeV kinetic energy each
    kink = Kink(
        position=np.array([-10.0, 0.0, 0.0]),
        velocity=np.array([+KE, 0.0, 0.0]),
        chirality=+1, winding=1, mass=M_K,
    )
    antikink = Kink(
        position=np.array([+10.0, 0.0, 0.0]),
        velocity=np.array([-KE, 0.0, 0.0]),
        chirality=-1, winding=1, mass=M_K,
    )

    event = scatterer.pair_annihilation(kink, antikink)

    E_in = math.sqrt(M_K**2 + KE**2) + math.sqrt(M_K**2 + KE**2)
    p_in = kink.velocity + antikink.velocity  # = 0 for symmetric head-on

    print(f"Kink mass          M_K        = {M_K:.2f} GeV")
    print(f"Beam kinetic energy KE each   = {KE:.2f} GeV")
    print(f"Total incoming energy E_in    = {E_in:.4f} GeV")
    print(f"Total incoming momentum |p_in| = {np.linalg.norm(p_in):.2e} GeV")
    print()
    print(f"√s (c.m. energy)              = {event.center_of_mass_energy:.4f} GeV")
    print(f"Process type                  = {event.process_type}")
    print(f"Q_value (energy to radiation) = {event.Q_value:.4f} GeV")
    print(f"Cross-section σ               = {event.cross_section:.4e} m²")
    print()

    # Outgoing photons
    ph1, ph2 = event.outgoing_kinks
    E_ph1 = math.sqrt(np.dot(ph1.velocity, ph1.velocity))
    E_ph2 = math.sqrt(np.dot(ph2.velocity, ph2.velocity))
    p_ph = ph1.velocity + ph2.velocity
    print(f"Photon 1 energy   E_γ1        = {E_ph1:.4f} GeV")
    print(f"Photon 2 energy   E_γ2        = {E_ph2:.4f} GeV")
    print(f"Photon 1 momentum direction   = {ph1.velocity / (E_ph1 + 1e-30)}")
    print(f"Total outgoing momentum |Δp|  = {np.linalg.norm(p_ph):.4e} GeV")
    print()

    # Checks
    ok_type = event.process_type == "annihilation"
    ok_energy_conserved = event.energy_conserved
    ok_momentum_conserved = event.momentum_conserved
    ok_q_positive = event.Q_value > 0.0
    ok_chirality_out = ph1.chirality == 0 and ph2.chirality == 0  # photons
    ok_two_photons = len(event.outgoing_kinks) == 2
    ok_sigma_positive = event.cross_section > 0.0

    print(f"  Process type == 'annihilation'  : {_pass_fail(ok_type)}")
    print(f"  Energy conserved               : {_pass_fail(ok_energy_conserved)}")
    print(f"  Momentum conserved             : {_pass_fail(ok_momentum_conserved)}")
    print(f"  Q_value > 0 (exothermic)       : {_pass_fail(ok_q_positive)}")
    print(f"  2 outgoing photons             : {_pass_fail(ok_two_photons)}")
    print(f"  Outgoing chirality = 0 (γ)     : {_pass_fail(ok_chirality_out)}")
    print(f"  σ > 0                          : {_pass_fail(ok_sigma_positive)}")


# ---------------------------------------------------------------------------
# Test 5 — Elastic kink-kink scattering
# ---------------------------------------------------------------------------


def test_elastic_scattering() -> None:
    header("5. ELASTIC KINK-KINK SCATTERING  (§18.48.3 potential)")

    M_K = M_K_CANONICAL
    scatterer = KinkScattering(M_K=M_K, rng_seed=0)

    KE = 10.0  # GeV kinetic energy
    k1 = Kink(
        position=np.array([-5.0, 0.5, 0.0]),
        velocity=np.array([+KE, 0.0, 0.0]),
        chirality=+1, winding=1, mass=M_K,
    )
    k2 = Kink(
        position=np.array([+5.0, 0.5, 0.0]),
        velocity=np.array([-KE, 0.0, 0.0]),
        chirality=+1, winding=1, mass=M_K,
    )

    b = 0.1  # impact parameter
    event = scatterer.elastic_scattering(k1, k2, impact_parameter=b)

    print(f"Kink mass      M_K             = {M_K:.2f} GeV")
    print(f"Kinetic energy KE each         = {KE:.2f} GeV")
    print(f"Impact parameter b             = {b}")
    print()
    print(f"√s (c.m. energy)               = {event.center_of_mass_energy:.4f} GeV")
    print(f"Process type                   = {event.process_type}")
    print(f"Cross-section σ                = {event.cross_section:.4e} m²")
    print()

    ok_type = event.process_type == "elastic"
    ok_energy = event.energy_conserved
    ok_momentum = event.momentum_conserved

    # Topology preserved: outgoing chiralities same as incoming
    in_chiralities = [k.chirality for k in event.incoming_kinks]
    out_chiralities = [k.chirality for k in event.outgoing_kinks]
    ok_topology = sorted(in_chiralities) == sorted(out_chiralities)

    ok_n_in = event.multiplicity_in == 2
    ok_n_out = event.multiplicity_out == 2
    ok_sigma = event.cross_section > 0.0

    print(f"  Process type == 'elastic'     : {_pass_fail(ok_type)}")
    print(f"  Energy conserved              : {_pass_fail(ok_energy)}")
    print(f"  Momentum conserved            : {_pass_fail(ok_momentum)}")
    print(f"  Topology preserved (chirality): {_pass_fail(ok_topology)}")
    print(f"  N_in = N_out = 2              : {_pass_fail(ok_n_in and ok_n_out)}")
    print(f"  σ > 0                         : {_pass_fail(ok_sigma)}")


# ---------------------------------------------------------------------------
# Test 6 — Collider event simulation
# ---------------------------------------------------------------------------


def test_collider_event() -> None:
    header("6. COLLIDER EVENT SIMULATION  simulate_collider_event()  (§§18.30, 18.37, 18.49)")

    M_K = M_K_CANONICAL  # 27 GeV
    # Beam energy above threshold: √s = 2 × 30 = 60 GeV > 2 M_K = 54 GeV
    beam_energy = 30.0  # GeV per beam

    print(f"Kink mass       M_K            = {M_K:.1f} GeV")
    print(f"Beam energy per particle       = {beam_energy:.1f} GeV")
    print(f"√s = 2 × beam_energy           = {2*beam_energy:.1f} GeV")
    print(f"Pair production threshold      = {pair_production_threshold(M_K):.1f} GeV")
    print()

    # kink-antikink beam
    event_kk = simulate_collider_event(
        beam_energy=beam_energy, particle_type="kink_antikink", M_K=M_K, rng_seed=1
    )
    print(f"[kink_antikink] Process        = {event_kk.process_type}")
    print(f"[kink_antikink] √s             = {event_kk.center_of_mass_energy:.4f} GeV")
    print(f"[kink_antikink] σ              = {event_kk.cross_section:.4e} m²")
    print(f"[kink_antikink] N_out          = {event_kk.multiplicity_out}")
    print(f"[kink_antikink] Conserved?     = E:{event_kk.energy_conserved}  p:{event_kk.momentum_conserved}")
    print()

    # electron-positron beam at 100 GeV → expected Bhabha or kink pair
    event_ep = simulate_collider_event(
        beam_energy=50.0, particle_type="electron_positron", M_K=M_K, rng_seed=7
    )
    print(f"[e+e-] Process                 = {event_ep.process_type}")
    print(f"[e+e-] √s                      = {event_ep.center_of_mass_energy:.4f} GeV")
    print(f"[e+e-] σ                       = {event_ep.cross_section:.4e} m²")
    print()

    # Checks
    valid_types = {"elastic", "inelastic", "pair_production", "annihilation"}
    ok_type_kk = event_kk.process_type in valid_types
    ok_type_ep = event_ep.process_type in valid_types
    ok_physical_kk = event_kk.is_physical
    ok_sigma_kk = event_kk.cross_section > 0.0

    print(f"  kink_antikink process is valid    : {_pass_fail(ok_type_kk)}")
    print(f"  e+e- process is valid             : {_pass_fail(ok_type_ep)}")
    print(f"  kink_antikink event is physical   : {_pass_fail(ok_physical_kk)}")
    print(f"  σ > 0                             : {_pass_fail(ok_sigma_kk)}")

    # Below-threshold should raise
    try:
        simulate_collider_event(
            beam_energy=1.0, particle_type="photon", M_K=M_K, rng_seed=0
        )
        ok_raises = False
    except ValueError:
        ok_raises = True
    print(f"  Below-threshold photon raises ValueError: {_pass_fail(ok_raises)}")


# ---------------------------------------------------------------------------
# Test 7 — Cross-section energy scan
# ---------------------------------------------------------------------------


def test_cross_section_scan() -> None:
    header("7. CROSS-SECTION ENERGY SCAN  (§§18.48.3, 18.49.8)")

    M_K = M_K_CANONICAL
    E_threshold = pair_production_threshold(M_K)

    energies_gev = [55.0, 80.0, 100.0, 200.0, 500.0, 1000.0]

    col = 14
    print(
        f"  {'√s (GeV)':>{col}}  {'σ_el (GeV⁻²)':>{col}}  "
        f"{'σ_ann (GeV⁻²)':>{col}}  {'σ_total (GeV⁻²)':>{col}}  "
        f"{'σ_Bhabha (pb)':>{col}}"
    )
    print("  " + "-" * (col * 5 + 10))

    prev_sigma_total = None
    all_decreasing = True

    for E in energies_gev:
        sig_el  = elastic_cross_section(E, M_K)
        sig_ann = annihilation_cross_section(E, M_K)
        sig_tot = sig_el + sig_ann
        sig_bha_pb = bhabha_scattering_cross_section(E) * GEV_INV2_TO_M2 / 1e-40

        print(
            f"  {E:>{col}.1f}  {sig_el:>{col}.4e}  "
            f"{sig_ann:>{col}.4e}  {sig_tot:>{col}.4e}  "
            f"{sig_bha_pb:>{col}.4f}"
        )

        if prev_sigma_total is not None and sig_tot >= prev_sigma_total:
            all_decreasing = False
        prev_sigma_total = sig_tot

    print()
    print(f"  σ_total decreases with energy (1/s behavior): {_pass_fail(all_decreasing)}")

    # All cross-sections positive above threshold
    all_positive = all(
        elastic_cross_section(E, M_K) >= 0 and annihilation_cross_section(E, M_K) >= 0
        for E in energies_gev
    )
    print(f"  All cross-sections >= 0 above threshold: {_pass_fail(all_positive)}")

    # Below threshold: elastic and annihilation both 0
    E_below = E_threshold * 0.5
    ok_below = (
        elastic_cross_section(E_below, M_K) == 0.0
        and annihilation_cross_section(E_below, M_K) == 0.0
    )
    print(f"  σ_el = σ_ann = 0 below threshold: {_pass_fail(ok_below)}")


# ---------------------------------------------------------------------------
# Test 8 — Conservation law verification
# ---------------------------------------------------------------------------


def test_conservation_laws() -> None:
    header("8. CONSERVATION LAW VERIFICATION  (energy + momentum for all processes)")

    M_K = M_K_CANONICAL
    scatterer = KinkScattering(M_K=M_K, rng_seed=99)

    processes: list[tuple[str, ScatteringEvent]] = []

    # Annihilation at multiple energies
    for KE in [1.0, 5.0, 20.0]:
        kink = Kink(
            position=np.zeros(3),
            velocity=np.array([+KE, 0.0, 0.0]),
            chirality=+1, winding=1, mass=M_K,
        )
        antikink = Kink(
            position=np.zeros(3),
            velocity=np.array([-KE, 0.0, 0.0]),
            chirality=-1, winding=1, mass=M_K,
        )
        ev = scatterer.pair_annihilation(kink, antikink)
        processes.append((f"annihilation KE={KE:.0f}GeV", ev))

    # Pair production
    E_min = pair_production_threshold(M_K)
    for E_gamma in [E_min * 1.01, E_min * 1.5, E_min * 2.0]:
        ev = scatterer.pair_production(photon_energy=E_gamma, target=None)
        processes.append((f"pair_prod E_γ={E_gamma:.1f}GeV", ev))

    # Elastic scattering
    for KE in [5.0, 30.0]:
        k1 = Kink(position=np.zeros(3), velocity=np.array([+KE, 0.0, 0.0]),
                  chirality=+1, winding=1, mass=M_K)
        k2 = Kink(position=np.zeros(3), velocity=np.array([-KE, 0.0, 0.0]),
                  chirality=+1, winding=1, mass=M_K)
        ev = scatterer.elastic_scattering(k1, k2, impact_parameter=0.5)
        processes.append((f"elastic    KE={KE:.0f}GeV", ev))

    col_n = 38
    col_s = 8
    print(f"  {'Process':<{col_n}}  {'E_ok':{col_s}}  {'p_ok':{col_s}}  {'physical':{col_s}}")
    print("  " + "-" * (col_n + col_s * 3 + 6))

    all_physical = True
    for name, ev in processes:
        e_ok = "PASS" if ev.energy_conserved else "FAIL"
        p_ok = "PASS" if ev.momentum_conserved else "FAIL"
        phys = "PASS" if ev.is_physical else "FAIL"
        if not ev.is_physical:
            all_physical = False
        print(f"  {name:<{col_n}}  {e_ok:{col_s}}  {p_ok:{col_s}}  {phys:{col_s}}")

    print()
    print(f"  All events physically consistent: {_pass_fail(all_physical)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print()
    print("=" * 72)
    print("  KINK-ANTIKINK SCATTERING  —  Substrate-Mechanical Collider Physics")
    print("  Spec refs: §§18.37, 18.48-49, 18.49.8, 18.53.2, 18.30")
    print("=" * 72)

    test_pair_production_threshold()
    test_bhabha_cross_section()
    test_compton_cross_section()
    test_pair_annihilation()
    test_elastic_scattering()
    test_collider_event()
    test_cross_section_scan()
    test_conservation_laws()

    print()
    print("=" * 72)
    print("  All tests completed.  Check PASS/FAIL markers above.")
    print("=" * 72)
    print()


if __name__ == "__main__":
    main()
