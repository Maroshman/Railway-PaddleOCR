FROM python:3.9-slim

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Upgrade pip early
RUN pip install --no-cache-dir --upgrade pip

# --- Download PaddleOCR v5 model if not already present ---
RUN mkdir -p /app/models/latin_PP-OCRv5_rec_infer && \
    if [ ! -f /app/models/latin_PP-OCRv5_rec_infer/inference.pdmodel ]; then \
        curl -L https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0//PP-OCRv5_server_rec_infer.tar -o /app/models/PP-OCRv5_server_rec_infer.tar && \
        tar -xf /app/models/PP-OCRv5_server_rec_infer.tar -C /app/models/PP-OCRv5_server_rec_infer && \
        rm /app/models/PP-OCRv5_server_rec_infer.tar; \
    fi

# Install system dependencies with retry-safe apt install
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libglib2.0-0 libsm6 libxrender1 libxext6 \
    libgl1 ffmpeg build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy code
COPY . .

# Pre-install numpy before others (important for opencv)
RUN pip install --no-cache-dir numpy==1.23.5

# Install all remaining dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Run server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
