# Execute with:
# blender --background --python Image_acquisition.py

import bpy
import os
import math
import json

# —————————————————————————
# Configurable parameters
# —————————————————————————

NUM_VIEWS    = 360
OUTPUT_BASE  = os.path.abspath(os.path.join(__file__, "..", "images"))
MODELS_DIR   = os.path.abspath(os.path.join(__file__, "..", "..", "CAD_models"))

# DJI Mini 4 Pro intrinsics
INTRINSICS = {
    "fx": 1422.2222222222222,
    "fy": 1422.2222222222222,
    "cx": 512.0,
    "cy": 512.0,
    "width": 1024,
    "height": 1024
}

# Routine type: 'middle' (camera at mid-plane) or 'upper' (half object height)
ROUTINE_TYPE = 'middle'  # options: 'middle', 'upper'

# gather all .stl files
stl_files = [f for f in os.listdir(MODELS_DIR) if f.lower().endswith(".stl")]

# —————————————————————————
# Utility functions
# —————————————————————————

def clear_scene():
    """Remove all objects from the current Blender scene."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

def import_and_center_model(stl_path):
    """
    Import an STL, set its origin to its bounding-box center,
    then translate so that the model center is at (0,0,0).
    Returns the object, its maximum bbox dimension, and its height.
    """
    bpy.ops.import_mesh.stl(filepath=stl_path)
    obj = bpy.context.selected_objects[0]
    obj.name = "Target"

    # Move origin to the geometry center
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")

    # Assign red material
    mat = bpy.data.materials.new(name="RedMaterial")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    # RGBA: pure red, opacity 1
    bsdf.inputs["Base Color"].default_value = (1.0, 0.0, 0.0, 1.0)
    # Replace first slot or add new slot
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    # Compute bounding-box in world coords
    verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    min_x, max_x = min(v.x for v in verts), max(v.x for v in verts)
    min_y, max_y = min(v.y for v in verts), max(v.y for v in verts)
    min_z, max_z = min(v.z for v in verts), max(v.z for v in verts)

    # Compute center of bbox
    center = (
        (min_x + max_x) / 2,
        (min_y + max_y) / 2,
        (min_z + max_z) / 2
    )

    # Translate object so its center is at the world origin
    obj.location.x -= center[0]
    obj.location.y -= center[1]
    obj.location.z -= center[2]

    # Determine maximum dimension and height
    max_dim = max(obj.dimensions)  # max of x, y, z
    height  = obj.dimensions.z     # z-extent

    return obj, max_dim, height

def setup_lighting():
    """Add a sun light to the scene for basic illumination."""
    bpy.ops.object.light_add(type="SUN", location=(5, -5, 5))
    light = bpy.context.object
    light.data.energy = 3.0

def setup_camera(radius, cam_height, target_empty):
    """
    Add a camera at a given distance from the origin,
    at a specified height, and constrain it to look at the empty at (0,0,0).
    """
    bpy.ops.object.camera_add(location=(radius, 0, cam_height))
    cam = bpy.context.object
    bpy.context.scene.camera = cam

    # Add Track To constraint to look at the empty
    constraint = cam.constraints.new(type='TRACK_TO')
    constraint.target = target_empty
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'

    return cam

# —————————————————————————
# Main process
# —————————————————————————

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.render.resolution_x = INTRINSICS["width"]
scene.render.resolution_y = INTRINSICS["height"]
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"

for stl in stl_files:
    model_name = os.path.splitext(stl)[0]
    out_dir = os.path.join(OUTPUT_BASE, model_name)
    os.makedirs(out_dir, exist_ok=True)

    # 1) Clear previous objects
    clear_scene()

    # 2) Add an empty at the origin for camera target
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    empty_origin = bpy.context.object
    empty_origin.name = "CameraTarget"

    # 3) Import and center the model
    model, max_dim, height = import_and_center_model(os.path.join(MODELS_DIR, stl))

    # 4) Setup lighting
    setup_lighting()

    # 5) Compute camera radius and height
    radius = 2 * max_dim
    if ROUTINE_TYPE == 'middle':
        cam_height = 0.0
    else:  # 'upper'
        cam_height = height * 5

    # 6) Add camera and constrain to empty
    cam = setup_camera(radius, cam_height, empty_origin)

    # Prepare to collect extrinsic matrices
    extrinsics = {}

    # 7) Render loop
    for i in range(NUM_VIEWS):
        angle = 2 * math.pi * i / NUM_VIEWS
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)

        cam.location = (x, y, cam_height)

        filename = f"{model_name}_{i:03}.png"
        scene.render.filepath = os.path.join(out_dir, filename)
        bpy.ops.render.render(write_still=True)

        # Export the camera extrinsic matrix
        ext_mat = cam.matrix_world.inverted().to_4x4()
        extrinsics[filename] = [list(row) for row in ext_mat]

    # 8) Save intrinsics + extrinsics to JSON
    camera_data = {
        "intrinsics": INTRINSICS,
        "extrinsics": extrinsics
    }
    with open(os.path.join(out_dir, "camera_params.json"), "w") as fp:
        json.dump(camera_data, fp, indent=2)

    print(f"✅ Completed rendering for {model_name}. Output in: {out_dir}")

print("🎉 All models have been processed!")
