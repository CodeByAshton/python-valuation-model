import pandas as pd
import numpy as np
import os
import yfinance as yf
from numpy.testing.print_coercion_tables import print_new_cast_table

from schema import HistoricalFinancials

userInput = "TSLA"
ticker = yf.Ticker(userInput)

#importing financial statements
income_stmt = pd.DataFrame(ticker.financials)
balance_sheet = pd.DataFrame(ticker.balance_sheet)
cash_flow = pd.DataFrame(ticker.cash_flow)

pd.set_option("display.float_format", lambda x: f"{x:,.2f}")

# Functions
def cleandata(dataframe):
    dataframe.index = dataframe.index.str.lower()
    dataframe.index = dataframe.index.str.replace(' ', '_')
    dataframe = dataframe.apply(pd.to_numeric, errors="coerce").fillna(0)
    return dataframe

def refactor(income_stmt,cash_flow,balance_sheet):
    income_stmt = cleandata(income_stmt)
    cash_flow = cleandata(cash_flow)
    balance_sheet = cleandata(balance_sheet)

    # Revenue Dict
    total_revenue = income_stmt.loc['total_revenue']
    years = pd.to_datetime(total_revenue.index).year
    total_revenue.index = years
    print('--- Total Revenue ---')
    print(total_revenue)

    #Operating Expense Dict
    operating_expenses = income_stmt.loc['gross_profit'] - income_stmt.loc['operating_income']
    operating_expenses.index = years
    operating_expenses.name = 'operating_expenses'
    print('--- Operating Expenses ---')
    print(operating_expenses)

    # Depreciation Dict
    depreciation = income_stmt.loc['reconciled_depreciation']
    depreciation.index = years
    depreciation.name = 'depreciation'
    print('--- Depreciation ---')
    print(depreciation)

    #Capex Dict
    capex = cash_flow.loc['capital_expenditure']
    capex.index = years
    capex.name = 'capex'
    print('--- Capex ---')
    print(capex)

    #nwc
 ### NEED THIS



# Income Statement Data
cleandata(balance_sheet)
print(balance_sheet.)
refactor(income_stmt,cash_flow,balance_sheet)
