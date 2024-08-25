from pydantic import BaseModel


class GoogleSheet(BaseModel):
    sheet_name: str