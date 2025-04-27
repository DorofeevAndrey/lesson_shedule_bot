from sqlalchemy import Column, Integer, String, ForeignKey, Time, Date
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)

    # Связь с уроками
    lessons = relationship("Lesson", back_populates="user")
    free_slots = relationship("FreeSlot", back_populates="admin")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String, nullable=False)
    start_time = Column(Time, nullable=False)
    date = Column(Date, nullable=True)  # можно пустым, если регулярные уроки

    # Связь с пользователем
    user = relationship("User", back_populates="lessons")


class FreeSlot(Base):
    __tablename__ = "free_slots"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    admin_id = Column(Integer, ForeignKey("users.id"))

    admin = relationship("User", back_populates="free_slots")
