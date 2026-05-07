# download_dataset.py
from roboflow import Roboflow

rf = Roboflow(api_key="cAFHCTIcCh9JsayWt7YI")

# Replace with your forked workspace and project name
project = rf.workspace("jan-maviric-workspace").project("medetect-9kphx-yybfd")
version = project.version(1)

# Downloads into a folder and auto-creates data.yaml
dataset = version.download("yolov8")