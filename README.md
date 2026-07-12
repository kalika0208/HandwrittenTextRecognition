# Handwritten Text Recognition (CLI Version)

A simple command-line project: put an image in a folder, run the
script, and it prints the text it found in that image — no web server,
no browser, nothing to deploy.

---

## Tech Stack

Python, OpenCV, EasyOCR, SQLite (built into Python — no install needed).

---

## Why EasyOCR instead of Tesseract?

Tesseract needs a separate program installed on your system outside of
Python (a `.exe` on Windows, a system package on Mac/Linux). EasyOCR
installs entirely through `pip install`, so there's nothing extra to
set up — just Python packages. The trade-off: EasyOCR uses a pretrained
deep learning model internally (unlike Tesseract's classical pattern
matching), and its first run downloads the model files automatically
(needs internet the first time only, then works fully offline).

---

## Folder Structure
HandwrittenTextRecognition/
├── main.py              # Run this - the program's entry point (a menu)
├── utils/
│   ├── init.py
│   ├── ocr_utils.py       # OpenCV preprocessing + EasyOCR text extraction
│   └── db_utils.py          # SQLite history logging
├── requirements.txt
├── README.md
├── images/                   # PUT YOUR INPUT IMAGES HERE
└── output/                     # Extracted .txt files are saved here automatically
---

## Step-by-Step Explanation of Every File

**`main.py`**
The entry point. Shows a simple menu: process an image, view history,
or exit. Calls into `utils/` for the actual work.

**`utils/ocr_utils.py`**
Preprocesses the image with OpenCV (grayscale → resize → adaptive
threshold), then passes it to EasyOCR to extract text and confidence.

**`utils/db_utils.py`**
Creates a small SQLite database (`ocr_history.db`) and saves/reads past
OCR results — filename, extracted text, confidence, timestamp.

---

## Why Each Preprocessing Step Improves OCR Accuracy

1. **Resize** – ensures letters are a consistent, readable size regardless of the original photo's resolution.
2. **Grayscale** – strips out colour information the recognizer doesn't need, leaving just the brightness data that matters for detecting shapes.
3. **Adaptive thresholding** – converts the image to clean black text on white, handling uneven lighting/shadows across a page far better than a single fixed brightness cutoff.

---

## How to Run It

### 1. Set up a virtual environment (recommended)
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```
This may take a few minutes the first time — EasyOCR depends on PyTorch, which is a large package.

### 3. Put an image in the `images/` folder
Any `.jpg` or `.png` with text in it — printed or handwritten.

### 4. Run the program
```bash
python main.py
```

### 5. Use the menu
Process an image   -> type the filename, e.g. sample.jpg
View history        -> see every image you've processed so far
Exit
The extracted text prints to your screen, gets saved as a `.txt` file
inside `output/`, and gets logged into `ocr_history.db` (created
automatically on first run).

---

## Testing Accuracy

Start with a clear, well-lit photo of printed text (like a book page)
to confirm everything works end-to-end. Then try neater handwriting,
and finally messier/cursive handwriting to see where accuracy drops off
— a good thing to mention in an interview: you tested the model's
real-world limitations yourself.

---

## Common Interview Questions

1. Why does OpenCV alone need EasyOCR — can't OpenCV read text by itself?
2. What's the difference between Tesseract and EasyOCR under the hood?
3. Why do you resize and threshold the image before OCR?
4. What is adaptive thresholding, and why is it better than a fixed threshold here?
5. Why is SQLite a reasonable choice for this project instead of MySQL/Postgres?
6. How is the confidence score calculated when there are multiple lines of text?
7. What would you change to make this work as a web app instead of a CLI tool?
8. What are the accuracy limitations of this approach on messy handwriting?

---

## Resume-Ready Description

- Built a command-line Handwritten/Printed Text Recognition tool in Python using OpenCV for image preprocessing (grayscale conversion, resizing, adaptive thresholding) and EasyOCR for text extraction, with results logged to a local SQLite database.

## Technologies Used (1 line)

Python, OpenCV, EasyOCR, SQLite.


Author: Kalika Mehtani