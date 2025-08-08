import base64
import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from paddleocr import PaddleOCR
from io import BytesIO
from PIL import Image

# Load API key from file
API_KEY_FILE = "api_key.txt"
if not os.path.exists(API_KEY_FILE):
    raise RuntimeError("API key file not found. Please create 'api_key.txt' with your API key.")
with open(API_KEY_FILE, "r") as f:
    API_KEY = f.read().strip()

# Init PaddleOCR (English only)
ocr = PaddleOCR(use_angle_cls=True, lang='en')

app = FastAPI()

class OCRRequest(BaseModel):
    base64Image: str

@app.post("/ocr")
def ocr_image(req: OCRRequest, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        img_data = base64.b64decode(req.base64Image)
        image = Image.open(BytesIO(img_data)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid image data")

    result = ocr.ocr(image, cls=True)
    response = []

    for line in result[0]:
        text, confidence = line[1][0], line[1][1]
        response.append({
            "text": text,
            "confidence": round(float(confidence), 4)
        })

    return {"results": response}
