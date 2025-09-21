from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from starlette import status

from app.common.exceptions import DatabaseException
from app.common.exceptions import DuplicateEmployeeException
from app.common.exceptions import IntegrityDataException
from app.common.exceptions import NotFoundException
from app.common.exceptions import ServiceException
from app.dependencies import get_employee_service
from app.dependencies import get_quest_service
from app.schemas import EmployeeCreateSchema
from app.schemas import EmployeeSchema
from app.schemas import EmployeeUpdateSchema
from app.schemas import EmployeeWithSkillsSchema
from app.schemas import ProfileCompletionSchema
from app.schemas import QuestEventSchema
from app.services.employee_service import EmployeeService
from app.services.quest_service import QuestService

router = APIRouter(
    prefix="/employees/v1",
    tags=["employees"],
)


@router.post("/", response_model=EmployeeSchema, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreateSchema,
    service: EmployeeService = Depends(get_employee_service),
):
    """Create a new employee"""
    try:
        employee = await service.create_employee(employee_data)
        return employee
    except DuplicateEmployeeException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        ) from None
    except (DatabaseException, IntegrityDataException) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from None

@router.get("/me", response_model=EmployeeWithSkillsSchema)
async def get_employee_profile(
    employee_id: int,
    service: EmployeeService = Depends(get_employee_service),
):
    """Get current employee profile"""
    try:
        employee = await service.get_employee_profile(employee_id)
        return employee
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        ) from None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from None

@router.put("/{employee_id}", response_model=EmployeeSchema)
async def update_employee(
    employee_id: int,
    update_data: EmployeeUpdateSchema,
    service: EmployeeService = Depends(get_employee_service),
):
    """Update employee information"""
    try:
        employee = await service.update_employee(employee_id, update_data)
        return employee
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        ) from None
    except (DatabaseException, IntegrityDataException) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from None

@router.get("/{employee_id}", response_model=EmployeeWithSkillsSchema)
async def get_employee(
    employee_id: int,
    service: EmployeeService = Depends(get_employee_service),
):
    """Get employee by ID"""
    try:
        employee = await service.get_employee_by_id(employee_id)
        return employee
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        ) from None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from None

@router.get(
    "/{employee_id}/completion",
    response_model=ProfileCompletionSchema,
    summary="Calculate profile completion percentage",
    description="Calculate the completion percentage of employee profile including skills"
)
async def calculate_profile_completion(
    employee_id: int,
    service: EmployeeService = Depends(get_employee_service),
    quest_service: QuestService = Depends(get_quest_service)
):
    """Calculate profile completion percentage for employee"""
    try:
        completion = await service.calculate_completion(employee_id)

        await quest_service.handle_quest_event(QuestEventSchema(
            employee_id=employee_id,
            action_type="profile_completion",
            count=completion.completion_percentage
        ))

    except ServiceException as e:
        raise HTTPException(status_code=404, detail=str(e)) from None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate completion: {str(e)}") from None
