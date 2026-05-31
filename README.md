## 🛠️ Instalasi & Konfigurasi Environment

Proyek ini memerlukan instalasi library Python serta software eksternal untuk mendukung fitur OCR.

### 1. Instalasi Dependensi Python

Pastikan Python 3.8+ sudah terinstall. Lalu jalankan:

```bash
pip install -r requirements.txt

```

### 2. Instalasi Software Eksternal (Wajib untuk OCR)

Karena modul main3.py menangani PDF gambar, Anda WAJIB menginstall dua software berikut di sistem operasi Windows Anda. Tanpa ini, program akan error saat memproses file scan.

#### A. Tesseract-OCR (Mesin Pengenal Teks)

Digunakan oleh library pytesseract untuk mengenali karakter dari gambar.

1. Download Installer: [UB-Mannheim Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki?spm=a2ty_o01.29997173.0.0.49f755fb8UqXhb)
2. Proses Instalasi:
   - Jalankan file .exe yang diunduh.
   - Saat muncul pilihan komponen (Choose Components), PENTING: Centang opsi "Additional language data" -> lalu pilih Indonesian (ind) dan English (eng). Ini agar OCR bisa membaca bahasa Indonesia dengan baik.
   - Selesaikan instalasi.
   - Catat path instalasi (default biasanya: C:\Program Files\Tesseract-OCR).
3. Verifikasi:
   - Buka CMD atau PowerShell.
   - Ketik: tesseract --version
   - Jika muncul nomor versi, instalasi berhasil.

#### B. Poppler (PDF Rendering Engine)

Digunakan oleh library pdf2image untuk mengubah halaman PDF menjadi gambar (PNG/JPG) sebelum di-proses oleh Tesseract.

1. Download Binary: Unduh release terbaru untuk Windows dari [Poppler for Windows by oschwartz10612](https://github.com/oschwartz10612/poppler-windows/releases/?spm=a2ty_o01.29997173.0.0.49f755fb8UqXhb). Pilih file zip terbaru (misal: Release-xx.xx.x-0.zip).
2. Ekstrak & Pindahkan:
   - Extract file zip tersebut.
   - Pindahkan folder hasil extract (misalnya bernama poppler-xx.xx.x) ke lokasi permanen yang mudah diakses.
   - Rekomendasi: Pindahkan ke C:\Tools\poppler atau D:\Tools\poppler.
