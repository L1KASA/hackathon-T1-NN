from typing import Optional

from pydantic import BaseModel, Field


class JsonMessage(BaseModel):
    success: bool = Field(examples=["true"])
    message: str | None = Field(None, examples=["Incorrect code"])


class SkillSchema(BaseModel):
    name: str = Field(
        max_length=60, examples=["Java", "Python", "GO", "Docker-compose/Docker"], description="The name of the skill"
    )
    description: Optional[str] = Field(default=None, max_length=500, description="Description of the skill")


class SkillCreateSchema(SkillSchema):
    pass


class SkillResponseSchema(SkillSchema):
    id: int = Field(gt=0, examples=[1])

    class Config:
        from_attributes = True


class GetSkillSchema(SkillSchema):
    pass
