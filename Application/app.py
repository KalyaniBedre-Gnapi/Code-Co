from flask import Flask, request, jsonify
from flask_cors import CORS
from inference_sdk import InferenceHTTPClient
import os
import tempfile

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("ROBOFLOW_API_KEY")
if not API_KEY:
    raise ValueError("ROBOFLOW_API_KEY is not set.")

CLIENT = InferenceHTTPClient(
    api_url="https://classify.roboflow.com",
    api_key=API_KEY
)

MODEL_ID = "pole-vs-no-pole/1"
CONFIDENCE_THRESHOLD = 0.80


@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files["image"]

    if image_file.filename == "":
        return jsonify({"error": "Empty file name"}), 400

    suffix = os.path.splitext(image_file.filename)[1] or ".jpg"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        temp_path = tmp.name
        image_file.save(temp_path)

    try:
        result = CLIENT.infer(temp_path, model_id=MODEL_ID)

        label = result.get("top")
        confidence = float(result.get("confidence", 0) or 0)

        if confidence < CONFIDENCE_THRESHOLD:
            final_label = "uncertain"
        else:
            final_label = label

        return jsonify({
            "label": final_label,
            "raw_label": label,
            "confidence": confidence,
            "predictions": result.get("predictions", [])
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    app.run(debug=True)