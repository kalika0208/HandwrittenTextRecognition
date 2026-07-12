import cv2
import easyocr

reader = easyocr.Reader(['en'], gpu=False)


def convert_to_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def resize_image(image, target_width=1000):
    height, width = image.shape[:2]
    scale = target_width / width
    new_size = (target_width, int(height * scale))
    return cv2.resize(image, new_size, interpolation=cv2.INTER_CUBIC)


def apply_threshold(gray_image):
    return cv2.adaptiveThreshold(
        gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 2
    )


def preprocess_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image at: {image_path}")
    resized = resize_image(image)
    gray = convert_to_grayscale(resized)
    return apply_threshold(gray)


def extract_text(processed_image):
    results = reader.readtext(processed_image)
    if not results:
        return "No text detected in this image.", 0.0
    lines = [text for (_, text, _) in results]
    confidences = [conf for (_, _, conf) in results]
    combined_text = "\n".join(lines)
    avg_confidence = round((sum(confidences) / len(confidences)) * 100, 2)
    return combined_text, avg_confidence