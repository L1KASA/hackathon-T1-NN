from app.common.logging import logger
from app.events.event_handler_factory import EventHandlerFactory
from app.schemas import QuestEventSchema


class EventDispatcherService:
    def __init__(self, handler_factory: EventHandlerFactory):
        self.handler_factory = handler_factory

    async def dispatch(self, event: QuestEventSchema) -> None:
        """Dispatch event to appropriate handler"""
        try:
            handler = self.handler_factory.get_handler(event.action_type)
            await handler.handle(event)
            logger.info(f"Successfully handled event: {event.action_type}")

        except ValueError:
            logger.warning(f"No handler registered for action type: {event.action_type}")
        except Exception as e:
            logger.error(f"Error handling event {event.action_type}: {str(e)}")
