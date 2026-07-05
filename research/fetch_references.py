# SPDX-License-Identifier: Apache-2.0
"""Fetch registrar-verified records for seeded research references.

THE SEEDING CONTRACT: titles (and any DOIs) below are SEEDS — proposed from
model knowledge or supplied by the curator — never citations. Each seed is
resolved against a registrar (DOI lookup, Crossref title search, arXiv
title-phrase search, in that order) and the returned record must AGREE with
the seeded title under the strict token guard. Only the registrar's
metadata is committed; a seed nothing agrees with is dropped and reported.

    PYTHONPATH=/Users/stian/vericlaim python3 research/fetch_references.py
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
from pathlib import Path

sys.path.insert(0, "/Users/stian/vericlaim/integrations/library")
from biblio_curate import titles_agree  # noqa: E402
from litfetch import _http_get, crossref_search, parse_arxiv_atom, parse_crossref  # noqa: E402

# (id, title-seed, optional doi-seed, expected-surname, expected-year, why).
# Everything is a SEED: the resolved record must agree on TITLE (strict token
# guard), carry the expected AUTHOR surname, and land within 2 years of the
# expected YEAR — title alone proved insufficient live (a 2025 critique
# titled "Is Attention All You Need?", a book REVIEW of GEB, and an
# unrelated Apress chapter all passed the title guard).
SEEDS = [
    ("REF-001", "Time-uniform, nonparametric, nonasymptotic confidence sequences",
     None, "howard", 2021, "anytime-valid monitoring bounds; used by library bundle CLAIM-011"),
    ("REF-002", "Selective classification for deep neural networks",
     None, "geifman", 2017, "the canonical accuracy/coverage trade-off formulation"),
    ("REF-003", "On Calibration of Modern Neural Networks",
     None, "guo", 2017, "temperature scaling and modern-miscalibration baseline"),
    ("REF-004", "Conformal Risk Control",
     None, "angelopoulos", 2022, "distribution-free risk guarantees beyond coverage"),
    ("REF-005", "AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents",
     None, "andriushchenko", 2024, "external agent-safety benchmark; used by library bundle CLAIM-002"),
    ("REF-006", "Attention Is All You Need",
     None, "vaswani", 2017, "the transformer architecture underlying modern LLMs"),
    ("REF-007", "A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification",
     None, "angelopoulos", 2021, "standard on-ramp to conformal prediction"),
    ("REF-008", "Multilayer feedforward networks are universal approximators",
     None, "hornik", 1989, "Hornik/Stinchcombe/White 1989 — the universal approximation theorem; context for THM-UAT-001"),
    ("REF-009", "Brewer's conjecture and the feasibility of consistent, available, partition-tolerant web services",
     "10.1145/564585.564601", "gilbert", 2002, "Gilbert & Lynch 2002 — the CAP theorem, formally proved"),
    ("REF-010", "Flow diagrams, turing machines and languages with only two formation rules",
     "10.1145/355592.365646", "bohm", 1966, "Bohm & Jacopini 1966 — the structured program theorem"),
    ("REF-011", "Pattern Recognition and Machine Learning",
     None, "bishop", 2006, "Bishop 2006 — Bayes-based ML; context for THM-BAYES-001"),
    ("REF-012", "All of Statistics: A Concise Course in Statistical Inference",
     None, "wasserman", 2004, "Wasserman — CLT and inference; context for THM-CLT-001"),
    ("REF-013", "Introduction to Algorithms",
     None, "cormen", 2009, "CLRS — the master theorem; context for THM-MASTER-001"),
    ("REF-014", "Learning with Kernels",
     None, "scholkopf", 2002, "Scholkopf & Smola — Mercer's theorem and the kernel trick"),
    ("REF-015", "Über formal unentscheidbare Sätze der Principia Mathematica und verwandter Systeme I",
     None, "godel", 1931, "Godel 1931 — the incompleteness theorems, original paper"),
    ("REF-016", "Gödel, Escher, Bach: An Eternal Golden Braid",
     None, "hofstadter", 1979, "Hofstadter — popular exposition connecting Godel to computation (context, not a proof source)"),
    # --- batch 3: optimization, information/learning theory, graphs, logic ---
    ("REF-017", "The Lack of A Priori Distinctions Between Learning Algorithms",
     None, "wolpert", 1996, "Wolpert — the No Free Lunch theorem for learning; context for THM-NFL-001"),
    ("REF-018", "On the Uniform Convergence of Relative Frequencies of Events to Their Probabilities",
     None, "vapnik", 1971, "Vapnik & Chervonenkis — VC dimension and uniform convergence; context for THM-VC-001"),
    ("REF-019", "A Mathematical Theory of Communication",
     None, "shannon", 1948, "Shannon 1948 — information theory and the sampling context for THM-NYQ-001"),
    ("REF-020", "Classes of Recursively Enumerable Sets and Their Decision Problems",
     None, "rice", 1953, "Rice's theorem — undecidability of nontrivial semantic properties"),
    ("REF-021", "Convex Optimization",
     None, "boyd", 2004, "Boyd & Vandenberghe — KKT conditions; context for THM-KKT-001"),
    ("REF-022", "Understanding Machine Learning: From Theory to Algorithms",
     None, "shalev-shwartz", 2014, "Shalev-Shwartz & Ben-David — Rademacher/VC generalization theory"),
    ("REF-023", "Introduction to Graph Theory",
     None, "west", 2001, "West — Euler circuits and fundamental graph theory; context for THM-EULER-001"),
    ("REF-024", "Lectures on the Curry-Howard Isomorphism",
     None, "sorensen", 2006, "Sorensen & Urzyczyn — proofs-as-programs; context for THM-CH-001"),
    ("REF-025", "Matrix Analysis",
     None, "horn", 1985, "Horn & Johnson — Perron-Frobenius theory; context for THM-PF-001"),
    # --- batch 4/5: dimensionality, information, graphs, research front ---
    ("REF-026", "Extensions of Lipschitz mappings into a Hilbert space",
     None, "johnson", 1984, "Johnson & Lindenstrauss — the JL lemma; context for THM-JL-001"),
    ("REF-027", "Asymptotic Statistics",
     None, "vaart", 1998, "van der Vaart — Glivenko-Cantelli and empirical processes; context for THM-GC-001"),
    ("REF-028", "Probability and Computing: Randomization and Probabilistic Analysis in Algorithms and Data Structures",
     None, "mitzenmacher", 2005, "Mitzenmacher & Upfal — Markov/Chebyshev in algorithm analysis; context for THM-INEQ-001"),
    ("REF-029", "The Two-Valued Iterative Systems of Mathematical Logic",
     None, "post", 1941, "Post — functional completeness; context for THM-POST-001"),
    ("REF-030", "Maximal Flow Through a Network",
     None, "ford", 1956, "Ford & Fulkerson — the max-flow min-cut theorem; context for THM-MFMC-001"),
    ("REF-031", "Algebraic Geometry and Statistical Learning Theory",
     None, "watanabe", 2009, "Watanabe — singular learning theory (research front; no bounded instance attempted)"),
    ("REF-032", "Flow Matching for Generative Modeling",
     None, "lipman", 2022, "Lipman et al. — flow matching / optimal-transport paths; 1-D OT instance is THM-OT-001"),
    ("REF-033", "Geometric Deep Learning: Grids, Groups, Graphs, Geodesics, and Gauges",
     None, "bronstein", 2021, "Bronstein et al. — equivariance program (research front; no bounded instance attempted)"),
    ("REF-034", "Topology and Data",
     None, "carlsson", 2009, "Carlsson — topological data analysis (research front; no bounded instance attempted)"),
    ("REF-035", "Algorithmic Learning in a Random World",
     None, "vovk", 2005, "Vovk, Gammerman & Shafer — the founding conformal-prediction monograph; context for THM-CONF-001..004"),
    ("REF-036", "The Lean 4 Theorem Prover and Programming Language",
     None, "moura", 2021, "de Moura & Ullrich — the kernel that checks THM-LEAN-001..003"),
    # --- batch A: alignment & safety landmarks ---
    ("REF-037", "Training language models to follow instructions with human feedback",
     None, "ouyang", 2022, "InstructGPT — RLHF as the alignment baseline of modern assistants"),
    ("REF-038", "Constitutional AI: Harmlessness from AI Feedback",
     None, "bai", 2022, "principle-guided self-critique replacing human harm labels"),
    ("REF-039", "Direct Preference Optimization: Your Language Model is Secretly a Reward Model",
     None, "rafailov", 2023, "preference optimization without an explicit reward model"),
    ("REF-040", "Concrete Problems in AI Safety",
     None, "amodei", 2016, "the agenda paper that framed practical safety research"),
    ("REF-041", "Sleeper Agents: Training Deceptive LLMs that Persist Through Safety Training",
     None, "hubinger", 2024, "deceptive behavior surviving safety training — core threat model for gating"),
    ("REF-042", "Weak-to-Strong Generalization: Eliciting Strong Capabilities with Weak Supervision",
     None, "burns", 2023, "supervising models stronger than the supervisor — scalable-oversight core"),
    ("REF-043", "AI safety via debate",
     None, "irving", 2018, "adversarial verification as an oversight mechanism"),
]


def _norm(s: str) -> str:
    import unicodedata
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def _record_agrees(seed_title, surname, year, work) -> bool:
    """Title tokens + author surname + year window — all three, always."""
    if not titles_agree(seed_title, work["title"]):
        return False
    if not any(_norm(surname) in _norm(a) for a in work.get("authors", [])):
        return False
    wy = work.get("year")
    return isinstance(wy, int) and abs(wy - year) <= 2


def _lookup(title: str, doi: str | None, surname: str, year: int):
    """Registrar resolution order: DOI -> Crossref title -> arXiv phrase.
    Every path ends at the same title+author+year guard."""
    if doi:
        try:
            works = parse_crossref(_http_get("https://api.crossref.org/works/"
                                             + urllib.parse.quote(doi)))
            if works and _record_agrees(title, surname, year, works[0]):
                return works[0], "doi"
            if works:
                return None, (f"DOI seed resolves to {works[0]['title']!r} "
                              f"({works[0].get('year')}) — fails the "
                              f"title+author+year guard")
        except Exception as exc:  # noqa: BLE001
            return None, f"doi lookup failed: {exc}"
    try:
        # generic titles drown in look-alikes: search with the author
        # appended too, and scan more candidates — the guard still decides.
        seen = []
        for q in (f"{title} {surname}", title):
            for w in crossref_search(q, 10):
                if w["work_id"] in seen:
                    continue
                seen.append(w["work_id"])
                if _record_agrees(title, surname, year, w):
                    return w, "crossref-title"
    except Exception:  # noqa: BLE001 — fall through to arXiv
        pass
    time.sleep(3)
    try:
        q = urllib.parse.quote(f'ti:"{title}"')
        for w in parse_arxiv_atom(_http_get(
                "https://export.arxiv.org/api/query?search_query="
                + q + "&max_results=3")):
            if _record_agrees(title, surname, year, w):
                return w, "arxiv-title-phrase"
    except Exception as exc:  # noqa: BLE001
        return None, f"arxiv lookup failed: {exc}"
    return None, "no registrar record with an agreeing title"


def main() -> int:
    out_dir = Path(__file__).resolve().parent / "extracts"
    out_dir.mkdir(exist_ok=True)
    index, dropped = {}, []
    for rid, title, doi, surname, year, why in SEEDS:
        found, how = _lookup(title, doi, surname, year)
        if found is None:
            dropped.append((rid, title, how))
            print(f"[DROPPED] {rid}: {how} — the seed dies here, honestly")
            time.sleep(1)
            continue
        acc = ("peer-reviewed venue" if found.get("accredited")
               else found.get("source_type", "?"))
        extract = (
            f"# {found['title']}\n\n"
            f"REGISTRAR-VERIFIED metadata (via {how}, retrieved at build "
            f"time); the seed was only a search key. This work supports "
            f"*context* for library claims — it proves nothing about them.\n\n"
            f"- id: {found['work_id']}\n"
            f"- authors: {', '.join(found['authors'][:6])}"
            f"{' et al.' if len(found['authors']) > 6 else ''}\n"
            f"- year: {found['year']}\n"
            f"- venue: {found.get('venue') or 'n/a'}\n"
            f"- source_type: {found['source_type']} ({acc})\n"
            f"- url: {found['url']}\n"
            f"- curation note: {why}\n\n"
            f"## Abstract (registrar snapshot)\n\n"
            f"{found['abstract'] or '(registrar record carries no abstract)'}\n")
        (out_dir / f"{rid.lower()}.md").write_text(extract, encoding="utf-8")
        index[rid] = {"work_id": found["work_id"], "title": found["title"],
                      "year": found["year"], "url": found["url"],
                      "how": how, "accredited": bool(found.get("accredited")),
                      "extract": f"research/extracts/{rid.lower()}.md",
                      "why": why}
        print(f"[OK] {rid}: {found['work_id']} ({how}, {acc}) — "
              f"{found['title'][:50]}")
        time.sleep(2)
    (out_dir.parent / "references.json").write_text(
        json.dumps({"schema": "references_v2", "verified": index,
                    "dropped": [{"id": r, "seed_title": t, "reason": why}
                                for r, t, why in dropped]},
                   indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[OK] {len(index)} verified, {len(dropped)} dropped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
