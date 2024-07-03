from typing import Dict, Any
from services.cache_services import cached
import random
@cached
async def get_report(ticker: str, year: str, force_reload: bool = False) -> Dict[str, Any]:
    # Implement report fetching logic here
    return {"ticker": ticker, "year": year, "report_data": "Sample report data"}

@cached
async def get_data(report: Dict[str, Any], header: str, sheet_name: str, force_reload: bool = False) -> Dict[str, Any]:
    # Implement data extraction logic here
    data = random.randint(1, 100)
    return {
        "report": report,
        "header": header,
        "sheet_name": sheet_name,
        "extracted_data": data
    }

# @cached
async def get_data_api(header: str, year: str, sheet_name: str, ticker: str, force_reload: bool = False) -> Dict[str, Any]:
    report = await get_report(ticker, year, force_reload=force_reload)
    data = await get_data(report, header, sheet_name, force_reload=force_reload)
    return data