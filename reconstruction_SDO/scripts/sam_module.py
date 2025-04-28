# sam_module.py
import torch
import numpy as np
import cv2
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.abspath("segment-anything"))
from segment_anything import sam_model_registry, SamPredictor

def run_sam(image_path: str, output_path: str, checkpoint_path: str):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    model_type = "vit_b"
    device = "cuda" if torch.cuda.is_available() else "cpu"

    sam = sam_model_registry[model_type](checkpoint=checkpoint_path).to(device)
    predictor = SamPredictor(sam)
    predictor.set_image(image)

    h, w = image.shape[:2]
    input_point = np.array([[w // 2, h // 2]])
    input_label = np.array([1])

    masks, scores, logits = predictor.predict(
        point_coords=input_point,
        point_labels=input_label,
        multimask_output=True
    )

    # Solo guardamos la primera máscara
    masked_image = image.copy()
    masked_image[~masks[0]] = 0
    output_file = os.path.join(output_path, "masked_image.png")
    cv2.imwrite(output_file, cv2.cvtColor(masked_image, cv2.COLOR_RGB2BGR))

    print(f"✅ Imagen segmentada guardada en: {output_file}")
    return output_file
