import nltk
import ssl

# Блок для SSL (чтобы nltk мог качать данные)
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('stopwords')

from fastapi import FastAPI, UploadFile
import pysubs2
import spacy
from nltk.corpus import stopwords
import io

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Загружаем ресурсы
nlp = spacy.load("en_core_web_sm")
stop_words = set(stopwords.words('english'))

def extract_unique_words(content):
    with open("temp.srt", "w", encoding="utf-8") as f:
        f.write(content.decode('utf-8'))
    
    subs = pysubs2.load("temp.srt")
    full_text = " ".join([sub.text for sub in subs])
    
    doc = nlp(full_text)
    unique_words = set()
    
    for token in doc:
        if token.ent_type_ != "PERSON" and token.text.lower() not in stop_words and token.is_alpha:
            unique_words.add(token.text.lower())
            
    return list(unique_words)

@app.post("/process")
async def process_file(file: UploadFile):
    content = await file.read()
    words_list = extract_unique_words(content)
    return {"unique_words": words_list}
