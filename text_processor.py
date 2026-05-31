import re
import numpy as np
from sentence_transformers import SentenceTransformer
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from pythainlp import word_tokenize
from nltk.corpus import stopwords

# 1. LOAD MODEL SEKALI SAJA (Global Scope)
# Jangan load model di dalam fungsi cleaning!
print("🔄 Loading NLP Model & Tokenizer...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
tokenizer = model.tokenizer
factory = StopWordRemoverFactory()
stopword_list = factory.get_stop_words() # Ini akan return list berisi 750+ kata Indonesia

# Konversi ke SET agar pencarian lebih cepat (O(1))
STOPWORDS_ID = set(stopword_list)

try:
    stopwords_en = set(stopwords.words('english'))
except:
    # Fallback jika nltk data belum didownload
    stopwords_en = set() 

# Tambahkan custom stopwords jika perlu (misal istilah teknis yang umum tapi tidak penting)
CUSTOM_STOPWORDS = {"bertanggung", "jawab", "melakukan", "mengelola", "membuat", "menyusun", "membantu", "bekerja", "mencapai", "meningkatkan", "mengembangkan", 
    "memimpin", "melaksanakan", "terlibat", "menangani", "menjalankan", "memberikan",
    "cv", "resume", "nama", "alamat", "telepon", "email", "lahir", "tanggal", 
    "status", "ringkasan", "profil", "biodata", "kontak", "no", "hp", "linkedin", 
    "github", "website", "portofolio", "jenis", "kelamin", "warga", "negara", 
    "agama", "menikah", "pengalaman", "kerja", "pendidikan", "riwayat", "pelatihan", "sertifikasi", 
    "keahlian", "keterampilan", "bahasa", "referensi", "hobi", "minat", 
    "organisasi", "akademik", "jurusan", "universitas", "sekolah", "fakultas", 
    "gelar", "sarjana", "kuliah", "kursus", "mampu", "bersedia", "profesional", "tinggi", "baik", "sangat", "ahli", 
    "mahir", "kompeten", "sukses", "aktif", "kuat", "memiliki", "dapat", 
    "bisa", "biasa", "andal", "kreatif", "motivasi", "disiplin", 
    "bertanggungjawab", "cepat", "pelajari", "fleksibel", "tahun", "bulan", "hari", "januari", "februari", "maret", "april", "mei", 
    "juni", "juli", "agustus", "september", "oktober", "november", "desember", 
    "sekarang", "saat", "ini", "present", "current", "indonesia", "jakarta", 
    "kota", "provinsi", "wilayah", "saya", "kami", "anda", "beliau", "dengan", "untuk", "yang", "adalah", 
    "sebagai", "dalam", "pada", "oleh", "secara", "serta", "phone", "contact", "address", "halaman"}
STOPWORDS_ID.update(CUSTOM_STOPWORDS)
STOPWORDS_ID.update(stopwords_en)
print("✅ Model Ready.")

def merge_short_tokens(text: str) -> str:
    """
    Menggabungkan kata-kata pendek (<4 huruf) yang berdekatan.
    Solusi untuk: 'be kal' -> 'bekal', 'fa u get' -> 'fauget'
    """
    words = text.split()
    merged_words = []
    i = 0
    
    while i < len(words):
        current_word = words[i]
        
        # Cek apakah kata saat ini pendek dan murni alfabet
        if len(current_word) < 4 and current_word.isalpha():
            # Coba gabung dengan kata berikutnya
            if i + 1 < len(words):
                next_word = words[i+1]
                if len(next_word) < 4 and next_word.isalpha():
                    merged = current_word + next_word
                    
                    # Cek lagi dengan kata ke-3 jika masih pendek
                    if len(merged) < 5 and i + 2 < len(words):
                        third_word = words[i+2]
                        if len(third_word) < 4 and third_word.isalpha():
                            merged += third_word
                            i += 3
                            merged_words.append(merged)
                            continue
                    
                    i += 2
                    merged_words.append(merged)
                    continue
        
        merged_words.append(current_word)
        i += 1
        
    return " ".join(merged_words)

def fix_ocr_fragmentation(text: str) -> str:
    """
    Menggabungkan huruf tunggal yang terpisah spasi (J U L I -> JULI).
    """
    if not text:
        return ""
    
    # Gabung huruf tunggal
    text = re.sub(r'\b([A-Za-z])\s+([A-Za-z])\b', r'\1\2', text)
    
    # Gabung pasangan huruf pendek (iteratif untuk rantai panjang)
    for _ in range(5):
        text = re.sub(r'\b([A-Za-z]{1,2})\s+([A-Za-z]{1,2})\b', 
                      lambda m: m.group(1)+m.group(2), text)
                      
    return text

def clean_cv_text(raw_text: str) -> str:
    """
    Pipeline Utama Cleaning Text untuk CV OCR.
    """
    if not raw_text or len(raw_text.strip()) < 50:
        return ""

    # Step 1: Fix Fragmentasi Huruf Tunggal (J U L I -> JULI)
    text = fix_ocr_fragmentation(raw_text)
    
    # Step 2: Hapus Noise Spesifik (Email, URL, No HP, Footer Web)
    text = re.sub(r'\S+@\S+', ' ', text)          # Email
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text) # URL
    text = re.sub(r'\+?\d[\d\s\-]{9,}\d', ' ', text)   # No HP
    text = re.sub(r'really great site\.com|hellII tsi te ero', ' ', text, flags=re.IGNORECASE)
    
    # Step 3: Normalisasi Dasar
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text) # Buang simbol aneh
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Step 4: Merge Short Tokens (be kal -> bekal)
    text = merge_short_tokens(text)
    
    # Step 5: PyThaiNLP Tokenize (Opsional, untuk validasi akhir)
    # Hanya lakukan jika teks tidak terlalu panjang agar tidak lambat
    try:
        if len(text.split()) < 1000: 
            tokens = word_tokenize(text, engine='newmm')
            # Buang token 1 huruf dan angka murni
            filtered = [t for t in tokens if len(t) > 1 and not t.isdigit()]
            text = " ".join(filtered)
    except Exception:
        pass # Fallback ke text biasa jika error
        
    # Step 6: stopword dengan Sastrawi
    tokens = text.split()
    filtered_tokens = [w for w in tokens if w not in STOPWORDS_ID and len(w) > 1]
    text = " ".join(filtered_tokens)
    return text

def inspect_tokens(text: str):
    """
    Debugging: Melihat token yang dihasilkan model.
    """
    if not text:
        return []
    encoded_input = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
    token_ids = encoded_input['input_ids'][0].tolist()
    return [tokenizer.decode([t]) for t in token_ids]

def get_embedding(text: str) -> np.ndarray:
    """
    Mengubah teks menjadi vektor.
    """
    if not text:
        return np.zeros(384)
    return model.encode([text])[0]