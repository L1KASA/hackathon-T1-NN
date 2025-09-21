import re
from typing import Optional


class BaseAppException(Exception):
    """Base exception for the application"""

    detail: str = "Internal server error"

    def __init__(self, detail: Optional[str] = None):
        if detail:
            self.detail = detail
        super().__init__(self.detail)

class RepositoryException(BaseAppException):
    """Base exception for repository layer"""


class ServiceException(BaseAppException):
    """Base exception for service layer"""


# Database exceptions
class IntegrityDataException(RepositoryException):
    """Handles database integrity errors with PostgreSQL detail extraction"""


    def __init__(self, message: str) -> None:
        detail_text = re.search(r"DETAIL: (.+)", message or "")
        refined_message = detail_text.group(1).strip() if detail_text else message
        super().__init__(f"Database integrity error: {refined_message}")

class DatabaseException(RepositoryException):
    """General database errors"""

class ConnectionException(RepositoryException):
    """Database connection errors"""

# CRUD exceptions
class NotFoundException(RepositoryException):
    """Resource not found"""

    def __init__(self, entity: str, identifier: str):
        super().__init__(f"{entity} with identifier '{identifier}' not found")

class AlreadyExistsException(RepositoryException):
    """Resource already exists"""

    def __init__(self, entity: str, identifier: str):
        super().__init__(f"{entity} with identifier '{identifier}' already exists")

class DuplicateSkillException(AlreadyExistsException):
    """Skill already exists"""
    def __init__(self, name: str):
        super().__init__("Skill", name)

class DuplicateEmployeeException(AlreadyExistsException):
    """Employee already exists"""
    def __init__(self, name: str):
        super().__init__("Employee", name)


class ValidationException(ServiceException):
    """Validation errors"""


class SkillNotFoundException(Exception):
    """Raised when a skill is not found"""
    pass
