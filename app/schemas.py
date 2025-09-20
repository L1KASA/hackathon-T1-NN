from datetime import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field


class JsonMessage(BaseModel):
    success: bool = Field(examples=["true"])
    message: str | None = Field(None, examples=["Incorrect code"])


class SkillSchema(BaseModel):
    id: int = Field(gt=0, examples=[1])
    name: str = Field(
        max_length=60, examples=["Java", "Python", "GO", "Docker-compose/Docker"], description="The name of the skill"
    )
    description: Optional[str] = Field(default=None, max_length=500, description="Description of the skill")


class SkillCreateSchema(SkillSchema):
    pass


class SkillResponseSchema(SkillSchema):
    pass

    class Config:
        from_attributes = True


class GetSkillSchema(SkillSchema):
    pass


class EmployeeBaseSchema(BaseModel):
    email: EmailStr = Field(..., examples=["john.doe@example.com"], description="Email address of the employee")
    first_name: str = Field(..., max_length=50, examples=["John"], description="First name of the employee")
    last_name: str = Field(..., max_length=50, examples=["Doe"], description="Last name of the employee")
    department: Optional[str] = Field(None, max_length=100, examples=["IT"], description="Department of the employee")
    rating: float = Field(default=0.0, ge=0.0, le=5.0, examples=[4.5], description="Rating of the employee")


class EmployeeCreateSchema(EmployeeBaseSchema):
    pass


class EmployeeUpdateSchema(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50, examples=["John"])
    last_name: Optional[str] = Field(None, max_length=50, examples=["Doe"])
    department: Optional[str] = Field(None, max_length=100, examples=["IT"])
    rating: Optional[float] = Field(None, ge=0.0, le=5.0, examples=[4.5])


class EmployeeSchema(EmployeeBaseSchema):
    id: int = Field(..., gt=0, examples=[1])
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployeeSkillSchema(BaseModel):
    skill_id: int
    proficiency_level: int


class EmployeeWithSkillsSchema(EmployeeSchema):
    skills: List[EmployeeSkillSchema] = Field(default_factory=list)
