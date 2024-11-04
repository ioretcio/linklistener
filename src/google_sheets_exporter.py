import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

class GoogleSheetsExporter:
    def __init__(self, CREDENTIALS_FILE):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_FILE,
            ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        )
        self.service = apiclient.discovery.build('sheets', 'v4', http=credentials.authorize(httplib2.Http()))
        self.drive_service = apiclient.discovery.build('drive', 'v3', http=credentials.authorize(httplib2.Http()))
        self.editor_emails = ["goncharukyou@gmail.com"]

    def create_spreadsheet(self, title):
        spreadsheet = {
            'properties': {'title': title}
        }
        spreadsheet = self.service.spreadsheets().create(body=spreadsheet).execute()
        spreadsheet_id = spreadsheet['spreadsheetId']

        self.share_with_user(spreadsheet_id, self.editor_emails)
        
        return spreadsheet_id


    def append_data(self, spreadsheet_id, range_name, data):
        body = {'values': data}
        self.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()

    def share_with_user(self, spreadsheet_id, emails):
        """Grant edit access to the specified email for the given spreadsheet if not already granted."""
        # Retrieve existing permissions, requesting the 'emailAddress' and 'role' fields
        for email in emails:
            permissions = self.drive_service.permissions().list(
                fileId=spreadsheet_id,
                fields="permissions(id, emailAddress, role)"
            ).execute()
            
            # Check if the specified email already has edit access
            for permission in permissions.get('permissions', []):
                if permission.get('emailAddress') == email and permission.get('role') == 'writer':
                    print(f"Edit access already granted to {email} for spreadsheet {spreadsheet_id}.")
                    return  # Permission already exists, no need to grant again

            # Grant edit access if no existing permission found
            new_permission = {
                'type': 'user',
                'role': 'writer',
                'emailAddress': email  # Use the email address here
            }
            self.drive_service.permissions().create(
                fileId=spreadsheet_id,
                body=new_permission,
                fields='id'
            ).execute()
            print(f"Granted edit access to {email} for spreadsheet {spreadsheet_id}.")
