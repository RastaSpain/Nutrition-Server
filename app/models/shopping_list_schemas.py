"""
Pydantic Models for Shopping List API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class ShoppingListGenerateRequest(BaseModel):
    """Request для генерации списка покупок"""
    meal_plan_id: str = Field(..., description="ID плана питания в Airtable")
    shopping_date: Optional[str] = Field(None, description="Дата покупок (YYYY-MM-DD)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "meal_plan_id": "recnd7GzJqTkiBTWa",
                "shopping_date": "2024-12-30"
            }
        }


class ShoppingListItem(BaseModel):
    """Элемент списка покупок"""
    id: str
    item_name: str
    ingredient_id: str
    quantity: float
    unit: str
    purchased: bool
    price: Optional[float] = None


class ShoppingListResponse(BaseModel):
    """Response при генерации списка покупок"""
    shopping_list_id: str
    meal_plan_id: str
    items_count: int
    total_recipes: int
    total_meals: int
    message: str = "Shopping list generated successfully"
    
    class Config:
        json_schema_extra = {
            "example": {
                "shopping_list_id": "rec123456789",
                "meal_plan_id": "recnd7GzJqTkiBTWa",
                "items_count": 15,
                "total_recipes": 20,
                "total_meals": 35,
                "message": "Shopping list generated successfully"
            }
        }


class ShoppingListDetailResponse(BaseModel):
    """Детальная информация о списке покупок"""
    shopping_list_id: str
    list_name: str
    status: str
    shopping_date: Optional[str]
    total_cost: Optional[float]
    items_count: int
    items: List[dict]
