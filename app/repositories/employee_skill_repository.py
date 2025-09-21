from typing import List

from sqlalchemy import delete
from sqlalchemy import exists
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.exceptions import DatabaseException
from app.common.exceptions import DuplicateSkillException
from app.common.exceptions import IntegrityDataException
from app.common.exceptions import SkillNotFoundException
from app.models import EmployeeSkill
from app.models import Skill


class EmployeeSkillRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_skill_to_employee(
        self, employee_id: int, skill_id: int, proficiency_level: int
    ) -> EmployeeSkill:
        """Add a skill to an employee"""
        try:
            if not await self._check_skill_exists(skill_id):
                raise SkillNotFoundException(f"Skill with ID {skill_id} not found")

            if await self._check_employee_has_skill(employee_id, skill_id):
                raise DuplicateSkillException(
                    f"Employee {employee_id} already has skill {skill_id}"
                )

            employee_skill = EmployeeSkill(
                employee_id=employee_id,
                skill_id=skill_id,
                proficiency_level=proficiency_level
            )

            self._session.add(employee_skill)
            await self._session.commit()
            await self._session.refresh(employee_skill, ['skills'])

            return employee_skill

        except IntegrityError as e:
            await self._session.rollback()
            raise IntegrityDataException(str(e)) from e
        except (DuplicateSkillException, SkillNotFoundException):
            await self._session.rollback()
            raise
        except Exception as e:
            await self._session.rollback()
            raise DatabaseException(f"Failed to add skill to employee: {str(e)}") from e

    async def _check_skill_exists(self, skill_id: int) -> bool:
        """Check if skill exists"""
        try:
            result = await self._session.execute(
                select(exists().where(Skill.id == skill_id))
            )
            return bool(result.scalar())
        except Exception as e:
            raise DatabaseException(f"Failed to check skill existence: {str(e)}") from e

    async def _check_employee_has_skill(self, employee_id: int, skill_id: int) -> bool:
        """Check if employee already has this skill"""
        try:
            result = await self._session.execute(
                select(
                    exists().where(
                        EmployeeSkill.employee_id == employee_id,
                        EmployeeSkill.skill_id == skill_id
                    )
                )
            )
            return bool(result.scalar())
        except Exception as e:
            raise DatabaseException(f"Failed to check employee skill existence: {str(e)}") from e

    async def get_employee_skills(self, employee_id: int) -> List[EmployeeSkill]:
        """Get all skills for an employee"""
        try:
            result = await self._session.execute(
                select(EmployeeSkill)
                .where(EmployeeSkill.employee_id == employee_id)
                .options(selectinload(EmployeeSkill.skills))
            )
            return list(result.scalars().all())
        except Exception as e:
            raise DatabaseException(f"Failed to get employee skills: {str(e)}") from e

    async def remove_skill_from_employee(self, employee_id: int, skill_id: int) -> None:
        """Remove a skill from an employee"""
        try:
            result = await self._session.execute(
                delete(EmployeeSkill).where(
                    EmployeeSkill.employee_id == employee_id,
                    EmployeeSkill.skill_id == skill_id
                )
            )
            if result.rowcount == 0:
                raise SkillNotFoundException(
                    f"Skill {skill_id} not found for employee {employee_id}"
                )
            await self._session.commit()
        except SkillNotFoundException:
            await self._session.rollback()
            raise
        except Exception as e:
            await self._session.rollback()
            raise DatabaseException(f"Failed to remove skill from employee: {str(e)}") from e

    async def update_employee_skill(
            self, employee_id: int, skill_id: int, proficiency_level: int
    ) -> EmployeeSkill:
        """Update employee skill proficiency level"""
        try:
            # Get existing skill
            result = await self._session.execute(
                select(EmployeeSkill).where(
                    EmployeeSkill.employee_id == employee_id,
                    EmployeeSkill.skill_id == skill_id
                )
            )
            employee_skill = result.scalar_one_or_none()

            if not employee_skill:
                raise SkillNotFoundException(
                    f"Skill {skill_id} not found for employee {employee_id}"
                )

            employee_skill.proficiency_level = proficiency_level
            await self._session.commit()
            await self._session.refresh(employee_skill)
            return employee_skill

        except SkillNotFoundException:
            await self._session.rollback()
            raise
        except Exception as e:
            await self._session.rollback()
            raise DatabaseException(f"Failed to update employee skill: {str(e)}") from e
