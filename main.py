import base64
import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from paddleocr import PaddleOCR
from io import BytesIO
from PIL import Image

# Load API key from environment variable
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY not set in environment.")

# Init PaddleOCR (English only)
ocr = None

def get_ocr():
    global ocr
    if ocr is None:
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(use_angle_cls=True, lang='en')
    return ocr
app = FastAPI()

class OCRRequest(BaseModel):
    base64Image: str

@app.post("/ocr")
def ocr_image(req: OCRRequest, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        img_data = base64.b64decode(req.base64Image, validate=True)
        image = Image.open(BytesIO(img_data))
        image = image.convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")
        result = get_ocr().ocr(image, cls=True)
        response = []

    for line in result[0]:
        text, confidence = line[1][0], line[1][1]
        response.append({
            "text": text,
            "confidence": round(float(confidence), 4)
        })

    return {"results": response}
