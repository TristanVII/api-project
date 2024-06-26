import os
from sqlalchemy import create_engine
from models import Base
from load_configs import load_app_conf

CONFIG = load_app_conf()
DATABASE = CONFIG['DATABASE']

engine = create_engine(f"sqlite:///{DATABASE}", echo=True)


def create_database():
    if not (os.path.exists(f"{DATABASE}")):
        Base.metadata.create_all(engine)
