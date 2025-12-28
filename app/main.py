from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.routers import health, nutrition

# Загрузить переменные окружения
load_dotenv()

# Создать FastAPI приложение
app = FastAPI(
    title="Nutrition Server API",
    description="Backend сервер для системы управления питанием",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (разрешаем запросы от n8n)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключить роутеры
app.include_router(health.router)
app.include_router(nutrition.router)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Выполняется при запуске сервера"""
    print("🚀 Nutrition Server starting...")
    print(f"📊 Airtable Base ID: {os.getenv('AIRTABLE_BASE_ID', 'appBgJb1hzG4vFT1b')}")
    print(f"✅ Server ready!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Выполняется при остановке сервера"""
    print("🛑 Nutrition Server shutting down...")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
