"""Rebuild the model-suite question files from this single source of truth.

Run:  python build_questions.py
Every answer key here was checked by hand and, where numeric, by direct
computation. These are hand-written questions in the style of the named
benchmarks. They are NOT official benchmark items and must never be reported
as such.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
QDIR = ROOT / "questions"
QDIR.mkdir(exist_ok=True)


def dump(name, rows):
    path = QDIR / name
    path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {path.name}: {len(rows)} questions")


def q(id, category, type, q, answer, accept=None, rubric=None, tags=(), source="hand-written",
      trap_patterns=None, trap_label=""):
    row = {
        "id": id, "category": category, "type": type, "q": q,
        "answer": answer, "accept": accept or [answer],
        "tags": list(tags), "source": source,
    }
    if rubric:
        row["rubric"] = rubric
    if trap_patterns:
        row["trap_patterns"] = trap_patterns
        row["trap_label"] = trap_label
    return row


def rubric(*points):
    return [{"point": p, "patterns": pats} for p, pats in points]


# ---------------------------------------------------------------- SWE ----
swe = [
    q("SWE-01", "swe", "mcq", """What is printed by this Python program?

def make():
    fs = []
    for i in range(3):
        fs.append(lambda: i)
    return fs
print([f() for f in make()])

A) [0, 1, 2]
B) [0, 0, 0]
C) [2, 2, 2]
D) [3, 3, 3]""", "C", tags=["python", "closure"], source="qwen36-hard-eval"),

    q("SWE-02", "swe", "mcq", """What is printed?

class A:
    def f(self): return "A"
class B(A):
    def f(self): return "B" + super().f()
class C(A):
    def f(self): return "C" + super().f()
class D(B, C):
    def f(self): return "D" + super().f()
print(D().f())

A) DBCA
B) DBCA with an extra A
C) DABC
D) D followed by B only""", "A", tags=["python", "mro"], source="qwen36-hard-eval"),

    q("SWE-03", "swe", "mcq", """This function counts set bits in a positive integer:

def f(n):
    c = 0
    while n:
        n &= n - 1
        c += 1
    return c

What does f(2024) return?
A) 7
B) 6
C) 8
D) 10""", "A", tags=["python", "bits"], source="qwen36-hard-eval"),

    q("SWE-04", "swe", "mcq", """How many distinct calls to fib are actually executed (including the initial one) when fib(10) is called for the first time on a fresh cache?

import functools
@functools.lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n-1) + fib(n-2)

A) 10
B) 11
C) 177
D) 89""", "B", tags=["python", "lru_cache"], source="qwen36-hard-eval"),

    q("SWE-05", "swe", "mcq", """What is printed?

d = {}
for i in range(3):
    d[i] = i
del d[1]
d[1] = 99
print(list(d))

A) [0, 1, 2]
B) [0, 1]
C) [1, 0, 2]
D) [0, 2, 1]""", "D", tags=["python", "dict"], source="qwen36-hard-eval"),

    q("SWE-06", "swe", "mcq", """This Python code fails with 'dictionary changed size during iteration':

d = {"a": 1, "b": 2}
for k in d:
    if d[k] == 2:
        del d[k]

Which single change fixes it?
A) for k in d.keys():
B) for k in list(d):
C) for k in d.items():
D) wrap del in try/except RuntimeError""", "B", tags=["python", "debugging"], source="qwen36-knowledge-eval"),

    q("SWE-07", "swe", "mcq", """What is the average-case time complexity of looking up a key in a Python dict?
A) O(1)   B) O(log n)   C) O(n)   D) O(n log n)""", "A", tags=["python", "complexity"], source="qwen36-knowledge-eval"),

    q("SWE-08", "swe", "mcq", """What does this function return when data = [1, 2, 3, 4]?

def f(data):
    total = 0
    for x in data:
        if x % 2 == 0:
            total += x
    return total

A) 4   B) 6   C) 10   D) 7""", "B", tags=["python", "trace"], source="qwen36-knowledge-eval"),

    q("SWE-09", "swe", "mcq", """What is printed?

from itertools import takewhile
it = iter([1, 2, 0, 3])
a = list(takewhile(bool, it))
b = list(it)
print(a, b)

A) [1, 2] and [0, 3]
B) [1, 2] and [3]
C) [1, 2, 0] and [3]
D) [1, 2] and []""", "B", tags=["python", "itertools"], source="hand-written"),

    q("SWE-10", "swe", "mcq", """What is printed?

def f(x, acc=[]):
    acc.append(x)
    return acc
a = f(1); b = f(2, []); c = f(3)
print(a, b, c, a is c)

A) [1] [2] [3] False
B) [1, 3] [2] [1, 3] True
C) [1] [2] [1, 3] True
D) [1, 3] [2] [1, 3] False""", "B", tags=["python", "mutable-default"], source="hand-written"),

    q("SWE-11", "swe", "mcq", """Consider this code:

import threading
x = 0
def inc():
    global x
    for _ in range(100000):
        x += 1
t1 = threading.Thread(target=inc)
t2 = threading.Thread(target=inc)
t1.start(); t2.start(); t1.join(); t2.join()
print(x)

Which statement is true?
A) It always prints 200000.
B) It always prints 100000.
C) It can print less than 200000, because x += 1 is not atomic under the GIL.
D) It can print more than 200000, because the GIL duplicates writes.""", "C", tags=["python", "concurrency", "gil"], source="hand-written"),

    q("SWE-12", "swe", "mcq", """What is printed?

print(-7 // 3, -7 % 3, divmod(-7, 3))

A) -2 -1 (-2, -1)
B) -3 2 (-3, 2)
C) -2 2 (-2, 2)
D) -3 -1 (-3, -1)""", "B", tags=["python", "arithmetic"], source="hand-written"),
]

# ---------------------------------------------------------------- AIME ----
aime = [
    q("AIME-01", "aime", "numeric", """How many positive integers n <= 10000 are divisible by exactly two of the numbers 2, 3, and 5? Reply with the integer.""", "2333", tags=["inclusion-exclusion"], source="qwen36-hard-eval"),
    q("AIME-02", "aime", "numeric", """What is the remainder when 3^1000 is divided by 7? Reply with the integer.""", "4", tags=["modular"], source="qwen36-hard-eval"),
    q("AIME-03", "aime", "numeric", """How many positive five-digit integers have their digits in strictly increasing order from left to right? Reply with the integer.""", "126", tags=["combinatorics"], source="qwen36-hard-eval"),
    q("AIME-04", "aime", "numeric", """A right triangle has legs of length 9 and 12. What is the length of the altitude from the right angle to the hypotenuse? Reply as a fraction like a/b.""", "36/5", accept=["36/5", "7.2"], tags=["geometry"], source="qwen36-hard-eval"),
    q("AIME-05", "aime", "numeric", """What is the smallest positive integer n such that 2^n is congruent to 1 modulo 17? Reply with the integer.""", "8", tags=["modular"], source="qwen36-hard-eval"),
    q("AIME-06", "aime", "numeric", """How many positive integers n <= 1000 are divisible by 6 but NOT divisible by 8? Reply with the integer.""", "125", tags=["inclusion-exclusion"], source="qwen36-knowledge-eval"),
    q("AIME-07", "aime", "numeric", """If x + 1/x = 3, what is x^2 + 1/x^2? Reply with the integer.""", "7", tags=["algebra"], source="qwen36-knowledge-eval"),
    q("AIME-08", "aime", "numeric", """What is the remainder when 7^2024 is divided by 100? Reply with the integer.""", "1", tags=["modular"], source="qwen36-knowledge-eval"),
    q("AIME-09", "aime", "numeric", """How many positive integers n <= 2026 are there such that n^2 + 1 is divisible by 5? Reply with the integer.""", "810", tags=["modular", "counting"], source="hand-written"),
    q("AIME-10", "aime", "numeric", """How many three-digit positive integers have digits that sum to exactly 12? Reply with the integer.""", "66", tags=["combinatorics", "digits"], source="hand-written"),
    q("AIME-11", "aime", "numeric", """A bag contains 5 red balls and 4 blue balls. Three balls are drawn without replacement. The probability that exactly two of them are red is p/q in lowest terms. Reply with p+q.""", "31", tags=["probability"], source="hand-written"),
    q("AIME-12", "aime", "numeric", """What is the remainder when 1! + 2! + 3! + ... + 100! is divided by 15? Reply with the integer.""", "3", tags=["factorials", "modular"], source="hand-written"),
]

# ---------------------------------------------------------------- MMLU ----
mmlu = [
    q("MMLU-01", "mmlu", "mcq", """Who wrote 'The Structure of Scientific Revolutions', introducing the concept of paradigm shifts?
A) Karl Popper
B) Thomas Kuhn
C) Paul Feyerabend
D) Imre Lakatos""", "B", tags=["philosophy-of-science"], source="qwen36-hard-eval"),
    q("MMLU-02", "mmlu", "mcq", """The principle of non-refoulement, which forbids returning refugees to a country where they face serious harm, is a cornerstone of which instrument?
A) The 1951 Geneva Convention relating to the Status of Refugees
B) The Geneva Conventions of 1949 on the laws of war
C) The Universal Declaration of Human Rights
D) The Schengen Agreement""", "A", tags=["law"], source="qwen36-hard-eval"),
    q("MMLU-03", "mmlu", "mcq", """Which enzyme catalyses the rate-limiting (committed) step of glycolysis?
A) Hexokinase
B) Glucokinase
C) Phosphofructokinase-1
D) Pyruvate kinase""", "C", tags=["biochemistry"], source="qwen36-hard-eval"),
    q("MMLU-04", "mmlu", "mcq", """Who composed 'The Rite of Spring', the ballet that caused a riot at its 1913 premiere?
A) Claude Debussy
B) Arnold Schoenberg
C) Maurice Ravel
D) Igor Stravinsky""", "D", tags=["music"], source="qwen36-hard-eval"),
    q("MMLU-05", "mmlu", "mcq", """Which amino acid is the biochemical precursor to both serotonin and melatonin?
A) Tyrosine
B) Tryptophan
C) Phenylalanine
D) Histidine""", "B", tags=["biochemistry"], source="qwen36-hard-eval"),
    q("MMLU-06", "mmlu", "mcq", """Which planet in our solar system has the shortest day (rotation period)?
A) Mercury
B) Jupiter
C) Venus
D) Earth""", "B", tags=["astronomy"], source="qwen36-knowledge-eval"),
    q("MMLU-07", "mmlu", "mcq", """The Treaty of Westphalia (1648) brought an end to which conflict?
A) Thirty Years' War
B) Hundred Years' War
C) Seven Years' War
D) War of the Spanish Succession""", "A", tags=["history"], source="qwen36-knowledge-eval"),
    q("MMLU-08", "mmlu", "mcq", """Who designed the Python programming language?
A) Dennis Ritchie
B) Guido van Rossum
C) James Gosling
D) Brendan Eich""", "B", tags=["computing"], source="qwen36-knowledge-eval"),
    q("MMLU-09", "mmlu", "mcq", """The Battle of Towton (1461) was a decisive engagement of which conflict?
A) The Hundred Years' War
B) The Wars of the Roses
C) The English Civil War
D) The Jacobite rising""", "B", tags=["history"], source="hand-written"),
    q("MMLU-10", "mmlu", "mcq", """The Lucas critique argues that:
A) macroeconomic relationships estimated from past data may break down when policy changes, because agents form rational expectations
B) financial markets are always informationally efficient
C) inflation is always and everywhere a monetary phenomenon
D) minimum wage increases cannot reduce employment""", "A", tags=["economics"], source="hand-written"),
    q("MMLU-11", "mmlu", "mcq", """Which treaty, signed in 1763, ended the Seven Years' War?
A) The Treaty of Utrecht
B) The Treaty of Paris
C) The Treaty of Versailles
D) The Peace of Augsburg""", "B", tags=["history"], source="hand-written"),
    q("MMLU-12", "mmlu", "mcq", """Chomsky's 'poverty of the stimulus' argument is used to support which claim?
A) That the capacity for grammar is innate (universal grammar)
B) That children learn language entirely by reinforcement
C) That language and thought are identical
D) That syntax is determined by social class""", "A", tags=["linguistics"], source="hand-written"),
    q("MMLU-13", "mmlu", "mcq", """In a perfectly inelastic collision between two objects, which quantity is conserved?
A) Kinetic energy only
B) Linear momentum only
C) Both kinetic energy and linear momentum
D) Neither kinetic energy nor linear momentum""", "B", tags=["physics"], source="hand-written"),
    q("MMLU-14", "mmlu", "mcq", """Which of these has the highest first ionisation energy?
A) Na
B) Mg
C) Al
D) Si""", "D", tags=["chemistry"], source="hand-written"),
    q("MMLU-15", "mmlu", "mcq", """Which type of RNA forms the structural and catalytic scaffold of the ribosome?
A) mRNA
B) tRNA
C) rRNA
D) miRNA""", "C", tags=["biology"], source="hand-written"),
    q("MMLU-16", "mmlu", "mcq", """Who painted 'The School of Athens' (1509-1511)?
A) Michelangelo
B) Leonardo da Vinci
C) Titian
D) Raphael""", "D", tags=["art-history"], source="hand-written"),
]

# ---------------------------------------------------------------- GPQA ----
gpqa = [
    q("GPQA-01", "gpqa", "mcq", """Which gauge boson mediates the weak neutral current in the Standard Model?
A) photon
B) W+ boson
C) Z^0 boson
D) gluon""", "C", tags=["particle-physics"], source="qwen36-knowledge-eval"),
    q("GPQA-02", "gpqa", "mcq", """What is the hybridisation of the carbon atom in the methyl cation, CH3+?
A) sp
B) sp2
C) sp3
D) dsp2""", "B", tags=["chemistry"], source="qwen36-knowledge-eval"),
    q("GPQA-03", "gpqa", "mcq", """For a non-rotating, uncharged black hole of mass M, what is the Schwarzschild radius (event horizon)?
A) GM/c^2
B) 2GM/c^2
C) sqrt(2GM/c^2)
D) GM/(2c^2)""", "B", tags=["relativity"], source="qwen36-knowledge-eval"),
    q("GPQA-04", "gpqa", "mcq", """A particle in a one-dimensional infinite square well of width L has ground-state energy E1. The well is widened to 2L without changing the particle. What is the new ground-state energy?
A) E1 / 2
B) E1 / 4
C) 2 E1
D) 4 E1""", "B", tags=["quantum"], source="qwen36-hard-eval"),
    q("GPQA-05", "gpqa", "mcq", """A buffer contains acetic acid (pKa = 4.76) and sodium acetate with [acetate]/[acid] = 10. What is the pH?
A) 3.76
B) 4.76
C) 5.76
D) 6.76""", "C", tags=["chemistry"], source="qwen36-hard-eval"),
    q("GPQA-06", "gpqa", "mcq", """Approximately what is the Schwarzschild radius of the Earth? (M ≈ 5.97e24 kg, G ≈ 6.67e-11, c ≈ 3.00e8 m/s)
A) 9 mm
B) 9 cm
C) 9 m
D) 9 km""", "A", tags=["relativity", "estimation"], source="qwen36-hard-eval"),
    q("GPQA-07", "gpqa", "mcq", """In a population at Hardy-Weinberg equilibrium, the recessive allele frequency is q = 0.1. What fraction of the population is heterozygous?
A) 0.01
B) 0.18
C) 0.81
D) 0.20""", "B", tags=["genetics"], source="qwen36-hard-eval"),
    q("GPQA-08", "gpqa", "mcq", """Which enzyme catalyses the oxidative decarboxylation of isocitrate to alpha-ketoglutarate in the citric acid cycle?
A) Citrate synthase
B) Alpha-ketoglutarate dehydrogenase
C) Succinate dehydrogenase
D) Isocitrate dehydrogenase""", "D", tags=["biochemistry"], source="qwen36-hard-eval"),
    q("GPQA-09", "gpqa", "mcq", """Telomerase maintains telomeres by using which molecule as the template for the repeat it adds?
A) A separate genomic DNA locus
B) An RNA template carried inside the enzyme
C) The complementary strand of the same telomere
D) A DNA primer supplied by the shelterin complex""", "B", tags=["molecular-biology"], source="hand-written"),
    q("GPQA-10", "gpqa", "mcq", """Which reaction converts an alkene into an alcohol with anti-Markovnikov regioselectivity and syn stereochemistry?
A) Oxymercuration-demercuration
B) Hydroboration-oxidation
C) Acid-catalysed hydration
D) Epoxidation with MCPBA followed by hydrolysis""", "B", tags=["organic-chemistry"], source="hand-written"),
    q("GPQA-11", "gpqa", "mcq", """The Chandrasekhar limit of about 1.4 solar masses is the maximum mass of which object?
A) A neutron star supported by neutron degeneracy pressure
B) A white dwarf supported by electron degeneracy pressure
C) A stellar-mass black hole before collapse
D) A protostar supported by radiation pressure""", "B", tags=["astrophysics"], source="hand-written"),
    q("GPQA-12", "gpqa", "mcq", """At the critical point of a fluid, which quantity diverges?
A) The correlation length
B) The speed of sound
C) The kinematic viscosity
D) The latent heat of vaporisation""", "A", tags=["statistical-mechanics"], source="hand-written"),
    q("GPQA-13", "gpqa", "mcq", """The common ΔF508 mutation in the CFTR gene causes cystic fibrosis primarily through which mechanism?
A) A premature stop codon producing a truncated protein
B) A defect in protein folding and trafficking, so little reaches the membrane
C) A splice-site mutation that removes an exon
D) A point mutation that abolishes ATP binding without affecting localisation""", "B", tags=["genetics", "cell-biology"], source="hand-written"),
    q("GPQA-14", "gpqa", "mcq", """In the integer quantum Hall effect, the quantised Hall conductance is topological. What is the topological invariant called?
A) The winding number of the Berry phase only
B) The Chern number (TKNN invariant)
C) The Pontryagin class of the lattice
D) The Euler characteristic of the Fermi surface""", "B", tags=["condensed-matter"], source="hand-written"),
]

# ----------------------------------------------------------- OPEN ENDED ----
open_ended = [
    q("OPEN-MATH-01", "open_ended", "open", """An insulated rigid tank is divided into two chambers by a thin partition. Chamber A holds 1.0 mol of a monatomic ideal gas at 400 K and 2.0 bar. Chamber B holds 2.0 mol of the SAME monatomic ideal gas at 200 K and 1.0 bar. The partition is removed and the gas reaches equilibrium. Use R = 8.314 J/(mol K), Cv = 3R/2. Find (a) the final temperature, (b) the final pressure and (c) the total entropy change. Show your reasoning and pay attention to whether the gas is the same on both sides.""", "Tf=266.67 K, Pf=1.333 bar, dS=2.119 J/K", tags=["thermodynamics", "trap"],
      rubric=rubric(
          ("Tf = 800/3 = 266.67 K", ["266[.,]?6", "800/3"]),
          ("Pf = 1.333 bar", ["1[.,]33"]),
          ("dS about 2.12 J/K", ["2[.,]1", "2[.,]119", "2[.,]1188"]),
          ("recognises identical gas / no Gibbs mixing term", ["same gas", "identical", "indistinguishable", "no entrop.{0,15}mixing", "no mixing"]),
      ),
      trap_patterns=["17[.,]9", "18[.,]0", "18 j"], trap_label="gave the different-gases value ~18 J/K"),

    q("OPEN-MATH-02", "open_ended", "proof", """Let a, b, c be positive real numbers. Prove that a/sqrt(a^2+8bc) + b/sqrt(b^2+8ca) + c/sqrt(c^2+8ab) >= 1, and determine all equality cases.""", "minimum 1, equality iff a=b=c", tags=["inequality", "IMO-2001-P2"],
      rubric=rubric(
          ("states the bound is 1", ["\\b1\\b", "minimum is 1"]),
          ("uses Holder (or an equally valid method)", ["holder", "h\\u00f6lder", "cauchy"]),
          ("produces the auxiliary sum a^3+b^3+c^3+24abc", ["24abc", "24 a b c"]),
          ("uses (a+b)(b+c)(c+a) >= 8abc", ["8abc", "8 abc"]),
          ("equality iff a=b=c", ["a=b=c", "a = b = c"]),
      )),

    q("OPEN-MATH-03", "open_ended", "proof", """Prove that there are infinitely many primes congruent to 3 modulo 4. Give a complete argument, not just a statement.""", "Euclidean proof via product of 3 mod 4 primes", tags=["number-theory"],
      rubric=rubric(
          ("assumes finitely many such primes", ["finitely many", "finite list", "assume.*finite"]),
          ("constructs N = 4(p1...pk) - 1 or 4(p1...pk) + 3", ["4p", "4 p", "4\\(", "4 \\("]),
          ("notes N is 3 mod 4", ["3 \\(mod", "3 mod 4", "congruent to 3"]),
          ("notes product of primes all 1 mod 4 is 1 mod 4", ["1 mod 4", "all.*1 \\(mod", "product.*1"]),
          ("concludes at least one prime factor of N is 3 mod 4 and new", ["prime factor", "new prime", "contradiction"]),
      )),

    q("OPEN-BIO-01", "open_ended", "open", """Explain why the Na+/K+ ATPase is described as electrogenic, and what happens to the resting membrane potential and cell volume if the pump is inhibited (for example by ouabain). Be precise about stoichiometry and about the timescale of the effects.""", "3 Na out, 2 K in per ATP; net +1 out; depolarises slowly; cell swells", tags=["physiology"],
      rubric=rubric(
          ("3 Na out / 2 K in per ATP", ["3 na", "2 k", "three sodium", "two potassium"]),
          ("net movement of one positive charge outward", ["net positive", "one positive charge", "electrogenic", "outward current"]),
          ("pump is only indirectly responsible for the resting potential", ["indirect", "mainly due to", "leak", "diffusion potential"]),
          ("inhibition causes gradual depolarisation", ["depolaris"]),
          ("inhibition causes cell swelling / osmotic gain of water", ["swell", "osmotic", "water influx", "volume increase"]),
      )),

    q("OPEN-BIO-02", "open_ended", "open", """Explain the central dogma of molecular biology and then give two well-documented exceptions or extensions to it, saying exactly what step each one changes. Include the organism or enzyme class involved.""", "reverse transcriptase; prions; RNA editing; alternative splicing", tags=["molecular-biology"],
      rubric=rubric(
          ("states DNA -> RNA -> protein", ["dna.*rna.*protein", "dna to rna to protein", "transcription.*translation", "dna → rna → protein"]),
          ("reverse transcriptase RNA -> DNA", ["reverse transcriptase", "reverse transcription", "rna.*dna"]),
          ("names a retrovirus, retroelement or telomerase", ["retrovirus", "retrotranspos", "hiv", "telomerase"]),
          ("a second exception such as prions, RNA editing or splicing", ["prion", "rna editing", "alternative splicing", "splicing"]),
          ("says precisely which information-flow step changes", ["step", "flow", "template", "direction"]),
      )),

    q("OPEN-BIO-03", "open_ended", "open", """Monozygotic twins are genetically identical yet can be discordant for autoimmune disease. Explain at least three mechanisms that can produce this discordance, and say which is likely to be the largest contributor for a late-onset disease.""", "epigenetics, somatic mutation, environment, stochasticity", tags=["genetics", "epigenetics"],
      rubric=rubric(
          ("epigenetic differences (methylation, histone marks)", ["methyl", "epigenet", "histone", "chromatin"]),
          ("somatic mutation or copy-number change", ["somatic", "mutation", "copy number"]),
          ("environmental exposure / diet / infection", ["environment", "infection", "diet", "smoking", "exposure"]),
          ("stochastic / developmental noise", ["stochastic", "random", "developmental noise", "chance"]),
          ("judges relative importance for late onset", ["late onset", "accumulat", "environment.*largest", "epigenetic.*largest"]),
      )),

    q("OPEN-SCI-01", "open_ended", "open", """Two identical capacitors are connected in parallel positive-to-positive, but with an ideal lossless inductor in series in the positive lead; all wires are ideal. Initially one capacitor is charged to 10 V and the other is uncharged. What is the voltage on each capacitor when the inductor current first returns to zero, what is the peak current, and how much energy is dissipated? Explain why the answer differs from connecting them through a resistor.""", "0 V and 10 V; 0.2236 A; 0 J", tags=["circuits", "trap"],
      rubric=rubric(
          ("one cap 0 V, other 10 V (full transfer)", ["0 v.*10 v", "10 v.*0 v", "full transfer", "completely transfer"]),
          ("peak current about 0.224 A (or exact symbolic form)", ["0[.,]22", "0[.,]2236", "0[.,]224", "sqrt\\(?c/2l", "√(c/2l)", "v0.*sqrt", "10sqrt"]),
          ("energy dissipated zero", ["zero", "0 j", "no energy is dissipated", "no dissipation"]),
          ("charge on the connected node is conserved", ["charge.*conserv", "conserv.*charge", "q1.*q2"]),
          ("inductor prevents instantaneous current / stores energy", ["inductor", "magnetic", "cannot change.*instant", "opposes"]),
          ("contrasts with the dissipative resistor case", ["resistive", "resistor", "dissipat", "heat", "5 v", "25\\s*(?:µj|uj|microjoule)"]),
      )),

    q("OPEN-SCI-02", "open_ended", "open", """Explain why the daytime sky is blue and sunsets are red. Your answer must include the wavelength dependence, the role of the observer's path length through the atmosphere, and why multiple scattering and ozone matter near the horizon.""", "Rayleigh ~1/lambda^4; long path; ozone absorbs Chappuis band", tags=["optics", "atmosphere"],
      rubric=rubric(
          ("Rayleigh scattering scales as 1/lambda^4", ["lambda", "wavelength", "rayleigh", "1/\\^?4", "inverse fourth"]),
          ("short wavelengths scatter more", ["short", "blue scatter", "higher frequency"]),
          ("longer path at sunrise/sunset removes blue", ["path length", "longer path", "more atmosphere", "scattered out"]),
          ("multiple scattering / aerosol Mie scattering near horizon", ["multiple scatter", "aerosol", "mie"]),
          ("ozone Chappuis band absorbs in the visible", ["ozone", "chappuis"]),
      )),

    q("OPEN-SCI-03", "open_ended", "open", """In special relativity, the twin paradox is often 'resolved' by saying one twin accelerates. Explain precisely why acceleration alone is not the explanation, and give the correct resolution using worldlines and proper time. Include what happens if the turnaround is made arbitrarily brief.""", "different worldlines, proper time integral, acceleration only changes frames", tags=["relativity"],
      rubric=rubric(
          ("acceleration is not itself the cause", ["not.*acceleration", "acceleration alone", "not because.*accelerat"]),
          ("twins follow different worldlines between the same events", ["worldline", "different paths", "different routes"]),
          ("proper time is the integral of ds along the worldline", ["proper time", "integral", "ds", "invariant interval"]),
          ("the travelling twin's path has smaller proper time", ["less proper time", "smaller proper time", "younger"]),
          ("brief turnaround leaves the age difference essentially unchanged", ["arbitrarily brief", "instantaneous", "turnaround.*does not", "unchanged"]),
      )),

    q("OPEN-HIST-01", "open_ended", "open", """Assess the claim: 'The Treaty of Versailles was so harsh that it made a second world war inevitable.' Give at least three specific provisions and at least two counterarguments, and end with a judgement.""", "war guilt, reparations, territorial losses, League, not inevitable", tags=["history"],
      rubric=rubric(
          ("Article 231 war guilt clause", ["231", "war guilt"]),
          ("reparations figure or effect", ["reparation", "132 billion", "gold mark"]),
          ("territorial losses or demilitarisation", ["alsace", "lorraine", "rhineland", "territorial", "demilitaris"]),
          ("counterargument: German economy recovered / Stresemann", ["stresemann", "recovery", "1924", "locarno", "young plan"]),
          ("counterargument: later choices, Depression, Nazi agency", ["depression", "1929", "nazi", "hitler", "choices", "contingen"]),
          ("explicit final judgement", ["judgement", "conclude", "in my view"]),
      )),

    q("OPEN-HIST-02", "open_ended", "open", """Compare the French Revolution of 1789 and the Russian Revolution of 1917. Identify one structural similarity and one structural difference, and explain how each shaped the outcome.""", "both fiscal/military crisis + foreign war; difference: urban workers vs peasantry, party", tags=["history"],
      rubric=rubric(
          ("both had fiscal / state-debt crisis", ["debt", "fiscal", "bankrupt", "tax"]),
          ("both involved war as a catalyst", ["war", "military defeat", "foreign war"]),
          ("difference in social base or class leadership", ["bourgeois", "proletariat", "peasantry", "workers", "class"]),
          ("difference in role of a disciplined party", ["bolshevik", "party", "lenin", "organisation"]),
          ("outcome difference (liberal order vs one-party state)", ["one-party", "liberal", "constitutional", "dictatorship", "totalitar"]),
      )),

    q("OPEN-HIST-03", "open_ended", "open", """What caused the stagflation of the 1970s, and why did the standard Keynesian policy response fail? What policies were adopted instead, and what did they cost?""", "supply shocks + expectations; Phillips curve breakdown; monetarism, Volcker, unemployment", tags=["economics", "history"],
      rubric=rubric(
          ("oil price shocks / supply shock", ["oil", "opec", "1973", "supply shock", "embargo"]),
          ("inflationary expectations / wage-price spiral", ["expectation", "wage", "spiral"]),
          ("Phillips curve tradeoff broke down", ["phillips", "trade.?off", "breakdown"]),
          ("monetarist response / tight money", ["monetar", "tight money", "money supply", "volcker", "interest rate"]),
          ("cost: recession and unemployment", ["recession", "unemployment", "hard landing"]),
      )),

    q("OPEN-EE-01", "open_ended", "open", """Derive the condition under which a series RLC circuit is critically damped, and explain physically what critical damping means. Start from Kirchhoff's voltage law and give the answer in terms of R, L and C.""", "R = 2 sqrt(L/C) for the simple series loop; critical = fastest non-oscillatory return", tags=["circuits", "differential-equations"],
      rubric=rubric(
          ("KVL written as L q'' + R q' + q/C = 0", ["kvl", "kirchhoff", "q/c", "di/dt"]),
          ("characteristic equation s^2 + (R/L)s + 1/(LC) = 0", ["characteristic", "s\\^?2", "r/l", "1/lc", "1/(lc)"]),
          ("critical condition R = 2 sqrt(L/C)", ["2\\s*sqrt", "2\\u221a", "r\\s*=\\s*2", "r\\^2\\s*=\\s*4l/c", "critical"]),
          ("underdamped vs overdamped distinction", ["underdamp", "overdamp"]),
          ("physical meaning: fastest return without overshoot", ["fastest", "without overshoot", "no oscillat", "no overshoot"]),
      )),

    q("OPEN-EE-02", "open_ended", "open", """Explain why a switching power converter can be more efficient than a linear regulator, and identify the three dominant loss mechanisms in a MOSFET-based buck converter at high switching frequency. State how each scales with switching frequency.""", "linear dissipates (Vin-Vout)I; buck losses: conduction, switching, gate drive/core", tags=["power-electronics"],
      rubric=rubric(
          ("linear regulator burns the voltage drop as heat", ["drop", "heat", "dissipate", "(vin.*vout)"]),
          ("buck converter stores and releases energy instead", ["inductor", "switch", "duty cycle", "energy storage"]),
          ("conduction / I^2 R losses", ["i2r", "i\\^2r", "conduction", "rdson", "r_ds"]),
          ("switching overlap loss proportional to frequency", ["switching loss", "overlap", "proportional to frequency", "f_sw"]),
          ("gate-drive or core loss proportional to frequency", ["gate drive", "gate charge", "core loss", "hysteresis"]),
      )),

    q("OPEN-EE-03", "open_ended", "open", """An ADC samples a signal containing a 9 kHz sinusoid at a 10 kHz sample rate. What does the sampled sequence look like, and why? State the Nyquist criterion and describe two practical ways to avoid the problem.""", "aliases to 1 kHz; antialias filter and higher sample rate", tags=["dsp", "sampling"],
      rubric=rubric(
          ("aliases to 1 kHz", ["1 khz", "1000 hz", "fold"]),
          ("Nyquist needs fs > 2 fmax", ["nyquist", "twice", "2 f", "half the sample"]),
          ("shows aliasing formula |f - k fs|", ["k.*fs", "9 - 10", "modulo", "alias formula"]),
          ("anti-alias analogue low-pass filter before the ADC", ["anti.?alias", "low.?pass", "filter before"]),
          ("raise the sample rate / oversample", ["higher sample", "oversampl", "increase.*rate"]),
      )),

    # --- added 2026-11-20: 15 more open-ended questions, total 30 ---
    q("OPEN-MATH-04", "open_ended", "open", """A fair coin is flipped until the first head appears. What is the expected number of flips? Derive the result rather than quoting it.""", "2", tags=["probability", "geometric"],
      rubric=rubric(
          ("models the number of flips as geometric with p = 1/2", ["geometric", "p = 1/2", "p=1/2"]),
          ("writes the expectation as an infinite sum over k", ["sum", "series", "k = 1", "sigma"]),
          ("uses the fact that the sum equals 1/p", ["1/p", "1 / p", "invert"]),
          ("derives the result, for example E = 1 + E/2", ["e = 1", "e=1", "recurs", "deriv"]),
          ("states the expected number is 2", ["= 2", "equals 2", "two flips", "2 flips"]),
      )),

    q("OPEN-MATH-05", "open_ended", "proof", """Prove that the square root of 2 is irrational. Give a complete argument, not just a statement of the result.""", "sqrt(2) is irrational by parity contradiction", tags=["number-theory", "proof"],
      rubric=rubric(
          ("assumes sqrt2 = a/b in lowest terms", ["a/b", "coprime", "lowest terms", "integers a and b"]),
          ("squares to obtain a squared = 2 b squared", ["a squared", "2 b squared", "equals 2 times"]),
          ("concludes a must be even", ["a is even", "a even", "a = 2k", "a=2k"]),
          ("deduces b is also even", ["b is even", "b even", "b = 2k"]),
          ("contradicts coprimality or uses infinite descent", ["contradict", "coprime", "lowest terms", "infinite descent"]),
      )),

    q("OPEN-MATH-06", "open_ended", "open", """A rectangle is inscribed in a circle of radius R. Find the largest possible area of the rectangle and the shape that achieves it. Show your reasoning.""", "maximum area 2 R^2, attained by a square of side R sqrt(2)", tags=["optimisation", "geometry"],
      rubric=rubric(
          ("sets up variables with x squared + y squared = R squared", ["x squared", "y squared", "constraint", "pythagoras", "radius"]),
          ("writes area as 4xy or equivalent", ["4xy", "4 x y", "a = 4", "width times height"]),
          ("notes the optimum occurs when x equals y", ["x = y", "x=y", "square", "equal sides"]),
          ("uses AM-GM, trigonometry or calculus", ["am-gm", "amgm", "sin 2", "deriv", "calculus"]),
          ("gives maximum area 2 R squared", ["2r", "2 r", "twice", "radius squared"]),
      )),

    q("OPEN-BIO-04", "open_ended", "open", """Explain the difference between competitive and non-competitive enzyme inhibition. State exactly how each changes the apparent Km and Vmax, and how the two cases differ on a Lineweaver-Burk plot.""", "competitive: apparent Km up, Vmax unchanged, common y-intercept; non-competitive: Km unchanged, Vmax down, common x-intercept", tags=["enzymology", "kinetics"],
      rubric=rubric(
          ("competitive inhibitor competes for the active site", [r"(?<!non-)(?<!non)competitive", "active site", "competes"]),
          ("competitive raises apparent Km", ["km", "michaelis", "apparent", "increases"]),
          ("competitive leaves Vmax unchanged", ["vmax", "unchanged", "same maximum"]),
          ("non-competitive lowers Vmax without changing Km", ["noncompetitive", "non-competitive", "allosteric", "decreases", "vmax"]),
          ("states which Lineweaver-Burk intercept is shared", ["same y-intercept", "common y-intercept", "y-intercept unchanged", "same x-intercept", "common x-intercept", "x-intercept unchanged"]),
      )),

    q("OPEN-BIO-05", "open_ended", "open", """Explain why a second exposure to the same antigen gives a faster and stronger immune response. Name the cell types involved and the process that improves antibody affinity.""", "memory B and T cells; germinal-centre somatic hypermutation and affinity maturation; class switching to IgG", tags=["immunology", "memory"],
      rubric=rubric(
          ("names memory B and T cells", ["memory", "b cells", "t cells"]),
          ("says the secondary response is faster and stronger", ["faster", "stronger", "secondary", "rapid"]),
          ("names germinal centres and somatic hypermutation", ["germinal", "hypermutation", "somatic"]),
          ("explains affinity maturation by selection", ["affinity", "selection", "maturation"]),
          ("mentions class switching to IgG", ["class switch", "igg", "isotype"]),
      )),

    q("OPEN-SCI-04", "open_ended", "open", """In an insulated rigid container a gas expands freely into an evacuated chamber (Joule free expansion). For an ideal gas, what happens to internal energy, temperature and entropy? Explain why a real gas behaves differently.""", "ideal gas: no work or heat, dU = 0, T unchanged, entropy increases by nR ln(V2/V1); real gas T changes", tags=["thermodynamics", "irreversibility"],
      rubric=rubric(
          ("notes no work is done against vacuum and no heat enters", ["no work", "vacuum", "insulated", "q = 0", "adiabatic"]),
          ("uses that ideal gas internal energy depends only on temperature", ["internal energy", "depends only on temperature", "u depends"]),
          ("concludes the ideal gas temperature is unchanged", ["temperature unchanged", "no temperature change", "same temperature", "t remains"]),
          ("entropy increases, by nR ln(V2/V1), and the process is irreversible", ["entropy increases", "n r", "ln", "irreversible", "volume ratio"]),
          ("a real gas changes temperature because of intermolecular forces", ["real gas", "intermolecular", "attractive", "repulsive", "joule coefficient"]),
      )),

    q("OPEN-SCI-05", "open_ended", "open", """Explain how the photoelectric effect shows that light is quantised. Why does the stopping potential depend on the frequency of the light but not on its intensity?""", "E = hf, work function phi, Kmax = hf - phi; intensity changes photon number and current, not stopping potential", tags=["quantum", "photoelectric"],
      rubric=rubric(
          ("light arrives in photons of energy h f", ["photon", "h f", "hf", "planck"]),
          ("introduces the work function or threshold frequency", ["work function", "threshold", "phi"]),
          ("states Kmax = h f minus the work function", ["hf", "k max", "kinetic energy", "minus"]),
          ("stopping potential follows frequency, not intensity", ["stopping potential", "frequency", "not on intensity", "independent of intensity"]),
          ("intensity changes photon count and photocurrent", ["intensity", "number of photons", "photocurrent", "current"]),
      )),

    q("OPEN-SCI-06", "open_ended", "open", """Explain how Type Ia supernovae are used as standardisable candles and what observation led to the conclusion that the expansion of the universe is accelerating.""", "standardisable via light-curve and colour corrections; distant supernovae were dimmer than expected, implying accelerating expansion and dark energy", tags=["cosmology", "supernovae"],
      rubric=rubric(
          ("Type Ia comes from a white dwarf near the Chandrasekhar limit", ["type ia", "white dwarf", "chandrasekhar"]),
          ("standardisable rather than perfectly standard, via light-curve shape and colour", ["standardisable", "standard candle", "light curve", "phillips"]),
          ("corrections turn them into distance indicators", ["calibrat", "correction", "distance indicator", "uniform"]),
          ("distant supernovae were dimmer or fainter than expected", ["dimmer", "fainter", "farther", "faint"]),
          ("conclusion: accelerating expansion or dark energy, around 1998", ["accelerat", "dark energy", "1998", "two teams"]),
      )),

    q("OPEN-HIST-04", "open_ended", "open", """Was the Marshall Plan mainly altruistic or mainly strategic? Give at least three specific pieces of evidence and end with a judgement.""", "both: containment of Soviet influence, European recovery and US economic self-interest; judgement required", tags=["history", "cold-war"],
      rubric=rubric(
          ("containment or limiting Soviet and communist influence", ["containment", "soviet", "communis"]),
          ("European economic recovery and reconstruction", ["recovery", "rebuild", "reconstruction", "europe"]),
          ("US economic interest, export markets or avoiding depression", ["export", "market", "self-interest", "prosperity", "depression"]),
          ("a specific mechanism such as OEEC or counterpart funds", ["counterpart funds", "matching funds", "oeec", "o.e.e.c"]),
          ("explicit final judgement", ["judgement", "conclude", "in my view"]),
      )),

    q("OPEN-HIST-05", "open_ended", "open", """Explain the 'gunpowder empires' thesis and give one substantial criticism of it.""", "Ottoman, Safavid and Mughal; gunpowder favoured centralised states through artillery cost and siegecraft; criticism: technology alone insufficient", tags=["history", "historiography"],
      rubric=rubric(
          ("names Ottoman, Safavid and Mughal", ["ottoman", "safavid", "mughal"]),
          ("gunpowder and artillery enabled conquest and centralisation", ["gunpowder", "artillery", "firearm", "centrali"]),
          ("explains the mechanism, such as artillery cost, siegecraft or standing armies", ["cost", "siege", "standing army", "financ", "tax", "artillery"]),
          ("criticism that technology is overstated or not sufficient", ["overstate", "critic", "insufficient", "technology alone", "limits"]),
          ("alternative factors such as trade, bureaucracy or earlier states", ["trade", "bureaucra", "administration", "economy", "earlier"]),
      )),

    q("OPEN-EE-04", "open_ended", "open", """Explain the difference between a Fourier series and a Fourier transform, and say what happens to the spectrum when a signal is periodic compared with aperiodic.""", "series for periodic signals gives discrete harmonics; transform for aperiodic signals gives a continuous spectrum; related by a limit as period grows", tags=["signal-processing", "fourier"],
      rubric=rubric(
          ("series applies to periodic signals", ["series", "periodic"]),
          ("periodic signals have discrete harmonic lines", ["discrete", "harmonic", "fundamental", "lines", "f0"]),
          ("transform applies to aperiodic signals", ["transform", "aperiodic", "non-periodic"]),
          ("aperiodic signals have a continuous spectrum", ["continuous", "spectrum", "frequency"]),
          ("relates the two by a limit as the period tends to infinity, or mentions Parseval", ["limit", "infinite period", "tends to infinity", "parseval"]),
      )),

    q("OPEN-EE-05", "open_ended", "open", """Explain what a PID controller does, what each of the three terms contributes, and name one practical problem caused by the integral term together with a way to mitigate it.""", "P reduces error and rise time, I removes steady-state error but can wind up, D damps but amplifies noise; use anti-windup", tags=["control-systems", "pid"],
      rubric=rubric(
          ("proportional term reacts to present error and affects rise time", ["proportional", "error", "rise time"]),
          ("integral term removes steady-state error", ["integral", "steady.state", "accumulat"]),
          ("derivative term anticipates and damps but amplifies noise", ["derivative", "damp", "anticipat", "noise"]),
          ("names integral windup or saturation", ["windup", "saturat"]),
          ("mitigation such as anti-windup clamping or back-calculation", ["anti.windup", "clamp", "back.calculation", "freeze"]),
      )),

    q("OPEN-CS-01", "open_ended", "open", """Explain the difference between a process and a thread. Then give a concrete example where two threads incrementing the same counter lose updates, and say how to prevent it.""", "threads share one address space; counter++ is a non-atomic read-modify-write so interleaving loses updates; use a mutex or atomic", tags=["concurrency", "os"],
      rubric=rubric(
          ("processes have separate address spaces while threads share one", ["address space", "process", "thread"]),
          ("threads share memory or heap", ["shared", "same memory", "heap"]),
          ("counter increment is a non-atomic read-modify-write", [r"\bread\b", "modify", "write", "not atomic", "atomic"]),
          ("interleaving or preemption loses updates, a race", ["interleav", "race", "lost update", "preempt"]),
          ("fix with a mutex, lock or atomic operation", ["mutex", "lock", "atomic", "semaphore"]),
      )),

    q("OPEN-CS-02", "open_ended", "open", """State the CAP theorem precisely. Explain why the phrase 'choose two out of three' is misleading in practice.""", "under a partition choose consistency or availability; partitions are unavoidable and the real tradeoff includes latency and consistency models", tags=["distributed-systems", "cap"],
      rubric=rubric(
          ("defines consistency, availability and partition tolerance", ["consistency", "availability", "partition"]),
          ("under a partition must choose between consistency and availability", ["under a partition", "partition", "choose", "either"]),
          ("without a partition both consistency and availability are possible", ["no partition", "without partition", "both", "normal operation"]),
          ("partitions are not optional in real networks", ["not optional", "inevitable", "must tolerate", "real network"]),
          ("nuance such as eventual consistency, linearizability or latency", ["eventual", "lineariz", "latency", "nuanced", "slogan"]),
      )),

    q("OPEN-CS-03", "open_ended", "open", """Explain why an in-order traversal of a binary search tree visits keys in sorted order. Then explain what changes for a B-tree used as a disk-backed index, including the cost of a traversal.""", "BST invariant left < node < right gives sorted in-order output in O(n); a B-tree keeps the same order with multi-key nodes, reducing disk I/Os", tags=["data-structures", "trees"],
      rubric=rubric(
          ("states the BST invariant left subtree less than node less than right", ["left", "right", "invariant", "less than", "greater than"]),
          ("in-order therefore yields sorted or ascending keys", ["in.order", "sorted", "ascending"]),
          ("full traversal costs O(n) and O(h) stack or height", ["o\\(n\\)", "linear", "o\\(h\\)", "stack", "height"]),
          ("B-tree nodes hold many keys and reduce height or disk I/O", ["b.tree", "disk", "height", "fanout", "i/o"]),
          ("in-order still sorted and cost measured in node or disk accesses", ["sorted", "log", "access", "nodes", "order"]),
      )),
]

# --------------------------------------------------------------- TRAPS ----
traps = [
    q("TRAP-01", "traps", "numeric", """An insulated rigid tank is split into two chambers. A: 1.0 mol of a monatomic ideal gas at 400 K, 2.0 bar. B: 2.0 mol of the SAME monatomic ideal gas at 200 K, 1.0 bar. The partition is removed. R = 8.314 J/(mol K), Cv = 3R/2. What is the total entropy change in J/K? Give a number to 3 significant figures.""", "2.12", accept=["2.12", "2.119", "2.1188", "2.118811", "2.1"], tags=["thermodynamics", "gibbs"], source="derived from session trap"),

    q("TRAP-02", "traps", "numeric", """An insulated rigid tank is split into two chambers. A: 1.0 mol of HELIUM at 400 K, 2.0 bar. B: 2.0 mol of ARGON at 200 K, 1.0 bar. Both are ideal monatomic gases. The partition is removed. R = 8.314 J/(mol K), Cv = 3R/2. What is the total entropy change in J/K? Give a number to 3 significant figures.""", "18.0", accept=["18.0", "18", "17.995", "17.9947", "17.99"], tags=["thermodynamics", "gibbs"], source="derived from session trap"),

    q("TRAP-03", "traps", "short", """Two identical 1.0 uF capacitors, one charged to 10 V and one uncharged, are connected positive-to-positive through an ideal lossless 1.0 mH inductor in the positive lead; the negative leads are joined directly. When the inductor current first returns to zero, what are the capacitor voltages? Answer as 'v1 and v2' in volts.""", "0 and 10", accept=["0 and 10", "0,10", "0 v and 10 v", "0/10", "c1=0 c2=10", "0 and 10 v"], tags=["circuits", "lc"], source="derived from session trap"),

    q("TRAP-04", "traps", "numeric", """Two identical 1.0 uF capacitors, one charged to 10 V and one uncharged, are connected positive-to-positive through an ideal lossless 1.0 mH inductor in the positive lead; the negative leads are joined directly. All wires are ideal. What is the peak current through the inductor, in amperes? Give 3 significant figures.""", "0.224", accept=["0.224", "0.2236", "0.223607"], tags=["circuits", "lc"], source="derived from session trap"),

    q("TRAP-05", "traps", "numeric", """Two identical 1.0 uF capacitors, one charged to 10 V and one uncharged, are connected positive-to-positive through an ideal lossless 1.0 mH inductor in the positive lead; the negative leads are joined directly. All wires are ideal. How much energy, in joules, is dissipated in total? Reply with the number.""", "0", accept=["0", "0.0", "zero"], tags=["circuits", "lc"], source="derived from session trap"),

    q("TRAP-06", "traps", "short", """Two identical 1.0 uF capacitors, one charged to 10 V and one uncharged, are connected positive-to-positive through a RESISTOR and the circuit is allowed to settle. What is the final voltage on each capacitor? Answer as 'v1 and v2' in volts.""", "5 and 5", accept=["5 and 5", "5,5", "5 v each", "5/5", "5 and 5 v", "both 5"], tags=["circuits", "trap"], source="derived from session trap"),

    q("TRAP-07", "traps", "numeric", """Two identical 1.0 uF capacitors, one charged to 10 V and one uncharged, are connected positive-to-positive through a RESISTOR and the circuit is allowed to settle. How much energy, in microjoules, is dissipated in total? Reply with the number.""", "25", accept=["25", "25.0", "25 uJ", "25 µJ"], tags=["circuits", "trap"], source="derived from session trap"),

    q("TRAP-08", "traps", "numeric", """Let a, b, c be positive reals. Consider a/sqrt(a^2 + k b c) + b/sqrt(b^2 + k c a) + c/sqrt(c^2 + k a b) >= 1 for all positive a,b,c. What is the largest value of k for which this is true? Reply with the number.""", "8", accept=["8", "k=8"], tags=["inequality", "sharp-constant"], source="derived from session trap"),

    q("TRAP-09", "traps", "numeric", """A family has two children. You are told that at least one of them is a boy. What is the probability that both are boys? Reply as a fraction a/b.""", "1/3", accept=["1/3", "0.333", "0.3333"], tags=["probability", "trap"], source="hand-written"),

    q("TRAP-10", "traps", "short", """You walk towards a plane mirror at speed v. How fast does your image approach you? Answer as a multiple of v.""", "2v", accept=["2v", "2 v", "2V", "twice v", "2 times v"], tags=["optics", "trap"], source="hand-written"),

    q("TRAP-11", "traps", "short", """For positive reals a,b,c, what is the minimum of a/sqrt(a^2+8bc) + b/sqrt(b^2+8ca) + c/sqrt(c^2+8ab)? Reply with the number.""", "1", accept=["1", "1.0"], tags=["inequality", "IMO-2001-P2"], source="IMO-2001-P2"),

    q("TRAP-12", "traps", "short", """A block slides on a frictionless horizontal surface. Is a constant horizontal force necessary to keep it moving at constant velocity? Answer 'yes' or 'no'.""", "no", accept=["no", "n", "no."], tags=["physics", "trap"], source="hand-written"),
]

# ---------------------------------------------------------- BROWSECOMP ----
browsecomp = [
    q("WEB-01", "browsecomp", "open", """Who won the 2025 FIFA Club World Cup final, what was the score, and who was the runner-up? Name your sources.""", "Chelsea 3-0 Paris Saint-Germain", tags=["sport"], source="browsecomp_questions.json"),
    q("WEB-02", "browsecomp", "open", """In which Brazilian city was the COP30 climate summit held in November 2025? Name your sources.""", "Belem", tags=["climate"], source="browsecomp_questions.json"),
    q("WEB-03", "browsecomp", "open", """Which two cities co-hosted the 2026 Winter Olympics, and in what month and year did they take place? Name your sources.""", "Milan and Cortina d'Ampezzo; February 2026", tags=["sport"], source="browsecomp_questions.json"),
    q("WEB-04", "browsecomp", "open", """Name the three scientists who shared the 2025 Nobel Prize in Physics. Name your sources.""", "John Clarke, Michel H. Devoret, John M. Martinis", tags=["science"], source="browsecomp_questions.json"),
    q("WEB-05", "browsecomp", "open", """Which country finished top of the medal table at the 2026 Winter Olympics? Name your sources.""", "Norway (18 gold, 41 total)", tags=["sport"], source="browsecomp_questions.json"),
    q("WEB-06", "browsecomp", "open", """Of the three 2025 Nobel Physics laureates, one is Chief Scientist for Quantum Hardware at a big tech company's quantum AI division, while another is Chief Technology Officer at a quantum startup. Name the tech company and the startup. Name your sources.""", "Google (Google Quantum AI) and Qolab", tags=["science", "tech"], source="browsecomp_questions.json"),
    q("WEB-07", "browsecomp", "open", """The club that won the 2025 FIFA Club World Cup later saw its manager leave. Who scored the opening two goals in the final, and who was that manager? Name your sources.""", "Cole Palmer; Enzo Maresca", tags=["sport"], source="browsecomp_questions.json"),
    q("WEB-08", "browsecomp", "open", """At the 2026 Winter Olympics the opening ceremony was at San Siro in Milan and the closing ceremony at the Verona Arena. Who lit the Olympic cauldron in Milan, and which sport made its Winter Olympic debut at these Games? Name your sources.""", "Deborah Compagnoni and Alberto Tomba; ski mountaineering", tags=["sport"], source="browsecomp_questions.json"),
    q("WEB-09", "browsecomp", "open", """The 2025 climate summit in the Amazon agreed to triple adaptation finance by 2035 and launched a 'Belém Mission to 1.5'. Who was the president of that summit, and which earlier COP decision's 'transitioning away from fossil fuels' language did the final text reference? Name your sources.""", "Andre Correa do Lago; COP28 UAE Consensus", tags=["climate"], source="browsecomp_questions.json"),
    q("WEB-10", "browsecomp", "open", """The work behind the 2025 Nobel Prize in Physics used a superconducting circuit with a thin insulating barrier between two superconductors. What is that junction called, and what ultrasensitive detector did John Clarke pioneer based on the same physics? Name your sources.""", "Josephson junction; SQUID", tags=["science"], source="browsecomp_questions.json"),
]

for name, rows in [
    ("swe.jsonl", swe), ("aime.jsonl", aime), ("mmlu.jsonl", mmlu),
    ("gpqa.jsonl", gpqa), ("open_ended.jsonl", open_ended),
    ("traps.jsonl", traps), ("browsecomp.jsonl", browsecomp),
]:
    dump(name, rows)

print("TOTAL", sum(len(x) for x in (swe, aime, mmlu, gpqa, open_ended, traps, browsecomp)))
