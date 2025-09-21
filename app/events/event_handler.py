from abc import ABC
from abc import abstractmethod
from typing import Protocol

from app.common.logging import logger
from app.schemas import QuestEventSchema
from app.services.employee_service import EmployeeService
from app.services.quest_service import QuestService


class EventHandler(Protocol):
    async def handle_event(self, event: QuestEventSchema) -> None:
        ...


class QuestEventHandler(ABC):
    @abstractmethod
    async def handle(self, event: QuestEventSchema) -> None:
        pass


class SkillAddedHandler(QuestEventHandler):
    def __init__(self, quest_service: QuestService):
        self.quest_service = quest_service

    async def handle(self, event: QuestEventSchema) -> None:
        if event.action_type == "skill_add":
            await self.quest_service.handle_quest_event(event)


class ProfileUpdatedHandler(QuestEventHandler):
    def __init__(self, quest_service: QuestService, employee_service: EmployeeService):
        self.quest_service = quest_service
        self.employee_service = employee_service

    async def handle(self, event: QuestEventSchema) -> None:
        if event.action_type == "profile_completion":
            completion = await self.employee_service.calculate_completion(event.employee_id)
            await self.quest_service.handle_quest_event(QuestEventSchema(
                employee_id=event.employee_id,
                action_type="profile_completion",
                count=completion.completion_percentage
            ))


class ProjectCompletedHandler(QuestEventHandler):
    def __init__(self, quest_service: QuestService):
        self.quest_service = quest_service

    async def handle(self, event: QuestEventSchema) -> None:
        if event.action_type == "complete_project":
            await self.quest_service.handle_quest_event(event)

class FallbackHandler(QuestEventHandler):
    async def handle(self, event: QuestEventSchema) -> None:
        logger.warning(f"No specific handler for action type: {event.action_type}. Using fallback.")


class PercentageQuestHandler(QuestEventHandler):
    def __init__(self, quest_service: QuestService):
        self.quest_service = quest_service

    async def handle(self, event: QuestEventSchema) -> None:
        if event.action_type == "profile_completion":
            await self.quest_service.update_percentage_quests(
                event.employee_id,
                event.action_type,
                event.count
            )
