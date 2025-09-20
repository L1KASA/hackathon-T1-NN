from typing import Optional

from app.exceptions import DuplicateSkillException, DatabaseException
from app.repositories.skill_repository import SkillRepository
from app.schemas import SkillSchema


class SkillService:
    def __init__(self, repository: SkillRepository):
        self.repository = repository


    async def create_skill(self, name: str, description: Optional[str]) -> SkillSchema:
        """Create a new skill"""
        if await self.repository.validate_skill_exists_by_name(name):
            raise DuplicateSkillException(
                f'Skill with name "{name}" already exists')

        skill = await self.repository.create_skill(name=name, description=description)
        return SkillSchema(
            id=skill.id,
            name=skill.name,
            description=skill.description,
            created_at=skill.created_at,
        )
