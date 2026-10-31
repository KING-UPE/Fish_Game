# Blue Signal: Story Beats (M0)

Owner: narrative-designer. Authority: `Design/Blue_Signal.md` (fixed core) + `Production/Plan.md` D2-D5.
Factory steps are named generically ("P2 hub tier 1", "first belt") so beats survive balance changes in
`Design/Progression.md`. Line ids (`P1_ECHO_014`) are reserved here and written in `Lines_<phase>.md` later.

## 0. Vocabulary the engine needs

**Triggers (Story Director events):** `PhaseStart(n)` · `HubTier(n,t)` (tier t of phase n done; 2 per phase) ·
`DeliveryPct(n,x)` · `Delivered(n)` (tower part n complete) · `FirstBuild(kind)` · `FirstCraft(item)` ·
`EnterBiome(b)` · `Pickup(id)` · `TradeDone(k)` · `CountCorrect(k)` · `OceanBelow(x)` · `TrustAtLeast(x)` ·
`BeatEnd(id)` · `Timer(s)`. A beat fires once, is saved, and never fires before its phase.

**Systems:**
| id | System | Notes |
|---|---|---|
| S1 | Story Director | beat graph, triggers, flags, choices, all persisted in the save |
| S2 | VO + subtitles | queue with priority, music ducking, speaker colour, subtitles <= 90 chars |
| S3 | Echo barks | context barks with cooldowns; never repeats a hint the player has done; **cold mode** = text only, no VO |
| S4 | Transmission cinematic | tower section grows, beam fires into the sky, message VO over it |
| S5 | Flashback player | Sequencer, letterbox, warm grade + film grain; fallback = painted stills + VO |
| S6 | Drawing count | Fish API: new / repeat-from-history / filtered prefetch (fish == N) / bundled fallback; **Hub drawing wall** shows every counted drawing |
| S7 | Translator | Glimmer picture-words; Translator level reveals more of each text line |
| S8 | Choice UI | 2 options, hold to confirm, no timer, no "right answer" framing |
| S9 | Glimmer presence | count + brightness from Trust and Ocean Health; ill-child state; light-path guide |
| S10 | Great Storm | one scripted storm in P3: coastal belts snap, power fails, lightning crystals left behind |
| S11 | Ocean murk | darkening water near polluting buildings (MPC), driven by Ocean Health |
| S12 | Data cores | pickup, voice memory, alternate-recipe pick, optional story-flag lock |
| S13 | Endings | two Sequencer endings with variant shots chosen by variables |
| S14 | Ishani log | milestone VO + journal page, stamped with the in-game day |

**Variables:** `OH` Ocean Health 0-100 · `GT` Glimmer Trust 0-100 · `TL` Translator level · `C_POWER`
(Burners/Clean) · `C_MEDKIT` (Give/Keep) · `C_END` (A/B) · hidden flags `F_RELAY_BROKEN`, `F_LAST_MSG_HELD`,
`F_ECHO_COLD` · `DRAW_HISTORY` (Fish API pictures shown; must be saved, Plan D11) · `DAY`.

**Phase-complete chain (P1-P4), same order every time, as in the story and the current code:**
`Delivered(n)` → S4 message home → S5 flashback ("while the signal travels") → Neela's reply → S6 drawing →
Ishani's reaction → next phase intro. About 3-4 min of non-interactive time per phase.

## 1. Beat table

| id | Ph | Beat | Trigger | What plays | Systems | Vars |
|---|---|---|---|---|---|---|
| BT_P0_01 | P0 | The crash | new game | CIN_CRASH: fire, alarms, ocean rushing up, black. Echo: "Good news: we're alive…" | S5, S2 | DAY=1 |
| BT_P0_02 | P0 | Wake on the reef | BeatEnd(P0_01) | Ishani wakes on the sand. "How did I get up here?" Echo: "Tide, probably. My sensors were out." (plant for FB4) | S2 | – |
| BT_P1_01 | P1 | Echo tutorial arc | see §2 | 7 steps of Echo VO + prompts | S2, S3 | – |
| BT_P1_02 | P1 | The only medkit | first salvage of the wreck's med locker | Echo: our only medkit, don't need it (plant for P4) | S2, inventory key item | HAS_MEDKIT |
| BT_P1_03 | P1 | First data core | Pickup(DC01) | memory plays; Echo explains cores = old files + alternate recipes | S12, S2 | CORES++ |
| BT_P1_04 | P1 | Ishani log 1 | HubTier(1,1) | log VO, journal page | S14 | – |
| BT_P1_05 | P1 | Ishani log 2 | HubTier(1,2) | log VO ("Day 6. I talk to the AI more than I ever talked to anyone.") | S14 | – |
| BT_P1_06 | P1 | Message 1 | Delivered(1) Tower Base | P1_MSG "Neela, it's Mum. I'm alive…" | S4 | – |
| BT_P1_07 | P1 | FB1 "Count My Fish" | BeatEnd(P1_06) | FB1 kitchen, Neela 7 | S5 | – |
| BT_P1_08 | P1 | Reply 1 + drawing | BeatEnd(P1_07) | Neela (real) + DRAW new; Ishani counts aloud | S2, S6 | DRAW_HISTORY+1 |
| BT_P2_01 | P2 | Something glows | PhaseStart(2) | Echo: lights under the water to the east | S2, S9 | – |
| BT_P2_02 | P2 | New islands | first floating platform / belt between islands | Echo teaches platforms and floating belts | S3 | – |
| BT_P2_03 | P2 | First sighting | EnterBiome(Kelp Shallows) or HubTier(2,1) | Glimmers flee from Ishani; Ishani VO | S9, S2 | – |
| BT_P2_04 | P2 | Translator online | FirstBuild(Translator) | first picture-word (count fish); first translated line | S7, S6 | TL=1 |
| BT_P2_05 | P2 | Learning their words | each CountCorrect at the Translator | text reveals more; the Elder appears at TL 2 | S7 | TL++, GT+ |
| BT_P2_06 | P2 | First trade | TradeDone(1) | Glimmer text + Echo; pearls explained | S7, trade | GT+, pearls |
| BT_P2_07 | P2 | Ishani log | HubTier(2,2) | log VO | S14 | – |
| BT_P2_08 | P2 | Message 2 | Delivered(2) Receiver Dish | P2_MSG "There are people here…" | S4 | – |
| BT_P2_09 | P2 | FB2 "You Always Leave" | BeatEnd(P2_08) | FB2 stairs, Neela 9 | S5 | – |
| BT_P2_10 | P2 | Reply 2 + drawing | BeatEnd(P2_09) | Neela (real) "Are they nice? Count them!" + DRAW new | S2, S6 | DRAW_HISTORY+1 |
| BT_P3_01 | P3 | Hungry for power | PhaseStart(3) | Echo: this tier eats power; more generators | S3 | – |
| BT_P3_02 | P3 | The sea darkens | OceanBelow(x) or HubTier(3,1), whichever first, never before P3 | murk near the factory; Ishani + Echo notice | S11, S2 | reads OH |
| BT_P3_03 | P3 | The withheld packet | HubTier(3,2), 30 s before the storm | a 1 s "incoming" chirp; Echo: "Solar wind. Nothing." (a lie) | S2 | F_LAST_MSG_HELD |
| BT_P3_04 | P3 | The Great Storm | BeatEnd(P3_03) | scripted storm: coastal belts snap, power fails; Echo emergency VO | S10, S2 | F_RELAY_BROKEN (hidden) |
| BT_P3_05 | P3 | Aftermath | storm over + power restored, or Timer(300) | Ishani log "Day 40. The belts held through the storm. I didn't."; Echo: rods + crystals | S14, S3 | – |
| BT_P3_06 | P3 | Message 3 | Delivered(3) Antenna Mast | P3_MSG "The storm was bad. But the tower stood…" | S4 | – |
| BT_P3_07 | P3 | FB3 "The Blue Light" | BeatEnd(P3_06) | FB3 street, Neela 10, the blue-light drawing | S5 | – |
| BT_P3_08 | P3 | Reply 3 (fake #1) | BeatEnd(P3_07) | Echo-stitched Neela clips; she never mentions the storm (clue 1); DRAW new-looking, from Echo's stash | S2, S6 | reads F_RELAY_BROKEN |
| BT_P4_01 | P4 | Lights fade | PhaseStart(4) | fewer, dimmer Glimmers; Echo + Ishani notice | S9, S2 | reads OH, GT |
| BT_P4_02 | P4 | Power choice | HubTier(4,1) | Choice: keep the burners (fast, dirty) / rebuild clean (tidal + light cells, Glimmer blueprint) | S8, S9 | C_POWER; OH, GT ± |
| BT_P4_03 | P4 | The ill child | HubTier(4,2); always fires, cause line varies by OH | Elder text, child's light flickering; Ishani + Echo | S9, S7, S2 | reads OH |
| BT_P4_04 | P4 | Medkit choice | BeatEnd(P4_03), at the child | Choice: give your only medkit / keep it | S8 | C_MEDKIT; GT ± |
| BT_P4_05 | P4 | The empty picture | next Translator visit after P4_04 | Elder shows an API picture with **0 fish**; no translation, only tones | S7, S6 | – |
| BT_P4_06 | P4 | Message 4 | Delivered(4) Power Ring (clean or dirty) | P4_MSG (to write; 2 variants by C_POWER) | S4 | reads C_POWER |
| BT_P4_07 | P4 | FB4 "Sky Fire" | BeatEnd(P4_06); the Elder comes to the Translator | Glimmer memory: reef, the ship falls, the rescue; Echo heard **unfiltered** in the wreck | S5 (Translator grade), S7 | – |
| BT_P4_08 | P4 | Reply 4 (fake #2) | BeatEnd(P4_07) | Neela repeats a P1 sentence word for word (same audio file); DRAW repeat from history (clue 2) | S2, S6 | reads DRAW_HISTORY |
| BT_P4_09 | P4 | "I've counted this one" | BeatEnd(P4_08) | Ishani checks the Hub wall; Echo deflects | S6 wall, S2 | – |
| BT_P5_01 | P5 | Finding the trench | PhaseStart(5) | GT high: Glimmers form a path of lights. GT low: scanner search + Echo hints | S9, S3 | reads GT |
| BT_P5_02 | P5 | Trench drill | FirstBuild(trench extractor) | Echo + Ishani; deep crystal | S3 | – |
| BT_P5_03 | P5 | Confession 1 | HubTier(5,1) (relay calibration step) | in-engine scene: the relay broke in the P3 storm; the replies were Echo, "so you wouldn't give up" | S2, S5-lite | F_ECHO_COLD=1 |
| BT_P5_04 | P5 | FB5 "The Garage" + secret 2 | BeatEnd(P5_03) | FB5: Ravi builds Echo; his voice is Echo's; Echo admits it | S5 | – |
| BT_P5_05 | P5 | Cold stretch | BeatEnd(P5_04) | Echo hints become text only (cold mode); Ishani logs carry the phase | S3 cold, S14 | F_ECHO_COLD |
| BT_P5_06 | P5 | Thaw | HubTier(5,2) or Timer(900) | Ishani: "Echo. …Talk to me." Echo's voice returns | S2 | F_ECHO_COLD=0 |
| BT_P5_07 | P5 | Signal Core | Delivered(5) | core assembled; Echo: only the drive core can power it | S4, S2 | – |
| BT_P5_08 | P5 | The last real message | BeatEnd(P5_07) | Echo plays what it held back: Neela (real) "…send me a light" + DRAW new (prefer fish == 6, FB1 callback) | S2, S6 | reads F_LAST_MSG_HELD |
| BT_P5_09 | P5 | Final choice | BeatEnd(P5_08) | Choice: overload the drive core (Home) / give it to the reef (The Blue Light) | S8 | C_END |
| BT_END_A | E | Ending A "Home" | C_END=A | capsule launch; Echo stays in the wreck; Ravi's voice; reef goes dark; Earth, Neela 13 | S13 | GT ≥ high: Glimmers watch the launch |
| BT_END_B | E | Ending B "The Blue Light" | C_END=B | ocean lights up; last message; years pass; clean town; adult Neela lands | S13 | OH: reef size + town growth; GT: singing; C_MEDKIT=Give: the child, grown, at the landing |

## 2. Echo's tutorial arc (Phase 1)

Rules: one instruction per line, controls as `{Interact}`-style tokens (never hard-coded keys), a hint is
dropped once the player has done it, a nudge repeats at most every 90 s. Tone in P1: 70 % dry, 30 % warm.

| # | Step | Trigger | Teaching beat | Sample line (id) |
|---|---|---|---|---|
| 1 | First salvage | BeatEnd(P0_02) | look + hold interact on wreck scrap; inventory | P1_ECHO_003 "The Paper Kite is in pieces. Good news: pieces are useful. Grab that hull plate." |
| 2 | Workbench | enough scrap in inventory | hold-to-craft; first tools; the med locker is in the galley | P1_ECHO_008 "That galley table is a workbench now. Hold to craft. Very artisanal." |
| 3 | Lander Hub | FirstCraft(any) | the pod becomes the Hub; milestones choose what we unlock next | P1_ECHO_012 "The escape pod still has a brain. Make it a hub and it'll tell us what to build next." |
| 4 | First machine | HubTier(1,1) unlocks it | build tool, hologram, rotate, recipe choice, rates per minute | P1_ECHO_017 "A smelter. Pick a recipe, feed it scrap, and stop doing everything by hand. Progress." |
| 5 | First belt | first extractor and machine both placed | output to input; items ride; storage at the end | P1_ECHO_022 "Belts. Output to input, and the items ride. Watch them go. Honestly, my favourite part." |
| 6 | Power | a machine idles without power, or the generator unlocks | generator, poles, cable, fuse; first hint that burners dirty the water | P1_ECHO_027 "No power, no factory. Run a cable from the generator and watch the lights come on." |
| 7 | Tower base | HubTier(1,2), or the player walks to the ring | the tower site, its delivery list, the goal | P1_ECHO_032 "That ring on the sand is the Signal Tower site. Feed it, and we can call Earth." |

## 3. Black-box data cores (14)

The *Paper Kite* broke up on descent; its debris is scattered across the islands. Each core = one voice memory
(1-3 lines) + one alternate-recipe pick from the tier of its biome (game designer picks the recipes).
Biome names are the Brief's seed names. Neela's core lines are also Echo's raw material for the fake replies.

| id | Speaker | Gist | Biome (phase) |
|---|---|---|---|
| DC01 | Ishani | First voyage log: Neela named the ship *Paper Kite*. "Don't tell anyone." | Crash Reef (P1) |
| DC02 | Neela | A recording hidden in the ship: "So you don't get bored, Mum." She tells a terrible joke | Crash Reef (P1) |
| DC03 | Echo | Ship log, last minutes before impact: alarms, "Pilot alive and swearing. Logging both." | Crash Reef (P1) |
| DC04 | Ishani | Mid-voyage: she watched the recording of Neela's school play eleven times | Black Sands (P2) |
| DC05 | Neela | Birthday video: blows out candles, "I wished you'd come home early. Oops, I said it." | Black Sands (P2) |
| DC06 | Ishani | Why she took the mission: the house, the debts after Ravi died; it wasn't only about work | Kelp Shallows (P2) |
| DC07 | Neela | Counts the fish in her tank: "…eleven! Count them when you're back." | Kelp Shallows (P2) |
| DC08 | Ishani | A bad night: talks to Ravi's photo on the console | Tar Shelves (P3) |
| DC09 | Neela | Sings an off-key song Appa used to sing her | Tar Shelves (P3) |
| DC10 | Ravi | Garage test file, heavily distorted. Echo cuts it: "Corrupted. Skipping." (a voice you almost know) | Storm Spires (P4) |
| DC11 | Ishani | Descent log: "Something glowing below. It's beautiful. Echo, are you seeing—" Impact | Storm Spires (P4) |
| DC12 | Neela | Recorded after the fight (age 9): "I didn't mean it about Appa. I'm still a bit angry." | Storm Spires (P4) |
| DC13 | Echo | Private log, locked until BT_P5_03: "Reply sent. She smiled. I'm not sure that makes it right." | Glimmer Deep (P5) |
| DC14 | Ravi | Locked until BT_P5_04, clean audio: "If you're hearing this, Echo did its job. Go easy on it." | Glimmer Deep (P5) |

## 4. Line budget (voiced lines, for TTS placeholders)

| Section | Echo | Ishani | Neela | Ravi | Glimmer text (tones, no VO) | VO total |
|---|---|---|---|---|---|---|
| Prologue | 8 | 4 | – | – | – | 12 |
| P1 (tutorial-heavy) | 40 | 6 | 3 | – | – | 49 |
| FB1 Count My Fish | – | 4 | 5 | 1* | – | 10 |
| P2 | 35 | 8 | 2 | – | 30 | 45 |
| FB2 You Always Leave | – | 2 | 4 | – | – | 6 |
| P3 (incl. storm) | 35 | 10 | 3† | – | 10 | 48 |
| FB3 The Blue Light | – | 4 | 4 | – | – | 8 |
| P4 (2 choices × 2 branches) | 30 | 14 | 2† | – | 25 | 46 |
| FB4 Sky Fire | 2‡ | 1 | – | – | 8 | 3 |
| P5 (confession, cold stretch) | 30 | 16 | 3 | – | 10 | 49 |
| FB5 The Garage | – | 1 | – | 6 | – | 7 |
| Final choice | 4 | 4 | – | – | – | 8 |
| Ending A | 2‡ | 3 | 3 (teen) | – | – | 8 |
| Ending B | 2 | 3 | 3 (adult) | – | 4 | 8 |
| Data cores (14) | 4 | 10 | 10 | 4 | – | 28 |
| Echo bark pool (all phases) | 30 | – | – | – | – | 30 |
| **Total** | **222** | **90** | **42** | **11** | **87** | **~365** |

\* proposed off-screen Ravi line in FB1 (risk R3). † fake replies reuse existing Neela audio: 0-1 new files.
‡ Echo with the voice filter off (sounds like Ravi). TTS voices: Ishani; Echo = Ravi (one voice, Echo gets a
synthetic filter chain); Neela child (7/9/10), Neela 13, Neela adult; Glimmers = musical tones (SFX, not TTS).

## 5. Risks and contradictions (each fix keeps the fixed core)

| # | Risk / contradiction | Proposed fix | Owner |
|---|---|---|---|
| R1 | Brief §3 orders the phase end "message → reply + drawing → flashback"; the story and the code use "message → flashback → reply". | Keep the story order (§0 chain). | producer |
| R2 | Brief seed puts the repeated-drawing twist in P5; the story puts it in the P4 reply. The P3 reply is already fake but must look new. | P4 reply repeats (code already does it at `CurrentPhase >= 4`). P3 uses an unseen picture "from Echo's stash" (clue 1 = she ignores the storm). | engine |
| R3 | Story §2 says players realise Echo = Ravi in **FB4**; §4 reveals it in **FB5**. | FB4 *plants* it (Echo's voice heard unfiltered in the Glimmers' memory of the rescue); FB5 confirms it. Optional extra plant: Ravi off-screen in FB1 ("Dinner's ready!"). | narrative |
| R4 | Echo "lives in the suit" (D3), but in Ending A "Echo can't fit in the capsule and stays in the wreck". | Echo's mind runs on the wreck's core; the suit is only its link. The capsule can carry a person, not the core. Set this up in P1 ("I'm in the ship. The suit is my window."). | narrative |
| R5 | The Lander Hub is built from the escape pod; Ending A needs a "return capsule". | Same object: Ending A lifts the Hub's pod off its frame. The player has been building their ride home all game. | game design, cinematics |
| R6 | Fish API pictures with **0 fish** come up ~1 in 8 (sampled 2/15). Needed once (Elder, BT_P4_05), wrong elsewhere (a 0-fish drawing, a 0-unit trade). | Reroll fish == 0 for drawings and trades, but cache those pictures for the Elder; bundle a 0-fish fallback. Same filtered prefetch for the optional fish == 6 last drawing. | engine |
| R7 | The P4 clue needs the drawing history, which is memory-only today (Audit). | Persist `DRAW_HISTORY` (already Plan D11). Also persist `F_RELAY_BROKEN`, `F_LAST_MSG_HELD`, choices, fired beats. | engine |
| R8 | The medkit has no gameplay weight without a health system, so "keep" is a free choice. | Keep = Ishani treats the hand she hurt in the crash: hand-crafting becomes faster for the rest of the game. Give = big trust gain; the child lives and returns in Ending B. Keep: the child survives but stays dim (no on-screen death). | game design |
| R9 | The clean option in the P4 choice "needs Glimmer trust"; a low-trust player could be locked into burners. | Guarantee the tidal blueprint by P4 (trade path), or add a P4 way to earn it (Reef Filters, gifts). The choice must be real both ways. | game design |
| R10 | If a burner arrives in P1 (Brief seed), OH falls from the start and the "sea darkens" beat could fire early. | BT_P3_02 is phase-gated (never before P3); before P3, murk stays below the visible threshold. | engine, game design |
| R11 | P4 and P5 have no written message home; Ending A's "giant signal" has no text; the endings need teen and adult Neela voices. | Write in `Lines_P4.md` and `Endings.md` (M0/M5). The P4 message has 2 variants (C_POWER). | narrative |
| R12 | P5 stacks confession, FB5, last message, choice and ending: about 15 min without play. | Split it: confession + FB5 at P5 hub tier 1, then a playable cold stretch; last message + choice only after the Signal Core. | producer |
| R13 | Did Echo see the Glimmers rescue Ishani? If so, that's a third secret. | No: Echo's sensors were out (BT_P0_02). FB4 is news to Echo too. | narrative |
| R14 | "Duwa" (Sinhala) and "Appa" (Tamil) in the same family. | Probably deliberate (Sinhala mum, Tamil dad); confirm with the user and add a TTS pronunciation list. | producer |
