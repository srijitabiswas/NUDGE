import json
import easyocr
from pathlib import Path
import cv2
import numpy as np

def preprocess_image(image_path):
    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    height, width = image.shape[:2]

    # Enlarge smaller screenshots to improve text detection
    if width < 1600:
        scale = 1600 / width
        image = cv2.resize(
            image,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC
        )

    return image

def clean_text(raw_text):
    lines = raw_text.splitlines()

    cleaned_lines = []

    for line in lines:
        line = " ".join(line.split())

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)

# Project folders
INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")

# Create output folder if it doesn't exist
OUTPUT_DIR.mkdir(exist_ok=True)

# Supported image formats
SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}

# Initialize OCR engine
print("Loading EasyOCR...")
reader = easyocr.Reader(["en"])

# Find all images in the input folder
images = [
    path for path in INPUT_DIR.iterdir()
    if path.is_file() and path.suffix.lower() in SUPPORTED_FORMATS
]

if not images:
    print("No images found in the input folder.")
else:
    print(f"Found {len(images)} images.")

    for image_path in images:
        print(f"\nProcessing: {image_path.name}")

        try:
            processed_image = preprocess_image(image_path)
            results = reader.readtext(processed_image)

            raw_text = "\n".join(
            detection[1] for detection in results
            )

            confidence_scores = [
            {
                "text": detection[1],
                "score": round(float(detection[2]), 4)
            }
            for detection in results
            ]

            cleaned_text = clean_text(raw_text)

            output_data = {
                "source": image_path.name,
                "raw_text": raw_text,
                "cleaned_text": cleaned_text,
                "confidence": confidence_scores
            }

            output_path = OUTPUT_DIR / f"{image_path.stem}.json"

            output_path.write_text(
                json.dumps(output_data, indent=4, ensure_ascii=False),
                encoding="utf-8"
            )

            print(f"JSON saved to: {output_path}")
            print(f"Detected text regions: {len(results)}")

        except Exception as error:
            print(f"Failed to process {image_path.name}: {error}")

    print("\nOCR processing completed.")