import gspread
from oauth2client.service_account import ServiceAccountCredentials

def create_app():
    app = Flask(__name__)
    app.secret_key = 'oiasjdofpj4523p46j3o456'  # Reemplaza 'your-secret-key' con una clave secreta única

# Use the service account credentials to access the Google Sheets API
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('./api/keys.json', scope)
    client = gspread.authorize(creds)
    
return app