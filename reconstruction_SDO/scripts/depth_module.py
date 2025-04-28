# depth_module.py
import os
import subprocess

def run_depth_anything(image_path: str, outputs_path: str, repo_path: str):
    """
    Ejecuta Depth Anything sobre una imagen específica.
    
    Args:
        image_path (str): Ruta a la imagen de entrada (puede ser archivo o carpeta).
        outputs_path (str): Carpeta de salida donde se guardará el mapa de profundidad.
        repo_path (str): Ruta al repositorio clonado de Depth Anything.
    """
    # Asegura rutas absolutas
    image_path = os.path.abspath(image_path)
    outputs_path = os.path.abspath(outputs_path)
    repo_path = os.path.abspath(repo_path)

    # Ruta al script run.py dentro del repo
    run_script = os.path.join(repo_path, "run.py")

    # Comando para subprocess
    command = [
        "python", run_script,
        "--encoder", "vitl",
        "--img-path", image_path,
        "--outdir", outputs_path,
        "--pred-only",
        "--grayscale"
    ]

    print(f"🚀 Ejecutando Depth Anything con imagen: {image_path}")
    result = subprocess.run(command, cwd=repo_path)

    # Obtener nombre base (sin extensión) si se trató de un archivo
    if os.path.isfile(image_path):
        name = os.path.splitext(os.path.basename(image_path))[0]
        output_depth = os.path.join(outputs_path, f"{name}_depth.png")

        if os.path.exists(output_depth):
            print(f"✅ Mapa de profundidad generado: {output_depth}")
            return output_depth
        else:
            print("❌ No se encontró el mapa de salida esperado.")
            return None
 
