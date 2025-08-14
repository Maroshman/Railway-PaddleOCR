import base64
import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from paddleocr import PaddleOCR
from io import BytesIO
from PIL import Image
import numpy as np
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
        ocr = PaddleOCR(
            use_angle_cls=True,
            lang='en',
            rec_model_dir='models/latin_PP-OCRv5_mobile_rec_infer'
        )
        # ✅ Debug prints to confirm actual models being used
        print("🔍 Detection model:", ocr.det_model.det_model)
        print("🔍 Recognition model:", ocr.rec_model.rec_model)
        print("🔍 Classifier model:", ocr.cls_model.cls_model)
    return ocr
app = FastAPI()

class OCRRequest(BaseModel):
    base64Image: str

@app.post("/ocr")
def ocr_image(req: OCRRequest, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    def fix_base64_padding(b64_string):
        return b64_string + '=' * (-len(b64_string) % 4)

    try:
        padded_b64 = fix_base64_padding(req.base64Image)
        img_data = base64.b64decode(padded_b64)
        image = Image.open(BytesIO(img_data)).convert("RGB")
        image = np.array(image)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")

    # 🧠 OCR runs only if image decoding succeeds
    result = get_ocr().ocr(image, cls=True)
    response = []

    for line in result[0]:
        text, confidence = line[1][0], line[1][1]
        response.append({
            "text": text,
            "confidence": round(float(confidence), 4)
        })

    return {"results": response}

