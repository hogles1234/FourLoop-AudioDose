## Table of Contents

1. [What You're Building](#1-what-youre-building)
2. [What You Need Before Starting](#2-what-you-need-before-starting)
3. [Project Files Overview](#3-project-files-overview)
4. [Step 1 — Set Up Your Environment](#step-1--set-up-your-environment)
5. [Step 2 — Get the Dataset from Roboflow](#step-2--get-the-dataset-from-roboflow)
6. [Step 3 — Set Up the Project Folder](#step-3--set-up-the-project-folder)
7. [Step 4 — Fix the data.yaml File](#step-4--fix-the-datayaml-file)
8. [Step 5 — Train the Model](#step-5--train-the-model)
9. [Step 6 — Run the Web App](#step-6--run-the-web-app)
10. [Common Errors & Fixes](#common-errors--fixes)
11. [Adding More Pills to the Database](#adding-more-pills-to-the-database)
12. [Quick Reference Cheat Sheet](#quick-reference-cheat-sheet)

---

## 1. What You're Building

By the end of this tutorial you will have a working web app that:

- Accepts a photo of Philippine pills (Biogesic, Neozep, Alaxan, etc.)
- Detects and draws bounding boxes around each pill using a YOLOv8 AI model
- Shows detailed information for each detected pill — generic name, dosage, indications, side effects, price range, and safety warnings
- Runs entirely on your local machine with GPU acceleration

The project has three main parts that work together:

```
Your Photo  →  YOLOv8 Model (train.py)  →  FastAPI Server (app.py)  →  Web UI (index.html)
```

---

## 2. What You Need Before Starting

### Hardware
- A Windows PC or laptop with an NVIDIA GPU
- At least 8GB of GPU VRAM (the project was tested on an RTX 5060 Laptop)
- At least 10GB of free disk space

### Software to install first
Before touching the project, install these three things:

**A — Anaconda (Python environment manager)**
Download from: https://www.anaconda.com/download
This lets you create isolated Python environments so packages don't conflict.

**B — Git (optional but helpful)**
Download from: https://git-scm.com/downloads
Used to manage your code.

**C — A code editor**
VS Code is recommended: https://code.visualstudio.com/
This is where you'll edit files like `train.py` and `data.yaml`.

### Accounts to create
- **Roboflow** — https://roboflow.com (free account, needed to download the dataset)

---

## 3. Project Files Overview

Here is every file in the project and what it does. You don't need to memorize this — just refer back here when you're confused about what a file is for.

```
AudioDose/
│
├── train.py                ← Trains the YOLOv8 model on your pill images
├── app.py                  ← Runs the web server and detection API
├── requirements.txt        ← List of Python packages to install
│
├── dataset/                ← Your pill images and label files go here
│   ├── data.yaml           ← Config file that tells YOLOv8 where the data is
│   ├── train/
│   │   ├── images/         ← Training photos (.jpg or .png)
│   │   └── labels/         ← Matching label files (.txt, YOLO format)
│   ├── valid/
│   │   ├── images/         ← Validation photos
│   │   └── labels/
│   └── test/
│       ├── images/
│       └── labels/
│
├── models/
│   └── best.pt             ← Your trained model is saved here after training
│
├── templates/
│   └── index.html          ← The web UI (the page you see in the browser)
│
└── utils/
    └── pill_database.json  ← Database of pill info (name, dosage, warnings, etc.)
```

> **Key concept:** The `dataset/` folder holds your raw photos and labels. The `models/` folder holds the trained AI brain. They are separate — training reads from `dataset/` and writes to `models/`.

---

## Step 1 — Set Up Your Environment

This step installs all the software your project needs to run.

### 1.1 — Open Anaconda Prompt

Press **Windows key**, search for **Anaconda Prompt**, and open it. You should see a terminal with `(base)` at the start of the line.

> Always use Anaconda Prompt for all commands in this tutorial — not regular Command Prompt or PowerShell.

### 1.2 — Create a dedicated environment

This creates a clean Python 3.10 environment just for this project:

```bash
conda create -n yolov8_env python=3.10 -y
```

Activate it:

```bash
conda activate yolov8_env
```

Your prompt should now show `(yolov8_env)` at the start. Every time you come back to work on this project, run this activate command first.

### 1.3 — Install PyTorch with CUDA

This is the deep learning engine that runs YOLOv8 on your GPU.

> **⚠️ Important for RTX 5060 / RTX 50-series users:** The RTX 5060 uses NVIDIA's new Blackwell architecture (sm_120). Standard PyTorch builds do NOT support it yet. You must install the nightly build:

**For RTX 5060 / RTX 5070 / RTX 5080 / RTX 5090 (Blackwell — new 50-series):**
```bash
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
```

**For RTX 3000 or RTX 4000 series and older:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

Not sure which you have? Run this and it will tell you:
```bash
python -c "import torch; print(torch.cuda.get_device_name(0))"
```

### 1.4 — Install project dependencies

Navigate to your project folder first:
```bash
cd C:\Users\YourName\Downloads\AudioDose
```

Then install everything listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

This installs:

| Package | What it does |
|---|---|
| `ultralytics` | The YOLOv8 library — training and detection |
| `opencv-python` | Draws bounding boxes on detected images |
| `Pillow` | Opens and resizes uploaded photos |
| `numpy` | Handles image data as number arrays |
| `fastapi` | The web framework that powers your API |
| `uvicorn` | The server that runs FastAPI |
| `python-multipart` | Allows FastAPI to accept file uploads |
| `PyYAML` | Reads and writes `.yaml` config files |

### 1.5 — Verify GPU is working

Run this to confirm Python can see your GPU:

```bash
python -c "import torch; print('GPU available:', torch.cuda.is_available()); print('GPU name:', torch.cuda.get_device_name(0))"
```

Expected output:
```
GPU available: True
GPU name: NVIDIA GeForce RTX 5060 Laptop GPU
```

If it says `False`, revisit Step 1.3 and make sure you installed the right PyTorch version.

---

## Step 2 — Get the Dataset from Roboflow

Instead of photographing and labeling hundreds of pills yourself, you can use an existing Philippine pill dataset from Roboflow Universe.

### 2.1 — Create a Roboflow account

Go to https://roboflow.com and sign up for a free account.

### 2.2 — Fork the dataset

1. Go to the dataset link: https://universe.roboflow.com/jan-maviric-workspace/medetect-9kphx-yybfd
2. Click the **Fork** button (top right area of the page)
3. This copies the dataset into your own Roboflow workspace — like copying a file to your own Google Drive

### 2.3 — Generate a version for download

After forking:

1. Open the dataset in your workspace
2. Click **Generate New Version**
3. Configure these settings:

| Setting | Value | Why |
|---|---|---|
| Resize | 640 × 640 | Matches YOLOv8's expected input size |
| Auto-Orient | ON | Fixes sideways phone photos automatically |
| Augmentation → Flip Horizontal | ON | Doubles data variety |
| Augmentation → Brightness ±15% | ON | Handles different lighting conditions |

4. Click **Generate** and wait (takes about 1–2 minutes)

### 2.4 — Get your API key

1. Click your profile icon (top right)
2. Go to **Settings → API**
3. Copy your **Private API Key** — it looks like a long string of random characters

### 2.5 — Download the dataset

Install the Roboflow Python package:
```bash
pip install roboflow
```

Create a new file called `download_dataset.py` in your project folder and paste this:

```python
from roboflow import Roboflow

# Paste your API key between the quotes below
rf = Roboflow(api_key="PASTE_YOUR_API_KEY_HERE")

# Replace with your workspace name (visible in your Roboflow URL)
project = rf.workspace("YOUR_WORKSPACE_NAME").project("medetect-9kphx-yybfd")

# Download as YOLOv8 format into the dataset folder
dataset = project.version(1).download("yolov8", location="dataset/")

print("Download complete!")
print("Class names:", dataset.classes)
```

Run it:
```bash
python download_dataset.py
```

After it finishes, your `dataset/` folder will look like this:
```
dataset/
├── data.yaml          ← Auto-generated config file
├── train/
│   ├── images/        ← Training photos
│   └── labels/        ← Label .txt files
├── valid/             ← Note: Roboflow uses "valid" not "val"
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/
```

---

## Step 3 — Set Up the Project Folder

At this point your `AudioDose/` folder should contain all the downloaded project files plus the newly downloaded dataset. Here's what the full structure should look like:

```
AudioDose/
├── train.py
├── app.py
├── requirements.txt
├── download_dataset.py     ← you just created this
├── dataset/
│   ├── data.yaml
│   ├── train/
│   ├── valid/
│   └── test/
├── models/                 ← empty for now, best.pt appears after training
├── templates/
│   └── index.html
└── utils/
    └── pill_database.json
```

If the `models/`, `templates/`, or `utils/` folders are missing, create them manually:
```bash
mkdir models
mkdir templates
mkdir utils
```

---

## Step 4 — Fix the data.yaml File

This is one of the most important steps. The `data.yaml` file tells YOLOv8 exactly where to find your images. If the paths are wrong, training will crash with a `FileNotFoundError`.

### 4.1 — Open the file

Open `dataset/data.yaml` in VS Code. It will look something like this:

```yaml
train: train/images
val: valid/images
test: test/images

nc: 10
names:
  - Alaxan
  - Bactidol
  - Bioflu
  - Biogesic
  - DayZinc
  - Decolgen
  - Fish_Oil
  - Kremil_S
  - Medicol
  - Neozep
roboflow:
  workspace: your-workspace
  ...
```

### 4.2 — Add the absolute path

YOLOv8 on Windows needs the full absolute path to your dataset folder. Add a `path:` line at the top and update the `val:` line:

```yaml
# ADD THIS LINE — use your actual username and folder location
path: C:\Users\YourName\Downloads\AudioDose\dataset

train: train/images
val: valid/images      # Roboflow uses "valid" — keep it as-is
test: test/images

nc: 10
names:
  - Alaxan
  - Bactidol
  - Bioflu
  - Biogesic
  - DayZinc
  - Decolgen
  - Fish_Oil
  - Kremil_S
  - Medicol
  - Neozep
```

> **How to find your exact path:** In File Explorer, navigate to your `dataset/` folder, click the address bar at the top — it shows the full path. Copy that.

### 4.3 — Sync class names to train.py

Open `train.py` in VS Code and find the `PILL_CLASSES` list near the top. Update it to match **exactly** what's in your `data.yaml` — same names, same order, same capitalization:

```python
PILL_CLASSES = [
    "Alaxan",
    "Bactidol",
    "Bioflu",
    "Biogesic",
    "DayZinc",
    "Decolgen",
    "Fish_Oil",
    "Kremil_S",
    "Medicol",
    "Neozep",
]
```

Also find the `train()` function in `train.py` and update it to use Roboflow's `data.yaml` directly instead of generating a new one:

```python
# Find this line inside the train() function:
yaml_path = create_dataset_yaml()

# Replace it with:
yaml_path = Path("dataset/data.yaml")
```

Save the file.

---

## Step 5 — Train the Model

Now you're ready to train. This teaches the AI to recognize pills from your dataset.

### 5.1 — Run training

Make sure your Anaconda Prompt is in the project folder and your environment is activated, then run:

```bash
python train.py --model yolov8s.pt
```

The `yolov8s.pt` is the "small" YOLOv8 model — a good balance of speed and accuracy for a GPU with 8GB VRAM.

### 5.2 — What happens during training

1. YOLOv8 automatically downloads the `yolov8s.pt` base model (~22MB) from the internet on the first run
2. Training begins — you'll see progress printed every epoch (one full pass through all your images)
3. Every 10 epochs, a checkpoint is saved
4. After all 100 epochs, the best model weights are saved

The output will look like this:
```
Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
  1/100    3.21G      1.823      2.341      1.203         45        640
  2/100    3.18G      1.756      2.187      1.188         52        640
  ...
```

### 5.3 — How long does it take?

| GPU | Approx. time for 100 epochs |
|---|---|
| RTX 5060 (8GB) | ~25–40 minutes |
| RTX 4060 (8GB) | ~30–45 minutes |
| RTX 3060 (12GB) | ~35–50 minutes |

### 5.4 — Understanding the results

When training finishes you'll see something like:

```
Training complete!
Best weights: models/AudioDose/weights/best.pt
mAP50       : 0.9234
mAP50-95    : 0.7891
```

**mAP50** (mean Average Precision at 50% IoU overlap) is the main accuracy metric:

| mAP50 score | What it means |
|---|---|
| Below 0.60 | Poor — needs more/better labeled data |
| 0.60 – 0.79 | Decent — usable but could be improved |
| 0.80 – 0.89 | Good — reliable for most conditions |
| 0.90 and above | Excellent — production-ready |

### 5.5 — Where is the trained model?

After training, the script automatically copies the best model to:
```
AudioDose/models/best.pt
```

This is the file the web app loads when you run it.

---

## Step 6 — Run the Web App

### 6.1 — Start the server

```bash
python app.py
```

You'll see:
```
==================================================
  AudioDose — FastAPI Server
  http://localhost:8000
==================================================
```

### 6.2 — Open the web app

Open your browser and go to: **http://localhost:8000**

You'll see the AudioDose interface with a drag-and-drop upload area.

### 6.3 — How to use it

1. Drag a pill photo onto the upload area or click to browse
2. Adjust the **Confidence** slider — higher means the model needs to be more sure before showing a detection (start at 40%)
3. Adjust the **IoU Threshold** — controls how much overlap is allowed between boxes (leave at 45% for now)
4. Click **⚡ Detect Pills**
5. The page will show:
   - An annotated image with colored bounding boxes around each detected pill
   - A card for each detection showing the pill name, generic name, category, dosage instructions, price range, side effects, and safety warnings
   - A green **OTC** badge for over-the-counter pills, red **Rx** for prescription-only

### 6.4 — API endpoints

The server also exposes these API endpoints if you want to use it programmatically:

| Method | URL | What it does |
|---|---|---|
| GET | `/` | Opens the web UI |
| POST | `/detect` | Upload an image, returns detections as JSON |
| GET | `/pills` | Lists all pills in the database |
| GET | `/pills/biogesic` | Gets full info for a specific pill |
| GET | `/health` | Checks if the server and model are ready |

---

## Common Errors & Fixes

### ❌ `FileNotFoundError: Dataset 'dataset/data.yaml' images not found, missing path '...\valid\images'`

**Cause:** The `path:` line is missing from `data.yaml` or points to the wrong location.

**Fix:** Open `dataset/data.yaml` and add the absolute path:
```yaml
path: C:\Users\YourName\Downloads\AudioDose\dataset
```

---

### ❌ `NVIDIA GeForce RTX 5060 with CUDA capability sm_120 is not compatible`

**Cause:** Your RTX 50-series GPU is newer than your PyTorch build supports.

**Fix:** Upgrade to the PyTorch nightly build:
```bash
pip uninstall torch torchvision torchaudio -y
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
```

---

### ❌ `Model not found at models/best.pt` (503 error in web app)

**Cause:** Training hasn't been run yet, so there's no model file.

**Fix:** Run training first:
```bash
python train.py --model yolov8s.pt
```

---

### ❌ `CUDA out of memory`

**Cause:** Your GPU doesn't have enough VRAM for a batch size of 16.

**Fix:** Open `train.py`, find `"batch": 16` in the `TRAIN_CONFIG` section, and reduce it:
```python
"batch": 8,   # Try 8, or even 4 if still crashing
```

---

### ❌ Low detection accuracy (missing pills or wrong labels)

**Cause:** Usually not enough training images per class or poorly drawn bounding boxes.

**Fix options:**
- Add more photos per pill class (aim for 200+ per class)
- Check your labels in Roboflow's label editor for badly drawn boxes
- Lower the Confidence slider in the web UI to catch more detections

---

### ❌ `No module named 'ultralytics'`

**Cause:** Packages were installed in the wrong environment, or the environment isn't activated.

**Fix:** Make sure `(yolov8_env)` is shown in your prompt. If not:
```bash
conda activate yolov8_env
pip install -r requirements.txt
```

---

## Adding More Pills to the Database

The pill info database is completely separate from the AI model. You can add new pills at any time without retraining.

Open `utils/pill_database.json` in VS Code and add a new entry following this template:

```json
"your_pill_key": {
  "name": "Full Brand Name (Active Ingredient Xmg)",
  "generic_name": "Generic / Chemical Name",
  "brand": "Manufacturer Name",
  "category": "Drug Classification",
  "dosage": "Strength e.g. 500mg",
  "form": "Tablet / Capsule / Syrup",
  "color": "Visual description e.g. white oval tablet",
  "description": "What this medicine is used for in plain language.",
  "indications": ["Condition 1", "Condition 2", "Condition 3"],
  "contraindications": ["Do not use if you have X", "Avoid if pregnant"],
  "side_effects": ["Nausea", "Dizziness", "Headache"],
  "dosage_instructions": "Adults: 1 tablet every 6 hours with food.",
  "price_range": "₱10-20 per tablet",
  "available_otc": true,
  "warnings": "Important safety information goes here."
}
```

Set `"available_otc": true` for over-the-counter pills and `false` for prescription-only medicines. The web UI will automatically show the correct OTC or Rx badge.

Common Philippine OTC medicines to add: Diatabs, Kremil-S, Lagundi, Medicol, Solmux, Robitussin, Bactidol, Stresstabs.

---

## Quick Reference Cheat Sheet

### Every time you start working

```bash
# 1. Open Anaconda Prompt
# 2. Activate environment
conda activate yolov8_env

# 3. Navigate to project
cd C:\Users\YourName\Downloads\AudioDose
```

### Train the model

```bash
python train.py --model yolov8s.pt          # Start fresh
python train.py --model yolov8s.pt --resume  # Continue interrupted training
```

### Run the web app

```bash
python app.py
# Then open: http://localhost:8000
```

### Model size guide

| Command flag | Model | Speed | Accuracy | Min VRAM |
|---|---|---|---|---|
| `--model yolov8n.pt` | Nano | Fastest | Lowest | 2GB |
| `--model yolov8s.pt` | Small | Fast | Good | 4GB |
| `--model yolov8m.pt` | Medium | Medium | Better | 8GB |
| `--model yolov8l.pt` | Large | Slow | Best | 12GB |

### File to edit for each task

| Task | File to edit |
|---|---|
| Change training settings (epochs, batch size) | `train.py` → `TRAIN_CONFIG` section |
| Change which pills to detect | `train.py` → `PILL_CLASSES` list |
| Add pill info to the app | `utils/pill_database.json` |
| Change the web UI appearance | `templates/index.html` |
| Change server port or host | `app.py` → last line (`uvicorn.run`) |
| Fix dataset paths | `dataset/data.yaml` → `path:` line |

---
