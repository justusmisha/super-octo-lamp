from pydantic import BaseModel


class OneLink(BaseModel):
    google_sheet_name: str
    url: str


class SaveByQuery(BaseModel):
    query: str
    page_numbers: int
    city: str


class ParserExecute(BaseModel):
    google_sheet_name: str
    query_id: int


class QueryDelete(BaseModel):
    query_name: str


class AddSeller(BaseModel):
    url: str


class ParseSeller(BaseModel):
    page_numbers: str
    seller_name: str
    google_sheet: str


class SellerDelete(BaseModel):
    seller_name: str