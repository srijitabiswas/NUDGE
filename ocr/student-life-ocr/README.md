# Student Life OCR Module

## Overview
This module extracts text from university notices, circulars, event posters, assignment announcements, and examination schedules using EasyOCR.

It processes real images, performs basic text cleaning, calculates OCR confidence scores, and generates structured JSON output for integration with the NLP module.

## Features
- Supports PNG, JPG, JPEG, BMP, and WEBP images.
- Processes multiple images from the input folder.
- Uses EasyOCR for text extraction.
- Uses OpenCV to resize smaller images before OCR.
- Generates raw and cleaned text.
- Calculates overall OCR confidence.
- Retains individual text-region confidence scores.
- Saves one JSON file per input image.

## Project Structure

```text
student-life-ocr/
├── input/                 # Input screenshots and images
├── output/                # Generated JSON files
├── tests/                 # Test files and baseline outputs
├── ocr_test.py            # Main OCR script
├── requirements.txt       # Python dependencies
└── README.md
```

## Requirements
- Python 3.10 or later
- pip

## Installation

Clone or download the project and open a terminal inside the project directory.

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows CMD:

```cmd
venv\Scripts\activate.bat
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## How to Run

1. Place university notice screenshots inside the `input/` folder.
2. Activate the virtual environment.
3. Run:

```bash
python ocr_test.py
```

4. Find the generated JSON files inside the `output/` folder.

The script resolves input and output paths relative to its own location, so it can also be launched from another working directory.

## Output Format

Each screenshot generates a JSON file containing:

```json
{
  "source": "payment_notice.png",
  "raw_text": "Original text extracted by EasyOCR",
  "cleaned_text": "Text after basic whitespace cleaning",
  "overall_confidence": 0.92,
  "confidence": [
    {
      "text": "Payment of Next Semester Fees",
      "score": 0.92
    }
  ]
}
```

The confidence values above are illustrative.

## Cleaning Approach

The current cleaning process:
- Removes unnecessary blank lines.
- Normalizes extra whitespace.
- Preserves the original extracted wording.
- Does not automatically correct OCR spelling mistakes or interpret notice content.

## Integration with NLP

The NLP module can use `cleaned_text` as its input.

The `raw_text`, `source`, `overall_confidence`, and individual `confidence` scores are retained for traceability and verification.

## Limitations
- OCR accuracy depends on image quality, font style, resolution, and layout.
- Decorative fonts and complex posters may produce recognition errors.
- Extracted dates, times, names, and deadlines should be verified against the original screenshot.