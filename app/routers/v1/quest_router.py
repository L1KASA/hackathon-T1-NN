from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from app.common.exceptions import NotFoundException
from app.common.exceptions import ServiceException
from app.dependencies import get_quest_service
from app.schemas import AssignQuestSchema
from app.schemas import EmployeeQuestProgressSchema
from app.schemas import QuestCreateSchema
from app.schemas import QuestEventSchema
from app.schemas import QuestSchema
from app.services.quest_service import QuestService

router = APIRouter(
    prefix="/quests/v1",
    tags=["quests"]
)

@router.post("/", response_model=QuestSchema, status_code=status.HTTP_201_CREATED)
async def create_quest(
    quest_data: QuestCreateSchema,
    service: QuestService = Depends(get_quest_service)
):
    """Create a new quest"""
    try:
        return await service.create_quest(quest_data)
    except ServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from None

@router.get("/", response_model=List[QuestSchema])
async def get_all_quests(
    service: QuestService = Depends(get_quest_service)
):
    """Get all available quests"""
    try:
        return await service.get_all_quests()
    except ServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from None

@router.post("/assign", status_code=status.HTTP_200_OK)
async def assign_quest(
    assign_data: AssignQuestSchema,
    service: QuestService = Depends(get_quest_service)
):
    """Assign a quest to an employee"""
    try:
        await service.assign_quest(assign_data.employee_id, assign_data.quest_id)
        return {"message": "Quest assigned successfully"}
    except ServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from None

@router.get("/employee/{employee_id}", response_model=List[EmployeeQuestProgressSchema])
async def get_employee_quests(
    employee_id: int,
    service: QuestService = Depends(get_quest_service)
):
    """Get all quests for an employee"""
    try:
        return await service.get_employee_quests(employee_id)
    except ServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from None

@router.get("/progress/{employee_id}/{quest_id}", response_model=EmployeeQuestProgressSchema)
async def get_quest_progress(
    employee_id: int,
    quest_id: int,
    service: QuestService = Depends(get_quest_service)
):
    """Get specific quest progress for an employee"""
    try:
        return await service.get_quest_progress(employee_id, quest_id)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        ) from None
    except ServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from None
