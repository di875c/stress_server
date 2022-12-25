# from aiohttp import web
#
#
# class PostgresAccessor:
#     def __init__(self) -> None:
#         from .tables import Message
#
#         self.message = Message
#         self.db = None
#
#     def setup(self, application: web.Application) -> None:
#         application.on_startup.append(self._on_connect)
#         application.on_cleanup.append(self._on_disconnect)
#
#     async def _on_connect(self, application: web.Application):
#         from .models import Base
#
#         self.config = application['config']('POSTGRES_HOST')
#         await Base.set_bind(self.config['database_url'])
#         self.db = Base
#
#     async def _on_disconnect(self, _) -> None:
#         if self.db is not None:
#             await self.db.pop_bind().close()