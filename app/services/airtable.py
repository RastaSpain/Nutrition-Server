from pyairtable import Api
from typing import List, Dict, Optional
import os

class AirtableService:
    """Сервис для работы с Airtable"""
    
    def __init__(self):
        self.api_key = os.getenv("AIRTABLE_API_KEY")
        self.base_id = os.getenv("AIRTABLE_BASE_ID", "appBgJb1hzG4vFT1b")
        
        if not self.api_key:
            raise ValueError("AIRTABLE_API_KEY не установлен в переменных окружения")
        
        self.api = Api(self.api_key)
        self.base = self.api.base(self.base_id)
    
    def get_table(self, table_name: str):
        """Получить таблицу"""
        return self.base.table(table_name)
    
    def create_record(self, table_name: str, fields: dict) -> dict:
        """Создать одну запись"""
        table = self.get_table(table_name)
        return table.create(fields)
    
    def create_records_batch(self, table_name: str, records: List[dict]) -> List[dict]:
        """Создать несколько записей (батчами по 10)"""
        table = self.get_table(table_name)
        results = []
        
        # Airtable API поддерживает батчи до 10 записей
        batch_size = 10
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            batch_results = table.batch_create(batch)
            results.extend(batch_results)
        
        return results
    
    def get_record(self, table_name: str, record_id: str) -> dict:
        """Получить запись по ID"""
        table = self.get_table(table_name)
        return table.get(record_id)
    
    def get_all_records(self, table_name: str, formula: Optional[str] = None) -> List[dict]:
        """Получить все записи из таблицы"""
        table = self.get_table(table_name)
        if formula:
            return table.all(formula=formula)
        return table.all()
    
    def update_record(self, table_name: str, record_id: str, fields: dict) -> dict:
        """Обновить запись"""
        table = self.get_table(table_name)
        return table.update(record_id, fields)
    
    def test_connection(self) -> bool:
        """Проверить подключение к Airtable"""
        try:
            # Пробуем получить одну запись из таблицы Recipes
            table = self.get_table("Recipes")
            table.first()
            return True
        except Exception as e:
            print(f"Ошибка подключения к Airtable: {e}")
            return False

# Глобальный экземпляр сервиса
airtable_service = None

def get_airtable_service() -> AirtableService:
    """Получить экземпляр сервиса Airtable (singleton)"""
    global airtable_service
    if airtable_service is None:
        airtable_service = AirtableService()
    return airtable_service
