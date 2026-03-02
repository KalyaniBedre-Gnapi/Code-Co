import os
import csv
from inference_sdk import InferenceHTTPClient

API_KEY = os.getenv("ROBOFLOW_API_KEY")
if not API_KEY:
    raise ValueError("ROBOFLOW_API_KEY is not set.")

CLIENT = InferenceHTTPClient(
    api_url="https://classify.roboflow.com",
    api_key=API_KEY
)

IMAGE_DIR = r"D:\Code&Co\streetview_images"
OUTPUT_CSV = r"D:\Code&Co\roboflow_pole_results.csv"

CONFIDENCE_THRESHOLD = 0.80

rows = []

for file_name in os.listdir(IMAGE_DIR):
    if not file_name.lower().endswith((".jpg", ".jpeg", ".png")):
        continue

    image_path = os.path.join(IMAGE_DIR, file_name)

    try:
        result = CLIENT.infer(image_path, model_id="pole-vs-no-pole/1")

        top_class = result.get("top")
        top_confidence = result.get("confidence", 0)

        if top_confidence is None:
            top_confidence = 0

        if top_confidence < CONFIDENCE_THRESHOLD:
            final_label = "uncertain"
        else:
            final_label = top_class

        rows.append({
            "file_name": file_name,
            "predicted_label": final_label,
            "raw_label": top_class,
            "confidence": round(float(top_confidence), 4)
        })

        print(f"{file_name} -> {final_label} (raw={top_class}, conf={top_confidence})")

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

print(f"\nDone. Results saved to {OUTPUT_CSV}")