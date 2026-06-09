from ekstraksi_pdf import ekstraksi_pdf_cv
from text_processor import clean_cv_text, get_embedding, inspect_tokens
def processing_file (file):
    text = ekstraksi_pdf_cv(file, file.filename)
    clean_cv = clean_cv_text(text)
    vec_cv = get_embedding(clean_cv)
    token = inspect_tokens(clean_cv)
    return token, vec_cv, clean_cv, file.filename