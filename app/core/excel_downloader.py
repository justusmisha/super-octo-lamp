import googleapiclient

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app_logging import logger

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def google_logger(SCOPES):
    creds = Credentials.from_authorized_user_file("C:/Users/yustu/ParserBack/ParserBack/app/database/data/token.json", SCOPES)
    return creds


class Downloader:
    def __init__(self, title, geo, number, views, description, description_html, photos, profile_link, product_link, rating):
        self.title = title
        self.geo = geo
        self.number = number
        self.views = views
        self.description = description
        self.description_html = description_html
        self.photos = photos
        self.profile_link = profile_link
        self.product_link = product_link
        self.rating = rating

    def export_to_google(self, spreadsheet_id, range_name, value_input_option):
        creds = google_logger(SCOPES)

        try:
            service = build("sheets", "v4", credentials=creds)

            values = [
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
                ],
            ]
            body = {"values": values}
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
            logger.info(f"{(result.get('updates').get('updatedCells'))} cells appended.")
            return result

        except HttpError as err:
            logger.warn(err)


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




