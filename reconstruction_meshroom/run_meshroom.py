# run_meshroom.py

"""
run_meshroom.py

Automates a Meshroom photogrammetry pipeline by calling the CLI 'meshroom_batch'.
"""

import os
import subprocess

# —————————————————————————
# Absolute path to Meshroom batch executable
# —————————————————————————
# Update this path to where meshroom_batch.exe is installed on your system
MESHROOM_EXEC = r"C:\Users\josej\Documents\Actual\GTI - phases\phase_1\reconstruction_meshroom\Meshroom-2023.3.0-win64 (1)\Meshroom-2023.3.0\meshroom_batch.exe"

# —————————————————————————
# Determine project directories relative to this script
# —————————————————————————
script_dir  = os.path.dirname(os.path.abspath(__file__))
phase1_dir  = os.path.abspath(os.path.join(script_dir, os.pardir))

# Input images folder (Phase 1)
DEFAULT_IMAGES    = os.path.join(
    phase1_dir,
    "Image_Acquisition",
    "images",
    "LowPoly_1_Bulbasaur"
)

# Output workspace for Meshroom
DEFAULT_WORKSPACE = os.path.join(
    phase1_dir,
    "reconstruction_meshroom",
    "output"
)

def run_meshroom(images_dir: str, output_dir: str):
    """
    Run the Meshroom batch CLI on the specified images,
    storing results in output_dir.
    """
    cmd = [
        MESHROOM_EXEC,
        "--input", images_dir,
        "--output", output_dir
    ]
    print("> Running:", " ".join(cmd))
    result = subprocess.run(cmd, check=True)
    if result.returncode == 0:
        print(f"✅ Meshroom pipeline completed. Results in: {output_dir}")
    else:
        print(f"❌ Meshroom failed with exit code {result.returncode}.")

def main():
    # Resolve and verify paths
    images_dir = os.path.abspath(DEFAULT_IMAGES)
    output_dir = os.path.abspath(DEFAULT_WORKSPACE)

    if not os.path.isdir(images_dir):
        print(f"ERROR: Images folder not found: {images_dir}")
        return

    os.makedirs(output_dir, exist_ok=True)

    # Execute Meshroom pipeline
    run_meshroom(images_dir, output_dir)

if __name__ == "__main__":
    main()
