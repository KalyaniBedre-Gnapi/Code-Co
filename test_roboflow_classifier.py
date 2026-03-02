import os
from inference_sdk import InferenceHTTPClient

API_KEY = os.getenv("ROBOFLOW_API_KEY")
if not API_KEY:
    raise ValueError("ROBOFLOW_API_KEY is not set.")

CLIENT = InferenceHTTPClient(
    api_url="https://classify.roboflow.com",
    api_key=API_KEY
)
# This code tests one image at a time. 
# Change this to img path
image_path = r"D:\Code&Co\streetview_images\SE_Division_St5.jpg"

result = CLIENT.infer(image_path, model_id="pole-vs-no-pole/1")

print("Full result:")
print(result)
print("\nTop class:", result.get("top"))
print("Top confidence:", result.get("confidence"))
print("Predictions:", result.get("predictions", []))