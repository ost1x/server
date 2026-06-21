import nltk
import ssl
import io
import pysubs2
import spacy
import csv
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from nltk.corpus import stopwords
from deep_translator import GoogleTranslator

# ... (SSL, nlp, cefr_dict загрузка остаются как были)

def extract_unique_words(content):
    # [Логика с pysubs2 и lemmatizer та же]
    # ... (получаем lemma_map)

    final_list = []
    keys = list(lemma_map.keys())
    
    # ПАКЕТНЫЙ ПЕРЕВОД (по 50 слов за раз)
    translations = []
    translator = GoogleTranslator(source='en', target='ru')
    
    for i in range(0, len(keys), 50):
        batch = keys[i:i+50]
        try:
            # Переводим сразу пачку
            translations.extend(translator.translate_batch(batch))
        except:
            translations.extend(["Error"] * len(batch))

    # Сборка данных
    for i, base in enumerate(keys):
        variants_str = ", ".join(sorted(list(lemma_map[base])))
        pos, level = cefr_dict.get(base, ("N/A", "Unknown"))
        translation = translations[i] if i < len(translations) else "Error"
        
        final_list.append(f"{base};{variants_str};{pos};{level};{translation}")
            
    return sorted(final_list)

@app.post("/process")
async def process_file(file: UploadFile):
    content = await file.read()
    words_list = extract_unique_words(content)
    header = "Слово;Формы;Часть речи;Уровень;Перевод\n"
    csv_content = header + "\n".join(words_list)
    
    return StreamingResponse(
        io.BytesIO(csv_content.encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=final_vocabulary.csv"}
    )
