# run_pipeline.py

import os
from sam_module import run_sam
from depth_module import run_depth_anything
from open3d_module import generate_pointcloud

# ⚙️ Configuración
image_name = "snorlax.PNG"  # Solo el nombre, sin ruta
output_mesh_name = os.path.splitext(os.path.basename(image_name))[0]+".ply"
image_path = os.path.join("images", image_name)
checkpoint_sam = os.path.join("models", "sam_vit_b_01ec64.pth")
outputs_path = "outputs"
depth_repo_path = "Depth-Anything"

# 1️⃣ Ejecutar SAM y obtener imagen segmentada
print("🔍 Ejecutando SAM...")
# Masked_img_path = run_sam(
#    image_path=image_path,
#    output_path=outputs_path,
#    checkpoint_path=checkpoint_sam
#)

# 2️⃣ Ejecutar Depth Anything con imagen original
print("🔎 Ejecutando Depth Anything...")
#depth_map_path = run_depth_anything(
#    image_path=image_path,
#    outputs_path=outputs_path,
#    repo_path=depth_repo_path
#)

depth_map_path = "outputs\snorlax_depth.png"

# 3️⃣ Generar nube de puntos con Open3D
print("🌐 Generando nube de puntos...")
generate_pointcloud(
    rgb_path=image_path,
    depth_path=depth_map_path,
    output_pcd_path=os.path.join(outputs_path, output_mesh_name)
)