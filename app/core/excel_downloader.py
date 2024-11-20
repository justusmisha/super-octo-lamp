import googleapiclient

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app_logging import logger

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def google_logger(SCOPES):
    creds = Credentials.from_authorized_user_file("./app/database/data/token.json", SCOPES)
    return creds


class Downloader:
    def __init__(self, title=None, geo=None, number=None, views=None, description=None,
                 description_html=None, photos=None, profile_link=None, product_link=None,
                 rating=None):
        self.title = title or ''
        self.geo = geo or ''
        self.number = number or ''
        self.views = views or ''
        self.description = description or ''
        self.description_html = description_html or ''
        self.photos = photos or ''
        self.profile_link = profile_link or ''
        self.product_link = product_link or ''
        self.rating = rating or ''

    def _get_values(self):
        """
        Prepares the data in the correct format for Google Sheets.
        """
        return [
            [
                self.number,
                self.title,
                self.geo,
                self.description,
                self.description_html,
                self.photos,
                self.views,
                self.rating,
                self.product_link,
                self.profile_link,
            ]
        ]

    def _get_google_service(self):
        """
        Returns an authenticated Google Sheets service.
        """
        creds = google_logger(SCOPES)
        try:
            return build("sheets", "v4", credentials=creds)
        except Exception as err:
            logger.error(f"Failed to build Google Sheets service: {err}")
            raise

    def _append_to_sheet(self, service, spreadsheet_id, range_name, value_input_option, body):
        """
        Appends the given data to the Google Sheets document.
        """
        try:
            result = (
                service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption=value_input_option,
                    body=body,
                )
                .execute()
            )
            return result
        except HttpError as err:
            logger.error(f"Failed to append data to Google Sheets: {err}")
            raise

    def export_to_google(self, spreadsheet_id, range_name, value_input_option):
        """
        Exports the current data to a Google Sheets spreadsheet.
        """
        service = self._get_google_service()
        values = self._get_values()

        values = [[str(cell) if isinstance(cell, (list, dict)) else cell for cell in row] for row in values]

        body = {"values": values}

        try:
            result = self._append_to_sheet(service, spreadsheet_id, range_name, value_input_option, body)
            updated_cells = result.get("updates", {}).get("updatedCells", 0)
            logger.info(f"{updated_cells} cells appended.")
            return result
        except Exception as err:
            logger.error(f"Error exporting data to Google Sheets: {err}")


async def create_new_sheet(query_name, spreadsheet_id, clear=True):
    creds = google_logger(SCOPES)
    service = build('sheets', 'v4', credentials=creds)

    spreadsheet_id = ''.join(spreadsheet_id)
    sheet_exists = False
    sheet = None

    try:
        sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()

        sheets = sheet_metadata.get('sheets', [])
        for s in sheets:
            title = s.get('properties', {}).get('title', '')
            if title == query_name:
                sheet_exists = True
                sheet = s

    except HttpError as err:
        logger.warning(f"An error occurred while retrieving sheet metadata: {err}")
        return False

    if sheet_exists:
        logger.info(f"A sheet with the name '{query_name}' already exists.")
        if clear:
            if sheet is not None:
                clear_request = {
                    'requests': [{
                        'updateCells': {
                            'range': {
                                'sheetId': sheet['properties']['sheetId']
                            },
                            'fields': 'userEnteredValue'
                        }
                    }]
                }

                try:
                    service.spreadsheets().batchUpdate(
                        spreadsheetId=spreadsheet_id,
                        body=clear_request
                    ).execute()
                    logger.info("Existing data cleared.")
                except HttpError as err:
                    logger.warn(f"An error occurred while clearing existing data: {err}")
                    return False

        return False

    sheet_body = {
        'requests': [{
            'addSheet': {
                'properties': {
                    'title': query_name
                }
            }
        }]
    }

    try:
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=sheet_body
        ).execute()
        logger.info(f"Sheet '{query_name}' created successfully.")
        return True
    except HttpError as err:
        logger.warn(f"An error occurred while creating the sheet: {err}")
        return False


async def create_google_dock(sheet_name):
    creds = google_logger(SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    spreadsheet = {
        'properties': {
            'title': sheet_name
        }
    }
    spreadsheet = service.spreadsheets().create(body=spreadsheet,
                                                fields='spreadsheetId').execute()
    drive_service = googleapiclient.discovery.build('drive', 'v3', credentials=creds)
    batch = drive_service.new_batch_http_request()
    user_permission = {
        'type': 'anyone',
        'role': 'writer',
    }
    batch.add(drive_service.permissions().create(
        fileId=spreadsheet['spreadsheetId'],
        body=user_permission,
        fields='id',
    ))
    batch.execute()
    return spreadsheet['spreadsheetId']




