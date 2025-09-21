from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from starlette import status

from app.common.exceptions import DatabaseException
from app.common.exceptions import DuplicateSkillException
from app.common.exceptions import IntegrityDataException
from app.dependencies import get_skill_service
from app.schemas import SkillCreateSchema
from app.schemas import SkillSchema
from app.services.skill_service import SkillService

router = APIRouter(
    prefix="/skills/v1",
    tags=["skills"],
)


@router.post("/", response_model=SkillSchema, status_code=status.HTTP_201_CREATED)
async def create_skill(
    skill_data: SkillCreateSchema,
    service: SkillService = Depends(get_skill_service),
):
    """Create a new skill"""
    try:
        skill = await service.create(
            name=skill_data.name, description=skill_data.description
        )
        return skill
    except DuplicateSkillException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        ) from None
    except (DatabaseException, IntegrityDataException) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from None
