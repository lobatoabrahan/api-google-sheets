# sheets.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def connect_to_sheet(sheet_name):
    # Use the service account credentials to access the Google Sheets API
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('./api/keys.json', scope)
    client = gspread.authorize(creds)

    # Open the Google Spreadsheet by its name
    sheet = client.open(sheet_name)

    return sheet