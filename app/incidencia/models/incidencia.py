from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Incidencia(Base):
    __tablename__ = "incidencias"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(Integer, ForeignKey("students.id"))

    date = Column(DateTime)

    leve_faction = Column(String(50))
    leve_other = Column(String(500))

    grave_faction = Column(String(50))
    grave_other = Column(String(500))

    muy_grave_faction = Column(String(50))
    muy_grave_other = Column(String(500))

    description = Column(String(900))
    disciplinary = Column(String(900))
    acuerdos_compromisos = Column(String(500))

    student = relationship("Student", back_populates="incidencias")