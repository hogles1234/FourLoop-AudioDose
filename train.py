import argparse
import os
import shutil
from pathlib import Path
from ultralytics import YOLO

# ── CONFIG ──────────────────────────────────────────────────────────────────
DATASET_ROOT = Path("dataset")
MODEL_OUTPUT  = Path("models")

# Direct path to the YAML downloaded from Roboflow
YAML_PATH = DATASET_ROOT / "data.yaml" 

TRAIN_CONFIG = {
    "epochs":      100,
    "imgsz":       640,
    "batch":       16,      
    "patience":    20,      
    "device":      0,       # Change to "cpu" if you don't have an NVIDIA GPU
    "project":     str(MODEL_OUTPUT),
    "name":        "pill_detector",
    "exist_ok":    True,
    "pretrained":  True,
    "verbose":     True,
    "plots":       True,    
    "save":        True,
}

# ── DATASET FIXES ────────────────────────────────────────────────────────────

def fix_dataset_structure():
    """Renames 'valid' to 'val' to ensure it matches the data.yaml."""
    old_val = DATASET_ROOT / "valid"
    new_val = DATASET_ROOT / "val"

    if old_val.exists() and not new_val.exists():
        old_val.rename(new_val)
        print(f"[✓] Renamed {old_val} to {new_val}")

# ── TRAINING ─────────────────────────────────────────────────────────────────

def train(base_model: str = "yolov8n.pt", resume: bool = False):
    """Run YOLOv8 training."""
    MODEL_OUTPUT.mkdir(exist_ok=True)

    print("=" * 60)
    print("  AudioDose — YOLOv8 Training")
    print("=" * 60)

    fix_dataset_structure()

    if not YAML_PATH.exists():
        print(f"[✗] ERROR: {YAML_PATH} not found. Run download_dataset.py first.")
        return

    if resume:
        last_ckpt = MODEL_OUTPUT / "pill_detector" / "weights" / "last.pt"
        model = YOLO(str(last_ckpt)) if last_ckpt.exists() else YOLO(base_model)
    else:
        print(f"[→] Loading base model: {base_model}")
        model = YOLO(base_model)

    # Start training
    results = model.train(
        data=str(YAML_PATH),
        resume=resume,
        **TRAIN_CONFIG
    )

    print("\n[✓] Training complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train YOLOv8 Pill Detector")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--model",  default="yolov8n.pt")
    args = parser.parse_args()

    train(base_model=args.model, resume=args.resume)