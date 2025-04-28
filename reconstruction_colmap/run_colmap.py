#!/usr/bin/env python3
"""
run_colmap.py

Automates the full COLMAP photogrammetry pipeline on Windows,
using intrinsics from camera_params.json and sequential matching
to ensure all 36 images (captured every 10°) are registered.
"""

import os
import subprocess
import json

# —————————————————————————
# Absolute path to COLMAP executable (cuda build with Qt plugins)
# —————————————————————————
COLMAP_EXEC    = r"C:\Users\josej\Documents\Actual\GTI - phases\phase_1\colmap-x64-windows-cuda\bin\colmap.exe"
COLMAP_BIN_DIR = os.path.dirname(COLMAP_EXEC)
COLMAP_ROOT    = os.path.abspath(os.path.join(COLMAP_BIN_DIR, os.pardir))
QT_PLUGIN_PATH = os.path.join(COLMAP_ROOT, "qt", "plugins", "platforms")

# —————————————————————————
# Locate phase_1 directory from this script’s location
# —————————————————————————
script_dir = os.path.dirname(os.path.abspath(__file__))
phase1_dir = os.path.abspath(os.path.join(script_dir, os.pardir))

# —————————————————————————
# Defaults relative to phase_1
# —————————————————————————
DEFAULT_IMAGES_DIR = os.path.join(
    phase1_dir, "Image_Acquisition", "images", "LowPoly_1_Bulbasaur"
)
DEFAULT_WORKSPACE = os.path.join(phase1_dir, "reconstruction_colmap", "output")
DEFAULT_OUTPUT    = "fused_model.ply"


def run_command(cmd, env=None):
    """Run COLMAP command inside its bin folder so DLLs & Qt plugins load."""
    if env is None:
        env = os.environ.copy()
    env["QT_QPA_PLATFORM_PLUGIN_PATH"] = QT_PLUGIN_PATH

    print(f"> Running: {' '.join(cmd)}")
    p = subprocess.run(
        cmd,
        cwd=COLMAP_BIN_DIR,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    print(p.stdout)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed (exit {p.returncode}): {' '.join(cmd)}")


def main():
    # 1) Paths
    images_dir  = os.path.abspath(DEFAULT_IMAGES_DIR)
    workspace   = os.path.abspath(DEFAULT_WORKSPACE)
    fused_model = os.path.join(workspace, DEFAULT_OUTPUT)
    params_file = os.path.join(images_dir, "camera_params.json")

    # 2) Load intrinsics from JSON
    if not os.path.exists(params_file):
        print(f"ERROR: camera_params.json not found at {params_file}")
        return
    with open(params_file) as f:
        intr = json.load(f)["intrinsics"]
    fx, fy = intr["fx"], intr["fy"]
    cx, cy = intr["cx"], intr["cy"]

    # 3) Prepare workspace
    os.makedirs(workspace, exist_ok=True)
    db_path    = os.path.join(workspace, "database.db")
    sparse_dir = os.path.join(workspace, "sparse")
    dense_dir  = os.path.join(workspace, "dense")
    os.makedirs(sparse_dir, exist_ok=True)
    os.makedirs(dense_dir, exist_ok=True)

    # 4) Feature extraction with fixed PINHOLE intrinsics
    run_command([
        COLMAP_EXEC,
        "feature_extractor",
        "--database_path",            db_path,
        "--image_path",               images_dir,
        "--ImageReader.camera_model", "PINHOLE",
        "--ImageReader.single_camera","1",
        "--ImageReader.camera_params",f"{fx},{fy},{cx},{cy}"
    ])

    # 5) Feature matching – use sequential matcher for circular image sequence
    run_command([
        COLMAP_EXEC,
        "sequential_matcher",
        "--database_path", db_path
    ])

    # 6) Sparse reconstruction (incremental mapper)
    run_command([
        COLMAP_EXEC,
        "mapper",
        "--database_path", db_path,
        "--image_path",    images_dir,
        "--output_path",   sparse_dir
    ])

    # 7) Convert sparse model to PLY
    run_command([
        COLMAP_EXEC,
        "model_converter",
        "--input_path",  os.path.join(sparse_dir, "0"),
        "--output_path", os.path.join(sparse_dir, "0", "model.ply"),
        "--output_type","PLY"
    ])

    # 8) Image undistortion for dense
    run_command([
        COLMAP_EXEC,
        "image_undistorter",
        "--image_path",    images_dir,
        "--input_path",    os.path.join(sparse_dir, "0"),
        "--output_path",   dense_dir,
        "--output_type",   "COLMAP",
        "--max_image_size","2000"
    ])

    # 9) Dense stereo (PatchMatch)
    run_command([
        COLMAP_EXEC,
        "patch_match_stereo",
        "--workspace_path",   dense_dir,
        "--workspace_format", "COLMAP",
        "--PatchMatchStereo.geom_consistency", "true"
    ])

    # 10) Stereo fusion to generate dense point cloud
    run_command([
        COLMAP_EXEC,
        "stereo_fusion",
        "--workspace_path",   dense_dir,
        "--workspace_format", "COLMAP",
        "--input_type",       "geometric",
        "--output_path",      fused_model
    ])

    print(f"\n✅ COLMAP pipeline completed successfully.")
    print(f"   Fused model saved to: {fused_model}")


if __name__ == "__main__":
    main()
