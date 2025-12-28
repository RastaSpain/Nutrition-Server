from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class MealPlanCreate(BaseModel):
    """Запрос на создание плана питания"""
    user_id: str = Field(..., description="ID пользователя в Airtable")
    week_start: date = Field(..., description="Начало недели (YYYY-MM-DD)")
    plan_name: Optional[str] = Field(None, description="Название плана")
    notes: Optional[str] = Field(None, description="Заметки")

class MealPlanResponse(BaseModel):
    """Ответ с созданным планом"""
    meal_plan_id: str
    plan_name: str
    week_start: str
    week_end: str
    total_meals: int
    avg_calories: float
    avg_protein: float
    status: str
    message: str

class ShoppingListCreate(BaseModel):
    """Запрос на создание списка покупок"""
    meal_plan_id: str = Field(..., description="ID плана питания")

class ShoppingListResponse(BaseModel):
    """Ответ со списком покупок"""
    shopping_list_id: str
    meal_plan_id: str
    total_items: int
    estimated_cost: Optional[float] = None
    items: List[dict]
    status: str
    message: str

class HealthResponse(BaseModel):
    """Health check ответ"""
    status: str
    version: str
    airtable_connected: bool
