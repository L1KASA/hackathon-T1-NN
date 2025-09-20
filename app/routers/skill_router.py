from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.dependencies import get_skill_service
from app.exceptions import DuplicateSkillException, DatabaseException, IntegrityDataException
from app.schemas import SkillSchema, SkillCreateSchema
from app.services.skill_service import SkillService

router = APIRouter(
    prefix="/skills",
    tags=["skills"],
)


@router.post("/", response_model=SkillSchema, status_code=status.HTTP_201_CREATED)
async def create_skill(
    skill_data: SkillCreateSchema,
    service: SkillService = Depends(get_skill_service),
):
    """Create a new skill"""
    try:
        skill = await service.create_skill(
            name=skill_data.name, description=skill_data.description
        )
        return skill
    except DuplicateSkillException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except (DatabaseException, IntegrityDataException) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
