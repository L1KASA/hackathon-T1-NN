from aiohttp import ClientSession
from fastapi import Depends
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.events.event_handler_factory import EventHandlerFactory
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.employee_skill_repository import EmployeeSkillRepository
from app.repositories.quest_repository import QuestRepository
from app.repositories.skill_repository import SkillRepository
from app.services.employee_service import EmployeeService
from app.services.employee_skill_service import EmployeeSkillService
from app.services.event_dispatcher_service import EventDispatcherService
from app.services.quest_service import QuestService
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

async def get_employee_skill_repository(
        session: AsyncSession = Depends(get_async_session)
) -> EmployeeSkillRepository:
    return EmployeeSkillRepository(session)


async def get_quest_repository(session: AsyncSession = Depends(get_async_session)) -> QuestRepository:
    return QuestRepository(session)

async def get_quest_service(
    repository: QuestRepository = Depends(get_quest_repository)
) -> QuestService:
    return QuestService(repository)

def get_employee_service(
    repository: EmployeeRepository = Depends(get_employee_repository), quest_service: QuestService = Depends(get_quest_service)
) -> EmployeeService:
    """Dependency for EmployeeService"""
    return EmployeeService(repository, quest_service)


async def get_event_handler_factory(
    quest_service: QuestService = Depends(get_quest_service),
    employee_service: EmployeeService = Depends(get_employee_service)
) -> EventHandlerFactory:
    factory = EventHandlerFactory(quest_service, employee_service)
    return factory


async def get_event_dispatcher(
    factory: EventHandlerFactory = Depends(get_event_handler_factory)
) -> EventDispatcherService:
    return EventDispatcherService(factory)
async def get_employee_skill_service(
    repository: EmployeeSkillRepository = Depends(get_employee_skill_repository),
    event_dispatcher_service: EventDispatcherService = Depends(get_event_dispatcher),
    employee_service: EmployeeService = Depends(get_employee_service),
) -> EmployeeSkillService:
    return EmployeeSkillService(repository, event_dispatcher_service, employee_service)
