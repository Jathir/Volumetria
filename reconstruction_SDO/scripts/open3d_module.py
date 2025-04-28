import open3d as o3d
import numpy as np
import cv2
import os

def generate_pointcloud(rgb_path: str, depth_path: str, output_pcd_path: str = None):
    """
    Genera y visualiza una nube de puntos a partir de una imagen RGB y un mapa de profundidad.
    Usa parámetros intrínsecos personalizados. También puede guardar la nube de puntos en .ply o .pcd.

    Args:
        rgb_path (str): Ruta a la imagen RGB.
        depth_path (str): Ruta al mapa de profundidad en escala de grises.
        output_pcd_path (str, opcional): Ruta donde guardar la nube de puntos.
    """
    print("Paths: ")
    print("rgb path: ", rgb_path)
    print("depth path: ", depth_path)

    # 1. Cargar imágenes
    color_raw = cv2.imread(rgb_path)
    color_raw = cv2.cvtColor(color_raw, cv2.COLOR_BGR2RGB)
    cv2.imwrite("/testOut/colorRaw.png", color_raw)

    depth_raw = cv2.imread(depth_path, cv2.IMREAD_UNCHANGED)

    cv2.imwrite("/testOut/depthRaw.png", depth_raw)
    if depth_raw is None or color_raw is None:
        print("❌ No se pudo cargar alguna de las imágenes.")
        return

    # Escalar profundidad a milímetros
    depth_raw = depth_raw.astype(np.float32)
    depth_raw = (depth_raw / 255.0) * 1000.0
    # depth_raw = ((255.0 - depth_raw) / 255.0) * 1000.0


    # 2. Crear RGBDImage
    color_o3d = o3d.geometry.Image(color_raw)
    depth_o3d = o3d.geometry.Image(depth_raw.astype(np.uint16))

    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
        color_o3d,
        depth_o3d,
        depth_scale=1000.0,
        convert_rgb_to_intensity=False
    )

    # 3. Definir intrínsecos personalizados
    fx = 1422.2222222222222
    fy = 1422.2222222222222
    cx = 512.0
    cy = 512.0
    width = 1024
    height = 1024

    camera_intrinsics = o3d.camera.PinholeCameraIntrinsic(
        width, height, fx, fy, cx, cy
    )

    # 4. Crear nube de puntos
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(
        rgbd_image,
        camera_intrinsics
    )

    # Corregir orientación 
    # pcd.transform([[1, 0, 0, 0],
    #               [0, -1, 0, 0],
    #               [0, 0, -1, 0],
    #               [0, 0, 0, 1]])

    print("🎉 Nube de puntos generada. Mostrando...")
    o3d.visualization.draw_geometries([pcd])

    if output_pcd_path:
        o3d.io.write_point_cloud(output_pcd_path, pcd)
        print(f"✅ Nube de puntos guardada en: {output_pcd_path}")
