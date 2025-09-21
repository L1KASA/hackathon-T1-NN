from typing import List

from app.common.exceptions import ServiceException
from app.repositories.employee_skill_repository import EmployeeSkillRepository
from app.schemas import EmployeeSkillResponseSchema
from app.schemas import QuestEventSchema
from app.services.employee_service import EmployeeService
from app.services.event_dispatcher_service import EventDispatcherService


class EmployeeSkillService:
    def __init__(
        self,
        repository: EmployeeSkillRepository,
        event_dispatcher: EventDispatcherService,
        employee_service: EmployeeService
    ):
        self.repository = repository
        self.event_dispatcher = event_dispatcher
        self.employee_service = employee_service


    async def add_skill_to_employee(
        self, employee_id: int, skill_id: int, proficiency_level: int
    ) -> EmployeeSkillResponseSchema:
        """Add a skill to an employee"""
        try:
            employee_skill = await self.repository.add_skill_to_employee(
                employee_id, skill_id, proficiency_level
            )

            await self.event_dispatcher.dispatch(QuestEventSchema(
                employee_id=employee_id,
                action_type="skill_add",
                count=1
            ))

            completion = await self.employee_service.calculate_completion(employee_id)
            await self.event_dispatcher.dispatch(QuestEventSchema(
                employee_id=employee_id,
                action_type="profile_completion",
                count=completion.completion_percentage
            ))

            return EmployeeSkillResponseSchema(
                skill_id=employee_skill.skill_id,
                proficiency_level=employee_skill.proficiency_level,
                skill_name=employee_skill.skills.name,
                skill_description=employee_skill.skills.description
            )
        except Exception as e:
            raise ServiceException(f"Failed to add skill to employee: {str(e)}") from e

    async def get_employee_skills(self, employee_id: int) -> List[EmployeeSkillResponseSchema]:
        """Get all skills for an employee"""
        try:
            employee_skills = await self.repository.get_employee_skills(employee_id)

            return [
                EmployeeSkillResponseSchema(
                    skill_id=es.skill_id,
                    proficiency_level=es.proficiency_level,
                    skill_name=es.skills.name,
                    skill_description=es.skills.description
                )
                for es in employee_skills
            ]
        except Exception as e:
            raise ServiceException(f"Failed to get employee skills: {str(e)}") from e

    async def remove_skill_from_employee(self, employee_id: int, skill_id: int) -> None:
        """Remove a skill from an employee"""
        try:
            await self.repository.remove_skill_from_employee(employee_id, skill_id)
        except Exception as e:
            raise ServiceException(f"Failed to remove skill from employee: {str(e)}") from e

    async def update_employee_skill(
            self, employee_id: int, skill_id: int, proficiency_level: int
    ) -> EmployeeSkillResponseSchema:
        """Update employee skill proficiency level"""
        try:
            employee_skill = await self.repository.update_employee_skill(
                employee_id, skill_id, proficiency_level
            )

            return EmployeeSkillResponseSchema(
                skill_id=employee_skill.skill_id,
                proficiency_level=employee_skill.proficiency_level,
                skill_name=employee_skill.skills.name,
                skill_description=employee_skill.skills.description
            )
        except Exception as e:
            raise ServiceException(f"Failed to update employee skill: {str(e)}") from e
