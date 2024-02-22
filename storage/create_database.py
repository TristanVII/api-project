from sqlalchemy import create_engine
from models import Base
from db_conf import load_app_conf

CONFIG = load_app_conf()

# Access the values like this:
USER = CONFIG['USER']
PASSWORD = CONFIG['PASSWORD']
HOST = CONFIG['HOST']
PORT = CONFIG['PORT']
DB = CONFIG['DB']


engine = create_engine(
    f'mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}', echo=True)


def create_database():
    Base.metadata.create_all(engine)


def drop_table(table):
    table.__table__.drop(engine)
