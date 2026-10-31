import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)

# Create test cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.2))
cube = bpy.context.active_object
cube.scale = (3.0, 3.0, 2.4)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Ensure object is selected
cube.select_set(True)
bpy.context.view_layer.objects.active = cube

fbx_out = r"D:\Game\FishGame\Saved\test_cube.fbx"
bpy.ops.export_scene.fbx(
    filepath=fbx_out,
    use_selection=False,  # export all objects
    global_scale=100.0,
    axis_forward='-Z',
    axis_up='Y',
    apply_unit_scale=True,
    bake_space_transform=True
)
print(f"Exported {len(bpy.data.objects)} objects to {fbx_out}")
