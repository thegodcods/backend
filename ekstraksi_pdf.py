import pdfplumber
import re, os
import pytesseract
from pdf2image import convert_from_path

# KONFIGURASI PENTING UNTUK WINDOWS
# Ganti path ini dengan lokasi instalasi Tesseract di komputermu
POPPLER_PATH = r'E:\data\poppler-25.12.0\Library\bin'
pytesseract.pytesseract.tesseract_cmd = r'E:\data\tesseract\tesseract.exe'

def ekstraksi_pdf_cv (pdf_file, filename):
    if not os.path.exists("temp_pdf"):
            os.mkdir("temp_pdf")
    pdf_file.save(f"temp_pdf/{filename}")
    detect = detect_pdf_type_pdfplumber(f"temp_pdf/{filename}")
    if detect == 'text':
        return extract_pdf_text(f"temp_pdf/{filename}")
    elif detect == 'image':
        return extract_pdf_image(f"temp_pdf/{filename}")
    else:
        print("Tipe PDF tidak diukur.")
        return

def detect_pdf_type_pdfplumber(pdf_path, threshold=0.5):
    """
    Mendeteksi apakah PDF berbasis Teks atau Gambar menggunakan pdfplumber.
    
    Args:
        pdf_path: Path ke file PDF.
        threshold: Batas persentase halaman berisi teks untuk dianggap 'text-based'.
                   Default 0.5 (50%).
    
    Returns:
        'text' jika mayoritas halaman berisi teks.
        'image' jika mayoritas halaman kosong dari segi teks (hasil scan/gambar).
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            text_pages_count = 0
            
            # Regex untuk mendeteksi karakter alfanumerik (huruf/angka)
            # Mengabaikan spasi, newline, atau karakter kontrol lainnya
            meaningful_pattern = re.compile(r'[a-zA-Z0-9]')
            
            print(f"Menganalisis {total_pages} halaman...")

            for i, page in enumerate(pdf.pages):
                # Ekstrak teks
                text = page.extract_text()
                
                # Cek 1: Jika extract_text mengembalikan None, berarti kosong
                if text is None:
                    continue
                
                # Cek 2: Cari apakah ada minimal satu huruf/angka di teks tersebut
                # Kadang PDF punya header/footer kosong yang terdeteksi sebagai string spasi
                if meaningful_pattern.search(text):
                    text_pages_count += 1
                    
        # Hitung rasio
        if total_pages == 0:
            return 'image'
            
        ratio = text_pages_count / total_pages
        
        print(f"Statistik: {text_pages_count} dari {total_pages} halaman mengandung teks berarti.")
        print(f"Rasio halaman teks: {ratio:.2f}")

        if ratio >= threshold:
            return 'text'
        else:
            return 'image'

    except Exception as e:
        print(f"Terjadi error saat membaca PDF: {e}")
        return 'error'
    
def extract_pdf_text(pdf_path):
    full_text = ""
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            
            if text:
                full_text += text + "\n" # newline antar halaman
    os.remove(pdf_path)
    return full_text


def extract_pdf_image(pdf_path):
    print("Sedang mengkonversi PDF ke Gambar...")

    # Cek apakah path Poppler valid
    if not os.path.exists(POPPLER_PATH):
        print(f"ERROR: Folder Poppler tidak ditemukan di: {POPPLER_PATH}")
        print("Silakan cek variabel POPPLER_PATH di kode.")
        return None
    
    # 1. Konversi PDF ke list of images (DPI 300 agar teks jelas)
    try:
        pages = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)
    except Exception as e:
        print(f"Gagal memproses PDF. Pastikan Poppler sudah diinstall & ada di PATH.")
        print(f"Error: {e}")
        return

    full_text = ""
    total_pages = len(pages)
    
    print(f"Memproses {total_pages} halaman dengan OCR...")

    # 2. Loop setiap halaman gambar
    for i, page in enumerate(pages):
        print(f"Memproses halaman {i+1}/{total_pages}...")
        
        # 3. Lakukan OCR
        # lang='ind+eng' artinya deteksi Bahasa Indonesia dan Inggris
        text = pytesseract.image_to_string(page, lang='ind+eng')
        
        full_text += f"\n--- Halaman {i+1} ---\n"
        full_text += text + "\n"

    os.remove(pdf_path)
    return full_text