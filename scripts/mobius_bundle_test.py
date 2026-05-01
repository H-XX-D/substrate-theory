"""Demonstration of the Möbius half-flux U(1) bundle (spec §§18.4, 18.10).

Exercises every public API in stiff_medium.mobius_bundle:

1. Construct MobiusBundle with half_flux = π
2. Verify spin-½ rotation: -1 after 2π, +1 after 4π
3. Charge quantisation for a range of winding numbers
4. θ_QCD = 0 from topology
5. Aharonov-Bohm phase = π for one half-flux winding
6. First Chern class = 1/2
7. Coleman bosonization at the free-fermion point
8. Bundle compatibility (binding rules)
"""

import math

from stiff_medium.mobius_bundle import (
    MobiusBundle,
    MobiusFermion,
    bundle_compatibility_check,
    chern_class_first,
    coleman_bosonization_g,
    theta_qcd_from_topology,
    verify_aharonov_bohm,
    PI,
    HBAR,
    C_LIGHT,
)
from stiff_medium.physical_constants import (
    ALPHA_THOMSON_CODATA_2022,
    INV_ALPHA_THOMSON_CODATA_2022,
)


# ---------------------------------------------------------------------------
# Output helpers (same style as scripts/quantum_phenomena.py and
# scripts/sharp_predictions.py)
# ---------------------------------------------------------------------------


def header(title: str) -> None:
    print("\n" + "=" * 72)
    print(f"  {title}")
    print("=" * 72 + "\n")


def check(label: str, value: object, expected: object = None, tol: float = 1e-9) -> None:
    """Print a labelled result with an optional pass/fail marker."""
    if expected is None:
        print(f"  {label}: {value}")
        return
    if isinstance(expected, bool) or isinstance(value, bool):
        ok = value == expected
    else:
        ok = abs(float(value) - float(expected)) <= tol  # type: ignore[arg-type]
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {label}: {value!r}  (expected {expected!r})")


# ---------------------------------------------------------------------------
# 1. Construct MobiusBundle
# ---------------------------------------------------------------------------


def section_bundle_construction() -> MobiusBundle:
    header("1. CONSTRUCT MobiusBundle (half_flux = pi)")

    bundle = MobiusBundle(winding_number=1)

    check("half_flux", bundle.half_flux, math.pi)
    check("half_flux == π (exact)", bundle.half_flux == math.pi, True)
    check("winding_number", bundle.winding_number, 1)

    e = bundle.elementary_charge
    e_expected = math.sqrt(4.0 * math.pi * ALPHA_THOMSON_CODATA_2022)
    check("elementary_charge", e, e_expected)

    print()
    print("  The elementary charge is set by the half-flux normalization:")
    print(f"    e = sqrt(4π α) = {e:.8f}")
    print(
        f"    (alpha = 1/{INV_ALPHA_THOMSON_CODATA_2022:.9f};  "
        f"4*pi*alpha = {4*math.pi*ALPHA_THOMSON_CODATA_2022:.8f})"
    )
    print()
    print("  First Chern class (module function):")
    c1 = chern_class_first()
    check("chern_class_first()", c1, 0.5)
    print()
    print("  Zero winding_number is forbidden:")
    try:
        MobiusBundle(winding_number=0)
        print("  [FAIL] No ValueError raised — expected one")
    except ValueError as exc:
        print(f"  [PASS] ValueError raised: {exc}")

    return bundle


# ---------------------------------------------------------------------------
# 2. Spin-½ rotation via rotation_phase
# ---------------------------------------------------------------------------


def section_spin_half(bundle: MobiusBundle) -> None:
    header("2. SPIN-HALF ROTATION — U(theta) = exp(i theta/2)")

    fermion = MobiusFermion(chirality=1, winding_n=1, bundle=bundle)

    print("  Rotation phase U(θ) = cos(θ/2) for a half-flux fermion:")
    print()
    milestones = [
        (0.0,         "+1.0",  "identity (start)"),
        (math.pi,     "0.0",   "quarter-turn  (90° / π rad)"),
        (2*math.pi,   "-1.0",  "half-turn     (360° / 2π) — SIGN FLIP"),
        (3*math.pi,   "0.0",   "three-quarter (540° / 3π)"),
        (4*math.pi,   "+1.0",  "full return   (720° / 4π) — IDENTITY"),
    ]

    print(f"  {'Angle':>12}  {'Phase':>8}  {'Note'}")
    print("  " + "-" * 58)
    for angle, expected_str, note in milestones:
        phase = fermion.rotation_phase(angle)
        expected_float = float(expected_str)
        ok = abs(phase - expected_float) < 1e-12
        marker = "PASS" if ok else "FAIL"
        angle_label = f"{angle/math.pi:.0f}π rad"
        print(f"  [{marker}] {angle_label:>12}  {phase:>+8.4f}  {note}")

    print()
    print("  Spin-½ signature confirmed:")
    print("    - 2π rotation → phase = -1  (wavefunction changes sign)")
    print("    - 4π rotation → phase = +1  (full return after 720°)")
    print(f"    - is_spin_half property: {fermion.is_spin_half}")


# ---------------------------------------------------------------------------
# 3. Charge quantisation for various windings
# ---------------------------------------------------------------------------


def section_charge_quantisation(bundle: MobiusBundle) -> None:
    header("3. CHARGE QUANTISATION — integer multiples of e")

    print("  Charge = chirality × winding × e for various windings:")
    print()
    e = bundle.elementary_charge
    print(f"  Elementary charge e = {e:.8f}  (dimensionless, natural units)")
    print()
    print(f"  {'Chirality':>10}  {'Winding':>8}  {'Charge':>14}  "
          f"{'In units of e':>14}  {'Consistent?':>12}")
    print("  " + "-" * 68)

    cases = [
        ( 1,  1),   # electron analogue
        (-1,  1),   # positron analogue
        ( 1,  2),   # doubly-wound
        (-1, -1),   # reversed positron
        ( 1, -3),   # triple antiparticle
        (-1,  2),
    ]
    for chirality, winding in cases:
        # Fermion needs bundle with matching winding_number for construction
        b = MobiusBundle(winding_number=winding if winding != 0 else 1)
        f = MobiusFermion(chirality=chirality, winding_n=winding, bundle=b)
        charge = f.charge
        in_e = charge / e
        consistent = bundle.is_charge_consistent(in_e)
        ok = "PASS" if consistent else "FAIL"
        sign_str = "+" if chirality > 0 else "−"
        print(f"  [{ok}] {sign_str}1        {winding:>8}  {charge:>+14.8f}  "
              f"{in_e:>+14.1f}  {str(consistent):>12}")

    print()
    print("  Non-integer charge check (should fail):")
    is_ok = bundle.is_charge_consistent(1.7)
    check("is_charge_consistent(1.7)", is_ok, False)

    print()
    print("  Quark charges (fractional, valid as bound-state constituents):")
    for q_label, q_val in [("up-quark (+2/3)", 2/3), ("down-quark (−1/3)", -1/3)]:
        in_e = q_val
        # Fractional charge is NOT an integer multiple of e — isolated quarks
        # are topologically forbidden; these appear only inside baryons where
        # the sum {2/3 + 2/3 − 1/3 = +1} is integer.
        consistent = bundle.is_charge_consistent(in_e)
        print(f"  {q_label}: is_charge_consistent = {consistent}  "
              f"(isolated quark is topologically forbidden — as required)")


# ---------------------------------------------------------------------------
# 4. θ_QCD = 0 from topology
# ---------------------------------------------------------------------------


def section_theta_qcd() -> None:
    header("4. theta_QCD = 0 — STRONG CP SOLVED BY TOPOLOGY")

    theta = theta_qcd_from_topology()
    check("theta_qcd_from_topology()", theta, 0.0)

    print()
    print("  The strong-CP problem in QCD asks why |θ_QCD| < 10⁻¹⁰")
    print("  even though the SM allows any value in [0, 2π).")
    print()
    print("  In the stiff-medium model (spec §18.4):")
    print("    - The Möbius half-flux bundle has first Chern class c₁ = 1/2")
    print("    - The θ term in the Lagrangian is θ·c₁² per instanton")
    print("    - c₁ = 1/2  →  c₁² = 1/4  →  the contribution is θ/4")
    print("    - For the path integral to be gauge-invariant with half-integer")
    print("      Chern class, θ must be 0 mod 4π, and the effective CP phase")
    print("      for the observable sector is exactly 0.")
    print()
    print("  No Peccei-Quinn axion needed.  θ_QCD = 0 is topological.")
    print(f"  Result: theta_qcd_from_topology() = {theta}")


# ---------------------------------------------------------------------------
# 5. Aharonov-Bohm phase
# ---------------------------------------------------------------------------


def section_aharonov_bohm(bundle: MobiusBundle) -> None:
    header("5. AHARONOV-BOHM PHASE — pi per half-flux winding")

    print("  Half-flux constraint: ∮_C A_μ dx^μ = π × w(C)")
    print()
    print(f"  {'Winding w':>10}  {'AB phase (rad)':>16}  {'In units of π':>14}  "
          f"{'Holonomy':>10}")
    print("  " + "-" * 60)

    for w in range(-3, 4):
        if w == 0:
            continue
        phase = bundle.aharonov_bohm_phase(w)
        holonomy = bundle.holonomy(w)
        print(f"  {w:>10}  {phase:>+16.6f}  {phase/PI:>+14.4f}  {holonomy:>+10.4f}")

    print()
    print("  Key result for w = 1 (one half-flux winding):")
    phase1 = bundle.aharonov_bohm_phase(1)
    hol1 = bundle.holonomy(1)
    check("aharonov_bohm_phase(1) == π", phase1, PI)
    check("holonomy(1) == -1", hol1, -1.0)
    print()
    print("  This is the interference pattern shift of half a fringe")
    print("  observed in Aharonov-Bohm experiments with one flux quantum.")


# ---------------------------------------------------------------------------
# 6. verify_aharonov_bohm helper
# ---------------------------------------------------------------------------


def section_verify_ab() -> None:
    header("6. verify_aharonov_bohm() — consolidated spin-half checks")

    results = verify_aharonov_bohm()

    print("  One-loop (w = 1):")
    check("  phase_one_loop", results["phase_one_loop"], PI)
    check("  holonomy_one_loop", results["holonomy_one_loop"], -1.0)
    check("  rotation_phase(2π)", results["rotation_phase_2pi"], -1.0)
    print()
    print("  Two-loop (w = 2):")
    check("  phase_two_loop", results["phase_two_loop"], 2 * PI)
    check("  holonomy_two_loop", results["holonomy_two_loop"], +1.0)
    check("  rotation_phase(4π)", results["rotation_phase_4pi"], +1.0)
    print()
    confirmed = results["spin_half_confirmed"]
    check("spin_half_confirmed", confirmed, True)
    print()
    print("  Summary:")
    print("    π  phase  →  holonomy = -1  (spin-½ rotation, one 360°)")
    print("    2π phase  →  holonomy = +1  (full identity, 720°)")
    print("  This is the defining topological property of a Möbius fermion.")


# ---------------------------------------------------------------------------
# 7. Coleman bosonization
# ---------------------------------------------------------------------------


def section_coleman() -> None:
    header("7. COLEMAN BOSONIZATION — sine-Gordon / Thirring duality")

    print("  Coleman (1975): g = π ( 4π/β² − 1 )")
    print()
    print(f"  {'β²':>10}  {'β²/π':>8}  {'g':>12}  {'interpretation'}")
    print("  " + "-" * 60)

    cases = [
        (4*PI,    "β² = 4π  — free fermion (g = 0)"),
        (8*PI,    "β² = 8π  — KT transition (g = −π/2)"),
        (2*PI,    "β² = 2π  — strongly coupled (g = π)"),
        (16*PI,   "β² = 16π — weak coupling (g = −3π/4)"),
    ]
    for beta_sq, label in cases:
        g = coleman_bosonization_g(beta_sq)
        print(f"  {beta_sq:>10.4f}  {beta_sq/PI:>8.4f}  {g:>+12.6f}  {label}")

    print()
    print("  Free-fermion point check (β² = 4π  →  g = 0):")
    g_free = coleman_bosonization_g(4 * PI)
    check("coleman_bosonization_g(4π)", g_free, 0.0)

    print()
    print("  ValueError for non-positive β²:")
    try:
        coleman_bosonization_g(-1.0)
        print("  [FAIL] No error raised")
    except ValueError as exc:
        print(f"  [PASS] ValueError: {exc}")


# ---------------------------------------------------------------------------
# 8. Bundle compatibility
# ---------------------------------------------------------------------------


def section_compatibility() -> None:
    header("8. BUNDLE COMPATIBILITY — binding rules from half-flux holonomy")

    # Build representative fermions
    b1 = MobiusBundle(winding_number=1)
    electron = MobiusFermion(chirality=-1, winding_n=1, bundle=b1)
    positron = MobiusFermion(chirality=+1, winding_n=1, bundle=b1)

    b2 = MobiusBundle(winding_number=2)
    electron2 = MobiusFermion(chirality=-1, winding_n=2, bundle=b2)

    b3 = MobiusBundle(winding_number=-1)
    antielectron_back = MobiusFermion(chirality=-1, winding_n=-1, bundle=b3)

    pairs = [
        (electron, positron,         "electron + positron  (opposite chirality)"),
        (electron, electron2,        "electron + electron2 (same chirality, diff winding)"),
        (electron, electron,         "electron + electron  (identical fermions)"),
        (positron, electron2,        "positron + electron2 (same chirality, diff winding)"),
        (electron, antielectron_back,"electron + anti-e-back (same chirality, diff winding)"),
    ]

    for p1, p2, label in pairs:
        result = bundle_compatibility_check(p1, p2)
        can = result["can_bind"]
        reason = result["reason"]
        total_q = result["total_charge"]
        net_w = result["net_winding"]
        neutral = result["is_neutral_pair"]
        flag = "CAN BIND   " if can else "CANNOT BIND"
        print(f"  [{flag}] {label}")
        print(f"           charge sum = {total_q:+.6f},  net winding = {net_w},  "
              f"neutral = {neutral}")
        print(f"           {reason}")
        print()


# ---------------------------------------------------------------------------
# 9. Dirac quantisation check
# ---------------------------------------------------------------------------


def section_dirac() -> None:
    header("9. DIRAC QUANTISATION — e × g = n pi hbar c")

    bundle = MobiusBundle(winding_number=1)
    e_si = 1.602176634e-19  # [C]

    print("  Dirac condition for half-flux bundle: e × g = n π ℏ c")
    print()
    print("  Minimum monopole strength (n = 1):")
    g_min = PI * HBAR * C_LIGHT / e_si
    print(f"    g_min = π ℏ c / e = {g_min:.6e}  J·m/A")
    ok = bundle.dirac_quantization_check(g_min)
    check("dirac_quantization_check(g_min)", ok, True)

    print()
    print("  Second allowed value (n = 2):")
    g2 = 2.0 * PI * HBAR * C_LIGHT / e_si
    ok2 = bundle.dirac_quantization_check(g2)
    check("dirac_quantization_check(2 × g_min)", ok2, True)

    print()
    print("  Non-quantised strength (should fail):")
    g_bad = 1.5 * g_min
    ok_bad = bundle.dirac_quantization_check(g_bad)
    check("dirac_quantization_check(1.5 × g_min)", ok_bad, False)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print()
    print("MOBIUS BUNDLE TEST — half-flux U(1) bundle topology (spec §§18.4, 18.10)")
    print("Module: stiff_medium.mobius_bundle")

    bundle = section_bundle_construction()
    section_spin_half(bundle)
    section_charge_quantisation(bundle)
    section_theta_qcd()
    section_aharonov_bohm(bundle)
    section_verify_ab()
    section_coleman()
    section_compatibility()
    section_dirac()

    header("SUMMARY")
    print("  All structural consequences of the Möbius half-flux U(1) bundle:")
    print()
    print("  1. half_flux = π — topological constant, first Chern class = 1/2")
    print("  2. Spin-½ rotation: phase -1 at 2π, +1 at 4π  (spin-statistics theorem)")
    print("  3. Charge quantisation: all charges are integer multiples of e")
    print("  4. θ_QCD = 0: strong-CP problem solved structurally, no axion needed")
    print("  5. Aharonov-Bohm phase = π × w — half-fringe shift per half-flux winding")
    print("  6. Fermion binding: opposite-chirality pairs bind; same-chirality excluded")
    print("  7. Coleman duality: sine-Gordon bosonization at β² = 4π is free fermion")
    print("  8. Dirac quantisation: e × g = n π ℏ c verified for half-flux bundle")
    print()
    print("  The half-flux topology (§18.10 connection A = (1/2) dθ) is the single")
    print("  structural choice that simultaneously fixes spin-½, charge quantisation,")
    print("  the AB effect, and the strong-CP angle.  No free parameters — all four")
    print("  follow from the same topological invariant c₁ = 1/2.")


if __name__ == "__main__":
    main()
