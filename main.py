import nltk
import ssl
import io
import pysubs2
import spacy
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from nltk.corpus import stopwords

# Блок для SSL (чтобы nltk мог качать данные)
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('stopwords')

app = FastAPI()

# Настройка CORS, чтобы сайт мог общаться с сервером
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Загружаем ресурсы
nlp = spacy.load("en_core_web_sm")
stop_words = set(stopwords.words('english'))
stop_words.update(['mmm', 'uh', 'na', 'oh', 'ah', 'yeah'])

def extract_unique_words(content):
    with open("temp.srt", "w", encoding="utf-8") as f:
        f.write(content.decode('utf-8'))
    
    subs = pysubs2.load("temp.srt")
    full_text = " ".join([sub.text for sub in subs])
    
    doc = nlp(full_text)
    unique_words = set()
    
    for token in doc:
        # Убираем все имена собственные через spacy (PROPN)
        is_proper_noun = (token.pos_ == "PROPN")
        
        # ДОПОЛНИТЕЛЬНО: если слово начинается с большой буквы, 
        # но при этом оно не стоит в начале предложения (как "I" или первое слово), 
        # считаем его именем.
        is_capitalized = token.text[0].isupper() and not token.is_sent_start
        
        if not is_proper_noun and not is_capitalized and token.text.lower() not in stop_words and token.is_alpha:
            unique_words.add(token.text.lower())
            
    return list(unique_words)

@app.post("/process")
async def process_file(file: UploadFile):
    content = await file.read()
    words_list = extract_unique_words(content)
    
    # Превращаем список в CSV-строку (слова в столбик)
    csv_content = "\n".join(words_list)
    
    # Отдаем как файл
    return StreamingResponse(
        io.BytesIO(csv_content.encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=words.csv"}
    )
