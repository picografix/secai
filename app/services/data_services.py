from typing import Dict, Any
from services.cache_services import cached
import random
from edgar import *
from edgar.financials import Financials
from services.llm.get_header import QA

finQA = QA()
set_identity('secai secai@secai.com')
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
    # report = await get_report(ticker, year, force_reload=force_reload)
    # data = await get_data(report, header, sheet_name, force_reload=force_reload)
    data = await get_financial_data(ticker, header, sheet_name, year)
    resp = {
        "ticker": ticker,
        "year": year,
        "header": header,
        "sheet_name": sheet_name,
        "extracted_data": data
    }
    return resp

@cached
async def get_financial_data(ticker: str, header: str, sheet_name: str, year: str , quarter: str = None):
    #  now we have company name, header, sheet_name, year or quarter
    #  first we have to fetch the report 
    # then we have to parse the data
    
    # fetch report 
    filings = None
    if quarter is None:
        # fetch 10K report
        filing_date = f"{year}-01-01:{year}-12-31"
        filing = Company(ticker).get_filings(form='10-K', filing_date=filing_date).latest(1)
        
    else:
        # fetch quaterly report
        filing_date = None
        if quarter == 1:
            filing_date = f"{year}-01-01:{year}-03-31"
        elif quarter == 2:
            filing_date = f"{year}-04-01:{year}-06-30"
        elif quarter == 3:
            filing_date = f"{year}-07-01:{year}-09-30"
        elif quarter == 4:
            filing_date = f"{year}-10-01:{year}-12-31"
        else:
            raise ValueError("Invalid quarter")
        filing = Company(ticker).get_filings(form='10-Q', filing_date=filing_date).latest(1)
    
    if filing is None:
        return f"No data found for {ticker}"
        
    financials = Financials.from_xbrl(filing.xbrl())
    statement = get_statement(sheet_name, financials)
    statement_data = statement.to_dataframe()
    if header in statement_data['Label'].to_list():
        key = header
    else:
        header_list = statement_data['Label'].to_list()
        my_header = await finQA.acall(header, header_list)
        key = my_header.data.key

    column_list = statement_data.columns.to_list()[1:]
    my_column = await finQA.acall(year, column_list)
    
    column = my_column.data.key
    data = statement_data.loc[statement_data['Label'] == key, column].values[0]
    return int(data)
        
        


def get_statement(sheet_name, financials):
    
    if sheet_name == "balance_sheet":
        return financials.balance_sheet
    elif sheet_name == "income_statement":
        return financials.income_statement
    elif sheet_name == "cash_flow_statement":
        return financials.cash_flow_statement
    else:
        raise ValueError("Invalid sheet name")
    
        