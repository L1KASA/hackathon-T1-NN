# dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.skill_repository import SkillRepository
from app.services.skill_service import SkillService
from aiohttp import ClientSession
from fastapi import Request
from app.database import get_async_session


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