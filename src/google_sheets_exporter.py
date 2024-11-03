import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

CREDENTIALS_FILE = 'path_to_your_credentials.json'

class GoogleSheetsExporter:
    def __init__(self, creds_file):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_FILE,
            ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        )
        self.service = apiclient.discovery.build('sheets', 'v4', http=credentials.authorize(httplib2.Http()))

    def create_spreadsheet(self, title):
        spreadsheet = {
            'properties': {'title': title}
        }
        spreadsheet = self.service.spreadsheets().create(body=spreadsheet).execute()
        return spreadsheet['spreadsheetId']

    def create_tab(self, spreadsheet_id, tab_name):
        requests = [{
            'addSheet': {
                'properties': {
                    'title': tab_name
                }
            }
        }]
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()

    def append_data(self, spreadsheet_id, range_name, data):
        body = {'values': data}
        self.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
