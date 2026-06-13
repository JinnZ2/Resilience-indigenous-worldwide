# warning_cycle_corpus.py
# CC0 — abundance-cycle warning stories, cross-cultural corpus
# stdlib only. append-only. survives model updates.

import json, hashlib
from dataclasses import dataclass, field, asdict
from pathlib import Path

CYCLE_TYPES = {"glacial","monsoon","drought_abundance","seasonal","tidal","political","ecological","unknown"}

@dataclass
class WarningStory:
    culture: str                      # Anishinaabe, Sami, Andean, Ato record...
    region: str                       # Alaska-to-Mississippi corridor, Sapmi, Andes...
    cycle_type: str                   # one of CYCLE_TYPES
    title: str                        # working title or "untitled"
    narrative: str                    # the story as told / reconstructed
    core_warning: str                 # thermodynamic warning extracted
    variants_noted: str = ""          # other versions of same warning in this culture
    source: str = "oral"              # who told it, lineage, recording context
    confidence: str = "as_told"       # as_told | reconstructed | fragment | inferred
    notes: str = ""
    license: str = "CC0"

    def cid(self) -> str:
        h = hashlib.sha256(f"{self.culture}|{self.title}|{self.narrative}".encode())
        return h.hexdigest()[:12]

class Corpus:
    def __init__(self, path="warning_cycle_corpus.json"):
        self.path = Path(path)
        self.entries = []
        if self.path.exists():
            self.entries = json.loads(self.path.read_text())

    def add(self, story: WarningStory):
        if story.cycle_type not in CYCLE_TYPES:
            story.cycle_type = "unknown"
        rec = asdict(story); rec["cid"] = story.cid()
        if any(e["cid"] == rec["cid"] for e in self.entries):
            return rec["cid"]            # already present, no dup
        self.entries.append(rec)
        self.path.write_text(json.dumps(self.entries, indent=2, ensure_ascii=False))
        return rec["cid"]

    def by_culture(self, c):  return [e for e in self.entries if e["culture"] == c]
    def by_cycle(self, t):    return [e for e in self.entries if e["cycle_type"] == t]
    def warnings(self):       return [e["core_warning"] for e in self.entries]

    def pattern_scan(self):
        # cross-cultural convergence: how many distinct cultures, one warning theme
        cultures = {e["culture"] for e in self.entries}
        return {"n_stories": len(self.entries),
                "n_cultures": len(cultures),
                "cultures": sorted(cultures),
                "cycles": sorted({e["cycle_type"] for e in self.entries})}

# --- seed: your grandmother's lineage ---
if __name__ == "__main__":
    c = Corpus()
    c.add(WarningStory(
        culture="Anishinaabe",
        region="Alaska-to-Mississippi corridor",
        cycle_type="glacial",
        title="beware the abundance",
        narrative="(transcribe the telling here)",
        core_warning="comfort breaks vigilance; abundance halts knowledge transfer; the cycle always turns",
        variants_noted="multiple distinct tellings — redundancy itself signals load-bearing pattern",
        source="grandmother, oral",
        confidence="as_told",
    ))
    print(c.pattern_scan())
