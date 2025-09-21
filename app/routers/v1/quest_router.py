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
    """
    Create a new quest

    ## Params
    - **name**: Название квеста (например, "Идеальный профиль")

    - **description**: Описание квеста

    - **xp_reward**: Награда в опыте (например, 150)

    - **action_type**: Тип действия для отслеживания. На данный момент реализованы следующие типы:

        - `profile_completion` - Заполнение профиля (%)

        - `skill_add` - Добавление навыков (количество)

    - **required_count**: Требуемое количество или проценты

    - **is_active**: Активен ли квест

    ## Example:
    ```json
    {
        "name": "Идеальный профиль",
        "description": "Заполни профиль на 100%",
        "xp_reward": 150,
        "action_type": "profile_completion",
        "required_count": 100,
        "is_active": true
    }
    """
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
    """
    Get all available quests

    ## Returns:
    Список всех доступных квестов в системе

    ## Example:
    ```json
    [
        {
            "id": 1,
            "name": "Полиглот",
            "description": "Изучи 5 навыков",
            "xp_reward": 200,
            "action_type": "skill_add",
            "required_count": 5,
            "is_active": true,
            "created_at": "2025-09-20T10:00:00"
        }
    ]
    ```
    """
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
    """
    Assign a quest to an employee

    ## Params:
    - **employee_id**: ID сотрудника
    - **quest_id**: ID квеста для его назначения сотруднику

    ## Example:
    ```json
    {
        "employee_id": 7,
        "quest_id": 3
    }
    ```

    ## Response:
    ```json
    {
        "message": "Quest assigned successfully"
    }
    ```

    ##  Errors:
    - 404: Сотрудник или квест не найдены
    - 400: Квест уже назначен или не активен
    """
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
    """
    Get all quests for an employee with progress information

    ## Params:
    - **employee_id**: ID сотрудника

    ## Returns:
    Список квестов сотрудника с информацией о прогрессе

    ## Example:
    ```json
    [
        {
            "quest_id": 3,
            "quest_name": "Идеальный профиль",
            "current_count": 84,
            "required_count": 100,
            "is_completed": false,
            "progress_percentage": 84.0,
            "xp_reward": 150
        }
    ]
    ```

    ##  Errors:
    - 404: Сотрудник не найден
    - 500: Внутренняя ошибка сервера
    """
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
    """
    Get specific quest progress for an employee

    ## Params:
    - **employee_id**: ID сотрудника
    - **quest_id**: ID квеста

    ## Returns:
    Детальную информацию о прогрессе по конкретному квесту

    ## Example:
    ```json
    {
        "quest_id": 3,
        "quest_name": "Идеальный профиль",
        "current_count": 84,
        "required_count": 100,
        "is_completed": false,
        "progress_percentage": 84.0,
        "xp_reward": 150
    }
    ```

    ## Errors:
    - 404: Прогресс квеста не найден
    - 500: Внутренняя ошибка сервера
    """
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
