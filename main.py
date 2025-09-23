import base64
import os
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
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
            rec_model_dir='models/PP-OCRv5_mobile_rec_infer'
        )
    return ocr

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class OCRRequest(BaseModel):
    base64Image: str

@app.post("/ocr")
def ocr_image(req: OCRRequest, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    def fix_base64_padding(b64_string):
        # Strip data URL prefix if present (e.g., "data:image/jpeg;base64,")
        if b64_string.startswith('data:image/'):
            # Find the comma that separates the data URL from the base64 data
            comma_index = b64_string.find(',')
            if comma_index != -1:
                b64_string = b64_string[comma_index + 1:]
        
        return b64_string + '=' * (-len(b64_string) % 4)

    try:
        padded_b64 = fix_base64_padding(req.base64Image)
        img_data = base64.b64decode(padded_b64)
        image = Image.open(BytesIO(img_data)).convert("RGB")
        image = np.array(image)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")

    try:
        # 🧠 OCR runs only if image decoding succeeds
        result = get_ocr().ocr(image, cls=True)
        
        # Handle cases where no text is detected (return empty results instead of error)
        if result is None or len(result) == 0 or result[0] is None:
            return {"results": []}
        
        response = []
        for line in result[0]:
            # Check if line has valid structure before processing
            if line and len(line) >= 2 and line[1] and len(line[1]) >= 2:
                text, confidence = line[1][0], line[1][1]
                response.append({
                    "text": text,
                    "confidence": round(float(confidence), 4)
                })
        
        return {"results": response}
        
    except Exception as e:
        # Log the error for debugging but still return empty results
        print(f"OCR processing error: {str(e)}")
        # Return empty results instead of 500 error
        return {"results": []}

