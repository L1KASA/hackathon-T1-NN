import aiohttp
from fastapi import FastAPI

from app.common.logging import logger
from app.database import initialize_db
from app.database import shutdown_db


class AppLifecycle:
    def __init__(self, app: FastAPI):
        self.app = app
        self.aiohttp_session = None

    async def on_startup(self):
        logger.info("Starting up application...")
        await self._initialize_aiohttp()
        await initialize_db()
        logger.info(
            "Application startup complete. Ready to serve requests."
        )

    async def on_shutdown(self):
        logger.info("Shutting down application...")
        await self._close_aiohttp_session()
        await shutdown_db()
        logger.info("Application shutdown complete.")

    async def _initialize_aiohttp(self):
        self.aiohttp_session = aiohttp.ClientSession()
        self.app.state.aiohttp_session = self.aiohttp_session

    async def _close_aiohttp_session(self):
        try:
            if self.aiohttp_session and not self.aiohttp_session.closed:
                await self.aiohttp_session.close()
        except Exception as e:
            logger.error(f"Error closing aiohttp session: {e}", exc_info=True)
