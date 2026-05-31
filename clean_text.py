import re
from sentence_transformers import SentenceTransformer
from pythainlp import word_tokenize
import numpy as np

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
tokenizer = model.tokenizer
def cleaning(text):
    clean_teks = clean_cv_text_with_pythainlp(text)
    return [inspect_tokens(clean_teks), get_embedding(clean_teks)]
def clean_text(raw_text: str) -> str:
    """
    Membersihkan teks mentah dari noise dasar.
    Biarkan Tokenizer Hugging Face mengurus tokenization & konteks.
    """
    if not raw_text or len(raw_text.strip()) < 50:
        return ""

    # 1. Hapus Email
    text = re.sub(r'\S+@\S+', ' ', raw_text)
    
    # 2. Hapus URL
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    
    # 3. Hapus Nomor Telepon (10-15 digit)
    text = re.sub(r'\b\d{10,15}\b', ' ', text)
    
    # 4. Hapus karakter aneh, TAPI simpan simbol tech penting (+, #, ., -)
    # Contoh: C++, Node.js, .NET
    text = re.sub(r'[^a-zA-Z0-9\s+#.\-]', ' ', text)
    
    # 5. Normalisasi spasi (hapus newline ganda, tab, dll)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def fix_ocr_fragmentation(text: str) -> str:
    """
    Mencoba menggabungkan kembali kata-kata yang terpotong oleh OCR.
    Contoh: 'J U L I' -> 'JULI', 'PROFES I ONAL' -> 'PROFESIONAL'
    """
    if not text:
        return ""
    
    # Langkah 1: Gabungkan huruf tunggal yang terpisah spasi (Heuristic)
    # Ini sangat efektif untuk nama atau inisial yang hancur total
    # Pola: Huruf kapital/kecil tunggal diikuti spasi dan huruf lagi
    text = re.sub(r'\b([A-Za-z])\s+([A-Za-z])\b', r'\1\2', text)
    
    # Ulangi beberapa kali untuk menangkap rantai panjang (P R O F E S...)
    for _ in range(5):
        text = re.sub(r'\b([A-Za-z]{1,2})\s+([A-Za-z]{1,2})\b', 
                      lambda m: m.group(1)+m.group(2) if len(m.group(1)+m.group(2)) <= 10 else m.group(0), 
                      text)

    return text

def clean_cv_text_with_pythainlp(raw_text: str) -> str:
    """
    Pipeline cleaning lengkap dengan bantuan PyThaiNLP
    """
    if not raw_text or len(raw_text.strip()) < 50:
        return ""

    # 1. Fix Fragmentasi OCR (Huruf terpisah)
    text = fix_ocr_fragmentation(raw_text)
    
    # 2. Hapus Noise Kasar (Email, URL, No HP, Footer Web)
    text = re.sub(r'\S+@\S+', ' ', text)
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    text = re.sub(r'\+?\d[\d\s\-]{9,}\d', ' ', text)
    text = re.sub(r'really great site\.com|hellII tsi te ero', ' ', text, flags=re.IGNORECASE)
    
    # 3. Normalisasi Spasi & Lowercase
    text = re.sub(r'\s+', ' ', text).strip().lower()
    
    # 4. (Opsional) Gunakan PyThaiNLP Word Tokenize untuk validasi
    # Kita tokenize teks, lalu gabungkan lagi. Ini membantu menghilangkan 
    # spasi aneh di tengah kata yang tidak dikenali kamus.
    # Catatan: Ini bisa lambat untuk teks sangat panjang.
    try:
        tokens = word_tokenize(text, engine='newmm') # newmm adalah engine default yang cukup cepat
        # Filter token yang terlalu pendek atau hanya angka/simbol
        filtered_tokens = [t for t in tokens if len(t) > 1 and not t.isdigit()]
        text = " ".join(filtered_tokens)
    except Exception as e:
        print(f"PyThaiNLP Error: {e}")
        # Fallback ke teks biasa jika error
        
    return text

def inspect_tokens(text: str):
    """
    Fungsi untuk melihat bagaimana teks dipecah menjadi token.
    """
    if not text:
        return {"tokens": [], "ids": []}

    # Tokenize teks
    # return_tensors="pt" mengembalikan PyTorch tensor, tapi kita butuh list biasa untuk debug
    encoded_input = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
    
    # Ambil ID token
    token_ids = encoded_input['input_ids'][0].tolist()
    
    # Konversi ID token kembali menjadi kata/string agar mudah dibaca manusia
    tokens_text = [tokenizer.decode([t]) for t in token_ids]
    
    return {
        "tokens_readable": tokens_text
    }

def get_embedding(text: str) -> np.ndarray:
    """
    Mengubah teks bersih menjadi vektor numerik.
    """
    if not text:
        return np.zeros(384) # Ukuran vektor model MiniLM adalah 384
    
    # Encode teks menjadi vektor
    embedding = model.encode([text])
    return embedding[0]