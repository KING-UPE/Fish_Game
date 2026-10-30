# FishGame — Environment & Setup Notes

Everything a new session needs to know about how this machine and project are set up, what was
changed, and what is still open. Imported into `CLAUDE.md`, so it loads automatically.
Last updated: 2026-10-31.

---

## 1. Start-of-session checklist

1. **Editor must be running** before Claude Code starts, or the MCP servers won't connect.
   Check: `Get-Process UnrealEditor`. If not running, launch `D:\Game\FishGame\LaunchEditor.bat`
   and wait ~60–120 s (first launch compiles shaders).
2. **Confirm both MCP servers answer** (PowerShell):
   ```powershell
   Invoke-RestMethod http://127.0.0.1:3000/mcp/status          # UnrealClaude → status=running, 28 tools
   Get-NetTCPConnection -State Listen -LocalPort 18765,3000      # both owned by UnrealEditor
   ```
3. If the `unreal` / `unrealclaude` MCP tools are missing in this session, the session was started
   before the editor was up, or the servers weren't approved — restart Claude Code from this folder.
4. Before the first edit in any domain, load the matching VibeUE skill (see `CLAUDE.md` §0).

---

## 2. Machine & toolchain

| Thing | Value |
|---|---|
| OS | Windows 11 Pro, 16 GB RAM (often only 1–3 GB free — close apps before big builds) |
| Engine | UE **5.8.4** at `D:\UE_5.8` — **not registered with the Epic launcher** (`.uproject` double-click won't work; use `LaunchEditor.bat`) |
| Compiler | Visual Studio Build Tools 2026 (MSVC 14.51) + **.NET Framework 4.8 SDK** (added 2026-10-31; UE plugin builds fail with `RulesError` / "Could not find NetFxSDK" without it) |
| Node / Claude CLI | Node 24, `claude` at `C:\Users\info\.local\bin\claude.exe` |
| Claude settings | `~/.claude/settings.json` has `promptCacheTtl: "1h"`, `subagentPromptCacheTtl: "1h"` |

---

## 3. Project layout (`D:\Game\FishGame`)

| File | Purpose |
|---|---|
| `FishGame.uproject` | C++ project (module `FishGame`); enables ModelingToolsEditorMode, PythonScriptPlugin, EditorScriptingUtilities, ToolsetRegistry, ModelContextProtocol, AllToolsets, VibeUE, UnrealClaude, HttpBlueprint, JsonBlueprintUtilities |
| `Source/FishGame` | C++ factory core + story (`FG*` classes). Build with `BuildGame.bat` (editor closed) |
| `Tools/` | `ue.py` (MCP client for `execute_python_code`), `Setup/` content rebuild scripts, `Dev/` test helpers |
| `BuildGame.bat` | Compiles `FishGameEditor` (uses `UE_ROOT`, default `D:\UE_5.8`) |
| `LaunchEditor.bat` | Launches the editor with `-ddc=InstalledNoZenLocalFallback -ModelContextProtocolPort=18765` (uses `UE_ROOT`, default `D:\UE_5.8`) |
| `.mcp.json` | `unreal` → `http://127.0.0.1:18765/mcp` (HTTP); `unrealclaude` → node bridge `D:/UE_5.8/Engine/Plugins/Marketplace/UnrealClaude/Resources/mcp-bridge/index.js` with `UNREAL_MCP_URL=http://127.0.0.1:3000` |
| `Config/DefaultEditorPerProjectUserSettings.ini` | Epic MCP server: `bAutoStartServer=True`, `ServerPortNumber=18765`, `bEnableToolSearch=True` |
| `Config/DefaultGame.ini` | `GameFeatureData` entry in `PrimaryAssetTypesToScan` (fixes the "Asset Manager settings do not include an entry for GameFeatureData" load error) |
| `Config/DefaultEngine.ini` etc. | From `TP_BlankBP`, plus Lumen/distance fields, `NearClipPlane=5`, default + startup map `/Game/Blue/Maps/L_Blue`, game mode `BP_FirstPersonGameMode` |
| `CLAUDE.md` | Working agreement + UE/VibeUE gotchas (adapted from the user's UE 5.7 template on the Desktop: `C:\Users\info\OneDrive\Desktop\CLAUDE (1).md`) |
| Design brief | `D:\Game\2625935-Fish_Game_Idea-D.H.H.U.U._Dasanayaka.pdf` ("Tide & Treasure" web-game proposal; readable with the `Read` tool). **Not the spec**: the only thing kept from it is the Fish Game API (see `CLAUDE.md`) |

Project content: UE first-person template (`FirstPerson/`, `Characters/`, `Input/`, `LevelPrototyping/`) + the game
under `Blue/` (`Data/` tables, `Materials/`, `Meshes/`, `Maps/L_Blue`). See `README.md` for the player-facing setup.

---

## 4. Plugins

Both are installed as **engine plugins** in `D:\UE_5.8\Engine\Plugins\Marketplace\` (available to every
project on this engine). Built from source with `RunUAT BuildPlugin`.

### VibeUE v5 (kevinpbuckley/VibeUE, master @ 8828906, 2026-10-29)
- Requires UE 5.8. Extends Epic's native MCP server — **no own server, no :8088, no `manage_skills`**.
- On load: registers 37 service toolsets + 90 AgentSkills. Tools on the endpoint: `execute_python_code`,
  `discover_python_module/class/function`, `list_python_subsystems`, `capture_image`, `deep_research`,
  `terrain_data`, plus Epic's `list_toolsets` / `describe_toolset` / `call_tool`.
- Skills: `call_tool(tool_name="ListSkills"|"GetSkills", toolset_name="ToolsetRegistry.AgentSkillToolset")`.
- Optional once: `VibeUE.GenerateAgentConfig ClaudeCode import` in the editor console (adds VibeUE's own guide).
- Terrain tools need a free API key: Editor Preferences → Plugins → VibeUE.

### UnrealClaude (Natfii/UnrealClaude v1.5.1) — **locally patched for UE 5.8**
- Upstream targets UE 5.7. In 5.8, `FJsonObject::Values` keys became `UE::FSharedString` instead of
  `FString`, which broke 10 call sites. Patched by wrapping keys as `FString(*Pair.Key)` in:
  `MCP/MCPToolBase.h`, `AnimationBlueprintUtils.cpp`, `MCP/Tools/MCPTool_AnimBlueprintModify.cpp`,
  `MCP/Tools/MCPTool_BlueprintModify.cpp` (×2), `MCP/Tools/MCPTool_Material.cpp` (×3),
  `MCP/Tools/MCPTool_SetProperty.cpp`.
  **Do NOT** fix this by defining `UE_JSONOBJECT_LEGACY_STRING_KEYS=1` — it changes `FJsonObject`'s
  layout vs. the prebuilt engine binaries (ABI mismatch).
- Patched source: `D:\UEPluginBuild\src\UnrealClaude` (`git diff` there shows the patch). Re-apply if
  updating from upstream.
- HTTP server on `127.0.0.1:3000` (port is **hard-coded** in `UnrealClaudeConstants.h`). Endpoints:
  `GET /mcp/status`, `GET /mcp/tools`, `POST /mcp/tool/{name}`. 28 tools (spawn/move actors,
  blueprint_query/modify, anim_blueprint_modify, capture_viewport, enhanced_input, material, asset_*,
  open_level, run_console_command, execute_script, task_* async queue…).
- In-editor chat panel: **Tools → Claude Assistant** (uses the local Claude Code CLI login).
- MCP bridge `node_modules` were copied in manually (BuildPlugin doesn't package them).

### Rebuilding a plugin
```powershell
& "D:\UE_5.8\Engine\Build\BatchFiles\RunUAT.bat" BuildPlugin `
  -Plugin="D:\UEPluginBuild\src\UnrealClaude\UnrealClaude\UnrealClaude.uplugin" `
  -Package="D:\UEPluginBuild\out\UnrealClaude" -TargetPlatforms=Win64 -Rocket
# then robocopy out\<Plugin> → D:\UE_5.8\Engine\Plugins\Marketplace\<Plugin> (exclude HostProject, Intermediate)
```
Close the editor first. Builds need short paths (the session scratch path was too long for git/UBT —
that's why the build folder is `D:\UEPluginBuild`).

---

## 5. Ports — why 18765

This machine runs many local dev servers; the user's other projects claim the common ports.

| Port | Owner |
|---|---|
| **18765** | Unreal MCP + VibeUE (this project) |
| **3000** | UnrealClaude (127.0.0.1). ⚠ The Aruna Node dev server (`D:\ME\Aruna`) also uses 3000 on 0.0.0.0 when running — the bridge is pinned to `127.0.0.1` so it reaches the editor |
| 8000 | Emperors Den API (`php -S` / `artisan serve`) |
| 8010 | another PHP 8.5 dev server (`server.php`, `public/`) |
| 8020 / 8443 | Python `scripts/serve-local.py` |
| 8100 | Emperors Den white app (`php -S router.php`) |
| 5173 | Aruna web (Vite) |
| 3306 / 5432 | MySQL (XAMPP) / Postgres (`D:\ME\pgsql`) |
| 127.0.0.2:80/443 | **task.me** — `D:\tastauomate\w3stask.py serve` (the user's CRM task logger). **Never stop it.** |

If the MCP server logs `HttpListener unable to bind`, something else took the port: find it with
`Get-NetTCPConnection -LocalPort <p>` (check **all** states, not just Listen) and pick a free port by
test-binding, then update `.mcp.json`, `LaunchEditor.bat`, the ini, and this file.

On 2026-10-31 the user asked to stop all dev servers except task.me — done. MySQL was relaunched
immediately by an **Antigravity** agent (Google's agent IDE); left running, ask before fighting it.

---

## 6. Gotchas hit during setup

- **Editor won't close via `CloseMainWindow()`** while it's still compiling shaders — just retry after
  it finishes. Computer-use can't target Unreal Editor (not a Start-menu app).
- **`Get-NetTCPConnection -State Listen` misses some holders** — always confirm a port by test-binding.
- **Memory pressure:** UBT limits to 1 parallel compile action when free RAM < 1.5 GB.
- PowerShell 5.1 `Set-Content -Encoding utf8` writes a BOM — UE tolerates it in `.ini`/`.uproject`.
- The Desktop template `CLAUDE (1).md` describes UE 5.7 + VibeUE v4 (:8088, `manage_skills`,
  `ScreenshotService`). The project `CLAUDE.md` is the adapted 5.8 version — prefer it.

---

## 7. Open items / next steps

- [ ] Restart the editor once so the `GameFeatureData` config entry takes effect (load error goes away).
- [ ] Run `VibeUE.GenerateAgentConfig ClaudeCode import` in the editor console (optional).
- [x] Decide the game design with the user: *Blue Signal* (`Design/Blue_Signal.md`), chosen 2026-10-31.
- [x] Record pawn / map / game mode in `CLAUDE.md`.
- [x] Fish API: done in C++ (`FGFishApi`, HTTP module); the two Blueprint plugins are enabled but unused.
- [ ] `D:\UEPluginBuild` (plugin sources + build output, incl. the UnrealClaude patch) can be deleted
      when no longer needed — but it's the only copy of the patched source.
