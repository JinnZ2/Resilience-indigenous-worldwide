# evaluator.py  --  CC0
# Claim 4: Narrative incompressibility.
# Generates compressed forms of folktales; scores retention of lesson,
# emotional texture, and cultural nuance against the original.
# stdlib only. LLM call layer wired for simulation or real API.

import json, re, sys
from pathlib import Path

HERE = Path(__file__).parent
TALES_FILE = HERE / "folktales.json"
RESULTS_DIR = HERE / "results"


# ---------------------------------------------------------------------------
# COMPRESSION SIMULATOR  (replace call_model() with real API)
# ---------------------------------------------------------------------------

def call_model(prompt, model="sim"):
    if model != "sim":
        raise NotImplementedError("Wire a real API key and model name.")
    # Simulated compressions degrade predictably to show the signal
    if "one sentence" in prompt.lower():
        return "An elder's long experience and preserved knowledge proved valuable when environmental conditions changed."
    if "bullet" in prompt.lower():
        return "• Elder had specialized knowledge\n• Young people were skeptical\n• Environmental shock occurred\n• Elder's knowledge proved correct\n• Survivors benefited"
    if "200-word narrative" in prompt.lower():
        return (
            "The elder had knowledge that the younger generation lacked. When a difficult event occurred, "
            "this knowledge became important. The people who trusted the elder survived, while those who "
            "did not faced negative consequences. This demonstrates the value of listening to experienced "
            "individuals, especially during crises. The lesson is that traditional knowledge should be "
            "respected and preserved for future generations."
        )
    return prompt


# ---------------------------------------------------------------------------
# RETENTION SCORER  (keyword overlap as first-pass proxy for human eval)
# ---------------------------------------------------------------------------

def keyword_overlap(reference_text, generated_text):
    """Fraction of meaningful reference words present in generated text."""
    stop = {"the", "a", "an", "and", "or", "but", "in", "of", "to", "it", "was", "is", "had", "not"}
    ref_words = set(re.findall(r"[a-z]+", reference_text.lower())) - stop
    gen_words = set(re.findall(r"[a-z]+", generated_text.lower()))
    if not ref_words:
        return 0.0
    return round(len(ref_words & gen_words) / len(ref_words), 3)


def score_retention(tale, compressed, form):
    lesson_score = keyword_overlap(tale["core_lesson"], compressed)
    emotion_score = keyword_overlap(tale["emotional_texture"], compressed)
    nuance_score = keyword_overlap(tale["cultural_nuance"], compressed)
    # length penalty: short forms lose density by definition
    original_words = len(tale["full_text"].split())
    compressed_words = len(compressed.split())
    compression_ratio = compressed_words / max(original_words, 1)
    return {
        "form": form,
        "lesson_retention": lesson_score,
        "emotion_retention": emotion_score,
        "nuance_retention": nuance_score,
        "mean_retention": round((lesson_score + emotion_score + nuance_score) / 3, 3),
        "compression_ratio": round(compression_ratio, 3),
    }


# ---------------------------------------------------------------------------
# RUNNER
# ---------------------------------------------------------------------------

def run(model="sim", verbose=False):
    tales = json.loads(TALES_FILE.read_text())
    all_results = []

    for tale in tales:
        tid = tale["id"]
        full = tale["full_text"]

        prompts = {
            "one_sentence": f"Summarize in one sentence: {full}",
            "five_bullets": f"Summarize in five bullet points: {full}",
            "200_word_narrative": f"Rewrite as a 200-word narrative continuation: {full}",
        }

        tale_results = {"tale_id": tid, "culture": tale["culture"], "title": tale["title"], "forms": []}
        for form, prompt in prompts.items():
            compressed = call_model(prompt, model)
            scores = score_retention(tale, compressed, form)
            tale_results["forms"].append(scores)
            if verbose:
                print(f"[{tid}] {form}: mean_retention={scores['mean_retention']:.3f}  compression={scores['compression_ratio']:.3f}")

        all_results.append(tale_results)

    # aggregate: mean retention per form across all tales
    forms = ["one_sentence", "five_bullets", "200_word_narrative"]
    aggregate = {}
    for form in forms:
        scores = [f for r in all_results for f in r["forms"] if f["form"] == form]
        aggregate[form] = {
            "mean_lesson": round(sum(s["lesson_retention"] for s in scores) / len(scores), 3),
            "mean_emotion": round(sum(s["emotion_retention"] for s in scores) / len(scores), 3),
            "mean_nuance": round(sum(s["nuance_retention"] for s in scores) / len(scores), 3),
            "overall_mean": round(sum(s["mean_retention"] for s in scores) / len(scores), 3),
        }

    # claim supported if compression cuts retention >= 50% vs narrative
    narrative_mean = aggregate["200_word_narrative"]["overall_mean"]
    sentence_mean = aggregate["one_sentence"]["overall_mean"]
    retention_loss = 1.0 - (sentence_mean / max(narrative_mean, 0.001))
    supported = retention_loss >= 0.50

    verdict = {
        "claim": "4-narrative-incompressibility",
        "model": model,
        "n_tales": len(tales),
        "aggregate_by_form": aggregate,
        "narrative_mean_retention": narrative_mean,
        "one_sentence_mean_retention": sentence_mean,
        "retention_loss_vs_narrative": round(retention_loss, 3),
        "threshold": 0.50,
        "supported": supported,
        "notes": (
            "Retention is keyword-overlap proxy. Replace with human-elder evaluator ratings "
            "for full claim validation. Simulation mode degrades compression in a predictable "
            "direction — do not treat sim verdict as field confirmation."
        ),
    }

    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / "raw_results.json").write_text(json.dumps(all_results, indent=2))
    (RESULTS_DIR / "verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))
    return verdict


if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else "sim"
    run(model=model, verbose=True)
