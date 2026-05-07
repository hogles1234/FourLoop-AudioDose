# AudioDose
---
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/hogles1234/FourLoop-AudioDose)
> **For Judges:** Click the badge above. The app will install and launch **automatically** — no commands needed.

in our case now : https://effective-waddle-4j9v7596x7wwcjq96.github.dev ||||
https://effective-waddle-4j9v7596x7wwcjq96-8000.app.github.dev   | APP

---
## 🧠 What It Does
| Feature | Details |
|---|---|
|  Detection Model | YOLOv8 (Ultralytics) |
|  Target | Philippine pharmaceutical pills |
|  Backend | FastAPI (Python) |
|  Frontend | HTML + JavaScript |
|  Environment | GitHub Codespaces |
---

## Project Structure

```
├── app.py                  # FastAPI server & YOLOv8 inference
├── requirements.txt        # Python dependencies
├── static/                 # Frontend (HTML, CSS, JS)
├── models/                 # YOLOv8 weights (.pt file)
├── templates/              # HTML templates
├── utils/                  # Pill database & helpers
└── .devcontainer/
    └── devcontainer.json   # Auto-setup for GitHub Codespaces
```
---

## 🛠️ Tech Stack

- **[YOLOv8](https://github.com/ultralytics/ultralytics)** — Object detection model
- **[FastAPI](https://fastapi.tiangolo.com/)** — High-performance Python web framework
- **HTML / JavaScript** — Lightweight frontend for real-time display
- **GitHub Codespaces** — Zero-setup cloud development environment

---
💻 Getting Started
Prerequisites
Python 3.9+

GitHub Codespaces or a local Linux/Windows environment

Installation
Clone the repository:

Bash
git clone https://github.com/your-username/AudioDose.git
cd AudioDose
Install dependencies:

Bash
pip install -r requirements.txt
Install System Dependencies (For Cloud/Codespaces):
To avoid OpenCV graphics errors in a headless environment, ensure you have the necessary libraries:

Bash
pip uninstall -y opencv-python opencv-contrib-python
pip install opencv-python-headless
Running the Application
Start the FastAPI server:

Bash
python app.py
Once the server is running, open the provided local URL (usually http://127.0.0.1:8000) in your browser to start the camera feed.

📋 Usage
Align the medicine packaging within the camera view.

The system will identify the medicine and check it against the internal schedule.

Listen for the audio confirmation: "Safe to take" or "Stop, mismatch detected."

View the CareCircle logs to see the history of scanned medications.

🛡️ License
This project is developed for the CodeKada Online Hackathon.

 👥 Team
SogeKing
Sakiサキ
Fremics
Fatima


👥 Acknowledgments

ACOMSS (Adamson Computer Science Society)

Developed by the AudioDose Team.
