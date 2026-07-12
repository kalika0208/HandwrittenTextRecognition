import os
from utils.ocr_utils import preprocess_image, extract_text
from utils.db_utils import init_db, save_result, get_all_history

IMAGES_FOLDER = "images"
OUTPUT_FOLDER = "output"


def process_image(filename):
    image_path = os.path.join(IMAGES_FOLDER, filename)
    if not os.path.exists(image_path):
        print(f"\n❌ File not found: {image_path}\n")
        return

    print("\n🔍 Preprocessing image...")
    processed = preprocess_image(image_path)

    print("🧠 Running OCR...")
    text, confidence = extract_text(processed)

    print("\n----------- EXTRACTED TEXT -----------")
    print(text)
    print("---------------------------------------")
    print(f"Confidence: {confidence}%\n")

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    output_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(filename)[0] + ".txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"📄 Saved to: {output_path}")

    save_result(filename, text, confidence)
    print("💾 Logged to ocr_history.db\n")


def show_history():
    rows = get_all_history()
    if not rows:
        print("\nNo history yet.\n")
        return
    print("\n----------- HISTORY -----------")
    for filename, confidence, created_at in rows:
        print(f"{created_at}  |  {filename}  |  {confidence}%")
    print("--------------------------------\n")


def main():
    init_db()
    print("=== Simple Handwritten Text Recognition ===")
    print(f"Put images inside the '{IMAGES_FOLDER}' folder.\n")

    while True:
        print("1. Process an image\n2. View history\n3. Exit")
        choice = input("Choose: ").strip()
        if choice == "1":
            process_image(input("Filename (e.g. sample.jpg): ").strip())
        elif choice == "2":
            show_history()
        elif choice == "3":
            break
        else:
            print("Enter 1, 2, or 3.\n")


if __name__ == "__main__":
    main()