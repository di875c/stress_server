import pathlib
import os


BASE_DIR = pathlib.Path(__file__).parent.parent
ENV = os.environ.get('POSTGRES_ENGINE', None)
if not ENV:
    from dotenv import load_dotenv
    load_dotenv(f'{BASE_DIR}/.env')

    