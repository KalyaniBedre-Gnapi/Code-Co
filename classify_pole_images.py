import os
import csv
import shutil
from ultralytics import YOLO

MODEL_PATH = r"D:\Code&Co\runs\classify\runs_pole_classifier\pole_vs_no_pole_v1\weights\best.pt"
IMAGE_DIR = r"D:\Code&Co\streetview_images"
OUTPUT_CSV = r"D:\Code&Co\pole_results.csv"

POLE_DIR = os.path.join(IMAGE_DIR, "predicted_pole")
NO_POLE_DIR = os.path.join(IMAGE_DIR, "predicted_no_pole")
UNCERTAIN_DIR = os.path.join(IMAGE_DIR, "predicted_uncertain")

# If confidence is below this, send it to uncertain for manual review
CONFIDENCE_THRESHOLD = 0.75

def ensure_dirs():
    os.makedirs(POLE_DIR, exist_ok=True)
    os.makedirs(NO_POLE_DIR, exist_ok=True)
    os.makedirs(UNCERTAIN_DIR, exist_ok=True)

def main():
    ensure_dirs()

    model = YOLO(MODEL_PATH)
    rows = []

    for file_name in os.listdir(IMAGE_DIR):
        if not file_name.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        image_path = os.path.join(IMAGE_DIR, file_name)

        try:
            results = model(image_path, verbose=False)
            result = results[0]

            probs = result.probs
            top_index = probs.top1
            raw_label = result.names[top_index]
            confidence = float(probs.top1conf)

            if confidence < CONFIDENCE_THRESHOLD:
                final_label = "uncertain"
                target_dir = UNCERTAIN_DIR
            elif raw_label == "pole":
                final_label = "pole"
                target_dir = POLE_DIR
            else:
                final_label = "no_pole"
                target_dir = NO_POLE_DIR

            shutil.copy2(image_path, os.path.join(target_dir, file_name))

            rows.append({
                "file_name": file_name,
                "predicted_label": final_label,
                "raw_label": raw_label,
                "confidence": round(confidence, 4)
            })

            print(f"{file_name} -> {final_label} (raw={raw_label}, conf={confidence:.4f})")

        except Exception as e:
            print(f"Error processing {file_name}: {e}")
            rows.append({
                "file_name": file_name,
                "predicted_label": "error",
                "raw_label": "error",
                "confidence": ""
            })

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["file_name", "predicted_label", "raw_label", "confidence"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone. Results saved to: {OUTPUT_CSV}")
    print(f"Pole images copied to: {POLE_DIR}")
    print(f"No-pole images copied to: {NO_POLE_DIR}")
    print(f"Uncertain images copied to: {UNCERTAIN_DIR}")

if __name__ == "__main__":
    main()