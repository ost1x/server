import nltk
import ssl
import io
import pysubs2
import spacy
import csv
import time
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from nltk.corpus import stopwords
from deep_translator import GoogleTranslator # 1. Добавили импорт

# Блок SSL
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('stopwords')

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# 2. Инициализируем переводчик один раз
translator = GoogleTranslator(source='en', target='ru')

nlp = spacy.load("en_core_web_sm")
stop_words = set(stopwords.words('english'))
stop_words.update(['hmm', 'uh', 'oh', 'mm', 'ah', 'na', 'huh', 'em'])

# Загрузка словаря
cefr_dict = {}
try:
    with open("oxford-5000.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None) 
        for row in reader:
            if len(row) >= 3:
                cefr_dict[row[0].strip().lower()] = (row[1].strip(), row[2].strip())
except Exception as e:
    print(f"Ошибка загрузки словаря: {e}")

def extract_unique_words(content):
    with open("temp.srt", "w", encoding="utf-8") as f:
        f.write(content.decode('utf-8'))
    
    subs = pysubs2.load("temp.srt")
    full_text = " ".join([sub.text for sub in subs])
    doc = nlp(full_text)
    
    lemma_map = {}
    for token in doc:
        if not token.is_punct and token.is_alpha and len(token.text) > 2 and token.text.lower() not in stop_words:
            if token.pos_ != "PROPN" and not (token.text[0].isupper() and not token.is_sent_start):
                base = token.lemma_.lower()
                orig = token.text.lower()
                if base not in lemma_map: lemma_map[base] = set()
                if orig != base: lemma_map[base].add(orig)

    final_list = []
    for base, variants in lemma_map.items():
        variants_str = ", ".join(sorted(list(variants)))
        pos, level = cefr_dict.get(base, ("N/A", "Unknown"))
        
        # 3. Перевод слова с обработкой ошибок
        try:
            translation = translator.translate(base)
            time.sleep(0.05) # Небольшая пауза, чтобы не получить бан от Google
        except:
            translation = "Error"
        
        # 4. Добавили translation в строку
        final_list.append(f"{base};{variants_str};{pos};{level};{translation}")
            
    return sorted(final_list)

@app.post("/process")
async def process_file(file: UploadFile):
    content = await file.read()
    words_list = extract_unique_words(content)
    
    # 5. Обновили заголовок
    header = "Слово;Формы;Часть речи;Уровень;Перевод\n"
    csv_content = header + "\n".join(words_list)
    
    return StreamingResponse(
        io.BytesIO(csv_content.encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=words_pro.csv"}
    )
