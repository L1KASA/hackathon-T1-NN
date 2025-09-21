from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from starlette import status

from app.common.exceptions import DuplicateSkillException
from app.common.exceptions import ServiceException
from app.common.exceptions import SkillNotFoundException
from app.dependencies import get_employee_skill_service
from app.schemas import EmployeeSkillCreateSchema
from app.schemas import EmployeeSkillResponseSchema
from app.schemas import QuestEventSchema
from app.services.employee_skill_service import EmployeeSkillService

router = APIRouter(
    prefix="/employees/v1/skills",
    tags=["employees"],
)


@router.post(
    "/{employee_id}",
    response_model=EmployeeSkillResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Add skill to employee",
    description="Add a new skill to employee's profile with proficiency level"
)
async def add_skill_to_employee(
    employee_id: int,
    skill_data: EmployeeSkillCreateSchema,
    service: EmployeeSkillService = Depends(get_employee_skill_service),
):
    """Add a skill to employee profile"""
    try:
        skill = await service.add_skill_to_employee(
            employee_id=employee_id,
            skill_id=skill_data.skill_id,
            proficiency_level=skill_data.proficiency_level
        )
        return skill
    except DuplicateSkillException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        ) from None
    except SkillNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        ) from None
    except ServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from None


@router.get(
    "/{employee_id}/all",
    response_model=List[EmployeeSkillResponseSchema],
    summary="Get employee skills",
    description="Get all skills for an employee"
)
async def get_employee_skills(
        employee_id: int,
        service: EmployeeSkillService = Depends(get_employee_skill_service),
):
    """Get all skills for an employee"""
    try:
        skills = await service.get_employee_skills(employee_id)
        return skills
    except ServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from None
