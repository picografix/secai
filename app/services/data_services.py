import logging
from typing import Dict, Any, Optional
from datetime import datetime
from edgar import Company
from edgar.financials import Financials
from edgar.core import set_identity
from services.cache_services import cached
from services.llm.get_header import QA
from fastapi import HTTPException
import pandas
import random
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize QA service
fin_qa = QA()
def generate_random_id_email():
    """
    Generate a random ID and email for Edgar API.
    """
    username = f"secai_{random.randint(1000, 9999)}"
    email = f"{username}@secai.com"
    return f'{username} {email}'
# Set identity for Edgar API
set_identity(generate_random_id_email())



@cached
async def get_report(ticker: str, year: str, force_reload: bool = False) -> Dict[str, Any]:
    """
    Fetch financial report for a given ticker and year.
    This is a placeholder function and should be implemented with actual logic.
    """
    logger.info(f"Fetching report for ticker: {ticker}, year: {year}")
    return {"ticker": ticker, "year": year, "report_data": "Sample report data"}

@cached
async def get_data(report: Dict[str, Any], header: str, sheet_name: str, force_reload: bool = False) -> Dict[str, Any]:
    """
    Extract specific data from a financial report.
    This is a placeholder function and should be implemented with actual logic.
    """
    logger.info(f"Extracting data for header: {header}, sheet: {sheet_name}")
    return {
        "report": report,
        "header": header,
        "sheet_name": sheet_name,
        "extracted_data": "Sample extracted data"
    }

async def get_data_api(header: str, year: str, sheet_name: str, ticker: str, force_reload: bool = False) -> Dict[str, Any]:
    """
    Main API function to fetch financial data.
    """
    logger.info(f"API call received for ticker: {ticker}, year: {year}, sheet: {sheet_name}, header: {header}")
    try:
        data = await get_financial_data(ticker, header, sheet_name, year)
        return {
            "ticker": ticker,
            "year": year,
            "header": header,
            "sheet_name": sheet_name,
            "extracted_data": data
        }
    except ValueError as ve:
        logger.error(f"Value error in get_data_api: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as he:
        logger.error(f"HTTP exception in get_data_api: {str(he)}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in get_data_api: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@cached
async def get_financial_data(ticker: str, header: str, sheet_name: str, year: str, quarter: Optional[int] = None) -> int:
    """
    Fetch and extract specific financial data from Edgar filings.
    """
    logger.info(f"Fetching financial data for ticker: {ticker}, year: {year}, quarter: {quarter}")
    try:
        filing = await fetch_filing(ticker, year, quarter)
        if filing is None:
            raise ValueError(f"No filing found for {ticker} in {year}")

        financials = Financials.from_xbrl(filing.xbrl())
        statement = get_statement(sheet_name, financials)
        statement_data = statement.to_dataframe()
        logger.info(f"Statement data: {statement_data}")
        key = await get_matching_header(header, statement_data)
        column = await get_matching_column(year, statement_data)

        data = statement_data.loc[statement_data['Label'] == key, column].values[0]
        
        if isinstance(data, pandas._libs.missing.NAType):
            return "Data not found"
        
        logger.info(f"Extracted data: {data}")
        return int(data)
    except ValueError as ve:
        logger.error(f"Value error in get_financial_data: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error processing financial data: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error processing financial data")

async def fetch_filing(ticker: str, year: str, quarter: Optional[int] = None) -> Any:
    """
    Fetch the appropriate filing (10-K or 10-Q) based on the given parameters.
    """
    logger.info(f"Fetching filing for ticker: {ticker}, year: {year}, quarter: {quarter}")
    try:
        company = Company(ticker)
        if quarter is None:
            filing_date = f"{year}-01-01:{int(year)+1}-01-31"
            return company.get_filings(form='10-K', filing_date=filing_date).latest(1)
        else:
            filing_date = get_quarter_date_range(year, quarter)
            return company.get_filings(form='10-Q', filing_date=filing_date).latest(1)
    except Exception as e:
        logger.error(f"Error fetching filing: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching filing")

def get_quarter_date_range(year: str, quarter: int) -> str:
    """
    Get the date range for a specific quarter.
    """
    quarters = {
        1: (f"{year}-01-01", f"{year}-03-31"),
        2: (f"{year}-04-01", f"{year}-06-30"),
        3: (f"{year}-07-01", f"{year}-09-30"),
        4: (f"{year}-10-01", f"{year}-12-31")
    }
    if quarter not in quarters:
        logger.error(f"Invalid quarter: {quarter}")
        raise ValueError(f"Invalid quarter: {quarter}")
    start, end = quarters[quarter]
    return f"{start}:{end}"

def get_statement(sheet_name: str, financials: Financials) -> Any:
    """
    Get the appropriate financial statement based on the sheet name.
    """
    statements = {
        "balance_sheet": financials.balance_sheet,
        "income_statement": financials.income_statement,
        "cash_flow_statement": financials.cash_flow_statement
    }
    if sheet_name not in statements:
        logger.error(f"Invalid sheet name: {sheet_name}")
        raise ValueError(f"Invalid sheet name: {sheet_name}")
    return statements[sheet_name]

async def get_matching_header(header: str, statement_data: Any) -> str:
    """
    Get the matching header from the statement data.
    """
    logger.info(f"Getting matching header for: {header}")
    if header in statement_data['Label'].to_list():
        return header
    header_list = statement_data['Label'].to_list()
    try:
        my_header = await fin_qa.acall(header, header_list)
        return my_header.data.key
    except Exception as e:
        logger.error(f"Error getting matching header: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error matching header")

async def get_matching_column(year: str, statement_data: Any) -> str:
    """
    Get the matching column for the given year from the statement data.
    """
    logger.info(f"Getting matching column for year: {year}")
    column_list = statement_data.columns.to_list()[1:]
    try:
        my_column = await fin_qa.acall(year, column_list)
        return my_column.data.key
    except Exception as e:
        logger.error(f"Error getting matching column: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error matching column")