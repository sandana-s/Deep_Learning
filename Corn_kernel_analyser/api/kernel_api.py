from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import cv2
import numpy as np
import base64
from ultralytics import YOLO

# Create FastAPI app
app = FastAPI(
    title="Corn Kernel Detector API",
    description="API for detecting good and bad kernels using YOLO model"
)

# Enable CORS (so frontend can call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize model as None
model = None
model_path = None

def load_model():
    """Try to load YOLO model from common paths"""
    global model, model_path
    possible_paths = ["./models/best.pt", "best.pt", "/app/best.pt"]

    for path in possible_paths:
        if os.path.exists(path):
            try:
                model = YOLO(path)
                model_path = path
                print(f" Model loaded from: {path}")
                return True
            except Exception as e:
                print(f" Failed to load model from {path}: {e}")
                continue

    print(" Could not load model from any path")
    return False

# Load the model on startup
load_model()

@app.get("/")
async def root():
    return {"message": "Corn Kernel Detector API is running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_path": model_path,
    }

@app.post("/predict")
async def predict(file: UploadFile):
    try:
        if model is None:
            raise HTTPException(status_code=500, detail="Model not loaded. Ensure best.pt exists in /models/")

        # Read uploaded image
        image_data = await file.read()
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file.")

        # Run YOLO prediction
        results = model.predict(source=img, conf=0.5, imgsz=640)[0]
        classes = results.boxes.cls.cpu().numpy().astype(int)

        # Draw bounding boxes
        annotated_img = results.plot()
        _, buffer = cv2.imencode('.jpg', annotated_img)
        annotated_base64 = base64.b64encode(buffer).decode('utf-8')

        return {
            "total_kernels": len(classes),
            "good_kernels": int(np.sum(classes == 0)),
            "bad_kernels": int(np.sum(classes == 1)),
            "annotated_image": f"data:image/jpeg;base64,{annotated_base64}"
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
