from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False)
    grade = Column(String(50))
    group = Column(String(50))

    incidencias = relationship(
        "Incidencia",
        back_populates="student",
        cascade="all, delete"
    )