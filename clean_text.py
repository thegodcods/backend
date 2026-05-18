import re
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
tokenizer = model.tokenizer
def cleaning(text):
    clean_teks = clean_text(text)
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
        "original_text": text[:100] + "...", # Preview teks asli
        "token_count": len(token_ids),
        "tokens_readable": tokens_text,
        "token_ids": token_ids
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