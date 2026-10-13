import easyocr
from pathlib import Path

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
            results = reader.readtext(str(image_path))

            extracted_text = "\n".join(
                detection[1] for detection in results
            )

            output_path = OUTPUT_DIR / f"{image_path.stem}.txt"
            output_path.write_text(
                extracted_text,
                encoding="utf-8"
            )

            print(f"Text saved to: {output_path}")
            print(f"Detected text regions: {len(results)}")

        except Exception as error:
            print(f"Failed to process {image_path.name}: {error}")

    print("\nOCR processing completed.")