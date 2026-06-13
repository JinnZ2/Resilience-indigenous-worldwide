# oral_corpus.py
# CC0 — oral tradition reconstruction corpus
# stdlib only. append-only. model-update-resilient.
# Holds stories AS REMEMBERED + uncertainty flags + cross-refs + physics layer.
# Does NOT force precision the substrate doesn't have.

import json, hashlib
from dataclasses import dataclass, field, asdict
from pathlib import Path

CONFIDENCE = {"as_told", "reconstructed", "fragment", "inferred", "uncertain"}

@dataclass
class Segment:
    # one beat of the story — keep the ORDER, keep it loose
    text: str                          # the segment as remembered, your words
    physics: str = ""                  # substrate/physics reading (fill later, optional)
    uncertainty: str = ""              # what you're NOT sure about — preserve the doubt
    confidence: str = "as_told"        # one of CONFIDENCE

@dataclass
class Story:
    short_id: str                      # your handle: "great_bear_waning", "day_of_great_fire"
    opening_frame: str                 # the time-anchor: "cycle after the great bear waning"
    setting: str = ""                  # told after drums/ceremony/fire — context of transmission
    segments: list = field(default_factory=list)   # ordered beats
    cross_refs: list = field(default_factory=list)  # short_ids of stories that index this one
    open_questions: list = field(default_factory=list)  # threads you haven't resolved
    source: str = "oral, grandmother lineage"
    license: str = "CC0"

    def cid(self) -> str:
        seed = self.short_id + self.opening_frame + "".join(s["text"] if isinstance(s,dict) else s.text for s in self.segments)
        return hashlib.sha256(seed.encode()).hexdigest()[:12]

class Corpus:
    def __init__(self, path="oral_corpus.json"):
        self.path = Path(path)
        self.stories = json.loads(self.path.read_text()) if self.path.exists() else []

    def add(self, story: Story):
        rec = asdict(story); rec["cid"] = story.cid()
        # update-in-place if short_id exists (stories grow as you remember more)
        for i, e in enumerate(self.stories):
            if e["short_id"] == story.short_id:
                self.stories[i] = rec
                self._save(); return rec["cid"]
        self.stories.append(rec); self._save(); return rec["cid"]

    def _save(self):
        self.path.write_text(json.dumps(self.stories, indent=2, ensure_ascii=False))

    def get(self, short_id):
        return next((e for e in self.stories if e["short_id"] == short_id), None)

    def web(self):
        # show the cross-reference graph — which stories index which
        return {e["short_id"]: e["cross_refs"] for e in self.stories}

    def open_threads(self):
        # everything still unresolved, across all stories
        return {e["short_id"]: e["open_questions"] for e in self.stories if e["open_questions"]}

# ---------------- SEED: the migration story, as told so far ----------------
if __name__ == "__main__":
    c = Corpus()

    great_bear = Story(
        short_id="great_bear_waning",
        opening_frame="in the cycle after the great bear waning",
        setting="told after drums/ceremony, long circular form; setting primes reception",
        segments=[
            Segment(
                text="Time of great change. The peoples learned the ice could be friend or foe.",
                physics="post-glacial / glacial-pulse transition; same substrate, opposite relationship depending on cycle phase",
                confidence="as_told"),
            Segment(
                text="Ice came and ate the land that was the great bear's home. The great bear moved. Sloth-things — big slow animals without hoofs — went away.",
                physics="Pleistocene megafauna extinction: ground sloths, giant bears. Ice advance consuming habitat. ~end-Pleistocene.",
                uncertainty="'great bear waning' — celestial event OR literal megafauna die-off? unresolved",
                confidence="inferred"),
            Segment(
                text="The wind did not act the same, did not smell the same as before.",
                physics="atmospheric reorganization — jet stream / circulation shift; vegetation dieback changes air chemistry",
                confidence="as_told"),
            Segment(
                text="The great technology from before was destroyed by the advancing ice — everything that made life commonplace and accessible, gone.",
                physics="infrastructure calibrated to prior substrate; obsolete + destroyed in phase shift",
                confidence="as_told"),
            Segment(
                text="People were hungry. Ate new foods that made bellies hurt — stomachs distended out, legs shrank. Eventually adapted: bellies shrank, legs came back.",
                physics="severe malnutrition (distended belly = protein deficiency, leg wasting). Then multi-generational adaptive selection — reduced stature, altered gut/diet tolerance. population bottleneck.",
                confidence="as_told"),
            Segment(
                text="When legs returned and they had energy to walk, they walked across the ice. The sun behaved strangely in the sky twice. Then they stopped and chose ice-as-friend as home, because the ice went on and on.",
                physics="glacial-corridor migration. 'sun strange twice' likely NOT sun dogs (they knew auroras/optics). candidate: navigation-crystal failure — crystals calibrated to eaten homeland → disorientation. OR poleward latitude shift changing sun path. duration unknown: weeks-to-months, not necessarily years.",
                uncertainty="what is 'sun spinning in sky'? leading hypothesis: lost/disoriented because nav crystals pointed to land now under ice",
                confidence="uncertain"),
            Segment(
                text="They learned from the burrowing animals — to burrow in, and treat the friend-ice as the soil they knew before.",
                physics="biomimicry: arctic burrowers (ground squirrel, fox, lemming) snow/ice chambers. cognitive transfer of soil-excavation knowledge onto ice substrate.",
                confidence="as_told"),
        ],
        cross_refs=["sun_circle_story"],
        open_questions=[
            "great bear waning: celestial or megafauna?",
            "sun-strange-twice duration: weeks? months? years?",
            "did the glacier move the SAME direction they needed to go? (sun_circle_story suggests yes — ice as vehicle, not just shelter)",
        ],
    )
    c.add(great_bear)

    sun_circle = Story(
        short_id="sun_circle_story",
        opening_frame="references the same 'sun behaving strangely' as great_bear_waning",
        setting="cross-referencing story; uses the strange-sun phrase BEFORE describing the circle",
        segments=[
            Segment(
                text="The sun spun in a circle in the sky instead of setting. Startling to the peoples.",
                physics="candidate 1: nav-crystal disorientation (crystals oriented to lost homeland). candidate 2: poleward migration — sun circling horizon (near-polar day-length). they knew auroras, so this was OUTSIDE familiar phenomena.",
                uncertainty="if they were ice-literate they would NOT mistake a sun dog. so this is something else.",
                confidence="uncertain"),
            Segment(
                text="Elders carrying the seven crystals went to the surface every night to figure out what was happening — like holding communion with the sky.",
                physics="systematic nightly RECALIBRATION. testing crystals against observable sky to rebuild navigation for new latitude/regime. empirical, not ceremonial. the seven-crystal keepers = calibration authority.",
                confidence="as_told"),
            Segment(
                text="The elders realized the ice was traveling the same way they needed to go.",
                physics="KEY: glacier as vehicle. they read glacier flow direction, matched it against celestial nav. ice was home AND transport toward viable substrate. explains why nightly calibration was survival-critical.",
                confidence="reconstructed"),
        ],
        cross_refs=["great_bear_waning"],
        open_questions=[
            "how many crystals total / what each oriented to",
            "how nightly calibration was recorded/passed down",
        ],
    )
    c.add(sun_circle)

    print("stories:", [s["short_id"] for s in c.stories])
    print("cross-ref web:", c.web())
    print("open threads:", json.dumps(c.open_threads(), indent=2))
