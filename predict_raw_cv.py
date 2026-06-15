import torch
from quickhire_model import IndoBERTRanker
from global_ml_sys_config import MODEL_NAME, MAX_LEN, HIDDEN_DIM, DROPOUT
import re

def load_model(checkpoint_path="best.pt"):
    """Load model IndoBERTRanker dari checkpoint best.pt"""
    print("Loading Model Architecture...")
    
    # Inisialisasi arsitektur model kosong
    model = IndoBERTRanker(
        model_name=MODEL_NAME,
        hidden_dim=HIDDEN_DIM,
        dropout=DROPOUT,
        freeze_bert=False # Set False karena kita hanya butuh forward pass
    )
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Load checkpoint
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    
    # Ekstrak bobot model saja (karena checkpoint berisi optimizer state juga)
    model.load_state_dict(checkpoint['model_state_dict'])
    
    model.to(device)
    model.eval() # Penting: set ke mode evaluasi
    
    return model, device

def clean_raw_text(raw_text):
    """
    Fungsi bantuan sederhana untuk membersihkan noise dasar 
    dari hasil ekstraksi PDF sebelum diproses oleh TextStructurer.
    """
    # Ganti newline berlebihan dengan spasi
    text = re.sub(r'\n+', ' ', raw_text)
    # Pastikan ada spasi setelah tanda baca jika menempel dengan huruf
    text = re.sub(r'([.,!?])([A-Za-z])', r'\1 \2', text)
    return text.strip()

def predict_relevance(model, tokenizer, structurer, job_desc_raw, cv_raw, device):
    """
    Menghitung skor relevansi antara Job Desc dan CV Mentah
    Menggunakan TextStructurer bawaan dari preprocess.py
    """
    # 1. Bersihkan CV Mentah (opsional, tapi disarankan untuk hasil ekstraksi PDF yang kotor)
    cleaned_cv = clean_raw_text(cv_raw)
    
    # 2. STRUKTURKAN CV menggunakan fungsi BAWAAN preprocess.py
    # Ini mengubah teks berantakan menjadi format: [RESUME] TITLE:... SKILLS:...
    structured_cv = structurer.structure_resume(cleaned_cv)
    
    # 3. Strukturkan Job Desc (Query)
    structured_job = structurer.structure_job(job_desc_raw)
    
    # 4. Tokenize Pasangan Query-Document yang Sudah Terstruktur
    encoding = tokenizer(
        structured_job,
        structured_cv,
        padding=True,
        truncation=True,
        max_length=MAX_LEN, # Gunakan MAX_LEN dari config (256)
        return_tensors="pt"
    )
    
    input_ids = encoding['input_ids'].to(device)
    attention_mask = encoding['attention_mask'].to(device)
    
    # 5. Prediksi Skor
    with torch.no_grad():
        score = model(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
    return score.item(), structured_job, structured_cv

