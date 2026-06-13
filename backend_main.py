
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import io

app = FastAPI()

# Разрешаем запросы с GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Укажи точный URL своего GitHub сайта для безопасности
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process")
async def process_file(file: UploadFile):
    content = await file.read()
    
    # --- ТУТ ТВОЯ ЛОГИКА ---
    # Пример: просто возвращаем файл обратно
    processed_content = content 
    # -----------------------
    
    return StreamingResponse(
        io.BytesIO(processed_content),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename=processed_{file.filename}"}
    )
