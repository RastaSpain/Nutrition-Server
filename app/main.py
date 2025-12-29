"""
Nutrition Management System - FastAPI Server
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import nutrition_router, shopping_list_router
from app.routers.health import router as health_router
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title="Nutrition Management System API",
    description="API for managing meal plans, recipes, and shopping lists for camper living",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(health_router)
app.include_router(nutrition_router.router)
app.include_router(shopping_list_router.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Nutrition Management System API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
