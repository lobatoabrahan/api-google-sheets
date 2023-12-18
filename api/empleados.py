# empleado.py
from fastapi import APIRouter
from pydantic import BaseModel
from .sheets import connect_to_sheet

class Employee(BaseModel):
    name: str
    role: str

router = APIRouter()

# Open the Google Spreadsheet by its name
sheet = connect_to_sheet("asistencia")

@router.get("/empleados")
async def get_records():
    # Get all records from the Google Spreadsheet
    records = sheet.worksheet("empleados").get_all_records()
    return {"data": records}

@router.post("/empleados")
async def create_employee(employee: Employee):
    # Append a new record to the Google Spreadsheet
    sheet.worksheet("empleados").append_row([employee.name, employee.role])
    return {"message": "Employee created"}