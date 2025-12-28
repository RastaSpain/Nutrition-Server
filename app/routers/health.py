from fastapi import APIRouter, Depends
from app.models.schemas import HealthResponse
from app.services.airtable import get_airtable_service, AirtableService

router = APIRouter(tags=["health"])

@router.get("/health", response_model=HealthResponse)
async def health_check(airtable: AirtableService = Depends(get_airtable_service)):
    """
    Health check endpoint
    
    Проверяет:
    - Сервер работает
    - Подключение к Airtable OK
    """
    airtable_connected = airtable.test_connection()
    
    return HealthResponse(
        status="healthy" if airtable_connected else "degraded",
        version="1.0.0",
        airtable_connected=airtable_connected
    )

@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Nutrition Server",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "meal_plan_create": "POST /api/nutrition/meal-plan/create",
            "meal_plan_get": "GET /api/nutrition/meal-plan/{plan_id}",
            "shopping_list": "POST /api/nutrition/shopping-list/generate"
        }
    }
