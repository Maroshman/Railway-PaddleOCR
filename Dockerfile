FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxrender1 libxext6 \
    libgl1-mesa-glx ffmpeg build-essential \
    && rm -rf /var/lib/apt/lists/*

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
