from fastapi import APIRouter

router = APIRouter(
    prefix="/tip/v1",
    tags=["tip"],
)

# @router.post("/", response_model=SkillSchema, status_code=status.HTTP_201_CREATED)
# async def send_tip(
#     skill_data: SkillCreateSchema,
#     service: SkillService = Depends(get_skill_service),
# ):
#     """"""
#     pass
