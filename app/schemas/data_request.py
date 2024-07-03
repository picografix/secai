from pydantic import BaseModel

class DataRequest(BaseModel):
    header: str
    year: str
    sheetName: str
    ticker: str
    force_reload: bool = False