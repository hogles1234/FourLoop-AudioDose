"""
app.py — FastAPI Pill Detector Web Server
==========================================
Serves the pill detection API and web UI.

Usage:
  python app.py

Endpoints:
  GET  /                   → Web UI
  POST /detect             → Upload image, get detections + pill info
  GET  /pills              → List all pills in database
  GET  /pills/{name}       → Get info for a specific pill
  GET  /health             → Health check
"""

import base64
import io
import json
import time
import uuid
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from ultralytics import YOLO


# ── APP SETUP ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AudioDose",
    description="YOLOv8-powered pill recognition for Philippine medicines",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


# ── LOAD MODEL & DATABASE ─────────────────────────────────────────────────────

MODEL_PATH = Path("models/best.pt")
DB_PATH    = Path("utils/pill_database.json")

# Load pill database
with open(DB_PATH) as f:
    PILL_DB: dict = json.load(f)["pills"]

# Load YOLOv8 model (lazy; loaded on first request for fast startup)
_model: Optional[YOLO] = None

def get_model() -> YOLO:
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise HTTPException(
                status_code=503,
                detail=f"Model not found at {MODEL_PATH}. Run train.py first."
            )
        print(f"[→] Loading model from {MODEL_PATH}…")
        _model = YOLO(str(MODEL_PATH))
        print("[✓] Model loaded.")
    return _model


# ── HELPERS ───────────────────────────────────────────────────────────────────

def pil_to_numpy(image: Image.Image) -> np.ndarray:
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def draw_detections(image: np.ndarray, detections: list) -> np.ndarray:
    """Draw bounding boxes and labels on image."""
    img = image.copy()
    colors = [
        (0, 200, 100), (0, 130, 255), (255, 80, 0),
        (180, 0, 200), (0, 180, 200), (200, 200, 0),
    ]

    for i, det in enumerate(detections):
        x1, y1, x2, y2 = map(int, det["bbox"])
        color = colors[i % len(colors)]
        label = f"{det['class_name']} {det['confidence']:.0%}"

        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

        # Label background
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(img, (x1, y1 - th - 10), (x1 + tw + 6, y1), color, -1)
        cv2.putText(img, label, (x1 + 3, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    return img


def numpy_to_base64(image: np.ndarray) -> str:
    """Convert OpenCV image to base64 JPEG string."""
    _, buffer = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 90])
    return base64.b64encode(buffer).decode("utf-8")


def get_pill_info(class_name: str) -> dict:
    """Look up pill info from database with flexible key matching."""
    print(f"[DEBUG] Looking up: '{class_name}' | DB keys: {list(PILL_DB.keys())}")
    candidates = [
        class_name,
        class_name.lower(),
        class_name.lower().replace("authentic-", "").replace("authentic_", "").strip(),
        class_name.replace(" ", "_").lower(),
        class_name.lower().replace(" ", "_").replace("authentic-", "").replace("authentic_", "").strip(),
    ]
    for key in candidates:
        info = PILL_DB.get(key)
        if info:
            return info
    clean_name = class_name.replace("Authentic-", "").replace("Authentic_", "").replace("_", " ").title()
    return {
        "name": clean_name,
        "generic_name": "Unknown",
        "brand": "Unknown",
        "category": "Unknown",
        "description": "No information available for this pill yet.",
        "warnings": "Please consult a pharmacist or physician.",
        "available_otc": None,
    }


# ── ROUTES ───────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root():
    html_path = Path("templates/index.html")
    return HTMLResponse(html_path.read_text())


@app.get("/health")
async def health():
    model_ready = MODEL_PATH.exists()
    return {
        "status": "ok" if model_ready else "model_missing",
        "model_path": str(MODEL_PATH),
        "model_ready": model_ready,
        "pill_classes": len(PILL_DB),
        "db_keys": list(PILL_DB.keys()),
    }


@app.get("/debug/{class_name:path}")
async def debug_lookup(class_name: str):
    """Test pill DB lookup — open in browser: /debug/Biogesic"""
    info = get_pill_info(class_name)
    candidates = [
        class_name,
        class_name.lower(),
        class_name.lower().replace("authentic-", "").replace("authentic_", "").strip(),
        class_name.replace(" ", "_").lower(),
    ]
    return {
        "input":            class_name,
        "candidates_tried": candidates,
        "db_keys":          list(PILL_DB.keys()),
        "match_found":      info.get("generic_name") not in (None, "Unknown"),
        "result":           info,
    }


@app.get("/pills")
async def list_pills():
    """Return all pills in the database."""
    return {
        "count": len(PILL_DB),
        "pills": [
            {
                "id": key,
                "name": val["name"],
                "generic_name": val["generic_name"],
                "category": val["category"],
                "available_otc": val["available_otc"],
            }
            for key, val in PILL_DB.items()
        ],
    }


@app.get("/pills/{pill_id}")
async def get_pill(pill_id: str):
    """Return full info for a specific pill."""
    info = PILL_DB.get(pill_id)
    if not info:
        raise HTTPException(status_code=404, detail=f"Pill '{pill_id}' not found in database.")
    return info


@app.post("/detect")
async def detect_pills(
    file: UploadFile = File(...),
    confidence: float = 0.4,
    iou: float = 0.45,
):
    """
    Upload an image and detect pills.

    Returns:
    - detections: list of detected pills with bounding boxes, confidence, and pill info
    - annotated_image: base64 JPEG with bounding boxes drawn
    - inference_time_ms: how long detection took
    """
    # Validate file type — allow empty/octet-stream from canvas captures
    ALLOWED_TYPES = ("image/jpeg", "image/png", "image/webp", "application/octet-stream", "")
    if file.content_type and file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, or WebP images are accepted.")

    # Read image
    contents = await file.read()
    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read image file.")

    # Resize if very large (speeds up inference)
    max_dim = 1280
    w, h = image.size
    if max(w, h) > max_dim:
        scale = max_dim / max(w, h)
        image = image.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    img_np = pil_to_numpy(image)

    # Run YOLOv8 inference
    model = get_model()
    t0 = time.perf_counter()
    results = model.predict(
        source=img_np,
        conf=confidence,
        iou=iou,
        verbose=False,
    )
    inference_ms = (time.perf_counter() - t0) * 1000

    # Parse detections
    detections = []
    for result in results:
        boxes = result.boxes
        if boxes is None:
            continue
        for box in boxes:
            class_id   = int(box.cls[0])
            class_name = model.names[class_id]
            conf       = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            pill_info = get_pill_info(class_name)

            detections.append({
                "id":           str(uuid.uuid4())[:8],
                "class_name":   class_name,
                "confidence":   round(conf, 4),
                "bbox":         [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
                "pill_info":    pill_info,
            })

    # Sort by confidence (highest first)
    detections.sort(key=lambda d: d["confidence"], reverse=True)

    # Annotate image
    annotated = draw_detections(img_np, detections)
    annotated_b64 = numpy_to_base64(annotated)

    return JSONResponse({
        "success":          True,
        "detections":       detections,
        "detection_count":  len(detections),
        "inference_time_ms": round(inference_ms, 2),
        "image_size":       {"width": image.width, "height": image.height},
        "annotated_image":  annotated_b64,
    })


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  AudioDose — FastAPI Server")
    print("  http://localhost:8000")
    print("=" * 50)
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

import os
from pathlib import Path

# Get the directory where index.py is located
BASE_DIR = Path(__file__).resolve().parent.parent 

MODEL_PATH = BASE_DIR / "models" / "best.pt"
DB_PATH    = BASE_DIR / "utils" / "pill_database.json"

# Initialize YOLO inside the app so it persists between requests
model = YOLO(str(MODEL_PATH))
