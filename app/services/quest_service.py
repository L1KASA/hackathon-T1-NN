from typing import List

from app.common.exceptions import ServiceException
from app.repositories.quest_repository import QuestRepository
from app.schemas import EmployeeQuestProgressSchema
from app.schemas import QuestCreateSchema
from app.schemas import QuestEventSchema
from app.schemas import QuestSchema


class QuestService:
    def __init__(self, repository: QuestRepository):
        self.repository = repository

    async def create_quest(self, quest_data: QuestCreateSchema) -> QuestSchema:
        try:
            quest = await self.repository.create_quest(quest_data.model_dump())
            return QuestSchema.model_validate(quest)
        except Exception as e:
            raise ServiceException(f"Failed to create quest: {str(e)}") from e

    async def get_all_quests(self) -> List[QuestSchema]:
        try:
            quests = await self.repository.get_all_quests()
            return [QuestSchema.model_validate(quest) for quest in quests]
        except Exception as e:
            raise ServiceException(f"Failed to get quests: {str(e)}") from e

    async def assign_quest(self, employee_id: int, quest_id: int) -> None:
        try:
            await self.repository.assign_quest_to_employee(employee_id, quest_id)
        except Exception as e:
            raise ServiceException(f"Failed to assign quest: {str(e)}") from e

    async def get_employee_quests(self, employee_id: int) -> List[EmployeeQuestProgressSchema]:
        try:
            employee_quests = await self.repository.get_employee_quests(employee_id)

            result = []
            for eq in employee_quests:
                progress_percentage = (
                                                  eq.current_count / eq.quest.required_count) * 100 if eq.quest.required_count > 0 else 0
                result.append(EmployeeQuestProgressSchema(
                    quest_id=eq.quest_id,
                    quest_name=eq.quest.name,
                    current_count=eq.current_count,
                    required_count=eq.quest.required_count,
                    is_completed=eq.is_completed,
                    progress_percentage=round(progress_percentage, 1),
                    xp_reward=eq.quest.xp_reward
                ))

            return result
        except Exception as e:
            raise ServiceException(f"Failed to get employee quests: {str(e)}") from e

    async def handle_quest_event(self, event: QuestEventSchema) -> List[EmployeeQuestProgressSchema]:
        """Main method to handle quest progression events"""
        try:
            updated_quests = await self.repository.update_quest_progress(
                event.employee_id,
                event.action_type,
                event.count
            )

            result = []
            for eq in updated_quests:
                progress_percentage = (eq.current_count / eq.quest.required_count) * 100 if eq.quest.required_count > 0 else 0
                result.append(EmployeeQuestProgressSchema(
                    quest_id=eq.quest_id,
                    quest_name=eq.quest.name,
                    current_count=eq.current_count,
                    required_count=eq.quest.required_count,
                    is_completed=eq.is_completed,
                    progress_percentage=round(progress_percentage, 1),
                    xp_reward=eq.quest.xp_reward
                ))

            return result
        except Exception as e:
            raise ServiceException(f"Failed to handle quest event: {str(e)}") from e

    async def get_quest_progress(self, employee_id: int, quest_id: int) -> EmployeeQuestProgressSchema:
        try:
            eq = await self.repository.get_quest_progress(employee_id, quest_id)
            progress_percentage = (
                (eq.current_count / eq.quest.required_count) * 100 if eq.quest.required_count > 0 else 0
            )

            return EmployeeQuestProgressSchema(
                quest_id=eq.quest_id,
                quest_name=eq.quest.name,
                current_count=eq.current_count,
                required_count=eq.quest.required_count,
                is_completed=eq.is_completed,
                progress_percentage=round(progress_percentage, 1),
                xp_reward=eq.quest.xp_reward
            )
        except Exception as e:
            raise ServiceException(f"Failed to get quest progress: {str(e)}") from e

async def update_percentage_quests(self, employee_id: int, action_type: str, percentage: int):
    """Special method for percentage-based quests (max value, not sum)"""
    try:
        result = await self.repository.update_percentage_quests(
            employee_id, action_type, percentage
        )
        return result
    except Exception as e:
        raise ServiceException(f"Failed to update percentage quests: {str(e)}") from e
