from sqlalchemy import DateTime, Integer
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class Anomaly(Base):
    __tablename__ = "stats"
    id: Mapped[Integer] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[String] = mapped_column(String(250), nullable=False)
    trace_id: Mapped[String] = mapped_column(String(250), nullable=False)
    event_type: Mapped[String] = mapped_column(String(100), nullable=False)
    anomaly_type: Mapped[String] = mapped_column(String(100), nullable=False)
    description: Mapped[String] = mapped_column(String(250), nullable=False)
    date_created: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    def to_dict(self):
        """ Dictionary Representation of an anomaly """
        dict = {}
        dict['id'] = self.id
        dict['event_id'] = self.event_id
        dict['trace_id'] = self.trace_id
        dict['event_type'] = self.event_type
        dict['anomaly_type'] = self.anomaly_type
        dict['description'] = self.description

        return dict
