import torch
from transformers import AutoTokenizer
from quickhire_model import IndoBERTRanker
from global_ml_sys_config import MODEL_NAME, MAX_LEN, HIDDEN_DIM, DROPOUT
import json

def load_model(checkpoint_path):
    """
    Memuat model IndoBERTRanker dari checkpoint best.pt
    """
    # 1. Inisialisasi Model Kosong dengan Arsitektur yang Sama
    # Parameter HARUS SAMA dengan saat training (cek global_ml_sys_config.py)
    model = IndoBERTRanker(
        model_name=MODEL_NAME,
        hidden_dim=HIDDEN_DIM,
        dropout=DROPOUT,
        freeze_bert=False  # Set False karena kita hanya butuh forward pass, tidak update grad
    )
    
    # 2. Load Checkpoint
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    checkpoint = torch.load(checkpoint_path, map_location=device)
    
    # 3. Ekstrak State Dict Model (karena checkpoint berisi lebih dari sekadar bobot)
    model.load_state_dict(checkpoint['model_state_dict'])
    
    model.to(device)
    model.eval()  # Penting: set ke mode evaluasi
    
    return model, device

def predict_score(model, tokenizer, query, document, device):
    """
    Menghitung skor relevansi antara query dan document
    """
    # Tokenize pasangan Query-Document
    # Perhatikan: IndoBERTRanker mengharapkan input_ids dan attention_mask
    encoding = tokenizer(
        query,
        document,
        padding=True,
        truncation=True,
        max_length=MAX_LEN, # Gunakan MAX_LEN dari config (256)
        return_tensors="pt"
    )
    
    input_ids = encoding['input_ids'].to(device)
    attention_mask = encoding['attention_mask'].to(device)
    
    # Prediksi
    with torch.no_grad():
        score = model(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
    return score.item()

if __name__ == "__main__":
    # --- KONFIGURASI ---
    CHECKPOINT_PATH = "best.pt" # Pastikan file best.pt ada di folder ini
    
    # --- LOAD MODEL & TOKENIZER ---
    print("Loading model...")
    model, device = load_model(CHECKPOINT_PATH)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    print(f"Model loaded on {device}")
    
    # --- CONTOH DATA INPUT ---
    # Query: Lowongan Pekerjaan
    query = "Looking for a Full Stack Developer to develop end-to-end applications using React, Node.js, JavaScript, SQL, MongoDB, and Docker"
    
    # Document 1: CV yang Relevan
    doc_relevant = """
    [RESUME]
    john wilson full stack developer pacific avelos angeles ca united states place birth links profile employment history jan nov jan dec education jan nov san antenia driving license full twitter facebook experienced senior full stack developer years broad experience core fava kolin mabile development areas willing learn master front end development devopi app store seo specialist comprehensive undertanding uivux design javascript esg es areas willing leara master back end development well asweb servers ddminigration testing andddd tod expert full stack developer hsbc bank saint consgant responitble forthe wransition lamp sack mean stack reducing latency increasing database adniin fanctionadity maximized applications data quality efficiency scope flexibility operability weed various ideas distribuped computing real time dara processing dara storage large scale design mland aito solve dataset problems managed optimized updated php databases necessary developed app integration rest soap apis google maps payment processors social media logins services developed goal prioritization module toaid performance goals fusion erp using oracle adf agile methodology kept sole ownership modules security goal measurements eligibility profiles using jazn essand ee eradicated critical bugs within product maximize performance andaid customers needing togo live discussed analyzed planned product development design product managers ux team business managers carried prospective employee interviews mentored junior software developers junior full stack developer ashton telecoms south belair documented solution architecture forthe high volume dient facing partal decreasing thettm time market ensuring bigh code functionality creared full stack web applications analyzed processed rendered data visually communicated back front end developers quality assurance testers andcto sas required managed time sensitive updates including database upgrades content changes planned wrote debugged web applications software without mistakes created restful api endpoint using akka scala developed mobile web client consume theapi using angular html wrote several unit tests tests andapt rests implemented payment system using stripe included server push notifications using websocket protocols carried product research projects bachelor science software development champlain college burlington relevant coursework data engineering operating systems architecuure programming iiiweb page development linux unix programming usability software design relational database design sql advanced software programming
    """
    
    # Document 2: CV yang Tidak Relevan
    doc_irrelevant = """
    [RESUME]
    SUMMARY: Frontend Designer fokus pada UI/UX.
    SKILLS: Figma, Adobe XD, HTML, CSS, JavaScript.
    EXPERIENCE:
    TITLE: UI Designer
    RESPONSIBILITIES: Membuat desain mockup aplikasi mobile.
    """
    
    # --- PREDIKSI ---
    score_1 = predict_score(model, tokenizer, query, doc_relevant, device)
    score_2 = predict_score(model, tokenizer, query, doc_irrelevant, device)
    
    print("\n--- HASIL PREDIKSI ---")
    print(f"Query: {query[:50]}...")
    print(f"Score CV Relevan   : {score_1:.4f}")
    print(f"Score CV Irrelevan : {score_2:.4f}")
    
    if score_1 > score_2:
        print("✅ Model bekerja dengan baik! Skor relevan lebih tinggi.")
    else:
        print("️ Model mungkin perlu fine-tuning lebih lanjut.")