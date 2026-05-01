"""V13 closure attempt: derive B3's V13 integer from substrate primitives.

V13 is one of B3's 12 integers and currently lacks a rigorous
bottom-up derivation. M=268 has been closed (K_pair·K_rank^3 + n_R
= 2·125 + 18). e^{-N} and V13 remain.

This script speculates intelligently about what V13 might count,
tries multiple substrate-natural derivations, and assesses honestly
whether any constitute a closure or merely a candidate hypothesis.

Pattern: scripts/strain_medium_is_tighter.py
"""

from __future__ import annotations
import math
from itertools import combinations


PI = math.pi
TARGET = 13


def banner(s: str) -> None:
    print("=" * 70)
    print(s)
    print("=" * 70)
    print()


def check(label: str, value: int, target: int = TARGET) -> str:
    hit = "  HIT" if value == target else f"  miss (got {value})"
    return f"  {label:<55} = {value:>4}{hit}"


def main() -> None:
    print("V13 closure attempt: substrate-primitive derivation of integer 13")
    print("=" * 70)
    print()

    # ============================================================
    banner("1. V13 in B3: where it appears")
    # ============================================================
    print("V13 is one of B3's 12 integers (alongside N_BAM=6, K_pair=2,")
    print("K_rank=5, n_R=18, n_M=268, n_A=45, F=2, R=3, etc.).")
    print()
    print("Role in inventory: V13 typically enters as a vertex or mode")
    print("count in the substrate's simplicial closure for a specific")
    print("sector (commonly cited in the EW + Higgs counting branch).")
    print("Unlike n_M=268 — which has an explicit closure")
    print("    n_M = K_pair · K_rank^3 + n_R = 2·125 + 18,")
    print("V13 is currently quoted as 'given' in the master-card.")
    print()
    print("Goal: find an expression V13 = f(K, K_pair, K_rank, n_R, ...)")
    print("such that f evaluates to exactly 13 with no fitted residue.")
    print()

    # ============================================================
    banner("2. Natural integer-13 candidates (search space)")
    # ============================================================
    print("Topology / combinatorics:")
    print("  - 13 is prime; not a vertex count of any regular 4-polytope")
    print("    (5-cell=5, 16-cell=8, 8-cell=16, 24-cell=24, 600-cell=120)")
    print("  - Archimedean solids: 13 of them (a known classification)")
    print("  - Catalan solids: 13 (duals of Archimedean)")
    print("  - 13 = number of distinct 3-edge-colorings of K_4 up to S_3?")
    print("  - 13 = (4 choose 2) + (4 choose 1) + (4 choose 0) + 2 = 6+4+1+2")
    print("  - 13 = Euler characteristic of 13 disjoint points (trivial)")
    print()
    print("Particle physics:")
    print("  - 13 = 8 gluons + 3 W/Z + photon + Higgs = 13 SM gauge+scalar")
    print("  - 13 = 12 fermions + 1 Higgs scalar")
    print("  - 13 = 6 quarks + 6 leptons + 1 (Higgs or graviton placeholder)")
    print()
    print("Simplicial / K_4-derived:")
    print("  - K_4 has 4 vertices + 6 edges + 4 faces - 1 cell = 13")
    print("    (sum of f-vector entries minus the top cell)")
    print("  - K_4 f-vector = (4, 6, 4, 1) → 4+6+4-1 = 13 (Euler-style)")
    print("  - or 4+6+4 = 14, 4+6+4-1 = 13, 4+6+3 = 13")
    print()
    print("Möbius / bundle:")
    print("  - n_R = 18; 18 - K_rank = 13")
    print("  - n_R - K_rank = 18 - 5 = 13 → reflection modes minus rank")
    print("  - K_pair · K_rank + K_rank - K_pair = 2·5 + 5 - 2 = 13")
    print()

    # ============================================================
    banner("3. Numerical trials of substrate-natural derivations")
    # ============================================================
    K_pair = 2
    K_rank = 5
    n_R = 18
    N_BAM = 6
    F = 2
    R = 3

    candidates: list[tuple[str, int, str]] = []

    # --- topological / simplicial ---
    v, e, f, c = 4, 6, 4, 1  # K_4 / 3-simplex f-vector
    candidates += [
        ("K_4 f-vector sum (V+E+F+C)", v + e + f + c,
         "tetrahedron total face count incl. interior cell = 15 (miss)"),
        ("K_4 f-vector sum minus cell (V+E+F)", v + e + f,
         "boundary 2-complex face count = 14 (miss)"),
        ("K_4 V + E + F − 1 (Euler-style closure deficit)", v + e + f - 1,
         "closure-deficit count on tetrahedron"),
        ("K_4 V + E + F − C with interior subtracted", v + e + f - c,
         "same as above"),
        ("K_4 E + F + V − cell − apex", v + e + f - 1,
         "duplicate, sanity"),
    ]

    # --- K_pair / K_rank arithmetic ---
    candidates += [
        ("K_pair · K_rank + K_rank − K_pair", K_pair*K_rank + K_rank - K_pair,
         "doubled pentagon minus pair-doubling correction"),
        ("K_rank^2 − K_pair · K_rank − K_pair", K_rank**2 - K_pair*K_rank - K_pair,
         "rank-square minus mixing minus pair offset"),
        ("(K_rank − 1)·K_pair + K_rank − K_pair", (K_rank-1)*K_pair + K_rank - K_pair,
         "rank-1 doubled plus closure"),
        ("K_rank · (K_pair + 1) − K_pair", K_rank*(K_pair+1) - K_pair,
         "trinomial expansion of K_4 mixing"),
        ("K_rank · K_pair + R", K_rank*K_pair + R,
         "doubled pentagon plus rank-3 closure"),
    ]

    # --- bundle reflection minus rank ---
    candidates += [
        ("n_R − K_rank", n_R - K_rank,
         "Möbius reflection modes minus rank-5 simplex axes"),
        ("n_R − N_BAM + 1", n_R - N_BAM + 1,
         "reflections minus hex modes plus closure"),
        ("n_R/K_pair + N_BAM − 2", n_R // K_pair + N_BAM - 2,
         "half-bundle plus hex minus pair"),
    ]

    # --- particle-physics counts (gauge + Higgs branch) ---
    n_gluons = 8       # SU(3) adjoint
    n_EW = 4           # W+, W-, Z, gamma
    n_higgs = 1
    n_fermion_flavors = 12  # 6 quarks + 6 leptons
    candidates += [
        ("8 gluons + 4 EW + 1 Higgs", n_gluons + n_EW + n_higgs,
         "SM bosonic content: SU(3)×SU(2)×U(1) gauge bosons + Higgs"),
        ("12 fermions + 1 Higgs", n_fermion_flavors + n_higgs,
         "SM fermion flavor count + scalar"),
        ("6 quarks + 6 leptons + 1 graviton", 6 + 6 + 1,
         "matter content + tensor closure"),
    ]

    # --- 4-simplex / K_5 face counts ---
    # K_5 f-vector = (5, 10, 10, 5, 1)
    candidates += [
        ("K_5 vertices + edges − faces", 5 + 10 - 10 + (5-5) - (1-1),
         "alternating sum subset on 4-simplex (= 5)"),
        ("K_5 V + 2-faces − 3-faces", 5 + 10 - 5 + 5 - 1 - 1,
         "ad-hoc K_5 combination = 13?"),
    ]
    # Verify: 5 + 10 - 5 + 5 - 1 - 1 = 13
    assert 5 + 10 - 5 + 5 - 1 - 1 == 13

    # --- F/R rational closures ---
    candidates += [
        ("F · R + n_R/K_pair − F", F*R + n_R//K_pair - F,
         "F=2,R=3 closure plus half-bundle minus F-doubling"),
        ("F^2 · R + F + R", F**2 * R + F + R,
         "branch-square closure (= 17, miss)"),
    ]

    print("Candidate evaluations (target = 13):")
    print()
    for label, val, note in candidates:
        print(check(label, val))
        print(f"      note: {note}")
    print()

    # collect hits
    hits = [(lab, val, note) for (lab, val, note) in candidates if val == TARGET]
    print(f"Hits: {len(hits)} expressions evaluate to exactly 13.")
    print()

    # ============================================================
    banner("4. Best candidate with physical motivation")
    # ============================================================
    print("Among the hits, evaluate each for substrate-natural justification.")
    print("Criteria: (a) all inputs already derived in B3, (b) operation is")
    print("a closure/Euler-type sum, not arithmetic curve-fitting, (c) ties")
    print("to a known topological invariant.")
    print()

    print("CANDIDATE A — Möbius reflection minus simplex rank")
    print("  V13 = n_R − K_rank = 18 − 5 = 13")
    print("  Motivation: n_R counts Möbius half-integer reflection modes")
    print("  on the K_4 bundle. K_rank=5 are the axes of the rank-5 simplex.")
    print("  Subtracting the 'axis-aligned' modes leaves transverse modes.")
    print("  Status: arithmetically clean, BUT requires independent")
    print("  justification that V13 = transverse-reflection count.")
    print("  Strength: both inputs already topology-derived.")
    print()

    print("CANDIDATE B — SM bosonic content")
    print("  V13 = N_gluon + N_EW + N_Higgs = 8 + 4 + 1 = 13")
    print("  Motivation: if V13 enters in the EW-Higgs sector (where it")
    print("  is most often cited), 13 is exactly the count of SM gauge")
    print("  bosons + scalar.")
    print("  Status: physically suggestive, BUT this is essentially")
    print("  fitting V13 to the SM count post-hoc unless one can derive")
    print("  the gauge-boson partition (8/4/1) from K, ρ, ξ, γ first.")
    print("  Strength: the partition 8 = SU(3)_adj, 3+1 = SU(2)+U(1) is")
    print("  itself topology-derivable: 8 = K_rank·N_BAM/2·K_pair? actually")
    print(f"  K_rank·N_BAM/2 - 2 = {K_rank*N_BAM//2 - 2} ≠ 8 — does not close cleanly")
    print()

    print("CANDIDATE C — K_4 closure-deficit")
    print("  V13 = V + E + F − cell = 4 + 6 + 4 − 1 = 13")
    print("  Motivation: K_4 f-vector minus one for the closing cell —")
    print("  i.e. count of all simplicial faces of dim < 3 on the")
    print("  3-simplex. This is the Euler-style 'open boundary' count.")
    print("  Status: cleanest geometric interpretation. Both K_4 and the")
    print("  closure subtraction are already substrate primitives.")
    print("  Strength: directly tied to the K_4 nucleon cell and uses")
    print("  no new inputs. WEAKNESS: ad-hoc subtraction of '1' is")
    print("  exactly the kind of move that should be forced by topology")
    print("  (Stiefel-Whitney class? boundary operator?), not chosen.")
    print()

    print("CANDIDATE D — F·R + half-bundle − F")
    print("  V13 = F·R + n_R/K_pair − F = 2·3 + 9 − 2 = 13")
    print("  Motivation: branch closure (F·R) plus half of Möbius bundle")
    print("  minus pair-doubling correction.")
    print("  Status: arithmetic works, but the construction smells of")
    print("  hunting for 13 in the parameter space. No cleaner motivation.")
    print()

    print("RANKING:")
    print("  C (K_4 closure-deficit)        — best geometric story")
    print("  A (n_R − K_rank)               — cleanest arithmetic")
    print("  B (SM bosonic count)           — physical resonance, derivation gap")
    print("  D (F·R algebraic)              — likely coincidence")
    print()

    # ============================================================
    banner("5. Honest assessment — closure status")
    # ============================================================
    print("Status: PARTIAL. Not closed.")
    print()
    print("What WOULD constitute closure for V13:")
    print("  (i)   identify what V13 counts in the substrate (vertex,")
    print("        mode, reflection class, topological invariant)")
    print("  (ii)  derive its value from K, ρ, ξ, γ + saturation +")
    print("        orientability with no fitted constants")
    print("  (iii) cross-check it appears with the right sign/role in")
    print("        the SM prediction it enters")
    print()
    print("What we have here:")
    print(f"  - {len(hits)} substrate-natural arithmetic expressions hit 13")
    print("  - Best candidate (C, K_4 closure-deficit) has clean")
    print("    geometric meaning (open-boundary face count of K_4)")
    print("  - All candidates lack step (i): we have not identified WHAT")
    print("    V13 counts in the substrate, so any value ≈ 13 is suggestive")
    print("    but not a derivation")
    print()
    print("Honest verdict:")
    print("  V13 = K_4 closure-deficit (4+6+4-1) is the leading hypothesis")
    print("  but is NOT a closure — the '−1' must be forced by the")
    print("  boundary operator or Stiefel-Whitney class, not chosen.")
    print()
    print("  Equivalently: V13 = n_R − K_rank is arithmetically clean")
    print("  but lacks a derivation of the subtraction operation.")
    print()
    print("  The SM-bosonic interpretation (8+4+1) is intriguing IF V13")
    print("  enters the EW-Higgs sector counting — that should be the")
    print("  next thing to verify against the master-card.")
    print()
    print("Compared to M=268 (closed via K_pair·K_rank^3 + n_R) and")
    print("e^{-N} (open), V13 sits in the middle: multiple plausible")
    print("closures exist, but none is forced. Requires looking at")
    print("WHERE V13 enters predictions to disambiguate.")
    print()
    print("Next step: locate V13's prediction equation in the master-card")
    print("and check whether n_R − K_rank, the K_4 face count, or the")
    print("SM-bosonic decomposition gives the right multiplicative role")
    print("there. That contextual check is what would close the")
    print("derivation — pure number-matching is not enough.")
    print()
    print("CLOSURE STATUS: OPEN (3 plausible candidates, no forcing argument)")


if __name__ == "__main__":
    main()
