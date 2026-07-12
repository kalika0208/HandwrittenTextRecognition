"""
app.py
------
Main Flask application file. This file is intentionally kept "thin" -
it only handles routing (which URL does what) and basic request/response
logic. The actual OCR work lives in utils/ocr_utils.py, and file
validation/cleanup lives in utils/file_utils.py. This separation is a
common, resume-friendly pattern called "separation of concerns".
"""

import os
import uuid
from flask import Flask, render_template, request, jsonify, send_file
from utils.ocr_utils import extract_text_from_image
from utils.file_utils import is_allowed_file, delete_file_safely

# ---------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------
app = Flask(__name__)

# Folder where uploaded images are temporarily stored before processing
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Limit uploads to 10 MB to prevent someone from crashing the server
# with a huge file.
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB

# In-memory history of this session's uploads (extracted text + stats).
# NOTE: This resets every time the Flask server restarts, since it's
# just a plain Python list, not a database. That's fine for this
# project's scope - it's meant to demonstrate the idea of "history",
# not to be a production-grade persistent store.
session_history = []


# ---------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------

@app.route("/")
def home():
    """
    Renders the main upload page.
    """
    return render_template("index.html", history=session_history)


@app.route("/upload", methods=["POST"])
def upload_image():
    """
    Handles the image upload + OCR pipeline:
    1. Validate that a file was actually sent, and that it's an allowed type.
    2. Save it temporarily to the uploads/ folder with a unique name.
    3. Run preprocessing + OCR (via utils/ocr_utils.py).
    4. Save the result to session_history for the "history" feature.
    5. Delete the temporary file (we don't need to keep it after OCR).
    6. Return the extracted text + stats as JSON, which the frontend
       JavaScript will use to update the page without a full reload.
    """

    # --- Step 1: Validate the incoming file ---
    if "image" not in request.files:
        return jsonify({"error": "No file was uploaded."}), 400

    uploaded_file = request.files["image"]

    if uploaded_file.filename == "":
        return jsonify({"error": "No file was selected."}), 400

    if not is_allowed_file(uploaded_file.filename):
        return jsonify({"error": "Only JPG, JPEG, and PNG files are allowed."}), 400

    # --- Step 2: Save the file with a unique name so uploads never clash ---
    # We use uuid4() to generate a random unique ID, so two users
    # uploading files at the same time never overwrite each other.
    file_extension = uploaded_file.filename.rsplit(".", 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    saved_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    uploaded_file.save(saved_path)

    # --- Step 3: Run the OCR pipeline, with graceful error handling ---
    try:
        result = extract_text_from_image(saved_path)
    except Exception as error:
        # Even if something goes wrong, we still want to clean up the
        # saved file before returning an error to the user.
        delete_file_safely(saved_path)
        return jsonify({"error": f"Something went wrong while processing the image: {error}"}), 500

    # --- Step 4: Save this result into the session history list ---
    history_entry = {
        "filename": uploaded_file.filename,
        "text": result["text"],
        "confidence": result["confidence"],
        "processing_time": result["processing_time"],
    }
    session_history.append(history_entry)

    # --- Step 5: Delete the temporary uploaded file ---
    # We already extracted the text we need, so there's no reason to
    # keep the original image sitting on the server's disk.
    delete_file_safely(saved_path)

    # --- Step 6: Send the result back to the browser as JSON ---
    return jsonify(result)


@app.route("/download-text", methods=["POST"])
def download_text():
    """
    Lets the user download the extracted text as a .txt file.
    The frontend sends the text back to us in the request body, we
    write it to a temporary file, send it to the browser, and then
    delete it.
    """
    text_content = request.form.get("text", "")

    temp_filename = f"extracted_text_{uuid.uuid4().hex}.txt"
    temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)

    with open(temp_path, "w", encoding="utf-8") as file:
        file.write(text_content)

    # send_file() streams the file to the browser as a download.
    # We use a try/finally so the temp .txt file gets deleted even if
    # sending the file raises an error partway through.
    try:
        return send_file(
            temp_path,
            as_attachment=True,
            download_name="extracted_text.txt"
        )
    finally:
        delete_file_safely(temp_path)


@app.route("/clear-history", methods=["POST"])
def clear_history():
    """
    Clears the in-memory session history list.
    Useful so the demo doesn't get cluttered during a long session.
    """
    session_history.clear()
    return jsonify({"message": "History cleared."})


# ---------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------
if __name__ == "__main__":
    # debug=True gives auto-reload and helpful error pages during
    # development. Turn this off (debug=False) before any real deployment.
    app.run(debug=True)
