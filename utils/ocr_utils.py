"""
ocr_utils.py
------------
This file contains all the image preprocessing and OCR (Optical Character
Recognition) logic. Keeping this separate from app.py is good practice -
app.py should only handle routes (URLs), and this file should handle the
"real work" of turning an image into text.

Why preprocess an image before OCR?
Tesseract (the OCR engine) works by detecting shapes that match known
letter patterns. It gets confused by:
- Colour noise / shadows -> so we convert to grayscale first
- Random speckles/noise   -> so we remove noise
- Blurry or unclear edges between text and background -> so we threshold
- Very small or very large images -> so we resize to a good working size

Each step below is a small, focused function so it's easy to read and
easy to explain in an interview.
"""

import cv2
import pytesseract
import time


def convert_to_grayscale(image):
    """
    Converts a colour image (BGR, since OpenCV loads images in BGR order)
    into grayscale (black & white shades only).

    Why this helps OCR:
    Tesseract does not care about colour - it only cares about the shape
    of letters. Colour information is extra data that slows processing
    down and can even confuse thresholding later. Grayscale keeps only
    brightness information, which is exactly what we need.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray


def remove_noise(gray_image):
    """
    Removes small random speckles/noise from the grayscale image using a
    median blur filter.

    Why this helps OCR:
    Photos taken with a phone camera often have small grainy noise,
    especially in low light. This noise can look like extra dots or
    broken letter edges to Tesseract, causing wrong character guesses.
    A median blur replaces each pixel with the median value of its
    neighbours, smoothing out noise while keeping edges reasonably sharp.
    """
    denoised = cv2.medianBlur(gray_image, 3)
    return denoised


def apply_threshold(denoised_image):
    """
    Converts the grayscale image into a pure black-and-white (binary)
    image using adaptive thresholding.

    Why this helps OCR:
    Tesseract is trained to work best on clean black text on a white
    background. Real-world photos have uneven lighting (shadows on one
    side of the page, for example), so a single global brightness cutoff
    would turn some real text white and some background black.
    Adaptive thresholding calculates a different cutoff for each small
    region of the image, so it handles uneven lighting much better than
    a simple global threshold.
    """
    thresholded = cv2.adaptiveThreshold(
        denoised_image,
        255,                              # max value to assign (white)
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,    # weighted mean of neighbourhood
        cv2.THRESH_BINARY,                 # output is pure black or white
        31,                                 # size of neighbourhood block (must be odd)
        2                                    # constant subtracted from the mean
    )
    return thresholded


def resize_image(image, target_width=1200):
    """
    Resizes the image so its width matches target_width, keeping the
    aspect ratio the same.

    Why this helps OCR:
    - If the image is too small, individual letters become blurry blobs
      of only a few pixels, and Tesseract cannot tell them apart.
    - If the image is too large, processing is slower for no accuracy
      benefit.
    Resizing to a consistent, moderate width gives Tesseract enough
    detail per character without wasting processing time.
    """
    height, width = image.shape[:2]

    # Only resize if the image isn't already close to our target width,
    # so we don't blur a small image by stretching it too much.
    if width == 0:
        return image

    scale = target_width / width
    new_width = target_width
    new_height = int(height * scale)

    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
    return resized


def preprocess_image(image_path):
    """
    Runs the full preprocessing pipeline on an image file and returns
    the final processed image (ready for OCR) along with the path where
    we save it (useful for showing the "before/after" on the webpage).

    Order of operations matters here:
    1. Resize first  -> so noise removal and thresholding work on a
                         consistent image size.
    2. Grayscale      -> strip out colour before further processing.
    3. Remove noise   -> clean up speckles before thresholding, since
                         noise can trick the threshold into creating
                         fake black/white edges.
    4. Threshold      -> final step, produces clean black text on white.
    """
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Could not read the image file. It may be corrupted.")

    resized = resize_image(image)
    gray = convert_to_grayscale(resized)
    denoised = remove_noise(gray)
    thresholded = apply_threshold(denoised)

    return thresholded


def extract_text_from_image(image_path):
    """
    Main function called by app.py. Takes the path to an uploaded image,
    preprocesses it, runs Tesseract OCR, and returns:
    - the extracted text
    - an approximate confidence score (0-100)
    - the time taken to process (in seconds)

    We use pytesseract.image_to_data() instead of just image_to_string()
    because image_to_data() also gives us per-word confidence scores,
    which we average to get an overall confidence score for the page.
    """
    start_time = time.time()

    processed_image = preprocess_image(image_path)

    # image_to_data returns a dictionary with words, positions, and
    # confidence scores for each detected word.
    ocr_data = pytesseract.image_to_data(
        processed_image,
        output_type=pytesseract.Output.DICT
    )

    # Build the final text by joining all detected words together.
    words = [word for word in ocr_data["text"] if word.strip() != ""]
    extracted_text = " ".join(words)

    # Confidence scores come as strings, and Tesseract uses "-1" for
    # regions where it detected no text - we filter those out before
    # averaging so they don't unfairly lower the score.
    confidences = [
        int(conf) for conf in ocr_data["conf"]
        if conf != "-1" and str(conf).strip() != ""
    ]
    average_confidence = round(sum(confidences) / len(confidences), 2) if confidences else 0

    end_time = time.time()
    processing_time = round(end_time - start_time, 2)

    return {
        "text": extracted_text if extracted_text.strip() else "No text detected in this image.",
        "confidence": average_confidence,
        "processing_time": processing_time
    }
