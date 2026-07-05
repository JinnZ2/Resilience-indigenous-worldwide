# co_occurrence_analysis.py  --  CC0
# Claim 5: Elder value cross-cultural — co-occurrence analysis.
# Counts "elder + wisdom/knowledge/council/story" vs "elder + fertility/reproduction"
# across the corpus loaded by eHRAF_parser.py.
# stdlib only.

import json, re
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent
RESULTS_DIR = HERE / "results"
PARSED_CORPUS = RESULTS_DIR / "parsed_corpus.json"

# ---------------------------------------------------------------------------
# TERM SETS
# ---------------------------------------------------------------------------

ELDER_TERMS = {"elder", "elders", "grandmother", "grandfather", "kaumatua",
               "abuelo", "abuela", "lama", "grandparent", "old woman", "old man",
               "clan mother", "healer", "elder council"}

WISDOM_TERMS = {"wisdom", "knowledge", "memory", "council", "story", "stories",
                "teaching", "teachings", "genealogy", "archive", "authority",
                "spiritual", "ceremony", "lineage", "tradition", "guide",
                "transmit", "transmission", "survival", "heal", "healer",
                "navigate", "navigation", "ecological", "geographic"}

FERTILITY_TERMS = {"fertility", "reproduction", "reproductive", "childbearing",
                   "pregnant", "birth", "offspring", "fertility rate", "menarche",
                   "menopause", "ovulation", "fecundity"}


def has_term(text, terms):
    text_l = text.lower()
    return any(t in text_l for t in terms)


def count_cooccurrence(passages, elder_terms, target_terms):
    """Count passages where an elder term AND a target term both appear."""
    count = 0
    matching = []
    for p in passages:
        if has_term(p["text"], elder_terms) and has_term(p["text"], target_terms):
            count += 1
            matching.append(p)
    return count, matching


def run():
    # load parsed corpus (run eHRAF_parser.py first, or fall back to seed)
    if PARSED_CORPUS.exists():
        passages = json.loads(PARSED_CORPUS.read_text())
    else:
        from eHRAF_parser import SEED_CORPUS
        passages = SEED_CORPUS

    total = len(passages)
    cultures = len({p["culture"] for p in passages})

    elder_wisdom_count, ew_passages = count_cooccurrence(passages, ELDER_TERMS, WISDOM_TERMS)
    elder_fertility_count, ef_passages = count_cooccurrence(passages, ELDER_TERMS, FERTILITY_TERMS)

    ratio = elder_wisdom_count / max(elder_fertility_count, 1)
    threshold_ratio = 10.0
    falsification_ratio = 2.0
    supported = ratio >= threshold_ratio

    # per-culture breakdown
    by_culture = defaultdict(lambda: {"wisdom": 0, "fertility": 0})
    for p in passages:
        c = p["culture"]
        if has_term(p["text"], ELDER_TERMS):
            if has_term(p["text"], WISDOM_TERMS):
                by_culture[c]["wisdom"] += 1
            if has_term(p["text"], FERTILITY_TERMS):
                by_culture[c]["fertility"] += 1

    verdict = {
        "claim": "5-elder-value-cross-cultural",
        "total_passages": total,
        "cultures": cultures,
        "elder_wisdom_cooccurrences": elder_wisdom_count,
        "elder_fertility_cooccurrences": elder_fertility_count,
        "ratio_wisdom_to_fertility": round(ratio, 2),
        "threshold_for_support": threshold_ratio,
        "falsification_threshold": falsification_ratio,
        "supported": supported,
        "by_culture": dict(by_culture),
        "notes": (
            "Seed corpus is illustrative. Wire eHRAF export at claim5-cross-cultural/eHRAF_corpus.json "
            "for real validation. Keyword co-occurrence is a first-pass proxy; replace with "
            "embedding-based semantic similarity for publication-grade results."
        ),
    }

    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / "elder_wisdom_passages.json").write_text(json.dumps(ew_passages, indent=2, ensure_ascii=False))
    (RESULTS_DIR / "elder_fertility_passages.json").write_text(json.dumps(ef_passages, indent=2, ensure_ascii=False))
    (RESULTS_DIR / "verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))
    return verdict


if __name__ == "__main__":
    run()
