"""
Nutrition Router
Endpoints для работы с планами питания
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/nutrition", tags=["Nutrition"])


class MealPlanCreateRequest(BaseModel):
    """Request для создания плана питания"""
    user_id: str
    week_start: str
    plan_name: Optional[str] = None


@router.post("/meal-plan/create", status_code=status.HTTP_201_CREATED)
async def create_meal_plan(request: MealPlanCreateRequest):
    """
    Создаёт план питания на неделю
    
    NOTE: Этот endpoint был реализован ранее в meal_planner.py
    Здесь упрощённая версия для тестирования
    """
    try:
        logger.info(f"Creating meal plan for user: {request.user_id}")
        
        # TODO: Implement full meal plan creation logic
        # See meal_planner.py service for full implementation
        
        return {
            "message": "Meal plan creation endpoint",
            "user_id": request.user_id,
            "week_start": request.week_start,
            "note": "Full implementation in meal_planner.py service"
        }
        
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
        
        # TODO: Implement get meal plan logic
        
        return {
            "message": "Get meal plan endpoint",
            "plan_id": plan_id
        }
        
    except Exception as e:
        logger.error(f"Error fetching meal plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch meal plan: {str(e)}"
        )
