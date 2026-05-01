"""Bottom-up search for the e^{-N} exponent in B3 lepton mass ratios.

B3 lepton mass formulas contain an exponent of form e^{-N} (or e^{+N}) where
N is a specific number. The α derivation already showed exp(-3π/737) appears
naturally from drag γ on cone-bouncing — close cousin to the lepton exponents.

This script searches numerically for substrate-natural N values matching:
    m_μ/m_e = 206.7682830  → ln = 5.33165
    m_τ/m_μ = 16.81700     → ln = 2.82235
    m_τ/m_e = 3477.150     → ln = 8.15400

Sections:
  1. Lepton mass ratio data (PDG 2024)
  2. Existing B3 fits (recap)
  3. Search for substrate-natural N values fitting log-ratios
  4. Try several candidate forms numerically
  5. Best fit and physical interpretation
  6. Honest assessment
"""

from __future__ import annotations
import math
from itertools import product

PI = math.pi
E = math.e


# ============== 1. DATA ==============

# PDG 2024 charged lepton masses (MeV)
M_E = 0.51099895
M_MU = 105.6583755
M_TAU = 1776.93

R_MU_E = M_MU / M_E      # ~206.768
R_TAU_MU = M_TAU / M_MU  # ~16.817
R_TAU_E = M_TAU / M_E    # ~3477.15

LN_MU_E = math.log(R_MU_E)
LN_TAU_MU = math.log(R_TAU_MU)
LN_TAU_E = math.log(R_TAU_E)


# ============== B3 INTEGER INVENTORY ==============
# Substrate-natural primitives available for combinatorial fits
B3_INTS = {
    "N_BAM": 6,
    "K_pair": 2,
    "K_rank": 5,
    "n_R": 18,
    "n_M": 268,
    "n_A": 45,
    "F": 2,
    "R": 3,
    "V13": 13,
    "K3_cube": 8,
    "K4_tet": 4,
    "Q_drag_int": 246,  # round of 245.67
    "n_M_minus_R": 250,
    "halfRank": 5,
    "rankSq": 25,
}


# ============== UTILS ==============

def relerr(pred: float, obs: float) -> float:
    return (pred - obs) / obs


def fmt(pred: float, obs: float, label: str) -> str:
    re = relerr(pred, obs)
    return f"  {label}: pred={pred:.5f} obs={obs:.5f} relerr={re*100:+.3f}%"


# ============== 3. SUBSTRATE-NATURAL N CANDIDATE GENERATOR ==============

def candidate_pool() -> list[tuple[float, str]]:
    """Generate substrate-natural rational/π-rational candidates."""
    pool: list[tuple[float, str]] = []

    # Small integer ratios p/q with p in [1..40], q in [1..6]
    for p in range(1, 41):
        for q in range(1, 7):
            v = p / q
            pool.append((v, f"{p}/{q}"))

    # π-rationals
    for p in range(1, 25):
        for q in range(1, 12):
            pool.append((PI * p / q, f"π·{p}/{q}"))
            pool.append((p / (PI * q), f"{p}/(π·{q})"))

    # ln of small B3 integers
    for name, n in B3_INTS.items():
        if n > 1:
            pool.append((math.log(n), f"ln({name}={n})"))
            pool.append((math.log(n) / 2, f"ln({name})/2"))

    # K_rank, n_M combinations of form (a·X + b)/c
    for a, X_name, X in [(1, "K_rank", 5), (1, "N_BAM", 6), (1, "F+R", 5),
                         (1, "K_rank·F", 10), (1, "n_R", 18)]:
        for b in range(-3, 4):
            for c in range(1, 8):
                v = (a * X + b) / c
                pool.append((v, f"({a}·{X_name}+{b})/{c}"))

    # √n where n is small B3-y integer
    for n in [2, 3, 5, 6, 8, 18, 20, 25, 45, 268]:
        pool.append((math.sqrt(n), f"√{n}"))

    return pool


def best_match(target: float, pool: list[tuple[float, str]],
               topk: int = 5) -> list[tuple[float, str, float]]:
    """Return top-k matches by absolute relative error."""
    rows = [(v, name, abs((v - target) / target)) for v, name in pool]
    rows.sort(key=lambda r: r[2])
    return rows[:topk]


# ============== 4. CANDIDATE FORMS ==============

def search_log_form() -> None:
    """ln(ratio) = N: pure exponential ansatz m2/m1 = exp(N)."""
    print("=" * 70)
    print("3a. PURE-EXP ANSATZ: m2/m1 = exp(N)")
    print("=" * 70)
    pool = candidate_pool()

    for label, target in [("N_μ/e (=ln(206.768))", LN_MU_E),
                          ("N_τ/μ (=ln(16.817))", LN_TAU_MU),
                          ("N_τ/e (=ln(3477.15))", LN_TAU_E)]:
        print(f"\n  Target: {label} = {target:.6f}")
        for v, name, err in best_match(target, pool, topk=4):
            print(f"    candidate {name:24s}={v:.6f}  rel_err={err*100:+.4f}%")


def search_power_form() -> None:
    """Power-law ansatz m2/m1 = base^N for substrate base values."""
    print()
    print("=" * 70)
    print("3b. POWER ANSATZ: m2/m1 = base^N")
    print("=" * 70)

    bases = {
        "e": E,
        "π": PI,
        "2": 2.0,
        "3": 3.0,
        "5": 5.0,
        "K_rank=5": 5.0,
        "N_BAM=6": 6.0,
        "π²": PI**2,
        "2π": 2 * PI,
        "e^π": E**PI,
    }

    for ratio_name, R in [("μ/e", R_MU_E), ("τ/μ", R_TAU_MU), ("τ/e", R_TAU_E)]:
        print(f"\n  m_{ratio_name} = {R:.4f}")
        for bname, b in bases.items():
            N = math.log(R) / math.log(b)
            print(f"    base={bname:10s}: N = {N:.4f}")


def search_alpha_drag_form() -> None:
    """B3 α has factor exp(-3π/737). Test similar drag-corrected forms."""
    print()
    print("=" * 70)
    print("3c. α-DRAG-COUSIN ANSATZ: m_ratio = A · exp(-c·π/D)")
    print("=" * 70)
    print()
    print("  α used D=737 (≈ m_p/m_e × something). Search over D.")

    # Ratio ≈ A · exp(-c π / D). Try (A, c) drawn from B3 prefactors.
    forms = [
        ("11/(48π³) · exp(-3π/D)", 11 / (48 * PI**3), -3),
        ("e^N0 · exp(-3π/D), N0=int", None, None),
    ]

    # For μ/e, find D such that 11/(48π³)·exp(-3π/D) = R_MU_E (impossible — way too small).
    # Instead try a multiplicative drag correction on top of integer-N exponential.

    print()
    print("  Mode A: m_μ/m_e = exp(N0) · exp(+3π/D) with N0 ∈ ℤ")
    for N0 in [4, 5, 6]:
        # exp(N0) * exp(3π/D) = R_MU_E
        # 3π/D = ln(R_MU_E) - N0  →  D = 3π / (ln(R_MU_E) - N0)
        delta = LN_MU_E - N0
        if delta == 0:
            continue
        D = 3 * PI / delta
        print(f"    N0={N0}: required D = 3π/{delta:.5f} = {D:.4f}")

    print()
    print("  Mode B: m_τ/m_μ = exp(N0) · exp(+3π/D)")
    for N0 in [2, 3]:
        delta = LN_TAU_MU - N0
        if delta == 0:
            continue
        D = 3 * PI / delta
        print(f"    N0={N0}: required D = 3π/{delta:.5f} = {D:.4f}")

    print()
    print("  Mode C: m_τ/m_e = exp(N0) · exp(+3π/D)")
    for N0 in [7, 8, 9]:
        delta = LN_TAU_E - N0
        if delta == 0:
            continue
        D = 3 * PI / delta
        print(f"    N0={N0}: required D = 3π/{delta:.5f} = {D:.4f}")


def search_braid_index_form() -> None:
    """Generation-indexed Möbius/braid bundle: ratio_n = exp((2n+1)·something)."""
    print()
    print("=" * 70)
    print("3d. BRAID-INDEX ANSATZ: ratio = exp(B(n2) - B(n1))")
    print("=" * 70)
    print()
    print("  Generation indices: e=1, μ=2, τ=3.")
    print("  Try B(n) = a·n + b·n² + c·n³ etc. From the two ratios fix params.")

    # Two equations (μ/e and τ/μ), two unknowns (a, b) with B(n)=a n+b n^2.
    # B(2)-B(1) = a + 3b = LN_MU_E
    # B(3)-B(2) = a + 5b = LN_TAU_MU
    # Subtract: 2b = LN_TAU_MU - LN_MU_E  → b = (LN_TAU_MU - LN_MU_E)/2
    b = (LN_TAU_MU - LN_MU_E) / 2
    a = LN_MU_E - 3 * b
    print(f"    Linear+quad fit B(n)=a·n+b·n²: a={a:.5f}, b={b:.5f}")
    print(f"    B(1)={a+b:.5f}, B(2)={2*a+4*b:.5f}, B(3)={3*a+9*b:.5f}")
    # negative b means hierarchy compresses with generation — not natural.

    # B(n) = a·n + b/n
    # B(2)-B(1)=a-b/2=LN_MU_E
    # B(3)-B(2)=a-b/6=LN_TAU_MU
    # subtract: -b/2+b/6 = LN_MU_E - LN_TAU_MU → -b/3 = LN_MU_E - LN_TAU_MU
    bb = -3 * (LN_MU_E - LN_TAU_MU)
    aa = LN_MU_E + bb / 2
    print(f"    a·n+b/n fit: a={aa:.5f}, b={bb:.5f}")
    # Check for substrate-naturalness:
    pool = candidate_pool()
    print(f"    nearest substrate value to a={aa:.5f}:")
    for v, name, err in best_match(aa, pool, topk=3):
        print(f"      {name:24s}={v:.6f}  rel_err={err*100:+.4f}%")
    print(f"    nearest substrate value to b={bb:.5f}:")
    for v, name, err in best_match(bb, pool, topk=3):
        print(f"      {name:24s}={v:.6f}  rel_err={err*100:+.4f}%")


def search_n_M_anchored() -> None:
    """B3 hint: N might be n_M=268 with rational coefficient."""
    print()
    print("=" * 70)
    print("3e. n_M=268-ANCHORED: ratio = (small)^(p/q · n_M / D)")
    print("=" * 70)

    n_M = 268
    print(f"  ln(R_μ/e)/n_M = {LN_MU_E/n_M:.6f}")
    print(f"  n_M/ln(R_μ/e) = {n_M/LN_MU_E:.4f}")
    print(f"  ln(R_τ/μ)/n_M = {LN_TAU_MU/n_M:.6f}")
    print(f"  ln(R_τ/e)/n_M = {LN_TAU_E/n_M:.6f}")

    # Look for n_M / (LN_X) hitting near integer or B3 value
    pool = candidate_pool()
    for label, target in [("n_M/ln(μ/e)", n_M / LN_MU_E),
                          ("n_M/ln(τ/μ)", n_M / LN_TAU_MU),
                          ("n_M/ln(τ/e)", n_M / LN_TAU_E)]:
        print(f"\n  {label} = {target:.5f}")
        for v, name, err in best_match(target, pool, topk=3):
            print(f"    {name:24s}={v:.6f}  rel_err={err*100:+.4f}%")


# ============== 5. BEST-FIT REPORT ==============

def report_best_fits() -> None:
    print()
    print("=" * 70)
    print("4. BEST-OF-RUN: tightest substrate-natural matches")
    print("=" * 70)
    print()

    # 16/3 for ln(μ/e)
    pred = 16 / 3
    print(fmt(pred, LN_MU_E, "ln(m_μ/m_e) ?= 16/3 = K_rank+1/3"))
    pred_R = math.exp(16 / 3)
    print(fmt(pred_R, R_MU_E, "  → m_μ/m_e ?= e^(16/3)"))

    # ln(τ/μ) attempts
    print()
    pred = 17 / 6
    print(fmt(pred, LN_TAU_MU, "ln(m_τ/m_μ) ?= 17/6"))
    pred = math.log(17)
    print(fmt(pred, LN_TAU_MU, "ln(m_τ/m_μ) ?= ln(17)"))
    pred = PI * 9 / 10
    print(fmt(pred, LN_TAU_MU, "ln(m_τ/m_μ) ?= 9π/10"))

    # ln(τ/e)
    print()
    pred = 8 + 1 / 6
    print(fmt(pred, LN_TAU_E, "ln(m_τ/m_e) ?= 49/6"))
    pred = math.log(R_MU_E) + math.log(R_TAU_MU)  # consistency check
    print(fmt(pred, LN_TAU_E, "  log additivity check (must be exact)"))

    # The 3π/D drag form, tried bottom-up:
    print()
    print("  Drag-cousin form (mirroring α=11/(48π³)·exp(-3π/737)):")
    # Hypothesis: m_μ/m_e = (something integer-exp) · exp(3π/D_lepton)
    # If N0=5 (=K_rank), D_lepton fixed:
    delta = LN_MU_E - 5
    D = 3 * PI / delta
    print(f"    N0=K_rank=5: D = 3π/{delta:.5f} = {D:.4f}")
    print(f"      Compare α's D=737. Match? {D/737*100:.2f}% of 737.")

    # Hypothesis N0=K_rank+1=6 (N_BAM):
    delta6 = LN_MU_E - 6
    D6 = 3 * PI / delta6
    print(f"    N0=N_BAM=6: D = 3π/{delta6:.5f} = {D6:.4f}")


# ============== 6. HONEST ASSESSMENT ==============

def honest_assessment() -> None:
    print()
    print("=" * 70)
    print("5. HONEST ASSESSMENT")
    print("=" * 70)
    print()
    print("  ln(m_μ/m_e) = 5.33165")
    print(f"    16/3 = 5.33333  → match within 0.0315% — extremely close.")
    print(f"    But 16/3 has no obvious B3 derivation; K_rank+1/3 with the")
    print(f"    1/3 representing a 1-of-3-color-strain residual is suggestive")
    print(f"    but not derived. Status: SUGGESTIVE, NOT CLOSED.")
    print()
    print("  ln(m_τ/m_μ) = 2.82235")
    print(f"    Nothing within 0.5% of a clean substrate-natural form.")
    print(f"    Closest hits: ln(17)=2.833 (0.4% off), 9π/10=2.827 (0.18% off).")
    print(f"    9π/10 is intriguing (9 = K_rank·(K_rank-1)/2 + ... ?)")
    print(f"    but 'K_rank pairs out of 10' lacks a derivation.")
    print(f"    Status: NO CLEAN MATCH; speculative.")
    print()
    print("  ln(m_τ/m_e) = 8.15400")
    print(f"    Forced by additivity from above: NO INDEPENDENT DOF.")
    print(f"    49/6 = 8.16667 is 0.16% off — coincidence given the constraint.")
    print()
    print("  Drag-cousin hypothesis (e^{-N} = exp(±3π/D_lepton)):")
    print(f"    For N0=K_rank=5: D = {3*PI/(LN_MU_E-5):.2f}")
    print(f"    For N0=N_BAM=6: D = {3*PI/(LN_MU_E-6):.2f} (negative!)")
    print(f"    Neither D matches 737 nor any obvious substrate integer.")
    print(f"    No closure via this route on present search.")
    print()
    print("  Bottom line: NOT CLOSED. The cleanest fit is")
    print("    m_μ/m_e ≈ exp(16/3)  [match: 0.16% — borderline]")
    print("  but a topological derivation of 16/3 is missing. The")
    print("  τ-sector exponents have no sub-permille substrate-natural")
    print("  match in the searched candidate pool.")
    print()
    print("  Suggests two next steps:")
    print("    (a) Derive 16/3 from K_4 simplicial volume / color-residual.")
    print("    (b) Generation-indexed exponents may need a 2-parameter")
    print("        substrate model (not pure 1-N), matching the 2 DOF")
    print("        in lepton ratios. Current 1-N ansatz may be wrong.")


def main() -> None:
    print("e^{-N} closure search for B3 lepton mass ratios")
    print("=" * 70)
    print()

    # Section 1
    print("1. LEPTON MASS RATIO DATA (PDG 2024)")
    print(f"   m_e   = {M_E:.6f} MeV")
    print(f"   m_μ   = {M_MU:.6f} MeV")
    print(f"   m_τ   = {M_TAU:.4f} MeV")
    print(f"   m_μ/m_e = {R_MU_E:.6f}    ln = {LN_MU_E:.6f}")
    print(f"   m_τ/m_μ = {R_TAU_MU:.6f}    ln = {LN_TAU_MU:.6f}")
    print(f"   m_τ/m_e = {R_TAU_E:.4f}    ln = {LN_TAU_E:.6f}")
    print(f"   (Additivity check: {LN_MU_E + LN_TAU_MU:.6f} = {LN_TAU_E:.6f}? "
          f"{abs(LN_MU_E+LN_TAU_MU-LN_TAU_E)<1e-6})")
    print()

    # Section 2
    print("2. EXISTING B3 FITS (recap)")
    print("   B3 master-card lepton ratios use n_M=268 and rational")
    print("   prefactors but with several fitted constants. The α derivation")
    print("   α = 11/(48π³)·exp(-3π/737) at 0.004% match shows the")
    print("   exp(-c·π/D) drag form is substrate-natural for EM coupling.")
    print("   The lepton e^{-N} exponent should plausibly come from the")
    print("   same drag mechanism, with possibly different D.")
    print()

    # Section 3
    search_log_form()
    search_power_form()
    search_alpha_drag_form()
    search_braid_index_form()
    search_n_M_anchored()

    # Section 4-5
    report_best_fits()
    honest_assessment()


if __name__ == "__main__":
    main()
