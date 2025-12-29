"""
Shopping List Router
Endpoints для работы со списками покупок
"""
from fastapi import APIRouter, HTTPException, status
from app.models.shopping_list_schemas import (
    ShoppingListGenerateRequest,
    ShoppingListResponse,
    ShoppingListDetailResponse
)
from app.services.shopping_list import ShoppingListService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/nutrition/shopping-list", tags=["Shopping List"])


@router.post("/generate", response_model=ShoppingListResponse, status_code=status.HTTP_201_CREATED)
async def generate_shopping_list(request: ShoppingListGenerateRequest):
    """
    Генерирует список покупок на основе плана питания
    
    ## Процесс:
    1. Получает план питания и все запланированные приёмы пищи
    2. Извлекает все рецепты из плана
    3. Собирает ингредиенты из всех рецептов с учётом порций
    4. Агрегирует одинаковые ингредиенты (суммирует количество)
    5. Создаёт Shopping List и Shopping List Items в Airtable
    
    ## Пример:
    ```json
    {
      "meal_plan_id": "recnd7GzJqTkiBTWa",
      "shopping_date": "2024-12-30"
    }
    ```
    
    ## Response:
    - `shopping_list_id`: ID созданного списка покупок
    - `items_count`: Количество уникальных ингредиентов
    - `total_recipes`: Количество уникальных рецептов в плане
    - `total_meals`: Общее количество запланированных приёмов пищи
    """
    try:
        logger.info(f"Generating shopping list for meal plan: {request.meal_plan_id}")
        
        service = ShoppingListService()
        result = service.generate_shopping_list(
            meal_plan_id=request.meal_plan_id,
            shopping_date=request.shopping_date
        )
        
        logger.info(f"Shopping list generated: {result['shopping_list_id']} with {result['items_count']} items")
        
        return ShoppingListResponse(**result)
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating shopping list: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate shopping list: {str(e)}"
        )


@router.get("/{shopping_list_id}", response_model=ShoppingListDetailResponse)
async def get_shopping_list(shopping_list_id: str):
    """
    Получает детальную информацию о списке покупок
    
    ## Parameters:
    - `shopping_list_id`: ID списка покупок в Airtable
    
    ## Response:
    Возвращает информацию о списке и все элементы (items)
    """
    try:
        logger.info(f"Fetching shopping list: {shopping_list_id}")
        
        service = ShoppingListService()
        result = service.get_shopping_list(shopping_list_id)
        
        shopping_list = result['shopping_list']['fields']
        
        return ShoppingListDetailResponse(
            shopping_list_id=shopping_list_id,
            list_name=shopping_list.get('List Name', ''),
            status=shopping_list.get('Status', ''),
            shopping_date=shopping_list.get('Shopping Date'),
            total_cost=shopping_list.get('Total Cost (EUR)'),
            items_count=result['items_count'],
            items=result['items']
        )
        
    except Exception as e:
        logger.error(f"Error fetching shopping list: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch shopping list: {str(e)}"
        )


@router.delete("/{shopping_list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_list(shopping_list_id: str):
    """
    Удаляет список покупок и все его элементы
    
    ## Parameters:
    - `shopping_list_id`: ID списка покупок в Airtable
    """
    try:
        logger.info(f"Deleting shopping list: {shopping_list_id}")
        
        service = ShoppingListService()
        # TODO: Implement delete logic
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Delete functionality not implemented yet"
        )
        
    except Exception as e:
        logger.error(f"Error deleting shopping list: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete shopping list: {str(e)}"
        )
