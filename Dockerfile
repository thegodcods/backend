# Gunakan image dasar Python
FROM python:3.12.10-slim

# Set variabel lingkungan agar Python tidak membuat file .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set direktori kerja
WORKDIR /app

# 1. Install dependensi sistem (Tesseract & Poppler)
# update: memperbarui daftar paket
# install: menginstal tesseract-ocr (untuk pytesseract) dan poppler-utils (untuk pdf2image/poppler)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# 2. Salin file requirements.txt
COPY requirements.txt .

# 3. Install dependensi Python
# Pastikan di requirements.txt Anda ada: pytesseract, pdf2image, pillow, dll.
RUN pip install --no-cache-dir -r requirements.txt

# 4. Salin seluruh kode sumber
COPY . .

# 5. Jalankan aplikasi
CMD ["python", "app.py"]