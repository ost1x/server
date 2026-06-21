import nltk
import ssl
import io
import pysubs2
import spacy
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from nltk.corpus import stopwords

# Блок для SSL
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('stopwords')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

nlp = spacy.load("en_core_web_sm")
stop_words = set(stopwords.words('english'))
stop_words.update(['hmm', 'uh', 'oh', 'mm', 'ah', 'na', 'huh', 'em'])

def extract_unique_words(content):
    with open("temp.srt", "w", encoding="utf-8") as f:
        f.write(content.decode('utf-8'))
    
    subs = pysubs2.load("temp.srt")
    full_text = " ".join([sub.text for sub in subs])
    
    doc = nlp(full_text)
    
    # Словарь для лемматизации
    lemma_map = {}
    
    for token in doc:
        is_proper_noun = (token.pos_ == "PROPN")
        is_capitalized = token.text[0].isupper() and not token.is_sent_start
        
        if not is_proper_noun and not is_capitalized and len(token.text) > 2 and token.text.lower() not in stop_words and token.is_alpha:
            
            base_form = token.lemma_.lower()
            original_form = token.text.lower()
            
            if base_form not in lemma_map:
                lemma_map[base_form] = set()
            
            if original_form != base_form:
                lemma_map[base_form].add(original_form)

    # Формируем список
    final_list = []
    for base, variants in lemma_map.items():
        if variants:
            variants_str = ", ".join(sorted(list(variants)))
            final_list.append(f"{base} ({variants_str})")
        else:
            final_list.append(base)
            
    return sorted(final_list)

@app.post("/process")
async def process_file(file: UploadFile):
    content = await file.read()
    words_list = extract_unique_words(content)
    
    # Добавляем заголовок таблицы
    header = "Слово (формы)\n"
    csv_content = header + "\n".join(words_list)
    
    return StreamingResponse(
        io.BytesIO(csv_content.encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=words.csv"}
    )
