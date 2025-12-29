"""
Nutrition Router
Endpoints для работы с планами питания
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import logging

from .airtable import AirtableService
from .meal_planner import MealPlannerService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/nutrition", tags=["Nutrition"])

# Инициализируем сервисы
airtable_service = AirtableService()
meal_planner = MealPlannerService(airtable_service)


class MealPlanCreateRequest(BaseModel):
    """Request для создания плана питания"""
    user_id: str
    week_start: str  # Format: "YYYY-MM-DD"
    plan_name: Optional[str] = None
    notes: Optional[str] = None


@router.post("/meal-plan/create", status_code=status.HTTP_201_CREATED)
async def create_meal_plan(request: MealPlanCreateRequest):
    """
    Создаёт план питания на неделю
    
    Returns:
        {
            "meal_plan_id": str,
            "plan_name": str,
            "week_start": str,
            "week_end": str,
            "total_meals": int,
            "avg_calories": float,
            "avg_protein": float,
            "status": "success"
        }
    """
    try:
        logger.info(f"Creating meal plan for user: {request.user_id}")
        
        # Парсим дату
        week_start = datetime.strptime(request.week_start, "%Y-%m-%d")
        
        # Создаём план через сервис
        result = meal_planner.create_weekly_meal_plan(
            user_id=request.user_id,
            week_start=week_start,
            plan_name=request.plan_name,
            notes=request.notes
        )
        
        logger.info(f"✅ Meal plan created: {result['meal_plan_id']}")
        
        return result
        
    except ValueError as e:
        logger.error(f"Invalid date format: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format. Use YYYY-MM-DD: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error creating meal plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create meal plan: {str(e)}"
        )


@router.get("/meal-plan/{plan_id}")
async def get_meal_plan(plan_id: str):
    """
    Получает информацию о плане питания
    """
    try:
        logger.info(f"Fetching meal plan: {plan_id}")
        
        # Получаем meal plan из Airtable
        meal_plan = airtable_service.get_record("Meal_Plans", plan_id)
        
        return {
            "meal_plan_id": plan_id,
            "fields": meal_plan.get("fields", {}),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error fetching meal plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch meal plan: {str(e)}"
        )
