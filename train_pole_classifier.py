from ultralytics import YOLO

def main():
    # Use a small classification model as the starting point.
    # If this checkpoint name differs in your installed version,
    # replace it with any available Ultralytics classification checkpoint.
    model = YOLO("yolo11n-cls.pt")

    model.train(
    data="dataset", # dataset folder with train/val/test class subfolders
    epochs=25,
    imgsz=224,
    batch=16,
    project="runs_pole_classifier",
    name="pole_vs_no_pole_v2"   #"pole_vs_no_pole_v1"  #chane name everytime the model is retrained
)

if __name__ == "__main__":
    main()