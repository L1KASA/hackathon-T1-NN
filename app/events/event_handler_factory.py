from app.events.event_handler import ProfileUpdatedHandler
from app.events.event_handler import ProjectCompletedHandler
from app.events.event_handler import QuestEventHandler
from app.events.event_handler import SkillAddedHandler
from app.services.employee_service import EmployeeService
from app.services.quest_service import QuestService


class EventHandlerFactory:
    def __init__(self, quest_service: QuestService, employee_service: EmployeeService):
        self.quest_service = quest_service
        self.employee_service = employee_service
        self._handlers: dict[str, QuestEventHandler] = {}
        self.create_default_handlers()


    def register_handler(self, action_type: str, handler: QuestEventHandler) -> None:
        self._handlers[action_type] = handler

    def get_handler(self, action_type: str) -> QuestEventHandler:
        handler = self._handlers.get(action_type)
        if not handler:
            raise ValueError(f"No handler registered for action type: {action_type}")
        return handler

    def create_default_handlers(self) -> None:
        self.register_handler("skill_add", SkillAddedHandler(self.quest_service))
        self.register_handler("profile_completion", ProfileUpdatedHandler(self.quest_service, self.employee_service))
        self.register_handler("complete_project", ProjectCompletedHandler(self.quest_service))
        self.register_handler("profile_update", ProfileUpdatedHandler(self.quest_service, self.employee_service))

