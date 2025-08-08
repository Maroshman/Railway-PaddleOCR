# PaddleOCR FastAPI OCR Service

A simple, secure, self-hosted OCR API using PaddleOCR + FastAPI. Deployable to Railway.

## Features

- Accepts base64-encoded image via POST `/ocr`
- Returns structured JSON with text and confidence
- Protected by API key (`X-API-KEY` header)
- English model (accurate for real-world text)

## Deploy

You can deploy to [Railway](https://railway.app) using the Dockerfile.

## Example Request

```bash
curl -X POST https://your-domain/ocr \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: your-secure-api-key" \
  -d '{"base64Image": "<base64-encoded-image>"}'
```

## Response

```json
{
  "results": [
    {
      "text": "Hello",
      "confidence": 0.987
    },
    ...
  ]
}
```
