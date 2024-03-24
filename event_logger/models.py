from sqlalchemy import DateTime, Integer
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class Event(Base):
    __tablename__ = "stats"
    id: Mapped[String] = mapped_column(
        String(26), primary_key=True)
    message: Mapped[String] = mapped_column(String(255), nullable=False)
    code: Mapped[String] = mapped_column(
        String(4), nullable=False)
    date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    def to_dict(self, full=False):
        data = self.__dict__

        keys = ['message', 'code', 'time']

        return {k: v for k, v in data.items() if k in keys}
