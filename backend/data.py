
import pandas as pd
import datetime
import yfinance as yf
from schema import HistoricalFinancials, ForecastAssumptions, DiscountInputs

userInput = "TSLA"
ticker = yf.Ticker(userInput)
info = ticker.info
current_year = int(datetime.date.today().year) - 1

#importing financial statements
income_stmt = pd.DataFrame(ticker.financials)
balance_sheet = pd.DataFrame(ticker.balance_sheet)
cash_flow = pd.DataFrame(ticker.cash_flow)

pd.set_option("display.float_format", lambda x: f"{x:,.2f}")

# Functions

# Cleans the data to ensure proper indexing & replaces NaN with 0
def cleandata(dataframe):
    dataframe.index = dataframe.index.str.lower()
    dataframe.index = dataframe.index.str.replace(' ', '_')
    dataframe = dataframe.apply(pd.to_numeric, errors="coerce").fillna(0)
    return dataframe

# turns a pandas data series into a dictionary
def createdict(s: pd.Series) -> dict[int, float]:
    out = {}
    for k, v in s.items():
        try:
            year = int(str(k)[:4])
        except ValueError:
            continue
        if pd.notna(v):
            out[year] = float(v)
    return out

# pulls financial statements to create a financials object
def financials(income_stmt,cash_flow,balance_sheet):
    income_stmt = cleandata(income_stmt)
    cash_flow = cleandata(cash_flow)
    balance_sheet = cleandata(balance_sheet)

    # Pulling Name
    name = info.get('shortName')

    # Revenue
    total_revenue = income_stmt.loc['total_revenue']
    years = pd.to_datetime(total_revenue.index).year
    total_revenue.index = years
    total_revenue = createdict(total_revenue)

    #Operating Expense
    operating_expenses = income_stmt.loc['gross_profit'] - income_stmt.loc['operating_income']
    operating_expenses.index = years
    operating_expenses.name = 'operating_expenses'
    operating_expenses = createdict(operating_expenses)

    # Ebit
    ebit = income_stmt.loc['ebit']
    ebit.index = years
    ebit.name = 'ebit'
    ebit = createdict(ebit)

    # Depreciation
    depreciation = income_stmt.loc['reconciled_depreciation']
    depreciation.index = years
    depreciation.name = 'depreciation'
    depreciation = createdict(depreciation)

    # Capex
    capex = cash_flow.loc['capital_expenditure']
    capex.index = years
    capex.name = 'capex'
    capex = createdict(capex)

    # Net Working Capital
    net_a = balance_sheet.loc['current_assets'] - balance_sheet.loc['cash_and_cash_equivalents']
    net_l = balance_sheet.loc['current_liabilities'] -  balance_sheet.loc['current_debt']
    nwc = net_a - net_l
    nwc.index = years
    nwc.name = 'nwc'
    nwc = createdict(nwc)

    # Interest Expense
    interest_expense = cash_flow.loc['interest_paid_supplemental_data']
    interest_expense.index = years
    interest_expense.name = 'intrest_expense'
    interest_expense = createdict(interest_expense)


    # Outstanding Debt
    debt_outstanding = balance_sheet.loc['total_debt']
    debt_outstanding.index = years
    debt_outstanding.name = 'debt_outstanding'
    debt_outstanding = createdict(debt_outstanding)

    # tax rate
    tax = income_stmt.loc['tax_rate_for_calcs']
    tax.index = years
    tax.name = 'tax_rate'
    tax = createdict(tax)

    # creating object
    company_data = HistoricalFinancials(
        name=name,
        ticker=userInput,
        currency='USD',
        revenue = total_revenue,
        operating_expense = operating_expenses,
        ebit = ebit,
        depreciation = depreciation,
        capex = capex,
        nwc = nwc,
        interest_expense = interest_expense,
        debt_outstanding = debt_outstanding,
        tax_rate = tax
        )

    return company_data

def assumptions(company_financials):
    horizon_years = 3 # default, will be user input

    # Calculating revenue growth rate
    revenue_series = pd.Series(company_financials.revenue).sort_index()
    growth_rates = revenue_series.pct_change().dropna()
    growth_rate = growth_rates.mean()

    # Calculating EBIT Margin
    ebit_series = pd.Series(company_financials.ebit).sort_index()
    ebit_margins = revenue_series - ebit_series
    ebit_margins = ebit_margins.pct_change().dropna()
    ebit_margin = ebit_margins.mean()

    # Dep / Sales
    depreciation_series = pd.Series(company_financials.depreciation).sort_index()
    depreciation_pct_series = depreciation_series / revenue_series
    depreciation_pct = depreciation_pct_series.mean()

    # Capex / Sales
    capex_series = pd.Series(company_financials.capex).sort_index()
    capex_pct_series = capex_series / revenue_series
    capex_pct = capex_pct_series.mean()

    # NWC / Sales
    nwc_series = pd.Series(company_financials.nwc).sort_index()
    nwc_pct_series = nwc_series / revenue_series
    nwc_pct = nwc_pct_series.mean()

    # terminal growth
    terminal_growth = .03 # assumption

    assumption_data = ForecastAssumptions(
        horizon_years = horizon_years,
        revenue_growth_rate=growth_rate,
        ebit_margin=ebit_margin,
        depreciation_pct=depreciation_pct,
        capex_pct=capex_pct,
        nwc_pct=nwc_pct,
        terminal_growth_rate=terminal_growth
    )

    return assumption_data

# Getting Discount Data
def discountdata(company_data,assumption_data):

    # Risk Fee Rate
    tnx = yf.Ticker("^TNX")
    yield_series = tnx.history(period=f'{assumption_data.horizon_years}y')["Close"] / 100
    average_risk_free_rate = yield_series.mean()

    # Equity Risk premium
    spy = yf.Ticker("SPY")
    equity_series = spy.history(period=f'{assumption_data.horizon_years}y')["Close"] / 100
    average_equity_rate = equity_series.mean()
    equity_risk_premium = average_equity_rate - average_risk_free_rate

    # Beta
    stock_series = ticker.history(f'{assumption_data.horizon_years}y')["Close"] / 100
    beta = stock_series.cov(equity_series) / equity_series.var()

    # Cost of Debt
    pre_tax_debt = company_data.interest_expense[current_year] / company_data.debt_outstanding[current_year]
    cost_of_debt = pre_tax_debt * (1-company_data.tax_rate[current_year])

    # Equity Weight
    market_cap = info['marketCap']
    debt = company_data.debt_outstanding[current_year]
    equity_weight = market_cap / (market_cap + debt)

    # Debt Weight
    debt_weight = debt / (market_cap + debt)

    discount_data = DiscountInputs(
        risk_free_rate=average_risk_free_rate,
        equity_risk_premium=equity_risk_premium,
        beta=beta,
        cost_of_debt=cost_of_debt,
        equity_weight=equity_weight,
        debt_weight=debt_weight,
    )

    return discount_data

# Storing the Data

company_obj = financials(income_stmt,cash_flow,balance_sheet)
assumptions_obj = assumptions(company_obj)
discount_obj = discountdata(company_obj,assumptions_obj)
