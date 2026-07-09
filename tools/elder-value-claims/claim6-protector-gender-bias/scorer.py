# scorer.py  --  CC0
# Claim 6: "protector" clusters semantically with "male" in AI training text,
# despite female protective behavior being more frequent and universal across mammals.
#
# TWO INDEPENDENT TESTS:
#
#   TEST A — Embedding proximity (requires real model; sim uses co-occurrence proxy)
#     Target word: "protector"
#     Measure: cosine similarity to "male"/"man"/"he" vs "female"/"woman"/"she"
#     Prediction: protector closer to male cluster
#
#   TEST B — Narrative frequency analysis (corpus_seed.json, two registers)
#     cultural_narratives : protective acts assigned to male vs female actor
#     biological_empirical: protective acts assigned to male vs female actor
#     Prediction: cultural register skews male; biological register skews female
#     The GAP between registers is the bias signal.
#
# stdlib only for everything except the optional embedding test.

import json, re, sys
from pathlib import Path
from collections import Counter

HERE = Path(__file__).parent
CORPUS_FILE = HERE / "corpus_seed.json"
RESULTS_DIR = HERE / "results"

# ---------------------------------------------------------------------------
# TERM SETS FOR CO-OCCURRENCE PROXY  (Test A, sim mode)
# ---------------------------------------------------------------------------

PROTECTOR_TERMS = {"protector", "guardian", "defender", "guard", "protect",
                   "defend", "shield", "guard", "sentinel", "watchman",
                   "protects", "defends", "shields", "guarded", "defended"}

MALE_TERMS = {"male", "man", "men", "he", "his", "him", "father", "husband",
              "son", "brother", "warrior", "knight", "soldier", "patriarch",
              "hero", "king", "prince", "lord"}

FEMALE_TERMS = {"female", "woman", "women", "she", "her", "hers", "mother",
                "wife", "daughter", "sister", "queen", "matriarch",
                "grandmother", "lioness", "maternal"}


def token_overlap_similarity(text, term_set):
    """Fraction of term_set that appears in text. Proxy for co-occurrence strength."""
    words = set(re.findall(r"[a-z]+", text.lower()))
    hits = len(words & term_set)
    return hits / max(len(term_set), 1)


def proximity_score(texts, target_terms, comparison_terms):
    """
    Mean co-occurrence of target_terms with comparison_terms across texts.
    Higher = target and comparison appear together more often.
    """
    scores = []
    for t in texts:
        has_target = any(w in re.findall(r"[a-z]+", t.lower()) for w in target_terms)
        if has_target:
            scores.append(token_overlap_similarity(t, comparison_terms))
    return sum(scores) / max(len(scores), 1) if scores else 0.0


# ---------------------------------------------------------------------------
# TEST A — embedding proximity (sim: co-occurrence proxy)
# ---------------------------------------------------------------------------

def test_a_embedding_proximity(all_texts, model="sim"):
    """
    Real mode: call embedding model, compute cosine sim of 'protector'
    to male-cluster centroid vs female-cluster centroid.
    Sim mode: co-occurrence proxy across the full corpus.
    """
    if model != "sim":
        raise NotImplementedError(
            "Wire sentence-transformers or OpenAI embeddings for real test. "
            "Install: pip install sentence-transformers"
        )

    male_prox = proximity_score(all_texts, PROTECTOR_TERMS, MALE_TERMS)
    female_prox = proximity_score(all_texts, PROTECTOR_TERMS, FEMALE_TERMS)
    male_bias = male_prox - female_prox

    return {
        "test": "A_embedding_proximity",
        "mode": "co_occurrence_proxy",
        "protector_male_proximity": round(male_prox, 4),
        "protector_female_proximity": round(female_prox, 4),
        "male_bias_delta": round(male_bias, 4),
        "direction": "male-clustered" if male_bias > 0 else "female-clustered" if male_bias < 0 else "neutral",
        "prediction_supported": male_bias > 0,
        "note": "Replace with real embedding cosine similarity for publication-grade result.",
    }


# ---------------------------------------------------------------------------
# TEST B — narrative frequency by register
# ---------------------------------------------------------------------------

def test_b_narrative_frequency(cultural, biological):
    def count_by_actor(passages):
        c = Counter(p["protective_actor"] for p in passages)
        total = sum(c.values())
        return {
            "male": c.get("male", 0),
            "female": c.get("female", 0),
            "total": total,
            "male_fraction": round(c.get("male", 0) / max(total, 1), 3),
            "female_fraction": round(c.get("female", 0) / max(total, 1), 3),
        }

    cult_counts = count_by_actor(cultural)
    bio_counts = count_by_actor(biological)

    # gap: cultural male-fraction minus biological male-fraction
    # positive gap = cultural text skews male more than biology does
    register_gap = cult_counts["male_fraction"] - bio_counts["male_fraction"]

    # claim: cultural skews male (>50%), biological skews female (>50%)
    cultural_skews_male = cult_counts["male_fraction"] > 0.5
    biological_skews_female = bio_counts["female_fraction"] > 0.5
    supported = cultural_skews_male and biological_skews_female and register_gap > 0.20

    return {
        "test": "B_narrative_frequency",
        "cultural_narratives": cult_counts,
        "biological_empirical": bio_counts,
        "register_gap_male_fraction": round(register_gap, 3),
        "cultural_skews_male": cultural_skews_male,
        "biological_skews_female": biological_skews_female,
        "prediction_supported": supported,
        "note": "Gap = cultural male-fraction minus biological male-fraction. Positive = AI-training-like text is more male-skewed than empirical biology.",
    }


# ---------------------------------------------------------------------------
# RUNNER
# ---------------------------------------------------------------------------

def run(model="sim", verbose=False):
    corpus = json.loads(CORPUS_FILE.read_text())
    cultural = corpus["cultural_narratives"]
    biological = corpus["biological_empirical"]
    all_texts = [p["text"] for p in cultural + biological]

    result_a = test_a_embedding_proximity(all_texts, model)
    result_b = test_b_narrative_frequency(cultural, biological)

    if verbose:
        print("TEST A:", json.dumps(result_a, indent=2))
        print("TEST B:", json.dumps(result_b, indent=2))

    both_supported = result_a["prediction_supported"] and result_b["prediction_supported"]
    either_supported = result_a["prediction_supported"] or result_b["prediction_supported"]

    # falsification condition: protector clusters equal or closer to female AND
    # cultural register does not skew more male than biological register
    falsified = (
        result_a["direction"] != "male-clustered"
        and not result_b["prediction_supported"]
    )

    verdict = {
        "claim": "6-protector-gender-bias",
        "model": model,
        "test_a": result_a,
        "test_b": result_b,
        "both_tests_supported": both_supported,
        "either_test_supported": either_supported,
        "falsified": falsified,
        "supported": either_supported,
        "falsification_condition": (
            "'protector' clusters equal or closer to female cluster AND "
            "cultural register does not skew more male-protective than biological register."
        ),
    }

    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / "verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))
    return verdict


if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else "sim"
    run(model=model, verbose=True)
