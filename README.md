# Handwritten Text Recognition System

A simple, beginner-friendly web application that lets you upload an image
containing handwritten or printed text, preprocesses it using OpenCV, and
extracts the text using Tesseract OCR — all shown in a clean Bootstrap UI.

---

## Tech Stack

Python, Flask, OpenCV, Tesseract OCR (pytesseract), HTML, CSS, Bootstrap.

---

## Folder Structure

```
HandwrittenTextRecognition/
├── app.py                  # Main Flask app - routes only
├── requirements.txt        # Python dependencies
├── README.md
├── .gitignore
├── utils/
│   ├── __init__.py
│   ├── ocr_utils.py         # Image preprocessing + OCR logic
│   └── file_utils.py        # File validation + cleanup helpers
├── templates/
│   └── index.html            # Main page (Bootstrap UI)
├── static/
│   ├── css/style.css
│   └── js/script.js          # Handles upload, drag-drop, results, history
└── uploads/                  # Temporary storage for uploaded images
    └── .gitkeep
```

---

## Step-by-Step Explanation of Every File

**`app.py`**
The entry point of the app. Only handles Flask routes:
- `/` → shows the upload page
- `/upload` → receives the image, calls the OCR utility, returns JSON
- `/download-text` → lets the user download the extracted text as `.txt`
- `/clear-history` → clears the in-session history list

It deliberately does *not* contain any OpenCV or Tesseract code — that logic
lives in `utils/`, which is a common professional pattern called
"separation of concerns" (routes vs. business logic).

**`utils/ocr_utils.py`**
Contains every preprocessing step as its own small function
(`convert_to_grayscale`, `remove_noise`, `apply_threshold`, `resize_image`),
plus `preprocess_image()` which chains them together, and
`extract_text_from_image()` which runs Tesseract and returns text +
confidence + processing time.

**`utils/file_utils.py`**
Two small helpers: checking whether an uploaded file has an allowed
extension, and safely deleting temporary files.

**`templates/index.html`**
A single-page Bootstrap UI with: upload/drag-drop zone, image preview,
extracted text box, confidence + timing badges, copy/download buttons,
and a session history list.

**`static/js/script.js`**
Handles drag-and-drop, sends the image to Flask using `fetch()`, and
updates the page with the results without reloading it.

**`static/css/style.css`**
Small custom styles layered on top of Bootstrap (the drag-drop zone
styling, image preview sizing).

---

## Why Each Preprocessing Step Improves OCR Accuracy

1. **Resize** – Tesseract needs enough pixels per character to recognize
   letter shapes reliably. Too small = blurry blobs; too large = wasted
   processing time. Resizing to a consistent width balances both.
2. **Grayscale** – Removes colour information Tesseract doesn't need,
   leaving only the brightness data that actually matters for detecting
   letter shapes.
3. **Noise removal (median blur)** – Phone photos often have small
   speckles/grain, especially in low light, which can look like broken
   letters to Tesseract. A median blur smooths these out.
4. **Adaptive thresholding** – Converts the image to pure black-and-white,
   which is what Tesseract is trained on. *Adaptive* thresholding (instead
   of one global cutoff) handles uneven lighting/shadows across the page
   much better, since it calculates a different cutoff for each region.

---

## How to Run the Project Locally

### 1. Install Tesseract OCR on your system (this is separate from the Python library)

- **Windows:** Download and install from
  https://github.com/UB-Mannheim/tesseract/wiki
  Then note the install path (usually `C:\Program Files\Tesseract-OCR\tesseract.exe`).
- **Mac:** `brew install tesseract`
- **Linux (Debian/Ubuntu):** `sudo apt install tesseract-ocr`

### 2. If you're on Windows, tell pytesseract where Tesseract is installed

At the top of `utils/ocr_utils.py`, add this line (adjust the path if needed):
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```
(Mac/Linux users usually don't need this — it's found automatically.)

### 3. Clone the repo and set up a virtual environment

```bash
git clone <your-repo-url>
cd HandwrittenTextRecognition
python -m venv venv

# Activate it:
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the app

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## Common Interview Questions Based on This Project

1. Why did you use Tesseract instead of a deep learning OCR model?
2. What is the difference between grayscale conversion and thresholding, and why do both?
3. Why did you choose adaptive thresholding over simple global thresholding?
4. What does `image_to_data()` give you that `image_to_string()` doesn't?
5. How does your app calculate an overall confidence score from Tesseract's output?
6. Why is the OCR logic separated into `utils/` instead of being written inside `app.py`?
7. How do you prevent two users uploading at the same time from overwriting each other's files?
8. Why do you delete the uploaded image after processing it?
9. What are the limitations of Tesseract for actual cursive handwriting (as opposed to printed/block text)?
10. How would you extend this project to store history permanently instead of only for the current session?

---

## Resume-Ready Project Description

- Built a full-stack Handwritten/Printed Text Recognition web app using Flask and Tesseract OCR, with an OpenCV preprocessing pipeline (grayscale conversion, denoising, adaptive thresholding, resizing) that improves text extraction accuracy on real-world photos.
- Designed a clean separation between routing (Flask) and business logic (OCR utilities), implementing file validation, error handling, per-word confidence scoring, and a session-based upload history.

---

## Technologies Used

Python, Flask, OpenCV, Tesseract OCR (pytesseract), HTML, CSS, Bootstrap.

---

## Notes on Limitations (good to mention proactively in an interview)

- Tesseract is a rule/pattern-based OCR engine, not a deep learning model —
  it works very well on printed/block text and reasonably on clean,
  neat handwriting, but struggles with cursive or messy handwriting.
  This is a deliberate, honest trade-off explained in the project rather
  than hidden.
- Session history is stored in memory (a Python list), so it resets when
  the server restarts. A natural "next step" to mention is upgrading this
  to a small SQLite database for persistence.
