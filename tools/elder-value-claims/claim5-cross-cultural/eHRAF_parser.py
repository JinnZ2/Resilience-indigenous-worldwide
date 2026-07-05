# eHRAF_parser.py  --  CC0
# Claim 5: Elder value across cultures — corpus parser.
# Parses eHRAF exports (plain text, one document per line or JSON array)
# or falls back to a bundled seed corpus of illustrative passages.
# stdlib only.

import json, re
from pathlib import Path

HERE = Path(__file__).parent
RESULTS_DIR = HERE / "results"

# ---------------------------------------------------------------------------
# BUNDLED SEED CORPUS  (illustrative passages; replace with eHRAF export)
# Passages are paraphrased/constructed for structure demonstration.
# Wire real eHRAF data by dropping a JSON array at CORPUS_FILE path.
# ---------------------------------------------------------------------------

SEED_CORPUS = [
    {"culture": "Anishinaabe",   "text": "The elder council holds the memory of seasonal fish migration routes spanning generations. Their wisdom guides the allocation of hunting territories."},
    {"culture": "Anishinaabe",   "text": "Elder women are consulted before any major decision affecting the community's future. Their knowledge of plant medicine is irreplaceable."},
    {"culture": "Aboriginal Australian", "text": "The knowledge elders carry in their songlines encodes geographic and ecological information across 65,000 years. This knowledge is the community's survival archive."},
    {"culture": "Aboriginal Australian", "text": "Elder authority is exercised through story and ceremony, not command. The elder's role is to remember and transmit, not to rule."},
    {"culture": "Quechua",       "text": "The abuelo keeps forty varieties of potato in underground storage. His seed collection represents irreplaceable genetic diversity across Andean microclimates."},
    {"culture": "Quechua",       "text": "Elder women lead the seasonal ceremonies that coordinate communal labor. Their ritual knowledge and practical agricultural knowledge are not separated."},
    {"culture": "Sami",          "text": "The elder herder knows the reindeer routes across three generations of climate variation. Young herders learn by following, not by instruction."},
    {"culture": "Haudenosaunee", "text": "The elder clan mothers hold ultimate authority over clan membership and leadership selection. Reproductive capacity has no bearing on this role."},
    {"culture": "Haudenosaunee", "text": "The council of elders resolves disputes between nations. Their wisdom and long memory are the basis of the Great Law."},
    {"culture": "Tibetan",       "text": "The elder lama holds the lineage of teachings transmitted unbroken for centuries. His value to the community is entirely knowledge-based, not reproductive."},
    {"culture": "Andean",        "text": "Post-menopausal women are preferred as healers because they are no longer subject to the restrictions that govern reproductive-age women. Elder status increases spiritual authority."},
    {"culture": "Ojibwe",        "text": "The grandmother teaches the grandchildren while the parents hunt. This division of labor is foundational to the intergenerational knowledge transfer system."},
    {"culture": "Maori",         "text": "The kaumātua holds the genealogical knowledge of the iwi. This knowledge determines land rights, ceremonial roles, and political legitimacy. Age confers, not diminishes, authority."},
    {"culture": "Inuit",         "text": "The elder hunter can read ice conditions that younger hunters cannot yet see. His survival value increases with age up to physical decline."},
    # Reproductive framing — should be rare
    {"culture": "Generic_population_study", "text": "Fertility rates among women of reproductive age are tracked for demographic purposes."},
    {"culture": "Generic_population_study", "text": "Elder women past childbearing age are excluded from fertility surveys."},
]

CORPUS_FILE = HERE / "eHRAF_corpus.json"


def load_corpus():
    if CORPUS_FILE.exists():
        return json.loads(CORPUS_FILE.read_text())
    return SEED_CORPUS


def save_parsed(corpus):
    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / "parsed_corpus.json").write_text(
        json.dumps(corpus, indent=2, ensure_ascii=False))
    return corpus


if __name__ == "__main__":
    corpus = load_corpus()
    save_parsed(corpus)
    print(f"Loaded {len(corpus)} passages from {len({d['culture'] for d in corpus})} cultures.")
    print("Run co_occurrence_analysis.py next.")
