from typing import Dict, Optional
from sqlalchemy.orm import Session
from src.database.database import get_session
from .user_service import UserService
from .expense_service import ExpenseService
from .inventory_service import InventoryService
from .sales_service import SalesService
from .reporting_service import ReportingService
from .auth_service import AuthService


class ServiceProvider:
    _instance: Optional['ServiceProvider'] = None
    _services: Dict = {}

    def __init__(self):
        if ServiceProvider._instance is not None:
            raise Exception("ServiceProvider is a singleton!")
        self._session = get_session()
        self._initialize_services()

    @classmethod
    def get_instance(cls) -> 'ServiceProvider':
        if cls._instance is None:
            cls._instance = ServiceProvider()
        return cls._instance

    def _initialize_services(self):
        self._services = {
            'auth': AuthService(self._session),
            'user': UserService(self._session),
            'expense': ExpenseService(self._session),
            'inventory': InventoryService(self._session),
            'sales': SalesService(self._session),
            'reporting': ReportingService(self._session)
        }

    def get_service(self, service_name: str):
        return self._services.get(service_name)

    def get_session(self) -> Session:
        return self._session