from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from app.models.schemas import (
    MealPlanCreate,
    MealPlanResponse,
    ShoppingListCreate,
    ShoppingListResponse
)
from app.services.airtable import get_airtable_service, AirtableService
from app.services.meal_planner import MealPlannerService

router = APIRouter(prefix="/api/nutrition", tags=["nutrition"])

def get_meal_planner() -> MealPlannerService:
    """Dependency для получения meal planner service"""
    airtable = get_airtable_service()
    return MealPlannerService(airtable)

@router.post("/meal-plan/create", response_model=MealPlanResponse)
async def create_meal_plan(
    request: MealPlanCreate,
    planner: MealPlannerService = Depends(get_meal_planner)
):
    """
    Создать план питания на неделю
    
    Создаёт:
    - 1 запись в Meal_Plans
    - ~35 записей в Planned_Meals
    
    Возвращает статистику плана
    """
    try:
        result = planner.create_weekly_meal_plan(
            user_id=request.user_id,
            week_start=datetime.combine(request.week_start, datetime.min.time()),
            plan_name=request.plan_name,
            notes=request.notes
        )
        
        return MealPlanResponse(
            meal_plan_id=result["meal_plan_id"],
            plan_name=result["plan_name"],
            week_start=result["week_start"],
            week_end=result["week_end"],
            total_meals=result["total_meals"],
            avg_calories=result["avg_calories"],
            avg_protein=result["avg_protein"],
            status="success",
            message=f"План питания создан! {result['total_meals']} приёмов пищи добавлено."
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при создании плана: {str(e)}")

@router.get("/meal-plan/{plan_id}")
async def get_meal_plan(
    plan_id: str,
    airtable: AirtableService = Depends(get_airtable_service)
):
    """
    Получить план питания по ID
    """
    try:
        meal_plan = airtable.get_record("Meal_Plans", plan_id)
        
        # Получить все приёмы пищи для этого плана
        formula = f"{{Meal Plan}} = '{plan_id}'"
        planned_meals = airtable.get_all_records("Planned_Meals", formula=formula)
        
        return {
            "meal_plan": meal_plan,
            "planned_meals": planned_meals,
            "total_meals": len(planned_meals)
        }
    
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"План не найден: {str(e)}")

@router.post("/shopping-list/generate", response_model=ShoppingListResponse)
async def generate_shopping_list(
    request: ShoppingListCreate,
    airtable: AirtableService = Depends(get_airtable_service)
):
    """
    Сгенерировать список покупок для плана питания
    
    TODO: Реализовать логику генерации списка покупок
    """
    # Пока заглушка - реализуем позже
    return ShoppingListResponse(
        shopping_list_id="rec_placeholder",
        meal_plan_id=request.meal_plan_id,
        total_items=0,
        items=[],
        status="not_implemented",
        message="Shopping list generation coming soon!"
    )
