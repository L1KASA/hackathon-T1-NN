from aiohttp import ClientSession
from fastapi import Depends
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.skill_repository import SkillRepository
from app.services.employee_service import EmployeeService
from app.services.skill_service import SkillService


async def get_aiohttp_session(request: Request) -> ClientSession:
    """
    Retrieves the single shared aiohttp.ClientSession instance from FastAPI's application state.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        aiohttp.ClientSession: The shared HTTP client session.
    """
    return request.app.state.aiohttp_session

async def get_skill_repository(
    session: AsyncSession = Depends(get_async_session)
) -> SkillRepository:
    """Dependency for SkillRepository"""
    return SkillRepository(session)

async def get_skill_service(
    repository: SkillRepository = Depends(get_skill_repository)
) -> SkillService:
    """Dependency for SkillService"""
    return SkillService(repository)


def get_employee_repository(
    session: AsyncSession = Depends(get_async_session)
) -> EmployeeRepository:
    """Dependency for EmployeeRepository"""
    return EmployeeRepository(session)


def get_employee_service(
    repository: EmployeeRepository = Depends(get_employee_repository)
) -> EmployeeService:
    """Dependency for EmployeeService"""
    return EmployeeService(repository)
