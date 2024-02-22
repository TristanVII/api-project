from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class JobListing(Base):
    __tablename__ = "job_listing"
    id: Mapped[Integer] = mapped_column(Integer, primary_key=True)
    job_listing_id: Mapped[String] = mapped_column(
        String(50), nullable=False)
    title: Mapped[String] = mapped_column(String(50), nullable=False)
    location: Mapped[String] = mapped_column(String(50), nullable=False)
    salary: Mapped[Integer] = mapped_column(Integer, nullable=False)
    sector: Mapped[String] = mapped_column(String(50), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    date_created: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    trace_id: Mapped[String] = mapped_column(String(50))

    def to_dict(self):

        data = self.__dict__
        keys = [
            "job_listing_id",
            "sector",
            "title",
            "salary",
            "location",
            "date",
            "trace_id"]

        return {k: v for k, v in data.items() if k in keys}


class JobApplication(Base):
    __tablename__ = "job_application"
    id: Mapped[Integer] = mapped_column(Integer, primary_key=True)
    job_application_id: Mapped[String] = mapped_column(
        String(50), nullable=False)
    job_listing_id: Mapped[String] = mapped_column(String(50), nullable=False)
    gender: Mapped[String] = mapped_column(String(20), nullable=False)
    age: Mapped[Integer] = mapped_column(Integer, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    years_of_experience: Mapped[Integer] = mapped_column(
        Integer, nullable=False)
    date_created: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    trace_id: Mapped[String] = mapped_column(String(50))

    def to_dict(self):
        data = self.__dict__
        keys = [
            "job_application_id",
            "job_listing_id",
            "age",
            "gender",
            "years_of_experience",
            "date",
            "trace_id"]

        return {k: v for k, v in data.items() if k in keys}
