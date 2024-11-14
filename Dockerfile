FROM python:3.11.4-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libmagic1 \
    gcc \
    g++ \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev

# Ensure pip, setuptools, and wheel are up to date
RUN python -m pip install --upgrade pip setuptools wheel

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Download NLTK punkt data
# Set the environment variable for Tesseract
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/tessdata/

# Copy the application files into the container
COPY . .

# Run the FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
