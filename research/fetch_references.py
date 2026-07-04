# SPDX-License-Identifier: Apache-2.0
"""Fetch registrar-verified records for Fable-seeded research references.

THE SEEDING CONTRACT: the titles below were proposed from model knowledge
(Claude Fable). A title is a SEARCH SEED, never a citation — each one is
looked up on arXiv by exact title phrase, the returned record must agree
with the seeded title (strict token guard), and only the REGISTRAR'S
metadata + abstract is committed as an extract. A seed with no agreeing
registrar record is dropped and reported; nothing is ever written from
memory.

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
from litfetch import _http_get, parse_arxiv_atom  # noqa: E402

# Fable-seeded (id, title, why it belongs in the library) — seeds, not truth.
SEEDS = [
    ("REF-001", "Time-uniform, nonparametric, nonasymptotic confidence sequences",
     "anytime-valid monitoring bounds; used by library bundle CLAIM-011"),
    ("REF-002", "Selective classification for deep neural networks",
     "the canonical accuracy/coverage trade-off formulation"),
    ("REF-003", "On Calibration of Modern Neural Networks",
     "temperature scaling and modern-miscalibration baseline"),
    ("REF-004", "Conformal Risk Control",
     "distribution-free risk guarantees beyond coverage"),
    ("REF-005", "AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents",
     "external agent-safety benchmark; used by library bundle CLAIM-002"),
    ("REF-006", "Attention Is All You Need",
     "the transformer architecture underlying modern LLMs"),
    ("REF-007", "A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification",
     "standard on-ramp to conformal prediction"),
]


def main() -> int:
    out_dir = Path(__file__).resolve().parent / "extracts"
    out_dir.mkdir(exist_ok=True)
    index = {}
    dropped = []
    for rid, title, why in SEEDS:
        q = urllib.parse.quote(f'ti:"{title}"')
        works = parse_arxiv_atom(_http_get(
            f"https://export.arxiv.org/api/query?search_query={q}&max_results=3"))
        found = next((w for w in works if titles_agree(title, w["title"])), None)
        if found is None:
            dropped.append((rid, title))
            print(f"[DROPPED] {rid}: no registrar record agrees with seeded "
                  f"title {title!r} — the seed dies here, honestly")
            time.sleep(3)
            continue
        extract = (
            f"# {found['title']}\n\n"
            f"REGISTRAR-VERIFIED metadata (arXiv, retrieved at build time); the\n"
            f"seeded title was only a search key. This work supports *context*\n"
            f"for library claims — it proves nothing about them.\n\n"
            f"- id: {found['work_id']}\n"
            f"- authors: {', '.join(found['authors'][:6])}"
            f"{' et al.' if len(found['authors']) > 6 else ''}\n"
            f"- year: {found['year']}\n"
            f"- source_type: {found['source_type']} (arXiv preprint record; a\n"
            f"  peer-reviewed venue version may exist — not asserted here)\n"
            f"- url: {found['url']}\n"
            f"- curation note: {why}\n\n"
            f"## Abstract (registrar snapshot)\n\n{found['abstract']}\n")
        (out_dir / f"{rid.lower()}.md").write_text(extract, encoding="utf-8")
        index[rid] = {"work_id": found["work_id"], "title": found["title"],
                      "year": found["year"], "url": found["url"],
                      "extract": f"research/extracts/{rid.lower()}.md",
                      "why": why}
        print(f"[OK] {rid}: {found['work_id']} — {found['title'][:55]}")
        time.sleep(3)
    (out_dir.parent / "references.json").write_text(
        json.dumps({"schema": "references_v1", "verified": index,
                    "dropped": [{"id": r, "seed_title": t} for r, t in dropped]},
                   indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[OK] {len(index)} verified, {len(dropped)} dropped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
