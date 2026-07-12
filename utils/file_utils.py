"""
file_utils.py
-------------
Small helper functions for validating uploaded files and cleaning up
temporary files afterward. Kept separate from app.py and ocr_utils.py
so that "file handling" logic and "OCR" logic don't get mixed together.
"""

import os

# Only these file extensions are allowed to be uploaded.
# Keeping this as a set makes the "in" check fast and simple.
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}


def is_allowed_file(filename):
    """
    Checks whether the uploaded file has an allowed extension.
    Returns True/False.

    Example: "photo.PNG" -> True, "notes.pdf" -> False
    """
    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


def delete_file_safely(file_path):
    """
    Deletes a file from disk if it exists.
    Wrapped in try/except so that a missing/locked file doesn't crash
    the whole request - deleting temporary uploads is "best effort"
    cleanup, not a critical operation.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError as error:
        # We just log this to the console - failing to delete a temp
        # file should never break the user's request.
        print(f"Warning: could not delete temp file {file_path}: {error}")
