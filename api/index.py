from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import gspread

# Define your data models with Pydantic
class Employee(BaseModel):
    name: str
    role: str

def create_app():
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Use the service account credentials to access the Google Sheets API
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('./api/keys.json', scope)
    client = gspread.authorize(creds)

    # Open the Google Spreadsheet by its name
    sheet = client.open("asistencia")

    @app.get("/empleados")
    async def get_records():
        # Get all records from the Google Spreadsheet
        records = sheet.worksheet("empleados").get_all_records()
        return {"data": records}
    
    @app.post("/empleados")
    async def create_employee(employee: Employee):
        # Append a new record to the Google Spreadsheet
        sheet.worksheet("empleados").append_row([employee.name, employee.role])
        return {"message": "Employee created"}

    return app

app = create_app()