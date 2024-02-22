from datetime import datetime
from sqlalchemy import DateTime, Integer
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class Stats(Base):
    __tablename__ = "stats"
    id: Mapped[String] = mapped_column(
        String(50), primary_key=True, nullable=False)
    num_jobs: Mapped[Integer] = mapped_column(Integer, nullable=False)
    num_applications: Mapped[Integer] = mapped_column(
        Integer, nullable=False)
    average_salary: Mapped[Integer] = mapped_column(Integer, nullable=False)
    max_experience: Mapped[Integer] = mapped_column(Integer, nullable=False)
    last_updated: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    def to_dict(self, full=False):
        data = self.__dict__

        keys = ['num_jobs', 'num_applications',
                'average_salary', 'max_experience']

        if full:
            keys += ['id', 'last_updated']

        return {k: v for k, v in data.items() if k in keys}
