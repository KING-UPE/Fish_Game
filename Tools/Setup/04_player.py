"""Blue Signal setup 4/4: hook the first-person template up to the C++ factory code (run inside the editor).
- BP_FirstPersonPlayerController is reparented to FGPlayerController (keeps its Enhanced Input setup).
- BP_FirstPersonGameMode uses FGHUD."""
import unreal
import warnings

warnings.simplefilter("ignore")

EAL = unreal.EditorAssetLibrary
BEL = unreal.BlueprintEditorLibrary

pc_path = "/Game/FirstPerson/Blueprints/BP_FirstPersonPlayerController"
pc_bp = EAL.load_asset(pc_path)
if BEL.get_blueprint_parent_class(pc_bp) != unreal.FGPlayerController.static_class():
    BEL.reparent_blueprint(pc_bp, unreal.FGPlayerController.static_class())
    print("MODIFIED: reparented", pc_path)
BEL.compile_blueprint(pc_bp)
EAL.save_asset(pc_path)

gm_path = "/Game/FirstPerson/Blueprints/BP_FirstPersonGameMode"
gm_bp = EAL.load_asset(gm_path)
gm_class = EAL.load_blueprint_class(gm_path)
cdo = unreal.get_default_object(gm_class)
cdo.set_editor_property("hud_class", unreal.FGHUD.static_class())
BEL.compile_blueprint(gm_bp)
EAL.save_asset(gm_path)
print("HUD:", unreal.get_default_object(EAL.load_blueprint_class(gm_path)).get_editor_property("hud_class"))
print("PC:", unreal.get_default_object(EAL.load_blueprint_class(gm_path)).get_editor_property("player_controller_class"))
print("PLAYER DONE")
