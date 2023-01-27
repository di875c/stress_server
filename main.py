from aiohttp import web  # основной модуль aiohttp
import jinja2  # шаблонизатор jinja2
import aiohttp_jinja2  # адаптация jinja2 к aiohttp
import os
# from app.store.database.models import init_models
from app.settings import BASE_DIR


# def setup_db(application):
#     init_models()
#    application['db'] = PostgresAccessor()
#    application['db'].setup(application)


def setup_config(application):
   application['config'] = os.environ.get


def setup_external_libraries(application):
   aiohttp_jinja2.setup(
      application,
      loader=jinja2.FileSystemLoader(f"{BASE_DIR}/templates"),
   )


# настроим url-пути для доступа к нашему будущему приложению
def setup_routes(application):
    from app.stress.routes import setup_routes as setup_stress_routes
    setup_stress_routes(application)


def setup_app(application):
   # настройка всего приложения состоит из:
   setup_config(application)
   # setup_db(application)
   setup_external_libraries(application)  # настройки внешних библиотек, например шаблонизатора
   setup_routes(application)  # настройки роутера приложения


app = web.Application()  # создаем наш веб-сервер

if __name__ == "__main__":  # эта строчка указывает, что данный файл можно запустить как скрипт
   setup_app(app)  # настраиваем приложение
   web.run_app(app)  # запускаем приложение