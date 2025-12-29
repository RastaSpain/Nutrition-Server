"""
Health Check Router
"""
from fastapi import APIRouter, HTTPException
from pyairtable import Api
import os

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    Проверяет работу сервера и подключение к Airtable
    """
    try:
        # Проверка Airtable connection
        api_key = os.getenv('AIRTABLE_API_KEY')
        if not api_key:
            return {
                "status": "unhealthy",
                "airtable_connection": "error - no API key",
                "error": "AIRTABLE_API_KEY not set"
            }
        
        api = Api(api_key)
        base_id = 'appBgJb1hzG4vFT1b'
        
        # Пробуем получить список таблиц
        try:
            table = api.table(base_id, 'tblgge1WnUvQSnMCh')  # Recipes table
            # Пробуем получить одну запись
            recipes = table.all(max_records=1)
            
            return {
                "status": "healthy",
                "airtable_connection": "ok",
                "base_accessible": True,
                "recipes_count": len(recipes)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "airtable_connection": "error",
                "error": str(e)
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
