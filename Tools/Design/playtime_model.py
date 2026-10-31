#!/usr/bin/env python3
"""Blue Signal: playtime model and data check (Python 3, stdlib only).

    python Tools/Design/playtime_model.py           estimate minutes per step, milestone and phase, print the
                                                     table and write Design/Playtime.md
    python Tools/Design/playtime_model.py --check   validate Design/Data/*.json (exit code 1 on any error)

Owner: game-designer. Every assumption is a named constant in the ASSUMPTIONS block. To change the playtime,
change the DATA (part counts, craft times, research seconds), never TARGET_MIN. All rates are per minute.
"""
import json
import math
import os
import re
import sys
from collections import OrderedDict, defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "Design", "Data")
BEATS_MD = os.path.join(ROOT, "Design", "Narrative", "StoryBeats.md")
OUT_MD = os.path.join(ROOT, "Design", "Playtime.md")

# =====================================================================================================
# TARGETS (Production/Brief.md §4). Not tunable: tune the data instead.
# =====================================================================================================
TARGET_MIN = {1: 90.0, 2: 120.0, 3: 120.0, 4: 135.0, 5: 120.0}   # P1 1.5 h, P2 2 h, P3 2 h, P4 2.25 h, P5 2 h
PHASE_TOL = 0.15                                                 # each phase +-15 %
TARGET_TOTAL_MIN, TOTAL_TOL_MIN = 600.0, 60.0                    # 10 h +- 1 h incl. prologue and ending
# Content counts (Brief §4) and the +-20 % the designer may move them.
COUNT_TOL = 0.20
COUNT_TARGETS = {"raw": 8.5, "items": 60, "recipes": 70, "alternates": 13.5, "buildables": 35}
BUILDABLE_SPLIT = {"Production": 8, "Extraction": 5, "Power": 5, "Logistics": 9, "Structure": 15}  # info only
SPECIALS = {"LanderHub", "Workbench", "SuitFabricator", "TideLab", "SignalTower", "TradeBuoy", "Translator"}
MAX_CHAIN_DEPTH = 5
BIOME_PHASE = OrderedDict([("CrashReef", 1), ("BlackSands", 2), ("KelpShallows", 2), ("TarShelves", 3),
                           ("StormSpires", 4), ("GlimmerDeep", 5)])
HAND_STATIONS = {"Workbench", "SuitFabricator"}   # recipes made by hand at these stations
NODE_FIT = {"Node:Solid": {"OreVent", "LimeBed", "SandDune", "StormSpire"}, "Node:KelpBed": {"KelpBed"},
            "Water": {"Sea", "TarSeep"}, "Node:TrenchVent": {"TrenchVent"}, "Node:TidalRace": {"TidalRace"},
            "Anywhere": {"StormSpire"}}   # extractor PlacementRule -> node kinds it can work

# =====================================================================================================
# ASSUMPTIONS: a first-time player on Normal. Each one is a guess about the player, not a balance knob.
# =====================================================================================================
# -- hands --
HAND_CRAFT_FACTOR = 0.5      # hand-crafting one recipe takes CraftTime x this (hold-to-craft at the Workbench)
HAND_GATHER_YIELD = {"ScrapMetal": 5, "Glowkelp": 5}   # items per gather action (others: 1); action = HandGatherSeconds
GATHER_WALK_FACTOR = 2.0     # walking between pickups doubles pure gather time
SALVAGE_CUTTER_SPEED = 2.0   # the Salvage Cutter doubles scrap salvage speed (items.json SalvageCutter)
# -- building --
PATIENCE_MIN = 12.0          # a player sizes each line so one step's parts finish in about this many minutes
MAX_PER_LINE = {1: 2, 2: 3, 3: 4, 4: 5, 5: 6}   # most machines a first-timer puts on one recipe, per phase
RUN_OVERLAP = 0.6            # share of a production run spent doing other useful things (not counted)
BUILD_MIN = {"Machine": 1.6, "Extractor": 1.2, "Generator": 1.4, "Battery": 1.0, "Special": 2.5,
             "Structure": 0.12, "Platform": 0.2, "Vehicle": 1.0}   # place + belts + cable, per building
FOUNDATIONS_PER_64_CELLS = 2.0   # foundations per 8x8 m of machine footprint (walkways, belts, spacing); from M2
LEARN_MIN = {"Machine": 4.0, "Extractor": 3.0, "Generator": 3.5, "Battery": 2.0, "Special": 3.0, "Belt": 4.0,
             "BeltLift": 1.5, "Splitter": 2.0, "Merger": 1.0, "Storage": 1.5, "Pipe": 4.0, "PowerPole": 3.0,
             "Structure": 1.0, "Platform": 3.0, "Vehicle": 3.0, "Hub": 0.0, "Workbench": 3.0,
             "TowerSite": 0.0, "Translator": 3.0, "TradeBuoy": 3.0, "TideLab": 3.0, "SuitFabricator": 2.0}
LEARN_RECIPE_MIN = 0.4       # first use of a recipe: pick it, read rates, wire the inputs
REWORK = {1: 0.10, 2: 0.10, 3: 0.12, 4: 0.12, 5: 0.10}   # share of factory time spent fixing, moving, tidying
BELT_UPGRADE_MIN = {"BeltMk2": 6.0, "BeltMk3": 8.0}     # re-laying main lines once a belt tier unlocks
# -- hub, tower, research --
HUB_STEP_MIN = 1.5           # walk to the hub, hand in, read the unlocks, Echo VO
TOWER_DELIVERY_MIN = 3.0     # route belts into the tower ring or haul the last parts
RESEARCH_MENU_MIN = 1.0      # pick, read and hand in a research
RESEARCH_WAIT_SHARE = 0.25   # share of ResearchSeconds the player actually waits (rest overlaps other work)
# -- world --
BIOME_FIRST_VISIT_MIN = {"CrashReef": 10.0, "BlackSands": 7.0, "KelpShallows": 7.0, "TarShelves": 9.0,
                         "StormSpires": 10.0, "GlimmerDeep": 10.0}   # explore, find nodes, landmark, scan
COMMUTE_MIN_PER_STEP = {1: 1.0, 2: 3.0, 3: 4.0, 4: 5.0, 5: 5.0}   # shuttling between islands per step
DATA_CORE_MIN = 2.0          # detour + voice memory + read the alternate, per core
GLOW_SHELL_MIN = {2: 4.0, 3: 3.0, 4: 3.0, 5: 3.0}   # optional night shell runs a typical player makes
# -- Fish API (sample of 60 calls on 2026-10-31: fish uniform 0-9, 10 % zero; chests mean 4.9) --
TRADE_ITEMS_PER_FISH = 5     # Blue_Signal.md §7: fish x 5 = units wanted
AVG_FISH = 4.9               # after the 0-fish re-roll (Plan D17)
AVG_PEARLS = 4.9             # chests per picture; the buoy pays max(1, chests)
TRADE_MIN = 4.0              # count both, fill the order from storage or a belt, collect
COUNT_MIN = 0.75             # one Translator picture count
TRANSLATOR_COUNTS = {2: 5, 3: 3, 4: 3, 5: 2}   # counts a typical player does at the Translator per phase
TRADES_EXTRA = {2: 1, 3: 2, 4: 2, 5: 1}        # trades beyond what pearls strictly need (trust, curiosity)
TRUST_PER_TRADE = 3          # engine tunable (code today: +1); Progression.md §7
TRUST_PER_COUNT = 1
# -- story (Design/Narrative/StoryBeats.md §0: phase-complete chain ~3-4 min) --
PROLOGUE_MIN = 3.0
PHASE_CHAIN_MIN = {1: 3.5, 2: 3.5, 3: 3.5, 4: 4.0, 5: 0.0}
MID_BEAT_MIN = {1: 2.0, 2: 3.0, 3: 3.0, 4: 5.0, 5: 8.0}   # sightings, choices, storm, confession + FB5 (D16)
STORM_RECOVERY_MIN = 8.0     # P3 Great Storm: repair snapped belts, reset fuses, pick up crystals
STORM_CRYSTAL_DROP = 30      # resources.json StormCrystal: the storm leaves ~30 on the ground
STORM_EXTRA_MIN = {4: 4.0, 5: 2.0}   # recurring storms in the Spires: fuse resets, rod placement
ENDING_MIN = 7.0             # last real message, final choice, ending cinematic
# -- choices --
DEFAULT_POWER_CHOICE = "Clean"   # the model's main path; Burners is reported as a variant
MEDKIT_CHOICE = "Give"
# -- power --
POWER_PLAN = {1: ["SalvagedSolar"], 2: ["SalvagedSolar", "KelpBurner"], 3: ["SalvagedSolar", "FuelBurner"],
              4: {"Clean": ["SalvagedSolar", "TidalTurbine", "GlowBank"], "Burners": ["SalvagedSolar", "FuelBurner"]},
              5: {"Clean": ["SalvagedSolar", "TidalTurbine", "GlowBank"], "Burners": ["SalvagedSolar", "FuelBurner"]}}
POWER_HEADROOM = 1.2         # players build ~20 % more power than the machines draw
NODE_PURITY_MULT = {"Impure": 0.5, "Normal": 1.0, "Pure": 2.0}
# -- what a typical first-timer builds or does beyond the critical path --
TYPICAL_RESEARCH = ["RS_KelpBiology", "RS_Optics", "RS_ResourceScanner", "RS_PressureSeals", "RS_PearlLexicon",
                    "RS_GlimmerCurrents", "RS_ReefSong", "RS_StormHarness"]
TYPICAL_EQUIPMENT = ["SalvageCutter", "DiveMask", "Scanner", "ZiplineHarness", "GliderPack"]
EXTRA_BUILDS = {2: {"FloatingPlatform": 10, "StorageCrate": 2, "Splitter": 4, "Merger": 3, "BeltLift": 2,
                    "Wall": 8, "Catwalk": 6},
                3: {"Breakwater": 4, "Accumulator": 2, "FloatingPlatform": 6, "Pipe": 10, "LightningRod": 2},
                4: {"LightningRod": 4, "ReefFilter": 2, "Roof": 6},
                5: {"FloatingPlatform": 4, "LightningRod": 2}}
EXTRA_BUILDS_P1 = {"StorageCrate": 2, "Ramp": 2, "Stairs": 1, "Wall": 4}


# =====================================================================================================
# Data
# =====================================================================================================
FILES = ["resources", "items", "recipes", "buildables", "milestones", "research", "tower"]


def load_data():
    data = {}
    for name in FILES:
        with open(os.path.join(DATA, name + ".json"), encoding="utf-8") as f:
            data[name] = json.load(f)
    return data


def by_name(rows):
    return OrderedDict((r["Name"], r) for r in rows)


def stacks(lst):
    return [(s["Item"], s["Count"]) for s in lst]


def story_beats():
    """Beat ids and data cores (id -> phase) from StoryBeats.md; empty if the file is missing."""
    beats, cores = set(), OrderedDict()
    if not os.path.exists(BEATS_MD):
        return beats, cores
    with open(BEATS_MD, encoding="utf-8") as f:
        text = f.read()
    beats.update(re.findall(r"\b(BT_[A-Z0-9_]+?)(?=\s*\|)", text))
    for m in re.finditer(r"^\|\s*(DC\d\d)\s*\|.*\(P(\d)\)\s*\|\s*$", text, re.M):
        cores[m.group(1)] = int(m.group(2))
    return beats, cores


class Db:
    def __init__(self, data):
        self.raw = data
        self.res = by_name(data["resources"])
        self.items = by_name(data["items"])
        self.rec = by_name(data["recipes"])
        self.bld = by_name(data["buildables"])
        self.ms = by_name(data["milestones"])
        self.rs = by_name(data["research"])
        self.tower = by_name(data["tower"])
        self.beats, self.cores = story_beats()
        self.by_output = defaultdict(list)
        for r in self.rec.values():
            for item, _ in stacks(r["Outputs"]):
                self.by_output[item].append(r)
        self.raw_items = {r["Item"]: r for r in self.res.values() if r["Item"] != "None"}
        self.machine_bld = {}
        for b in self.bld.values():
            if b["MachineType"] != "None":
                self.machine_bld[b["MachineType"]] = b["Name"]
        for st in HAND_STATIONS:
            self.machine_bld[st] = st

    def unlock_phase(self, token):
        """Phase in which an UnlockedBy / unlock source becomes available, or None if unknown."""
        if token == "Start":
            return 1
        if token in self.ms:
            return self.ms[token]["Phase"]
        if token in self.rs:
            return self.rs[token]["Phase"]
        if token in self.tower:
            return int(token.replace("Phase", "")) + 1
        if token.startswith("Story:"):
            m = re.match(r"Story:BT_P(\d)_", token)
            return int(m.group(1)) if m else None
        if token in self.cores:
            return self.cores[token]
        return None


# =====================================================================================================
# --check
# =====================================================================================================
class Checker:
    def __init__(self, db):
        self.db, self.errors, self.warnings, self.info = db, [], [], []

    def err(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def run(self):
        db = self.db
        for rule in (self.unique_names, self.references, self.unlock_symmetry, self.sizes, self.depths,
                     self.counts, self.data_cores, self.producibility, self.orphans):
            try:
                rule()
            except (KeyError, TypeError, ValueError) as e:   # broken references stop one rule, not the check
                self.err("%s: could not run (%s: %s); fix the errors above first" %
                         (rule.__name__, type(e).__name__, e))
        return not self.errors

    # -- names --
    def unique_names(self):
        for name in FILES:
            seen = set()
            for r in self.db.raw[name]:
                n = r.get("Name")
                if n in seen:
                    self.err("%s: duplicate Name %s" % (name, n))
                seen.add(n)

    # -- every reference points at a row --
    def references(self):
        db = self.db
        items = db.items
        for r in db.res.values():
            if r["Item"] != "None" and r["Item"] not in items:
                self.err("resources %s: Item %s is not an item" % (r["Name"], r["Item"]))
            for e in r["Extractors"]:
                if e not in db.bld:
                    self.err("resources %s: extractor %s is not a buildable" % (r["Name"], e))
                elif r["NodeKind"] not in NODE_FIT.get(db.bld[e]["PlacementRule"], ()):
                    self.err("resources %s: %s (%s) cannot sit on a %s" %
                             (r["Name"], e, db.bld[e]["PlacementRule"], r["NodeKind"]))
            for n in r["Nodes"]:
                if n["Biome"] not in BIOME_PHASE:
                    self.err("resources %s: unknown biome %s" % (r["Name"], n["Biome"]))
        for r in db.rec.values():
            for item, c in stacks(r["Inputs"]) + stacks(r["Outputs"]):
                if item not in items:
                    self.err("recipes %s: %s is not an item" % (r["Name"], item))
                if c <= 0:
                    self.err("recipes %s: count %s for %s" % (r["Name"], c, item))
            if r["Machine"] not in db.machine_bld:
                self.err("recipes %s: Machine %s is not a buildable" % (r["Name"], r["Machine"]))
            if db.unlock_phase(r["UnlockedBy"]) is None:
                self.err("recipes %s: UnlockedBy %s is not a row" % (r["Name"], r["UnlockedBy"]))
            if r["CraftTime"] <= 0:
                self.err("recipes %s: CraftTime must be > 0" % r["Name"])
            if r["bAlternate"] != r["Name"].startswith("Alt_"):
                self.warn("recipes %s: bAlternate and the Alt_ prefix disagree" % r["Name"])
        for b in db.bld.values():
            for item, _ in stacks(b["Cost"]):
                if item not in items:
                    self.err("buildables %s: cost %s is not an item" % (b["Name"], item))
            for key in ("ExtractItem", "FuelItem"):
                if b[key] != "None" and b[key] not in items:
                    self.err("buildables %s: %s %s is not an item" % (b["Name"], key, b[key]))
            for f in b["AltFuels"]:
                if f["Item"] not in items:
                    self.err("buildables %s: alt fuel %s is not an item" % (b["Name"], f["Item"]))
            if db.unlock_phase(b["UnlockedBy"]) is None:
                self.err("buildables %s: UnlockedBy %s is not a row" % (b["Name"], b["UnlockedBy"]))
            if b["UnlockedBy"].startswith("Story:") and db.beats and b["UnlockedBy"][6:] not in db.beats:
                self.err("buildables %s: beat %s is not in StoryBeats.md" % (b["Name"], b["UnlockedBy"][6:]))
        for src_name, rows in (("milestones", db.ms), ("research", db.rs), ("tower", db.tower)):
            for r in rows.values():
                costs = stacks(r.get("Cost", [])) + stacks(r.get("Requirements", [])) + \
                    stacks(r.get("AltRequirements", [])) + stacks(r.get("GrantItems", []))
                for item, c in costs:
                    if item not in items:
                        self.err("%s %s: %s is not an item" % (src_name, r["Name"], item))
                for x in r.get("UnlockBuildables", []):
                    if x not in db.bld:
                        self.err("%s %s: unlocks unknown buildable %s" % (src_name, r["Name"], x))
                for x in r.get("UnlockRecipes", []):
                    if x not in db.rec:
                        self.err("%s %s: unlocks unknown recipe %s" % (src_name, r["Name"], x))
        for r in db.rs.values():
            if r["Requires"] != "None" and r["Requires"] not in db.rs:
                self.err("research %s: Requires %s is not a row" % (r["Name"], r["Requires"]))
            if r["Requires"] in db.rs and db.rs[r["Requires"]]["Phase"] > r["Phase"]:
                self.err("research %s: requires a later-phase row %s" % (r["Name"], r["Requires"]))
        for m in db.ms.values():
            want = "HubTier(%d,%d)" % (m["Phase"], m["PhaseTier"])
            if m["StoryTrigger"] != want:
                self.err("milestones %s: StoryTrigger %s, expected %s" % (m["Name"], m["StoryTrigger"], want))
            for beat in re.findall(r"BT_[A-Z0-9_]+", m["StoryHook"]):
                if db.beats and beat not in db.beats:
                    self.warn("milestones %s: StoryHook beat %s not in StoryBeats.md" % (m["Name"], beat))
        tiers = sorted((m["Tier"], m["Phase"], m["PhaseTier"]) for m in db.ms.values())
        if [t[0] for t in tiers] != list(range(1, len(tiers) + 1)):
            self.err("milestones: Tier numbers are not 1..N")
        if len(db.ms) != 2 * len(db.tower):
            self.err("milestones: expected 2 hub tiers per tower phase (Brief §4: 10 steps)")

    # -- an UnlockedBy and the unlock list that grants it must agree --
    def unlock_symmetry(self):
        db = self.db
        granted = defaultdict(set)   # (kind, name) -> sources
        for src in list(db.ms.values()) + list(db.rs.values()) + list(db.tower.values()):
            for x in src.get("UnlockBuildables", []):
                granted[("b", x)].add(src["Name"])
            for x in src.get("UnlockRecipes", []):
                granted[("r", x)].add(src["Name"])
        for kind, rows in (("b", db.bld), ("r", db.rec)):
            for row in rows.values():
                ub = row["UnlockedBy"]
                srcs = granted.get((kind, row["Name"]), set())
                listed = ub in db.ms or ub in db.rs or ub in db.tower
                if listed and ub not in srcs:
                    self.err("%s %s: UnlockedBy %s, but %s does not list it" %
                             ("buildable" if kind == "b" else "recipe", row["Name"], ub, ub))
                if srcs - {ub}:
                    self.err("%s %s: also unlocked by %s (UnlockedBy says %s)" %
                             ("buildable" if kind == "b" else "recipe", row["Name"], sorted(srcs - {ub}), ub))
                ph = db.unlock_phase(ub)
                if ph is not None and row["Phase"] != ph:
                    self.err("%s %s: Phase %d but its unlock %s is in phase %d" %
                             ("buildable" if kind == "b" else "recipe", row["Name"], row["Phase"], ub, ph))

    # -- footprints in whole 100 cm cells (FIntPoint Size, Tech.md §1/§3) --
    def sizes(self):
        for b in self.db.bld.values():
            x, y = b["Size"]["X"], b["Size"]["Y"]
            if not (isinstance(x, int) and isinstance(y, int)) or x < 1 or y < 1:
                self.err("buildables %s: Size %s is not whole 100 cm cells" % (b["Name"], b["Size"]))

    # -- chain depth with the default (non-alternate) recipes --
    def depths(self):
        db = self.db
        memo = {}

        def depth(item, stack=()):
            if item in memo:
                return memo[item]
            if item in stack:
                self.err("recipes: cycle through %s" % item)
                return 0
            cands = [r for r in db.by_output.get(item, []) if not r["bAlternate"]]
            cands = [r for r in cands if r["Machine"] not in HAND_STATIONS] or cands
            if item in db.raw_items or not cands:
                memo[item] = 0
                return 0
            d = min(1 + max([depth(i, stack + (item,)) for i, _ in stacks(r["Inputs"])] or [0]) for r in cands)
            memo[item] = d
            return d

        for item in db.items:
            d = depth(item)
            if d > MAX_CHAIN_DEPTH:
                self.err("items %s: chain depth %d > %d" % (item, d, MAX_CHAIN_DEPTH))
        self.depth = memo

    # -- content counts vs Brief §4 --
    def counts(self):
        db = self.db
        alts = [r for r in db.rec.values() if r["bAlternate"]]
        nonspecial = [b for b in db.bld.values() if b["Name"] not in SPECIALS]
        got = {"raw": sum(1 for i in db.items.values() if i["Category"] == "Raw"), "items": len(db.items),
               "recipes": len(db.rec), "alternates": len(alts), "buildables": len(nonspecial)}
        for k, target in COUNT_TARGETS.items():
            lo, hi = target * (1 - COUNT_TOL), target * (1 + COUNT_TOL)
            line = "%-10s %3d  (Brief ~%s, allowed %.0f-%.0f)" % (k, got[k], target, math.ceil(lo), math.floor(hi))
            self.info.append(line)
            if not lo <= got[k] <= hi:
                self.err("counts: " + line)
        split = defaultdict(int)
        for b in nonspecial:
            split[b["Category"]] += 1
        self.info.append("buildable split " + ", ".join("%s %d/%d" % (c, split[c], t)
                                                         for c, t in BUILDABLE_SPLIT.items()))
        missing = SPECIALS - set(db.bld)
        if missing:
            self.err("buildables: specials missing %s" % sorted(missing))

    # -- 14 data cores, one alternate each, from the tier of the core's biome --
    def data_cores(self):
        db = self.db
        if not db.cores:
            self.warn("StoryBeats.md not found: data-core checks skipped")
            return
        per = defaultdict(list)
        for r in db.rec.values():
            if r["UnlockedBy"] in db.cores:
                per[r["UnlockedBy"]].append(r)
        for dc, ph in db.cores.items():
            if len(per[dc]) != 1:
                self.err("data core %s: %d alternates (want 1)" % (dc, len(per[dc])))
            for r in per[dc]:
                if not r["bAlternate"]:
                    self.err("data core %s: %s is not an alternate" % (dc, r["Name"]))
        spots = next((r for r in db.res.values() if r["Item"] == "DataCore"), None)
        if spots:
            by_phase = defaultdict(int)
            for n in spots["Nodes"]:
                by_phase[BIOME_PHASE[n["Biome"]]] += n["Normal"]
            want = defaultdict(int)
            for ph in db.cores.values():
                want[ph] += 1
            if dict(by_phase) != dict(want):
                self.err("resources DataCoreSpot: cores per phase %s, StoryBeats §3 has %s" %
                         (dict(by_phase), dict(want)))

    # -- simulate the unlock order: every cost must be makeable from what is unlocked before it --
    def producibility(self):
        db = self.db
        for variant in ("Clean", "Burners"):
            prog = Progress(db, variant)
            n = 0
            for step in prog.steps():
                n += 1
                missing = prog.unmakeable(step)
                for item, why in missing:
                    self.err("%s [%s]: %s cannot be made yet (%s)" % (step.label, variant, item, why))
                if step.kind == "tower":
                    self.phase_sweep(prog, step.phase, variant)
                prog.complete(step)
            self.info.append("unlock order [%s]: %d steps, every cost makeable from earlier unlocks "
                             "(no alternates, no shop)" % (variant, n) if not self.errors else
                             "unlock order [%s]: %d steps simulated" % (variant, n))
        # first-needed phase vs the item's Phase field
        first = {}
        prog = Progress(db, "Clean")
        for step in prog.steps():
            for item, _ in step.cost:
                first.setdefault(item, step.phase)
            prog.complete(step)
        for item, ph in first.items():
            if item in db.items and db.items[item]["Phase"] > ph:
                self.err("items %s: Phase %d but first needed in phase %d" % (item, db.items[item]["Phase"], ph))

    def phase_sweep(self, prog, ph, variant):
        """At the end of phase ph: every phase-ph building, research and recipe input is makeable."""
        db = self.db
        rows = [("buildable", b["Name"], stacks(b["Cost"])) for b in db.bld.values()
                if b["Phase"] == ph and b["Name"] in prog.buildables]
        rows += [("research", r["Name"], stacks(r["Cost"])) for r in db.rs.values()
                 if r["Phase"] == ph and r["Station"] != "Choice"]
        rows += [("recipe", r["Name"], stacks(r["Inputs"])) for r in db.rec.values() if r["Phase"] == ph]
        for kind, name, cost in rows:
            for item, _ in cost:
                ok = prog.makeable(item)
                if ok is not True and not (variant == "Burners" and item in ("LightCell", "GlowGel")):
                    self.err("phase %d %s %s [%s]: input %s not makeable by the end of the phase (%s)" %
                             (ph, kind, name, variant, item, ok))

    # -- items nobody makes or uses --
    def orphans(self):
        db = self.db
        used, made = set(), set()
        for r in db.rec.values():
            used.update(i for i, _ in stacks(r["Inputs"]))
            made.update(i for i, _ in stacks(r["Outputs"]))
        for rows in (db.bld.values(), db.ms.values(), db.rs.values(), db.tower.values()):
            for r in rows:
                for key in ("Cost", "Requirements", "AltRequirements"):
                    used.update(i for i, _ in stacks(r.get(key, [])))
        for b in db.bld.values():
            used.add(b["FuelItem"])
            used.update(f["Item"] for f in b["AltFuels"])
        for name, it in db.items.items():
            if it["Category"] in ("Equipment", "KeyItem", "Currency"):   # pearls come from trades
                continue
            if name not in made and name not in db.raw_items:
                self.err("items %s: no recipe or resource makes it" % name)
            if name not in used and it["Category"] not in ("Currency", "Pickup"):
                self.warn("items %s: made but never used" % name)

    def report(self):
        print("Blue Signal data check: %s" % DATA)
        for line in self.info:
            print("  " + line)
        for w in self.warnings:
            print("  WARN  " + w)
        for e in self.errors:
            print("  ERROR " + e)
        print("%s: %d error(s), %d warning(s)" % ("PASS" if not self.errors else "FAIL",
                                                   len(self.errors), len(self.warnings)))


# =====================================================================================================
# Play order and unlock state (shared by --check and the model)
# =====================================================================================================
class Step:
    def __init__(self, kind, name, phase, label, cost, row=None):
        self.kind, self.name, self.phase, self.label, self.cost, self.row = kind, name, phase, label, cost, row


class Progress:
    """Walks the 10 hub tiers and 5 tower deliveries in story order and tracks what is unlocked."""

    def __init__(self, db, power_choice="Clean"):
        self.db, self.choice = db, power_choice
        self.recipes = {r["Name"] for r in db.rec.values() if r["UnlockedBy"] == "Start"}
        self.buildables = {b["Name"] for b in db.bld.values() if b["UnlockedBy"] == "Start"}
        self.research_done = set()
        self.upgrades = set()
        self.phase = 1
        self.trust = 0

    def steps(self):
        db = self.db
        for ph in sorted({m["Phase"] for m in db.ms.values()}):
            for m in sorted((m for m in db.ms.values() if m["Phase"] == ph), key=lambda m: m["Tier"]):
                yield Step("milestone", m["Name"], ph, "%s %s" % (m["Name"], m["DisplayName"]), stacks(m["Cost"]), m)
            t = db.tower.get("Phase%d" % ph)
            if t:
                req = t["Requirements"]
                if self.choice == "Burners" and t["AltRequirements"]:
                    req = t["AltRequirements"]
                yield Step("tower", t["Name"], ph, "Tower %d %s" % (ph, t["TowerPart"]), stacks(req), t)

    def grant(self, row):
        self.buildables.update(row.get("UnlockBuildables", []))
        self.recipes.update(row.get("UnlockRecipes", []))
        self.upgrades.update(row.get("UnlockUpgrades", []))

    def enter_phase(self, ph):
        """Story unlocks and choices that happen inside a phase (before its tower delivery)."""
        db = self.db
        self.phase = ph
        for b in db.bld.values():
            ub = b["UnlockedBy"]
            if ub.startswith("Story:") and (db.unlock_phase(ub) or 99) <= ph:
                self.buildables.add(b["Name"])

    def after_milestone(self, m):
        """Choices fired by a hub tier (BT_P4_02 power choice at HubTier(4,1), BT_P4_04 medkit at (4,2))."""
        db = self.db
        if m["StoryTrigger"] == "HubTier(4,1)":
            row = db.rs.get("RS_Choice" + self.choice)
            if row:
                self.trust = max(self.trust, row["TrustRequired"])   # R9: gifts guarantee the clean option
                self.research_done.add(row["Name"])
                self.grant(row)
        if m["StoryTrigger"] == "HubTier(3,2)":
            self.enter_phase(3)   # the Great Storm (BT_P3_04) then aftermath BT_P3_05 unlock rods/breakwaters

    def complete(self, step):
        self.grant(step.row)
        if step.kind == "milestone":
            self.after_milestone(step.row)
        else:
            self.enter_phase(step.phase + 1)

    # -- what can be made right now --
    def raw_ok(self, item):
        db = self.db
        if item == "GlimmerPearl":
            return ("TradeBuoy" in self.buildables) or "TradeBuoy not built"
        r = db.raw_items.get(item)
        if not r:
            return "not a raw resource"
        if r["Phase"] > self.phase:
            return "raw %s arrives in phase %d" % (item, r["Phase"])
        if r["bHandGather"] or any(e in self.buildables for e in r["Extractors"]):
            return True
        return "no unlocked extractor for %s" % item

    def research_for(self, item):
        """Research rows (non-shop, non-choice, phase-available) that would unlock a recipe for item."""
        db = self.db
        out = []
        for r in db.by_output.get(item, []):
            src = db.rs.get(r["UnlockedBy"])
            if src and src["Station"] == "TideLab" and src["Phase"] <= self.phase and not r["bAlternate"]:
                out.append((r, src))
        return out

    def recipe_for(self, item, allow_research=True, _stack=()):
        """The default recipe for item right now (machine first, hand second), else None + reason."""
        db = self.db
        cands = [r for r in db.by_output.get(item, []) if r["Name"] in self.recipes and not r["bAlternate"]
                 and db.machine_bld.get(r["Machine"]) in self.buildables]
        cands.sort(key=lambda r: (r["Machine"] in HAND_STATIONS,
                                  any(db.raw_items.get(i, {}).get("bFinite") for i, _ in stacks(r["Inputs"]))))
        for r in cands:
            if all(self.makeable(i, allow_research, _stack + (item,)) is True for i, _ in stacks(r["Inputs"])):
                return r
        return None

    def makeable(self, item, allow_research=True, _stack=()):
        if item in _stack:
            return "cycle"
        if item in self.db.raw_items or item == "GlimmerPearl":
            return self.raw_ok(item)
        if self.recipe_for(item, allow_research, _stack):
            return True
        if allow_research:
            for r, src in self.research_for(item):
                if self.research_makeable(src, _stack + (item,)):
                    return True
        return "no unlocked recipe"

    def research_makeable(self, src, _stack=()):
        req = self.db.rs.get(src["Requires"])
        if req and req["Name"] not in self.research_done and not self.research_makeable(req, _stack):
            return False
        return all(self.makeable(i, True, _stack) is True for i, _ in stacks(src["Cost"]))

    def unmakeable(self, step):
        out = []
        for item, _ in step.cost:
            ok = self.makeable(item)
            if ok is not True:
                out.append((item, ok))
        return out


# =====================================================================================================
# Model (default mode): TODO
# =====================================================================================================


def main(argv):
    db = Db(load_data())
    if "--check" in argv:
        c = Checker(db)
        ok = c.run()
        c.report()
        return 0 if ok else 1
    print("model: TODO")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
