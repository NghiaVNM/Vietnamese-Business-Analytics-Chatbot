from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base

class Employee(Base):
  __tablename__ = "employees"

  id = Column(Integer, primary_key=True, index=True)
  employee_code = Column(String(20), unique=True, index=True, nullable=False)
  full_name = Column(String(100), nullable=False)
  email = Column(String(100), unique=True, index=True, nullable=False)
  phone = Column(String(20))
  department = Column(String(50), nullable=False)
  position = Column(String(50), nullable=False)
  salary = Column(Float)
  hire_date = Column(DateTime, nullable=False)
  is_active = Column(Boolean, default=True)
  address = Column(Text)
  emergency_contact = Column(String(100))
  emergency_phone = Column(String(20))
  created_at = Column(DateTime, server_default=func.now())
  updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())