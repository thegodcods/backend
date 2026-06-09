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

##### Untuk menjalankan di windows mohon ganti kode di ekstraksi_pdf.py dan sesuaikan dengan ruang lingkup anda

```bash
# sesuaikan path dengan path anda
POPPLER_PATH = r'E:\data\poppler-25.12.0\Library\bin'
pytesseract.pytesseract.tesseract_cmd = r'E:\data\tesseract\tesseract.exe'

```

### Untuk Build ke docker harap ganti url mongodbnya di .env

### di file ekstraksi_pdf.py komentari baris berikut

```bash
# komentari baris ini dan hapus variabel POPPLER_PATH disetiap pemanggilan
POPPLER_PATH = r'E:\data\poppler-25.12.0\Library\bin'
pytesseract.pytesseract.tesseract_cmd = r'E:\data\tesseract\tesseract.exe'

```

#### Untuk menggnakan API protected pada header set bagian Authorization

```bash
# ganti token setelah barier tersebut dengan token yang didapat dari setelah login
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNmEyODBlNTY4YWI5OWI2YWNkOWRiNGYyIiwiZXhwIjoxNzgxMDk2NDE0fQ.pzrCDebOvqL_vmwxcx5ELVluSEVOGVMoJfZeprf5kkU
```

3. Instalasi MongoDB Compass
   - Download MongoDB Compass
     Kunjungi situs resmi: https://www.mongodb.com/try/download/compass
     Pilih versi yang sesuai dengan sistem operasi Anda (Windows, macOS, atau Linux)
     Download installer-nya
   - Instalasi di Windows
     Jalankan file .exe yang sudah didownload
     Ikuti wizard instalasi (Next → Next → Install)
     Tunggu proses instalasi selesai
     Klik "Finish" untuk menyelesaikan

4. Menggunakan MongoDB Compass
   - Koneksi ke Database
     Buka MongoDB Compass
     Masukkan connection string:
     Lokal: mongodb://localhost:27017
     Atlas: Copy dari MongoDB Atlas dashboard
     Klik "Connect"
   - Membuat Database Baru
     Setelah terhubung, klik "Create Database"
     Masukkan nama database
     Masukkan nama collection pertama
     Klik "Create Database"
   - Menambahkan Data
     Pilih collection yang ingin ditambahkan data
     Klik "Add Data" → "Insert Document"
     Masukkan data dalam format JSON
     Klik "Insert"
   - Query Data
     Gunakan tab "Filter" untuk mencari data
     Contoh filter: { "nama": "John" }
     Klik "Find" untuk melihat hasil
