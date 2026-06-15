from ekstraksi_pdf import ekstraksi_pdf_cv
from text_processor import clean_cv_text
from predict_raw_cv import load_model, predict_relevance
import torch
from transformers import AutoTokenizer
from preprocess import TextStructurer
from global_ml_sys_config import MODEL_NAME
def processing_file (file, job_desc):
    text = ekstraksi_pdf_cv(file, file.filename)
    clean_cv = clean_cv_text(text)
     # --- KONFIGURASI ---
    CHECKPOINT_PATH = "best.pt"
    
    # --- LOAD SYSTEM ---
    print("Initializing System...")
    model, device = load_model(CHECKPOINT_PATH)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    structurer = TextStructurer() # Inisialisasi alat preprocessing bawaan
    print(f"System ready on {device}")
    score, job_struct, cv_struct = predict_relevance(model, tokenizer, structurer, job_desc, clean_cv, device)
    print(f"Score: {score}")
    print(f"Job Description: {job_struct}")
    print(f"CV: {cv_struct}")
    return score, job_struct, cv_struct, file.filename