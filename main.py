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
from deep_translator import GoogleTranslator  # Добавили импорт

# [Оставляем весь код с SSL и настройками как был...]
# ... (код загрузки cefr_dict остается без изменений)

def extract_unique_words(content):
    # [Оставляем логику pysubs2 и spacy как была...]
    # ...
    
    final_list = []
    translator = GoogleTranslator(source='en', target='ru') # Инициализируем переводчик
    
    for base, variants in lemma_map.items():
        variants_str = ", ".join(sorted(list(variants)))
        pos, level = cefr_dict.get(base, ("N/A", "Unknown"))
        
        # Переводим слово (добавляем try-except на случай проблем с сетью)
        try:
            translation = translator.translate(base)
        except:
            translation = "Error"
            
        # Записываем: Слово;Формы;Часть речи;Уровень;Перевод
        final_list.append(f"{base};{variants_str};{pos};{level};{translation}")
            
    return sorted(final_list)

@app.post("/process")
async def process_file(file: UploadFile):
    content = await file.read()
    words_list = extract_unique_words(content)
    
    # Обновленный заголовок
    header = "Слово;Формы;Часть речи;Уровень;Перевод\n"
    csv_content = header + "\n".join(words_list)
    
    return StreamingResponse(
        io.BytesIO(csv_content.encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=words_pro_translated.csv"}
    )
