from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.schemas.employee import Employee, EmployeeCreate, EmployeeUpdate, EmployeeList
from app.crud import employee as crud_employee

router = APIRouter()

@router.post("/", response_model=Employee)
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db)
):
    """Tạo nhân viên mới"""
    # Check if employee code already exists
    db_employee = crud_employee.get_employee_by_code(db, employee.employee_code)
    if db_employee:
        raise HTTPException(status_code=400, detail="Employee code already exists")
    
    # Check if email already exists
    db_employee = crud_employee.get_employee_by_email(db, employee.email)
    if db_employee:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    return crud_employee.create_employee(db=db, employee=employee)

@router.get("/", response_model=EmployeeList)
def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Lấy danh sách nhân viên với phân trang và filter"""
    employees, total = crud_employee.get_employees(
        db=db, 
        skip=skip, 
        limit=limit,
        search=search,
        department=department,
        is_active=is_active
    )
    
    return EmployeeList(
        employees=employees,
        total=total,
        page=skip // limit + 1,
        size=len(employees)
    )

@router.get("/{employee_id}", response_model=Employee)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    """Lấy thông tin nhân viên theo ID"""
    db_employee = crud_employee.get_employee(db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@router.put("/{employee_id}", response_model=Employee)
def update_employee(
    employee_id: int,
    employee_update: EmployeeUpdate,
    db: Session = Depends(get_db)
):
    """Cập nhật thông tin nhân viên"""
    db_employee = crud_employee.get_employee(db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check email uniqueness if email is being updated
    if employee_update.email:
        existing_employee = crud_employee.get_employee_by_email(db, employee_update.email)
        if existing_employee and existing_employee.id != employee_id:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    return crud_employee.update_employee(db=db, employee_id=employee_id, employee_update=employee_update)

@router.delete("/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    """Xóa nhân viên"""
    db_employee = crud_employee.get_employee(db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    crud_employee.delete_employee(db=db, employee_id=employee_id)
    return {"message": "Employee deleted successfully"}

@router.get("/departments/list")
def get_departments(db: Session = Depends(get_db)):
    """Lấy danh sách các phòng ban"""
    departments = crud_employee.get_departments(db)
    return [dept[0] for dept in departments if dept[0]]