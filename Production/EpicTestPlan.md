# Epic Test Plan — for the user's stronger PC

Blue Signal is developed on an Intel Iris Xe laptop, where Low / Medium / High are measured (`Plan.md` §6).
**Epic is full Satisfactory-1.0 quality and is never reduced to fit the laptop**, so it can only be judged on
a stronger PC. This file is the kit for that test. The lighting tech keeps it current; items marked
*(lands in Mx)* don't exist yet.

## 1. What you need
| Thing | Minimum | Ideal |
|---|---|---|
| GPU | RTX 2070 / RX 6700 class, 8 GB VRAM, DXR support | RTX 3070 or better |
| RAM | 16 GB | 32 GB |
| Disk | ~20 GB free for the packaged build | SSD |
| Build | the packaged Win64 build zip from the milestone release *(first one at M2)* | — |

No engine install is needed for the packaged build. (To test from source instead: UE 5.8.4 + this repo +
`BuildGame.bat`, then launch with `LaunchEditor.bat` and use Standalone Game, not PIE.)

## 2. Run it
1. Unzip, run `BlueSignal.exe -FGQuality=Epic` *(flag lands in M1)*. Or press the backtick key in game and type
   `FGQuality Epic`.
2. Load the test save `EpicTest.sav` *(M2)*: the vertical-slice area with a running factory.
3. Type `FGPerfRun` *(M1)*. It flies the fixed QA camera path at noon, golden hour and night, and writes
   `Saved/Profiling/FGPerfRun_<date>.csv` plus a `stat unit` summary in the log.
4. Repeat at 1440p if your monitor supports it.

## 3. What Epic turns on (keep in sync with `Config/DefaultScalability.ini` [*@3] sections)
| Area | Epic setting | Laptop High for comparison |
|---|---|---|
| Resolution | TSR at 100% | TSR at 67% |
| GI / reflections | Lumen, hardware ray tracing when the GPU supports it, high quality | software Lumen |
| Lights | MegaLights for the factory's night lights | standard lights, culled |
| Shadows | Virtual Shadow Maps, high | VSM |
| Sky | volumetric clouds high, volumetric fog with light shafts | lower sample counts |
| Foliage / PCG | full density | reduced density |
| Effects | full Niagara counts | scaled |

## 4. What to send back
- `Saved/Profiling/FGPerfRun_*.csv` and `Saved/Logs/BlueSignal.log`
- GPU model, driver version, resolution
- 3-4 screenshots (F9 or `HighResShot 1`) from the QA camera spots
- anything that looked broken, flickered or stuttered

## 5. Pass criteria
60 fps at 1080p and 30+ fps at 1440p on an RTX 3070-class GPU, no visual faults, no crashes in the run.
